# src/ui_alerts.py
from typing import Tuple
from AppKit import (
    NSAlert, NSView, NSTextView, NSScrollView, NSMakeRect,
    NSPopUpButton, NSTextField
)

OK_RETURN = 1000  # NSAlertFirstButtonReturn

def _label(frame, text):
    lbl = NSTextField.alloc().initWithFrame_(frame)
    lbl.setBezeled_(False)
    lbl.setDrawsBackground_(False)
    lbl.setEditable_(False)
    lbl.setSelectable_(False)
    lbl.setStringValue_(text)
    return lbl

def _popup(frame, items, selected):
    pop = NSPopUpButton.alloc().initWithFrame_pullsDown_(frame, False)
    pop.addItemsWithTitles_(items)
    try:
        idx = items.index(selected)
        pop.selectItemAtIndex_(idx)
    except Exception:
        pass
    return pop

def show_preview_dialog(
    initial_text: str,
    redactions_count: int,
    initial_mode: str = "optimized",
    estimate_line: str = "",
) -> Tuple[bool, str, str]:
    """
    Returns (clicked_ok, final_text, selected_mode)
    """
    alert = NSAlert.alloc().init()
    alert.setMessageText_("Preview")
    info = f"Redactions applied: {redactions_count}. {estimate_line}".strip()
    alert.setInformativeText_(info)
    alert.addButtonWithTitle_("Send")
    alert.addButtonWithTitle_("Cancel")

    # Accessory view: Mode + editable text in scroll view
    width, height = 600, 320
    acc = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, width, height))

    # Mode selector
    acc.addSubview_(_label(NSMakeRect(0, height - 22, 60, 18), "Mode:"))
    mode_popup = _popup(NSMakeRect(60, height - 26, 140, 22), ["baseline", "optimized"], initial_mode)
    acc.addSubview_(mode_popup)

    # Text area
    scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(0, 0, width, height - 36))
    scroll.setHasVerticalScroller_(True)
    text_view = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, width, height - 36))
    text_view.setString_(initial_text)
    text_view.setEditable_(True)
    text_view.setRichText_(False)
    scroll.setDocumentView_(text_view)
    acc.addSubview_(scroll)

    alert.setAccessoryView_(acc)
    res = alert.runModal()

    if res != OK_RETURN:
        return False, initial_text, initial_mode

    final_text = text_view.string()
    selected_mode = mode_popup.titleOfSelectedItem()
    return True, final_text, selected_mode