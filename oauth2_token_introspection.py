"""OAuth 2.0 token introspection grounding (factory Pattern)."""

INTROSPECT_PATH = "/oauth/introspect"


def introspection_result(*, active: bool, sub: str | None = None, scope: str | None = None):
    """RFC 7662-shaped dict coding agents should return from introspect."""
    body = {"active": bool(active)}
    if sub is not None:
        body["sub"] = sub
    if scope is not None:
        body["scope"] = scope
    return body
