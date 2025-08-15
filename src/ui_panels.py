# src/ui_panels.py
from typing import Tuple, Callable, Dict
from AppKit import (
    NSPanel, NSWindow, NSWindowStyleMaskTitled, NSWindowStyleMaskClosable, NSWindowStyleMaskResizable,
    NSApp, NSVisualEffectView, NSVisualEffectMaterialTitlebar, NSVisualEffectBlendingModeBehindWindow,
    NSStackView, NSTextView, NSScrollView, NSButton, NSTextField, NSFont, NSMakeRect, NSPopUpButton
)
from Foundation import NSObject
import objc
from .storage import load_config, save_config
from .settings_manager import SettingsManager


class PreviewPanel(NSObject):
    def init(self):
        self = objc.super(PreviewPanel, self).init()
        if self is None:
            return None
        self.win = None
        self.text = None
        self.modePopup = None
        self._on_send = None
        self._on_cancel = None
        return self

    def buildWith_initialText_initialMode_(self, estimate_line: str, initial_text: str, initial_mode: str):
        cfg = load_config()
        last_size = (cfg.get("ui", {}).get("preview_size") or [720, 420])
        frame = ((0, 0), (last_size[0], last_size[1]))
        self.win = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            frame,
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskResizable,
            2,
            False,
        )
        sm = SettingsManager()
        self.win.setTitle_(sm.get_string("preview.title", "Preview"))

        vib = NSVisualEffectView.alloc().initWithFrame_(NSMakeRect(0, 0, 720, 420))
        vib.setMaterial_(NSVisualEffectMaterialTitlebar)
        vib.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
        vib.setState_(1)

        stack = NSStackView.alloc().initWithFrame_(NSMakeRect(0, 0, 720, 420))
        stack.setOrientation_(1)
        stack.setAlignment_(1)
        stack.setSpacing_(8)
        stack.setEdgeInsets_((12, 12, 12, 12))
        stack.setTranslatesAutoresizingMaskIntoConstraints_(False)
        vib.addSubview_(stack)

        # Status line
        status = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 0, 10, 10))
        status.setBezeled_(False); status.setDrawsBackground_(False)
        status.setEditable_(False); status.setSelectable_(False)
        status.setStringValue_(estimate_line)

        # Mode popup
        modeRow = NSStackView.alloc().initWithFrame_(NSMakeRect(0,0,10,24))
        modeRow.setOrientation_(0); modeRow.setAlignment_(1); modeRow.setSpacing_(8)
        modeLbl = NSTextField.alloc().initWithFrame_(NSMakeRect(0,0,10,20))
        modeLbl.setBezeled_(False); modeLbl.setDrawsBackground_(False)
        modeLbl.setEditable_(False); modeLbl.setSelectable_(False)
        modeLbl.setStringValue_(sm.get_string("preview.mode", "Mode:"))
        self.modePopup = NSPopUpButton.alloc().initWithFrame_pullsDown_(NSMakeRect(0,0,120,24), False)
        self.modePopup.addItemsWithTitles_([sm.get_string("preview.mode.baseline", "baseline"), sm.get_string("preview.mode.optimized", "optimized")])
        try:
            self.modePopup.selectItemWithTitle_(initial_mode)
        except Exception:
            pass
        modeRow.addView_inGravity_(modeLbl, 1)
        modeRow.addView_inGravity_(self.modePopup, 1)

        # Text area
        scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(0, 0, 10, 10))
        scroll.setHasVerticalScroller_(True)
        self.text = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, 10, 10))
        self.text.setRichText_(False)
        self.text.setFont_(NSFont.systemFontOfSize_(13))
        self.text.setString_(initial_text or "")
        # Redaction highlighting
        try:
            s = self.text.string() or ""
            ns = self.text.textStorage()
            import re
            for pat in (re.compile("\\[REDACTED:email\\]"), re.compile("\\[REDACTED:phone\\]"), re.compile("\\[REDACTED:key\\]"), re.compile("\\[REDACTED:param\\]")):
                for m in pat.finditer(s):
                    ns.addAttribute_value_range_("NSBackgroundColor", (0.9,0.8,0.2,0.3), (m.start(), m.end()-m.start()))
        except Exception:
            pass
        scroll.setDocumentView_(self.text)

        # Buttons
        sendBtn = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, 120, 30))
        sendBtn.setTitle_(sm.get_string("preview.send", "Send  ⌘↩"))
        sendBtn.setKeyEquivalent_("\r"); sendBtn.setKeyEquivalentModifierMask_(256)
        cancelBtn = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, 120, 30))
        cancelBtn.setTitle_(sm.get_string("preview.cancel", "Cancel  Esc"))

        def _persist():
            try:
                f = self.win.frame().size
                cfg2 = load_config()
                ui = cfg2.get("ui", {})
                ui["preview_size"] = [int(f.width), int(f.height)]
                # Persist last selected mode globally
                mode_val = self.selected_mode()
                cfg2.setdefault("ab_choice", {})["adhoc"] = mode_val
                cfg2["ui"] = ui
                save_config(cfg2)
            except Exception:
                pass

        def _send(_):
            if self._on_send:
                _persist()
                # Defer close to avoid blocking the main loop while handlers run
                NSApp().performSelector_onThread_withObject_waitUntilDone_("noop:", None, None, False)
                self._on_send(self.text.string() or "")
        def _cancel(_):
            if self._on_cancel:
                _persist()
                NSApp().performSelector_onThread_withObject_waitUntilDone_("noop:", None, None, False)
                self._on_cancel()
        sendBtn.setTarget_(self); sendBtn.setAction_("doSend:")
        cancelBtn.setTarget_(self); cancelBtn.setAction_("doCancel:")
        self.doSend_ = _send; self.doCancel_ = _cancel

        # Assemble
        stack.addView_inGravity_(status, 1)
        stack.addView_inGravity_(modeRow, 1)
        stack.addView_inGravity_(scroll, 1)
        stack.addView_inGravity_(cancelBtn, 1)
        stack.addView_inGravity_(sendBtn, 1)

        # Layout
        vib.addConstraint_(stack.topAnchor().constraintEqualToAnchor_constant_(vib.topAnchor(), 12))
        vib.addConstraint_(stack.leadingAnchor().constraintEqualToAnchor_constant_(vib.leadingAnchor(), 12))
        vib.addConstraint_(stack.trailingAnchor().constraintEqualToAnchor_constant_(vib.trailingAnchor(), -12))
        vib.addConstraint_(stack.bottomAnchor().constraintEqualToAnchor_constant_(vib.bottomAnchor(), -12))

        self.win.setContentView_(vib)

    def set_handlers(self, on_send: Callable[[str], None], on_cancel: Callable[[], None]):
        self._on_send = on_send
        self._on_cancel = on_cancel

    def show(self):
        app = NSApp()
        if app:
            app.activateIgnoringOtherApps_(True)
        self.win.makeKeyAndOrderFront_(None)
        self.win.makeFirstResponder_(self.text)
        # Avoid UI freeze: let runloop process events briefly
        try:
            import time
            time.sleep(0.01)
        except Exception:
            pass

    def close(self):
        self.win.close()

    def selected_mode(self) -> str:
        try:
            return self.modePopup.titleOfSelectedItem()
        except Exception:
            return "optimized"


class HostWindow(NSObject):
    def init(self):
        self = objc.super(HostWindow, self).init()
        if self is None:
            return None
        frame = ((200, 200), (10, 10))
        self.win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame, NSWindowStyleMaskTitled, 2, False
        )
        self.win.setAlphaValue_(0.01)
        self.win.setTitle_(" ")
        return self

    def show(self):
        self.win.makeKeyAndOrderFront_(None)

    def close(self):
        self.win.close()



