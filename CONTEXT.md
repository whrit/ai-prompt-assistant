# AI Prompt Assistant — Implementation Context

**Last updated:** Aug 2025

This document summarizes the recent implementation work: architecture, features, UX flows, configuration, and extension points. Use it as a quick "source of truth" for what exists and how to build on it.

## Overview

The app is a macOS menubar assistant built on a single UI stack (rumps + light PyObjC views), focused on:

- **Fast capture** (selection or clipboard), visible PII redaction, and preview.
- **A/B Mode selection** (Baseline vs Optimized) right in a native NSAlert accessory.
- **A service & model router** (ChatGPT Web / OpenAI / Anthropic / Ollama) with cost & latency estimates.
- **Streaming for API providers** via a tiny popover (token count + live latency) that feeds results back into Preview.
- **Templates, Favorites, and a small Prompt Lab** for power-user configuration.
- **A pricing.json file** (editable without shipping code) + Manage Pricing… menu.

## UX at a glance (menubar items)

- **Ask…** — enter prompt (prefilled from selection/clipboard) → redaction → Preview (Mode selector) → Send (Web or stream).
- **Templates…** — pick from 10 curated templates; prefill `{context}` from selection/clipboard; same Preview & send flow; optional Favorite.
- **Favorites…** — open, edit, send; remove.
- **Prompt Lab…** — text commands to set A/B mode, redaction default, service/model, API keys/URL.
- **Service & Model…** — native dialog with two popups (service → dynamic models).
- **Manage Pricing…** — opens pricing.json in default editor.
- **Settings** — snapshot of current settings.
- **Quit**

Keyboard shortcut for Ask… is defined via the menu item's `key="@"` (⌘⇧2 by default; adjust as needed).

## Key features implemented

### 1) Single UI stack

- Consolidated on rumps for the status bar app.
- Small native UI pieces built with PyObjC:
  - Preview dialog with a Mode dropdown (Baseline/Optimized) and an editable text area (NSAlert accessory).
  - Service & Model… dialog with two popups; Model options update live when Service changes.
  - Streaming popover showing tokens + elapsed time; inserts completion back into Preview.

### 2) Selection + clipboard capture

- Attempts to read current selection via macOS Accessibility API (`AXSelectedText`).
- Fallbacks: `AXValue` (control value), then clipboard.
- First run prompts user to grant Accessibility access (System Settings → Privacy & Security → Accessibility).

### 3) Visible PII redaction

- Regex-based redaction for: emails, phone numbers, API-key-like strings, and URL tokens (token, apikey, key, signature).
- Shows count in Preview; you see exactly what will be sent.
- Toggle default in Prompt Lab… (on/off).

### 4) A/B Mode selection

- **Baseline:** send as-is.
- **Optimized:** applies small micro-transforms (safe, local; can be swapped for a real model call later).
- Remembers global choice (adhoc) and per-template choice.

### 5) Service & model router + estimates

- Providers: `chatgpt_web`, `openai`, `anthropic`, `ollama`.
- Cost estimate based on pricing.json (USD per 1K tokens; input + default 300 output tokens).
- Latency estimate is an EMA updated from actual calls (used for the "~Xs" shown in Preview).

### 6) Streaming + popover + re-preview

- For API providers: stream tokens (SSE or long-poll) into a small popover with token count + elapsed time.
- On completion, re-open Preview with prompt + streamed answer for final edits.
- One-click copy and optional Favorite.

### 7) Templates & Favorites

- 10 curated templates (email reply, bug report, meeting notes → actions, job tailoring, SQL helper, code fix, exec summary, brainstorm, translate, tasks extract).
- Favorites can be saved from the Ask… and Templates… flows. Stored as name + content.

### 8) Pricing as data (pricing.json) + Manage Pricing…

- `pricing.json` seeded on first run, then editable without code changes.
- Manage Pricing… opens the file for quick updates (add/rename models, adjust prices, tweak context limits, etc.).

### 9) Validation & helpful warnings

- Validates that the chosen model exists for the service.
- For OpenAI/Anthropic, warns if the API key is missing.
- For Ollama, probes the daemon (`/api/tags`) and warns if unreachable.

## Files added/updated

```
src/
  app.py                      # menubar app (menu, flows, validation, favorites prompts)
  storage.py                  # config load/save; favorites; paths
  redaction.py                # regex-based redaction
  templates.py                # 10 curated templates
  prompt_optimizer.py         # baseline/optimized micro-transforms
  clipboard.py                # read from macOS clipboard
  selection.py                # Accessibility API selection capture
  ui_alerts.py               # Preview dialog (NSAlert accessory with Mode + text area)
  ui_service_model.py        # "Service & Model..." dialog (two popups; dynamic)
  services.py                # cost/latency estimate, streaming, validation helpers
  ui_streaming.py            # popover for streaming tokens + elapsed time
  pricing.py                 # pricing.json loader/saver; path constants
tests/
  test_redaction.py          # unit tests for basic redaction behaviors
requirements.txt             # rumps, pyobjc frameworks, requests
```

## Config & data files (user-space)

**`~/Library/Application Support/AI Prompt Assistant/config.json`**

```json
{
  "favorites": [
    {"name": "...", "content": "..."}
  ],
  "ab_choice": {
    "adhoc": "baseline|optimized",
    "<template_key>": "..."
  },
  "redaction_enabled": true,
  "service": "chatgpt_web|openai|anthropic|ollama",
  "model": "string (must exist under service in pricing.json)",
  "api_keys": {
    "openai": "...",
    "anthropic": "...",
    "ollama_url": "http://localhost:11434"
  },
  "lat_ema": {
    "provider:model": 0.5
  }
}
```

**`~/Library/Application Support/AI Prompt Assistant/pricing.json`**

Per-provider model lists with `{ "in": price_per_1k, "out": price_per_1k, "ctx": max_tokens }`.

Created on first run with conservative defaults; editable at any time.

## Flows & logic

### Ask…

1. Capture text (selection → control value → clipboard) → show in Ask input.
2. On Preview, apply redaction and compute estimates (cost, latency), then open the Preview dialog:
   - Mode dropdown: Baseline/Optimized (remembers adhoc choice).
   - Editable text area (shows exactly what will be sent).
3. On Send:
   - Validate provider/model & credentials/daemon.
   - If `chatgpt_web`: copy prompt to clipboard, open ChatGPT in browser, optional Favorite.
   - Else: start streaming popover → on completion, re-open Preview with streamed answer appended → copy on confirm → optional Favorite.

### Templates…

Same as Ask… but pre-fills `{context}` from selection/clipboard and remembers per-template A/B mode.

After send or after re-preview, offer Favorite (defaults to template name).

### Favorites…

List → open → edit → send (web) → optional remove.

### Prompt Lab…

Text commands (one per line):

```
baseline | optimized
on | off (redaction default)
service:<chatgpt_web|openai|anthropic|ollama>
model:<model_name>
openai_key:sk-...
anthropic_key:...
ollama_url:http://localhost:11434
```

### Service & Model…

Native dialog with two popups; Model list updates when Service changes.

On save: if current model is missing, fallback to the first model for that service; if no models, prompt to edit pricing.

### Manage Pricing…

Ensures `pricing.json` exists and opens it with `open` (default editor on macOS).

## Estimation & streaming details

- **Token estimate heuristic:** `tokens ≈ len(text) / 4` (English-ish).
- **Cost:** `(in_tokens/1000)*in_price + (expected_out/1000)*out_price` with default `expected_out=300`.
- **Latency:** EMA per `provider:model` (seeded by provider default; updated after streams/requests).

### Streaming implementations:

- **OpenAI:** `POST /v1/chat/completions` with `stream=true` (parses `data:` SSE lines).
- **Anthropic:** `POST /v1/messages` with `stream=true` (parses `delta`/`content_block_delta` events).
- **Ollama:** `POST /api/generate` with `stream=true` (reads JSON lines with `response`).

### On completion:

- Popover enables "Insert into Preview".
- Preview reopens with `---\nAssistant:\n` section appended for final edits/acceptance.

## Redaction patterns (current)

- **Email:** `something@domain.tld` → `[REDACTED:email]`
- **Phone:** `415-555-1234`, `+1 415 555 1234`, etc. → `[REDACTED:phone]`
- **API keys:** `sk-...` or long hex-like strings → `[REDACTED:key]`
- **URL tokens:** `token|apikey|key|signature=...` → `...=[REDACTED:param]`

Redaction preview shows the count and lets users edit the final message before sending.

## Security & privacy notes

- API keys currently live in `config.json` under `api_keys`.
- **Recommendation:** move to macOS Keychain (e.g., via `keyring` or PyObjC Security APIs) for at-rest protection.
- Crash/telemetry: not implemented. If you add diagnostics, keep it opt-in and redact content.
- Clipboard and selection contents are only processed locally unless user explicitly sends to an API provider.

## Requirements & running

**requirements.txt includes:**

```
rumps
pyobjc
pyobjc-framework-AppKit
pyobjc-framework-Quartz
requests
```

**Run locally:**

```bash
python run_app.py
```

(Or import `src.app:run()` from your custom launcher.)

## Extending the system

### Add a new provider/model

1. Update `pricing.json` (via Manage Pricing…):

```json
{
  "openai": {
    "gpt-4o-mini": { "in": 0.00015, "out": 0.00060, "ctx": 128000 },
    "new-model":   { "in": 0.00050, "out": 0.00150, "ctx": 200000 }
  }
}
```

2. Switch to it in Service & Model… (models list is read from `pricing.json`).
3. If it's a new provider or a different streaming scheme, add a small `_provider_stream()` in `services.py` and wire it in `stream_completion()`.

### Customize "Optimized" mode

Replace `prompt_optimizer.optimize()` with a model call or a richer composition of micro-transforms.

Keep the Mode selector behavior intact (Preview dropdown & saved choices).

### Add template(s)

Append to `TEMPLATES` in `templates.py`. Use a short key, user-friendly name, and a `{context}` placeholder.

## Testing & troubleshooting

- Redaction tests live in `tests/test_redaction.py`.
- **Accessibility:** if selection is empty, confirm the app has Accessibility permission and the frontmost app exposes `AXSelectedText`.
- **Ollama:** ensure the daemon is running (`ollama serve`) and update `ollama_url` in Prompt Lab if not default.
- **API keys:** set via Prompt Lab. Missing keys/daemon will show an alert before sending.
- **Model missing?** Edit `pricing.json` (Manage Pricing…), then re-open Service & Model….

## Known limitations / future polish

- Preview is an NSAlert accessory; it's modal and not ideal for live streaming. We work around this by using a popover and re-preview pattern.
- Keys in `config.json`: move to Keychain for better security.
- Add a Settings → Check configuration button that runs `validate_ready()` and shows a readiness summary.
- Consider a dedicated "Service & Model" panel with live validation & pricing info per model.
- Add unit tests for selection/clipboard and streaming parsers.

## Maintainers' quick map (modules → responsibilities)

- **app.py** — menubar, UX flows, validation, favorites prompts.
- **ui_alerts.py** — Preview dialog (Mode dropdown + editor).
- **ui_service_model.py** — Service/Model selection dialog.
- **ui_streaming.py** — Streaming popover and glue (insert/copy).
- **services.py** — Pricing lookup, estimates, streaming implementations, `validate_ready()`.
- **pricing.py** — `pricing.json` load/save; path constant.
- **selection.py** — Accessibility capture.
- **clipboard.py** — Clipboard text access.
- **redaction.py** — Redaction functions.
- **templates.py** — Template catalog.
- **prompt_optimizer.py** — Baseline/Optimized text transform.
- **storage.py** — Config persistence, favorites helpers.
