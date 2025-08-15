import rumps
from AppKit import NSApp
from Foundation import NSTimer
try:
    from AppKit import NSRunningApplication, NSApplicationActivateIgnoringOtherApps
except Exception:
    NSRunningApplication = None  # type: ignore
    NSApplicationActivateIgnoringOtherApps = 1  # type: ignore
from .storage import load_config, save_config, add_favorite, remove_favorite
from .debugging import setup_debugging, log_debug, log_error, log_exception
from .clipboard import read_clipboard_text
from .selection import get_selected_text_if_any, ensure_accessibility_trust
from .redaction import redact
from .templates import TEMPLATES
from .prompt_optimizer import optimize
from .ui_panels import PreviewPanel, HostWindow
from .ui_ask import AskPopover
from .ui_menus import ensure_edit_menu
from .ui_service_model import show_service_model_dialog
from .ui_streaming import StreamingPopover
from .services import (
    estimate_cost_and_latency,
    route_and_send,
    list_services_models,
    validate_ready,
    model_exists,
)
from .pricing import PRICING_PATH, ensure_pricing_file

APP_TITLE = "AI Prompt Assistant"


def _activate_app():
    """Bring this agent app to the front so dialogs get focus."""
    try:
        if NSRunningApplication is not None:
            NSRunningApplication.currentApplication().activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
            return
    except Exception:
        pass
    try:
        NSApp().activateIgnoringOtherApps_(True)
    except Exception:
        pass


class AIPromptAssistant(rumps.App):
    def __init__(self):
        super().__init__(APP_TITLE, icon=None, template=True)
        setup_debugging(True)
        # Disable rumps' default Quit to avoid duplicates; we'll add our own
        self.quit_button = None
        # Ensure standard Edit actions are available
        try:
            ensure_edit_menu()
        except Exception:
            pass
        self.menu = [
            rumps.MenuItem("Ask…", callback=self.ask_dialog),
            rumps.MenuItem("Templates…", callback=self.templates_dialog),
            rumps.MenuItem("Favorites…", callback=self.favorites_dialog),
            None,
            rumps.MenuItem("Prompt Lab…", callback=self.prompt_lab),
            rumps.MenuItem("Service & Model…", callback=self.service_model_dialog),
            rumps.MenuItem("Manage Pricing…", callback=self.manage_pricing),
            None,
            rumps.MenuItem("Settings", callback=self.settings_dialog),
            rumps.MenuItem("Quit", callback=rumps.quit_application),
        ]
        self.cfg = load_config()
        self._ask_pop: AskPopover | None = None
        self._ask_anchor_rect = None
        self._ask_anchor_view = None

    # ---- Manage Pricing ----
    def manage_pricing(self, _):
        # Ensure the pricing file exists, then open in default editor
        ensure_pricing_file()
        import subprocess

        try:
            subprocess.run(["open", str(PRICING_PATH)], check=False)
            rumps.notification(APP_TITLE, "Opening pricing.json", str(PRICING_PATH))
        except Exception:
            rumps.alert(f"Could not open {PRICING_PATH}. Please open it manually.")

    # ---- Service & Model (with validation) ----
    def service_model_dialog(self, _):
        svc = self.cfg.get("service", "chatgpt_web")
        mdl = self.cfg.get("model", "web")
        ok, new_svc, new_mdl = show_service_model_dialog(svc, mdl)
        if not ok:
            return

        # Ensure the chosen model exists for the selected service
        if not model_exists(new_svc, new_mdl):
            # pick the first available model for the service as a fallback
            models_map = list_services_models().get(new_svc, {})
            if models_map:
                new_mdl = list(models_map.keys())[0]
                rumps.notification(
                    APP_TITLE,
                    "Adjusted Model",
                    f"'{mdl}' not found; using '{new_mdl}' for {new_svc}.",
                )
            else:
                rumps.alert(
                    f"No models found for service '{new_svc}'. "
                    f"Check pricing.json via 'Manage Pricing…'."
                )
                return

        self.cfg["service"] = new_svc
        self.cfg["model"] = new_mdl
        save_config(self.cfg)
        rumps.notification(APP_TITLE, "Service updated", f"{new_svc} / {new_mdl}")

    # ---- Core Ask flow ----
    def ask_dialog(self, _):
        # Ensure our app is active so the window is front and editable
        _activate_app()
        # Prefer AX selection if available; prompt the user once to allow it.
        try:
            ensure_accessibility_trust(prompt_user=True)
        except Exception:
            log_exception("ensure_accessibility_trust")
        text = get_selected_text_if_any(prompt_user=False) or read_clipboard_text()
        # Build or reuse Ask popover
        if self._ask_pop is None:
            def _estimate(txt: str):
                provider = self.cfg.get("service", "chatgpt_web")
                model = self.cfg.get("model", "web")
                cost, lat = estimate_cost_and_latency(txt, provider, model)
                from .services import token_estimate
                return cost, lat, token_estimate(txt)
            self._ask_pop = AskPopover.alloc().initWithEstimator_(_estimate)
        self._ask_pop.set_text(text or "")
        try:
            status_btn = self._menu_bar.statusitem.button()
        except Exception:
            status_btn = NSApp().mainWindow()
        self._ask_pop.set_handlers(
            lambda: self._after_ask(self._ask_pop.text.string() or ""),
            lambda: self._ask_pop.close(),
        )
        # Prefer anchoring to the button's bounds if available; present after menu closes
        try:
            rect = status_btn.bounds() if status_btn else ((0,0),(1,1))
        except Exception:
            rect = ((0,0),(1,1))
        self._ask_anchor_rect = rect
        self._ask_anchor_view = status_btn
        log_debug("Scheduling Ask popover", rect=self._ask_anchor_rect)
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(0.05, self, "presentAsk:", None, False)
        return

    def presentAsk_(self, _):
        try:
            rect = self._ask_anchor_rect or ((0,0),(1,1))
            view = self._ask_anchor_view
            self._ask_pop.presentAnchored_to_preferredEdge_(rect, view, 1)
        except Exception:
            log_exception("presentAsk_")
        finally:
            self._ask_anchor_rect = None
            self._ask_anchor_view = None

    def _after_ask(self, raw_text: str):
        # Called after Ask popover Preview
        self._ask_pop.close()

        # Redaction pass (visible)
        redacted, count = (raw_text, 0)
        if self.cfg.get("redaction_enabled", True):
            redacted, count = redact(raw_text)

        # Compute estimate with current router setting
        provider = self.cfg.get("service", "chatgpt_web")
        model = self.cfg.get("model", "web")
        cost, latency = estimate_cost_and_latency(redacted, provider, model)
        est_line = f"Using {provider}/{model} — est. cost ${cost} • ~{latency}s"

        # Optimized text (default from saved A/B choice)
        mode = self.cfg.get("ab_choice", {}).get("adhoc", "optimized")
        preview_text = optimize(redacted, mode)

        # Use PreviewPanel as a sheet-like modal via an invisible host window
        host = HostWindow.alloc().init()
        host.show()
        panel = PreviewPanel.alloc().init()
        panel.buildWith_initialText_initialMode_(est_line, preview_text, mode)
        result = {"ok": False, "text": preview_text, "mode": mode}
        def _send(txt: str):
            result["ok"] = True
            result["text"] = txt
            result["mode"] = panel.selected_mode()
            panel.close(); host.close()
        def _cancel():
            result["ok"] = False
            panel.close(); host.close()
        panel.set_handlers(_send, _cancel)
        panel.show()
        # Let the runloop process while waiting for handlers; avoid hard spin waits
        import time
        t0 = time.time()
        while panel.win.isVisible() and (time.time() - t0) < 30:
            time.sleep(0.02)
        if not result["ok"]:
            return
        final_text = result["text"]
        selected_mode = result["mode"]

        # Persist A/B choice (already there)
        self.cfg.setdefault("ab_choice", {})["adhoc"] = selected_mode
        save_config(self.cfg)

        provider = self.cfg.get("service", "chatgpt_web")
        model = self.cfg.get("model", "web")

        # Validation (model exists + keys/daemon as needed)
        okv, msgv = validate_ready(provider, model)
        if not okv:
            rumps.alert(msgv)
            return

        if provider == "chatgpt_web":
            rumps.notification(APP_TITLE, "Opening ChatGPT Web…", est_line)
            route_and_send(final_text, provider, model)

            # Offer to favorite the prompt you just sent
            if rumps.alert("Add to Favorites?", ok="Yes", cancel="No") == 1:
                # Default name = first 40 chars of the prompt (or edit)
                default_name = (final_text.strip()[:40] or "Ad hoc prompt").replace("\n", " ")
                name_win = rumps.Window(
                    title="Save Favorite",
                    message="Name this favorite:",
                    default_text=default_name,
                    ok="Save",
                    cancel=True,
                )
                res = name_win.run()
                if res.clicked:
                    add_favorite(res.text.strip() or default_name, final_text)
        else:
            # Streaming popover
            pop = StreamingPopover()
            # Try to anchor to the status item button; fall back to main window if needed
            try:
                status_btn = self._menu_bar.statusitem.button()
            except Exception:
                status_btn = NSApp().mainWindow()

            pop.show(status_btn)

            def on_insert(result_text: str):
                # Re-open Preview with assistant text appended, so user can edit/accept
                combined = final_text + "\n\n---\nAssistant:\n" + result_text
                host2 = HostWindow.alloc().init(); host2.show()
                panel2 = PreviewPanel.alloc().init()
                panel2.buildWith_initialText_initialMode_(est_line, combined, selected_mode)
                res2 = {"ok": False, "text": combined}
                def _send2(txt: str):
                    res2["ok"] = True; res2["text"] = txt
                    panel2.close(); host2.close()
                def _cancel2():
                    res2["ok"] = False; panel2.close(); host2.close()
                panel2.set_handlers(_send2, _cancel2)
                panel2.show()
                import time
                while panel2.win.isVisible():
                    time.sleep(0.05)
                if res2["ok"] and res2["text"]:
                    # copy to clipboard and notify
                    import subprocess

                    try:
                        subprocess.run(["/usr/bin/pbcopy"], input=res2["text"].encode("utf-8"))
                    except Exception:
                        pass
                    rumps.notification(
                        APP_TITLE, "Copied to clipboard", "Final text is ready to paste."
                    )
                    # Ask to favorite the edited text
                    if rumps.alert("Add to Favorites?", ok="Yes", cancel="No") == 1:
                        default_name = (res2["text"].strip()[:40] or "Ad hoc prompt").replace("\n", " ")
                        name_win = rumps.Window(
                            title="Save Favorite",
                            message="Name this favorite:",
                            default_text=default_name,
                            ok="Save",
                            cancel=True,
                        )
                        res2 = name_win.run()
                        if res2.clicked:
                            add_favorite(res2.text.strip() or default_name, res2["text"])

            def on_copy(_result_text: str):
                # handled inside popover; no-op here
                pass

            pop.set_handlers(on_insert=on_insert, on_copy=on_copy)
            pop.stream(provider, model, final_text)

    def open_service(self, prompt: str):
        # Minimal: open ChatGPT web with prompt in clipboard (safer) and instruct user to paste.
        import webbrowser, subprocess

        try:
            # Copy to clipboard for user
            subprocess.run(["/usr/bin/pbcopy"], input=prompt.encode("utf-8"))
        except Exception:
            pass
        # Open ChatGPT (cannot safely prefill), explain via notification
        webbrowser.open("https://chat.openai.com/")
        rumps.notification(APP_TITLE, "Prompt copied to clipboard", "Paste into the chat.")

    # ---- Templates ----
    def templates_dialog(self, _):
        items = [t["name"] for t in TEMPLATES]
        choice = rumps.Window(
            title="Templates",
            message="Type the number of a template:\n"
            + "\n".join(f"{i+1}. {n}" for i, n in enumerate(items)),
            default_text="",
            ok="Open",
            cancel=True,
        ).run()
        if not choice.clicked:
            return
        try:
            idx = int(choice.text.strip()) - 1
            t = TEMPLATES[idx]
        except Exception:
            rumps.alert("Invalid selection.")
            return

        context = get_selected_text_if_any(prompt_user=False) or read_clipboard_text() or ""
        mode = self.cfg.get("ab_choice", {}).get(t["key"], "optimized")
        base = t["prompt"].format(context=context)
        if self.cfg.get("redaction_enabled", True):
            base, _ = redact(base)

        provider = self.cfg.get("service", "chatgpt_web")
        model = self.cfg.get("model", "web")
        cost, latency = estimate_cost_and_latency(base, provider, model)
        est_line = f"Using {provider}/{model} — est. cost ${cost} • ~{latency}s"

        preview = optimize(base, mode)
        host = HostWindow.alloc().init(); host.show()
        panel = PreviewPanel.alloc().init(); panel.buildWith_initialText_initialMode_(est_line, preview, mode)
        res = {"ok": False, "text": preview, "mode": mode}
        def _send(txt: str):
            res["ok"] = True; res["text"] = txt; res["mode"] = panel.selected_mode(); panel.close(); host.close()
        def _cancel():
            res["ok"] = False; panel.close(); host.close()
        panel.set_handlers(_send, _cancel); panel.show()
        import time
        while panel.win.isVisible():
            time.sleep(0.05)
        if not res["ok"]:
            return
        final_text = res["text"]; selected_mode = res["mode"]

        # Persist per-template A/B choice
        self.cfg.setdefault("ab_choice", {})[t["key"]] = selected_mode
        save_config(self.cfg)

        provider = self.cfg.get("service", "chatgpt_web")
        model = self.cfg.get("model", "web")

        # Validation (model exists + keys/daemon as needed)
        okv, msgv = validate_ready(provider, model)
        if not okv:
            rumps.alert(msgv)
            return

        if provider == "chatgpt_web":
            rumps.notification(APP_TITLE, "Opening ChatGPT Web…", est_line)
            route_and_send(final_text, provider, model)

            # Offer to favorite using the template name
            if rumps.alert("Add to Favorites?", ok="Yes", cancel="No") == 1:
                add_favorite(t["name"], final_text)
        else:
            # Streaming popover
            pop = StreamingPopover()
            try:
                status_btn = self._menu_bar.statusitem.button()
            except Exception:
                status_btn = NSApp().mainWindow()

            pop.show(status_btn)

            def on_insert(result_text: str):
                combined = final_text + "\n\n---\nAssistant:\n" + result_text
                host2 = HostWindow.alloc().init(); host2.show()
                panel2 = PreviewPanel.alloc().init(); panel2.buildWith_initialText_initialMode_(est_line, combined, selected_mode)
                r2 = {"ok": False, "text": combined}
                def _send2(txt: str):
                    r2["ok"] = True; r2["text"] = txt; panel2.close(); host2.close()
                def _cancel2():
                    r2["ok"] = False; panel2.close(); host2.close()
                panel2.set_handlers(_send2, _cancel2); panel2.show()
                import time
                while panel2.win.isVisible():
                    time.sleep(0.05)
                if r2["ok"] and r2["text"]:
                    import subprocess

                    try:
                        subprocess.run(["/usr/bin/pbcopy"], input=r2["text"].encode("utf-8"))
                    except Exception:
                        pass
                    rumps.notification(
                        APP_TITLE, "Copied to clipboard", "Final text is ready to paste."
                    )
                    # Offer to favorite the final edited template output
                    if rumps.alert("Add to Favorites?", ok="Yes", cancel="No") == 1:
                        add_favorite(t["name"], r2["text"])

            def on_copy(_result_text: str):
                pass

            pop.set_handlers(on_insert=on_insert, on_copy=on_copy)
            pop.stream(provider, model, final_text)

    # ---- Favorites ----
    def favorites_dialog(self, _):
        cfg = load_config()
        favs = cfg.get("favorites", [])
        if not favs:
            rumps.alert("No favorites yet.")
            return
        choice = rumps.Window(
            title="Favorites",
            message="Type the number to open:\n"
            + "\n".join(f"{i+1}. {f['name']}" for i, f in enumerate(favs)),
            default_text="",
            ok="Open",
            cancel=True,
        ).run()
        if not choice.clicked:
            return
        try:
            idx = int(choice.text.strip()) - 1
            fav = favs[idx]
        except Exception:
            rumps.alert("Invalid selection.")
            return
        w = rumps.Window(
            title=fav["name"],
            message="Edit then Send.",
            default_text=fav["content"],
            ok="Send",
            cancel=True,
        )
        res = w.run()
        if res.clicked:
            self.open_service(res.text)

        # Option to remove
        if rumps.alert("Remove from Favorites?", ok="Yes", cancel="No") == 1:
            remove_favorite(fav["name"], fav["content"])

    # ---- Prompt Lab (A/B + redaction default) ----
    def prompt_lab(self, _):
        msg = (
            "Prompt Lab\n"
            "Commands:\n"
            "- baseline | optimized  (set global A/B)\n"
            "- on | off              (redaction default)\n"
            "- service:<chatgpt_web|openai|anthropic|ollama>\n"
            "- model:<model_name>    (must exist for chosen service)\n"
            "- openai_key:sk-... | anthropic_key:... | ollama_url:http://localhost:11434"
        )
        win = rumps.Window(title="Prompt Lab", message=msg, default_text="", ok="Apply", cancel=True)
        res = win.run()
        if not res.clicked:
            return
        text = res.text.strip()
        cfg = load_config()
        for line in [l.strip() for l in text.splitlines() if l.strip()]:
            lc = line.lower()
            if lc in ("baseline", "optimized"):
                cfg.setdefault("ab_choice", {})["adhoc"] = lc
            elif lc in ("on", "off"):
                cfg["redaction_enabled"] = (lc == "on")
            elif line.startswith("service:"):
                cfg["service"] = line.split(":", 1)[1].strip()
            elif line.startswith("model:"):
                cfg["model"] = line.split(":", 1)[1].strip()
            elif line.startswith("openai_key:"):
                cfg.setdefault("api_keys", {})["openai"] = line.split(":", 1)[1].strip()
            elif line.startswith("anthropic_key:"):
                cfg.setdefault("api_keys", {})["anthropic"] = line.split(":", 1)[1].strip()
            elif line.startswith("ollama_url:"):
                cfg.setdefault("api_keys", {})["ollama_url"] = line.split(":", 1)[1].strip()
        save_config(cfg)
        self.cfg = cfg
        rumps.notification(
            APP_TITLE, "Prompt Lab updated", f"Service: {cfg.get('service')}, Model: {cfg.get('model')}"
        )

    # ---- Settings (unchanged snapshot) ----
    def settings_dialog(self, _):
        cfg = load_config()
        redaction = "on" if cfg.get("redaction_enabled", True) else "off"
        mode = cfg.get("ab_choice", {}).get("adhoc", "optimized")
        svc = cfg.get("service", "chatgpt_web")
        model = cfg.get("model", "web")
        rumps.alert(
            f"Settings:\nMode: {mode}\nRedaction: {redaction}\nService: {svc}\nModel: {model}\nFavorites: {len(cfg.get('favorites', []))}"
        )


def run():
    AIPromptAssistant().run()


if __name__ == "__main__":
    run()