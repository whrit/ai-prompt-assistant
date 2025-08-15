# src/ui_ask.py
from typing import Tuple, Callable
from AppKit import (
    NSPopover, NSView, NSVisualEffectView, NSVisualEffectMaterialSidebar,
    NSVisualEffectBlendingModeBehindWindow, NSStackView, NSStackViewGravityTop,
    NSTextView, NSScrollView, NSMakeRect, NSLayoutConstraint, NSLayoutAnchor,
    NSTextField, NSButton, NSFont, NSApp, NSViewController, NSWindow, NSWindowStyleMaskTitled,
)
from Foundation import NSObject, NSTimer
import objc


class _Debounce(NSObject):
    def initWithDelay_action_(self, delay: float, action: Callable[[], None]):
        self = objc.super(_Debounce, self).init()
        if self is None:
            return None
        self._delay = delay
        self._action = action
        self._timer = None
        return self

    def call(self):
        if self._timer is not None:
            self._timer.invalidate()
            self._timer = None
        self._timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            self._delay, self, "_fire:", None, False
        )

    def _fire_(self, _):
        if self._action:
            self._action()
        if self._timer is not None:
            self._timer.invalidate()
            self._timer = None


class AskPopover(NSObject):
    def initWithEstimator_(self, estimate_provider: Callable[[str], Tuple[float, float, int]]):
        self = objc.super(AskPopover, self).init()
        if self is None:
            return None
        self.pop = NSPopover.alloc().init()
        self.pop.setContentSize_((560, 320))
        self.pop.setBehavior_(1)  # transient

        # Vibrant background
        vib = NSVisualEffectView.alloc().initWithFrame_(NSMakeRect(0, 0, 560, 320))
        vib.setMaterial_(NSVisualEffectMaterialSidebar)
        vib.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
        vib.setState_(1)  # active
        vib.setAutoresizingMask_(18)

        # Vertical stack
        stack = NSStackView.alloc().initWithFrame_(NSMakeRect(0, 0, 560, 320))
        stack.setOrientation_(1)  # vertical
        stack.setAlignment_(1)
        stack.setDistribution_(4)
        stack.setSpacing_(8)
        stack.setEdgeInsets_((12, 12, 12, 12))
        stack.setTranslatesAutoresizingMaskIntoConstraints_(False)
        vib.addSubview_(stack)

        # Header: status line
        self.status = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 0, 10, 10))
        self.status.setBezeled_(False)
        self.status.setDrawsBackground_(False)
        self.status.setEditable_(False)
        self.status.setSelectable_(False)
        self.status.setStringValue_("")

        # Text area
        scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(0, 0, 10, 10))
        scroll.setHasVerticalScroller_(True)
        self.text = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, 10, 10))
        self.text.setRichText_(False)
        self.text.setFont_(NSFont.systemFontOfSize_(13))
        self.text.setEditable_(True)
        self.text.setSelectable_(True)
        scroll.setDocumentView_(self.text)

        # Buttons row
        btn_row = NSStackView.alloc().initWithFrame_(NSMakeRect(0, 0, 10, 10))
        btn_row.setOrientation_(0)  # horizontal
        btn_row.setAlignment_(1)
        btn_row.setDistribution_(4)
        btn_row.setSpacing_(8)
        btn_row.setTranslatesAutoresizingMaskIntoConstraints_(False)

        self.btnPreview = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, 80, 28))
        self.btnPreview.setTitle_("Preview  ⌘↩")
        self.btnPreview.setKeyEquivalent_("\r")
        self.btnPreview.setKeyEquivalentModifierMask_(256)  # cmd
        self.btnPreview.setTarget_(self)
        self.btnPreview.setAction_("doPreview:")

        self.btnCancel = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, 80, 28))
        self.btnCancel.setTitle_("Cancel  Esc")
        self.btnCancel.setTarget_(self)
        self.btnCancel.setAction_("doCancel:")

        btn_row.addView_inGravity_(self.btnCancel, 1)
        btn_row.addView_inGravity_(self.btnPreview, 1)

        # Assemble stack
        stack.addView_inGravity_(self.status, NSStackViewGravityTop)
        stack.addView_inGravity_(scroll, NSStackViewGravityTop)
        stack.addView_inGravity_(btn_row, NSStackViewGravityTop)

        # Auto Layout for stack in vib
        vib.addConstraint_(stack.topAnchor().constraintEqualToAnchor_constant_(vib.topAnchor(), 12))
        vib.addConstraint_(stack.leadingAnchor().constraintEqualToAnchor_constant_(vib.leadingAnchor(), 12))
        vib.addConstraint_(stack.trailingAnchor().constraintEqualToAnchor_constant_(vib.trailingAnchor(), -12))
        vib.addConstraint_(stack.bottomAnchor().constraintEqualToAnchor_constant_(vib.bottomAnchor(), -12))

        vc = NSViewController.alloc().init()
        vc.setView_(vib)
        self.pop.setContentViewController_(vc)

        # Debounce estimate updates
        self._deb = _Debounce.alloc().initWithDelay_action_(0.15, self._recalc)
        self._estimate_provider = estimate_provider
        self.text.setDelegate_(self)
        self._last_est = (0.0, 0.0, 0)
        self._on_preview = None
        self._on_cancel = None
        self._anchor_win = None
        return self

    # NSTextViewDelegate
    def textDidChange_(self, _):
        try:
            self._deb.call()
        except Exception:
            pass

    def _recalc(self):
        txt = self.text.string() or ""
        try:
            cost, latency, tokens = self._estimate_provider(txt)
            self.status.setStringValue_(f"{tokens} tokens • ~${cost} • ~{latency}s")
        except Exception:
            self.status.setStringValue_("")

    def set_text(self, text: str):
        self.text.setString_(text)
        self._recalc()

    def presentAnchored_to_preferredEdge_(self, anchor_rect, relative_to, preferred_edge):
        try:
            NSApp().activateIgnoringOtherApps_(True)
        except Exception:
            pass
        # Ensure anchor view
        rel_view = relative_to
        if not rel_view:
            # Create a tiny host window to anchor the popover
            self._anchor_win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(((200,200),(10,10)), NSWindowStyleMaskTitled, 2, False)
            self._anchor_win.setAlphaValue_(0.01)
            self._anchor_win.makeKeyAndOrderFront_(None)
            rel_view = self._anchor_win.contentView()
            if anchor_rect[1] == (0,0):
                anchor_rect = ((0,0),(1,1))
        self.pop.showRelativeToRect_ofView_preferredEdge_(anchor_rect, rel_view, preferred_edge)
        # Delay focus slightly to ensure popover window exists
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(0.05, self, "focusLater:", None, False)

    def close(self):
        self.pop.close()
        try:
            if self._anchor_win is not None:
                self._anchor_win.close()
        except Exception:
            pass
        self._anchor_win = None

    def focusLater_(self, _):
        try:
            w = self.text.window()
            if w:
                w.makeKeyAndOrderFront_(None)
                w.makeFirstResponder_(self.text)
        except Exception:
            pass

    # Handlers
    def set_handlers(self, on_preview: Callable[[], None], on_cancel: Callable[[], None]):
        self._on_preview = on_preview
        self._on_cancel = on_cancel

    def doPreview_(self, _):
        if self._on_preview:
            self._on_preview()

    def doCancel_(self, _):
        if self._on_cancel:
            self._on_cancel()


