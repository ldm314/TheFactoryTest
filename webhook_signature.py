"""HMAC webhook signature grounding (factory Pattern)."""

import hashlib
import hmac


SIGNATURE_HEADER = "X-Signature"


def sign_body(secret: str, body: bytes) -> str:
    digest = hmac.new(
        secret.encode("utf-8"), body, hashlib.sha256,
    ).hexdigest()
    return "sha256=" + digest


def verify_signature(secret: str, body: bytes, header: str | None) -> bool:
    if not header:
        return False
    expected = sign_body(secret, body)
    return hmac.compare_digest(expected, header.strip())
