import json
import os
from pathlib import Path
from typing import Any, Dict

APP_DIR = Path(os.path.expanduser("~/Library/Application Support/AI Prompt Assistant"))
APP_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = APP_DIR / "config.json"

DEFAULTS = {
    "favorites": [],
    "ab_choice": {},
    "redaction_enabled": True,
    "last_service": "chatgpt",
    "service": "chatgpt_web",
    "model": "web",
    "api_keys": {},      # {"openai":"...", "anthropic":"...", "ollama_url":"http://localhost:11434"}
    "pricing": None,     # kept for backward compat; not used now that pricing.json exists
    "lat_ema": {}
}

def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            return {**DEFAULTS, **json.loads(CONFIG_PATH.read_text())}
        except Exception:
            pass
    return DEFAULTS.copy()

def save_config(cfg: Dict[str, Any]) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))

def add_favorite(name: str, content: str):
    cfg = load_config()
    if not any(f["name"] == name and f["content"] == content for f in cfg["favorites"]):
        cfg["favorites"].append({"name": name, "content": content})
        save_config(cfg)

def remove_favorite(name: str, content: str):
    cfg = load_config()
    cfg["favorites"] = [f for f in cfg["favorites"] if not (f["name"] == name and f["content"] == content)]
    save_config(cfg)
