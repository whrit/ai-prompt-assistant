# src/pricing.py
import json
from .storage import APP_DIR

PRICING_PATH = APP_DIR / "pricing.json"

DEFAULT_PRICING = {
    "chatgpt_web": {"web": {"in": 0.0, "out": 0.0, "ctx": 0}},
    "openai": {
        "gpt-5":       {"in": 0.00125, "out": 0.01000, "ctx": 128000, "cached_in": 0.000125},
        "gpt-5-mini":  {"in": 0.00025, "out": 0.00200, "ctx": 128000, "cached_in": 0.000025}
    },
    "anthropic": {
        "claude-sonnet-4": {
            "in": 0.00300, "out": 0.01500, "ctx": 200000,
            "in_large": 0.00600, "out_large": 0.02250,
            "cache_write": 0.00375, "cache_read": 0.00030,
            "cache_write_large": 0.00750, "cache_read_large": 0.00060
        },
        "claude-haiku-3.5": {
            "in": 0.00080, "out": 0.00400, "ctx": 200000,
            "cache_write": 0.00100, "cache_read": 0.00008
        }
    },
    "ollama": {
        "llama3.1:8b":  {"in": 0.0, "out": 0.0, "ctx": 131072},
        "llama3.1:70b": {"in": 0.0, "out": 0.0, "ctx": 131072}
    }
}

def ensure_pricing_file():
    if not PRICING_PATH.exists():
        PRICING_PATH.write_text(json.dumps(DEFAULT_PRICING, indent=2))

def load_pricing() -> dict:
    ensure_pricing_file()
    try:
        return json.loads(PRICING_PATH.read_text())
    except Exception:
        # fall back to defaults if file is corrupted
        return DEFAULT_PRICING

def save_pricing(data: dict):
    PRICING_PATH.write_text(json.dumps(data, indent=2))