# src/selection.py
# Be robust to different PyObjC layouts (Quartz vs ApplicationServices) and environments
try:
    from Quartz import (
        AXIsProcessTrustedWithOptions,
        kAXTrustedCheckOptionPrompt,
        AXUIElementCreateSystemWide,
        AXUIElementCopyAttributeValue,
    )
except Exception:
    try:
        from ApplicationServices import (
            AXIsProcessTrustedWithOptions,
            kAXTrustedCheckOptionPrompt,
            AXUIElementCreateSystemWide,
            AXUIElementCopyAttributeValue,
        )
    except Exception:
        AXIsProcessTrustedWithOptions = None  # type: ignore
        kAXTrustedCheckOptionPrompt = None  # type: ignore
        AXUIElementCreateSystemWide = None  # type: ignore
        AXUIElementCopyAttributeValue = None  # type: ignore

# AX constants are strings in PyObjC
kAXFocusedUIElementAttribute = "AXFocusedUIElement"
kAXSelectedTextAttribute = "AXSelectedText"
kAXValueAttribute = "AXValue"

def ensure_accessibility_trust(prompt_user: bool = True) -> bool:
    if AXIsProcessTrustedWithOptions is None:
        return False
    prompt_key = (
        kAXTrustedCheckOptionPrompt if kAXTrustedCheckOptionPrompt is not None else "kAXTrustedCheckOptionPrompt"
    )
    opts = {prompt_key: True} if prompt_user else {}
    return bool(AXIsProcessTrustedWithOptions(opts))

def get_selected_text_if_any(prompt_user: bool = False) -> str:
    """
    Best-effort: returns the currently selected text in the focused UI element,
    or "" if unavailable or not permitted.
    """
    try:
        if AXUIElementCreateSystemWide is None or AXUIElementCopyAttributeValue is None:
            return ""
        if not ensure_accessibility_trust(prompt_user=prompt_user):
            return ""
        sys = AXUIElementCreateSystemWide()
        focused = AXUIElementCopyAttributeValue(sys, kAXFocusedUIElementAttribute)
        if not focused:
            return ""
        # Try AXSelectedText first
        sel = AXUIElementCopyAttributeValue(focused, kAXSelectedTextAttribute)
        if isinstance(sel, str) and sel.strip():
            return sel
        # Fallback: value of the field (not strictly the selection)
        val = AXUIElementCopyAttributeValue(focused, kAXValueAttribute)
        if isinstance(val, str):
            return val
    except Exception:
        pass
    return ""