from AppKit import NSPasteboard, NSStringPboardType

def read_clipboard_text() -> str:
    pb = NSPasteboard.generalPasteboard()
    types = pb.types()
    if types and (NSStringPboardType in types or "public.utf8-plain-text" in types):
        return pb.stringForType_(NSStringPboardType) or ""
    return ""