from src.redaction import redact

def test_redacts_email():
    out, n = redact("Contact me at a@b.com")
    assert "[REDACTED:email]" in out and n >= 1

def test_redacts_phone():
    out, n = redact("Call 415-555-1234 please")
    assert "[REDACTED:phone]" in out

def test_redacts_key_like():
    out, n = redact("key=abcdEFGH1234 and sk-abcdefghijklmnopqrstuv")
    assert "[REDACTED:param]" in out and "[REDACTED:key]" in out