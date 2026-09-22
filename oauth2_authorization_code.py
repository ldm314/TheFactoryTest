"""OAuth 2.0 authorization-code grounding (factory Pattern).

Route names and helpers only — not a hosted IdP. Coding agents implement
handlers against these names; do not invent parallel authorize/token paths.
"""

AUTHORIZE_PATH = "/oauth/authorize"
TOKEN_PATH = "/oauth/token"
TOKEN_TYPE = "Bearer"


def parse_bearer(authorization: str | None) -> str | None:
    """Return the raw token from ``Authorization: Bearer …``, else None."""
    if not authorization:
        return None
    scheme, _, rest = authorization.partition(" ")
    if scheme.lower() != "bearer" or not rest.strip():
        return None
    return rest.strip()


def authorization_code_grant_params():
    """Expected token-endpoint form fields for the code grant (documentation)."""
    return ("grant_type", "code", "redirect_uri", "client_id")
