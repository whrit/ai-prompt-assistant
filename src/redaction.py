import re
from typing import Tuple

RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
RE_PHONE = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}")
RE_APIKEY = re.compile(r"\b(?:sk-[A-Za-z0-9]{20,}|[A-Fa-f0-9]{32,64})\b")
RE_URLTOKEN = re.compile(r"(token|apikey|key|signature)=([A-Za-z0-9._-]+)", re.IGNORECASE)

def redact(text: str) -> Tuple[str, int]:
    count = 0
    def rpl_email(m):
        nonlocal count; count += 1
        return "[REDACTED:email]"
    def rpl_phone(m):
        nonlocal count; count += 1
        return "[REDACTED:phone]"
    def rpl_key(m):
        nonlocal count; count += 1
        return "[REDACTED:key]"
    def rpl_url(m):
        nonlocal count; count += 1
        return f"{m.group(1)}=[REDACTED:param]"
    text = RE_EMAIL.sub(rpl_email, text)
    text = RE_PHONE.sub(rpl_phone, text)
    text = RE_APIKEY.sub(rpl_key, text)
    text = RE_URLTOKEN.sub(rpl_url, text)
    return text, count