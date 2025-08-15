# src/services.py
import time
import json
import requests
from typing import Dict, Tuple, Iterable, Callable, Optional
from .storage import load_config, save_config
from .pricing import load_pricing

def _cfg_pricing() -> Dict:
    return load_pricing()

def list_services_models() -> Dict[str, Dict[str, Dict]]:
    return _cfg_pricing()

def model_exists(provider: str, model: str) -> bool:
    return model in (_cfg_pricing().get(provider, {}) or {})

def _provider_requires_key(provider: str) -> str:
    # returns the key name expected in config["api_keys"], or "" if none
    return {"openai": "openai", "anthropic": "anthropic"}.get(provider, "")

def _ollama_base(keys: Dict) -> str:
    return keys.get("ollama_url", "http://localhost:11434")

def validate_ready(provider: str, model: str) -> Tuple[bool, str]:
    """
    Returns (ok, message). If not ok, 'message' explains what's wrong.
    """
    # 1) model exists?
    if not model_exists(provider, model):
        return False, f"Model '{model}' does not exist under service '{provider}'. Please choose a valid model in Service & Model…"

    # 2) provider-specific configuration checks
    if provider == "chatgpt_web":
        return True, ""  # browser-based, no keys

    cfg = load_config()
    keys = cfg.get("api_keys", {})

    required = _provider_requires_key(provider)
    if required and not keys.get(required):
        return False, f"Missing API key for {provider}. Set it in Prompt Lab (e.g., '{required}_key:<value>')."

    if provider == "ollama":
        base = _ollama_base(keys)
        try:
            # quick probe to see if daemon is reachable
            r = requests.get(base.rstrip("/") + "/api/tags", timeout=2)
            if r.status_code >= 400:
                return False, f"Ollama daemon reachable but returned {r.status_code}. Check the server at {base}."
        except Exception:
            return False, f"Cannot reach Ollama daemon at {base}. Ensure it’s running or set ollama_url in Prompt Lab."
    return True, ""

def token_estimate(text: str) -> int:
    return max(1, int(len(text) / 4))

def estimate_cost_and_latency(prompt: str, provider: str, model: str, expected_output_tokens: int = 300) -> Tuple[float, float]:
    pricing = _cfg_pricing().get(provider, {}).get(model, {"in": 0.0, "out": 0.0})
    in_cost, out_cost = pricing.get("in", 0.0), pricing.get("out", 0.0)
    in_tokens = token_estimate(prompt)
    cost = (in_tokens / 1000.0) * in_cost + (expected_output_tokens / 1000.0) * out_cost
    defaults = {"chatgpt_web": 1.8, "openai": 2.0, "anthropic": 2.5, "ollama": 1.4}
    key = f"{provider}:{model}"
    cfg = load_config()
    ema = cfg.get("lat_ema", {}).get(key, defaults.get(provider, 2.0))
    return round(cost, 6), round(ema, 2)

def _update_latency_ema(provider: str, model: str, observed_seconds: float, alpha: float = 0.25):
    key = f"{provider}:{model}"
    cfg = load_config()
    lat = cfg.get("lat_ema", {}).get(key)
    new = observed_seconds if lat is None else alpha * observed_seconds + (1 - alpha) * lat
    cfg.setdefault("lat_ema", {})[key] = new
    save_config(cfg)

# ---------- Streaming ----------
def _openai_stream(prompt: str, model: str, api_key: str, stop_fn: Optional[Callable[[], bool]] = None) -> Iterable[str]:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": True, "max_tokens": 800}
    with requests.post(url, headers=headers, json=body, stream=True, timeout=300) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if stop_fn and stop_fn():
                try:
                    r.close()
                except Exception:
                    pass
                break
            if not line or not line.startswith("data:"): 
                continue
            if line.strip() == "data: [DONE]":
                break
            try:
                j = json.loads(line[len("data: "):])
                delta = j["choices"][0]["delta"].get("content")
                if delta:
                    yield delta
            except Exception:
                continue

def _anthropic_stream(prompt: str, model: str, api_key: str, stop_fn: Optional[Callable[[], bool]] = None) -> Iterable[str]:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {"model": model, "max_tokens": 800, "messages": [{"role": "user", "content": prompt}], "stream": True}
    with requests.post(url, headers=headers, json=body, stream=True, timeout=300) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if stop_fn and stop_fn():
                try:
                    r.close()
                except Exception:
                    pass
                break
            if not line or not line.startswith("data:"):
                continue
            try:
                j = json.loads(line[len("data: "):])
                # Look for content_block_delta or delta.text (varies by event type)
                if "delta" in j and isinstance(j["delta"], dict):
                    txt = j["delta"].get("text")
                    if txt:
                        yield txt
                elif j.get("type") == "content_block_delta":
                    txt = j.get("delta", {}).get("text")
                    if txt:
                        yield txt
            except Exception:
                continue

def _ollama_stream(prompt: str, model: str, base_url: str, stop_fn: Optional[Callable[[], bool]] = None) -> Iterable[str]:
    url = base_url.rstrip("/") + "/api/generate"
    with requests.post(url, json={"model": model, "prompt": prompt, "stream": True}, stream=True, timeout=300) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if stop_fn and stop_fn():
                try:
                    r.close()
                except Exception:
                    pass
                break
            if not line:
                continue
            try:
                j = json.loads(line)
                piece = j.get("response")
                if piece:
                    yield piece
            except Exception:
                continue

def stream_completion(provider: str, model: str, prompt: str, stop_fn: Optional[Callable[[], bool]] = None) -> Iterable[str]:
    cfg = load_config()
    keys = cfg.get("api_keys", {})
    if provider == "openai" and "openai" in keys:
        return _openai_stream(prompt, model, keys["openai"], stop_fn)
    if provider == "anthropic" and "anthropic" in keys:
        return _anthropic_stream(prompt, model, keys["anthropic"], stop_fn)
    if provider == "ollama":
        base = keys.get("ollama_url", "http://localhost:11434")
        return _ollama_stream(prompt, model, base, stop_fn)
    # No streaming available → empty generator
    def _empty():
        if False: yield ""  # pragma: no cover
    return _empty()

def route_and_send(prompt: str, provider: str, model: str) -> None:
    """Keep this for ChatGPT Web / fire-and-forget use cases."""
    import subprocess, webbrowser
    start = time.time()
    if provider == "chatgpt_web":
        try:
            subprocess.run(["/usr/bin/pbcopy"], input=prompt.encode("utf-8"))
        except Exception:
            pass
        webbrowser.open("https://chat.openai.com/")
        _update_latency_ema(provider, model, time.time() - start)
        return
    # API providers should use streaming path (see ui_streaming.route_with_popover)