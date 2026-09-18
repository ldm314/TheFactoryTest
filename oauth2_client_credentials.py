"""OAuth 2.0 client-credentials grounding (factory Pattern)."""

TOKEN_PATH = "/oauth/token"
GRANT_TYPE = "client_credentials"


def client_credentials_params():
    return ("grant_type", "client_id", "client_secret", "scope")
