# src/ui_streaming.py
import time, threading
from typing import Callable
from AppKit import (
    NSPopover, NSView, NSMakeRect, NSScrollView, NSTextView,
    NSButton, NSTextField, NSApp
)
from Foundation import NSObject, NSTimer
import objc
from .services import stream_completion, _update_latency_ema

class _Streamer(NSObject):
    def initWith_(self, update_fn):
        self = objc.super(_Streamer, self).init()
        if self is None: return None
        self.update_fn = update_fn
        return self

    def tick_(self, _timer):
        # Called by NSTimer on main run loop
        if self.update_fn:
            self.update_fn()

def _label(frame, text):
    lbl = NSTextField.alloc().initWithFrame_(frame)
    lbl.setBezeled_(False); lbl.setDrawsBackground_(False)
    lbl.setEditable_(False); lbl.setSelectable_(False)
    lbl.setStringValue_(text); return lbl

class StreamingPopover:
    def __init__(self):
        self.pop = NSPopover.alloc().init()
        self.pop.setContentSize_((520, 240))
        self.pop.setBehavior_(1)  # NSPopoverBehaviorTransient
        self.view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 520, 240))

        self.view.addSubview_(_label(NSMakeRect(10, 214, 500, 18), "Streaming…"))
        self.status = _label(NSMakeRect(10, 190, 500, 16), "0 tokens • 0.0s")
        self.view.addSubview_(self.status)

        self.scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(10, 40, 500, 145))
        self.scroll.setHasVerticalScroller_(True)
        self.text = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, 500, 145))
        self.text.setEditable_(False); self.text.setRichText_(False)
        self.scroll.setDocumentView_(self.text)
        self.view.addSubview_(self.scroll)

        self.btnInsert = NSButton.alloc().initWithFrame_(NSMakeRect(10, 10, 160, 24))
        self.btnInsert.setTitle_("Insert into Preview")
        self.btnInsert.setEnabled_(False)
        self.view.addSubview_(self.btnInsert)

        self.btnCopy = NSButton.alloc().initWithFrame_(NSMakeRect(180, 10, 120, 24))
        self.btnCopy.setTitle_("Copy")
        self.view.addSubview_(self.btnCopy)

        self.pop.setContentViewController_(None)
        self.pop.setContentSize_((520, 240))
        self.pop.setContentView_(self.view)

        self._accum = []
        self._start = None
        self._tokens = 0
        self._done = False

    def show(self, status_item_button):
        # Anchor to the status item button
        try:
            NSApp().activateIgnoringOtherApps_(True)
        except Exception:
            pass
        self.pop.showRelativeToRect_ofView_preferredEdge_(((0,0),(0,0)), status_item_button, 3)

    def set_handlers(self, on_insert: Callable[[str], None], on_copy: Callable[[str], None]):
        def _insert(_):
            on_insert("".join(self._accum))
        def _copy(_):
            from AppKit import NSPasteboard, NSStringPboardType
            pb = NSPasteboard.generalPasteboard()
            pb.clearContents()
            pb.setString_forType_("".join(self._accum), NSStringPboardType)
        self.btnInsert.setTarget_(self); self.btnInsert.setAction_("doInsert:")
        self.btnCopy.setTarget_(self); self.btnCopy.setAction_("doCopy:")
        self.doInsert_ = _insert
        self.doCopy_ = _copy

    def stream(self, provider: str, model: str, prompt: str):
        self._start = time.time()
        self._done = False
        self._accum.clear(); self._tokens = 0
        # Timer to update status
        streamer = _Streamer.alloc().initWith_(self._update_status)
        self._timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(0.2, streamer, "tick:", None, True)

        def _bg():
            try:
                for piece in stream_completion(provider, model, prompt):
                    if not piece: 
                        continue
                    self._accum.append(piece)
                    self._tokens += 1
                    # Update text on main thread
                    self.text.performSelectorOnMainThread_withObject_waitUntilDone_("setString:", "".join(self._accum), False)
            finally:
                self._done = True
                elapsed = time.time() - self._start if self._start else 0.0
                _update_latency_ema(provider, model, elapsed)
                self.btnInsert.performSelectorOnMainThread_withObject_waitUntilDone_("setEnabled:", True, False)
        threading.Thread(target=_bg, daemon=True).start()

    def _update_status(self):
        elapsed = (time.time() - self._start) if self._start else 0.0
        self.status.setStringValue_(f"{self._tokens} tokens • {elapsed:.1f}s")
        if self._done and self._timer:
            self._timer.invalidate(); self._timer = None