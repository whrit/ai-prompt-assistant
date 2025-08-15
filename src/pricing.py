# src/pricing.py
import json
from .storage import APP_DIR

PRICING_PATH = APP_DIR / "pricing.json"

DEFAULT_PRICING = {
    "chatgpt_web": {"web": {"in": 0.0, "out": 0.0, "ctx": 0}},
    "openai": {
        "gpt-4o-mini": {"in": 0.00015, "out": 0.00060, "ctx": 128000},
        "gpt-4.1":     {"in": 0.00500,  "out": 0.01500, "ctx": 128000}
    },
    "anthropic": {
        "claude-3-5-sonnet": {"in": 0.00300, "out": 0.01500, "ctx": 200000},
        "claude-3-5-haiku":  {"in": 0.00080, "out": 0.00400, "ctx": 200000}
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