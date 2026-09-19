"""OAuth authorization-code flow persistence models (build_plan.modules).

Generated from the build plan for this surface. The handlers live in
``oauth_authorize/__init__.py`` — that is the deployed entry point and must not
be rewritten — but the contract's build plan names ``oauth/`` as the package of
models, so making it an explicit package lets its sibling modules resolve both
at runtime and under the static checker. This file defines only persistence
shapes; no store is opened here at import time (D-30: each service opens its own).
"""

from dataclasses import dataclass


@dataclass
class OAuthClient:
    """A registered client (R-1387): id, secret, and the redirect URIs it may use."""

    client_id: str
    client_secret: str = ""
    redirect_uri: str = ""
    redirect_uris: list = None


@dataclass
class AuthorizationCode:
    """A one-time authorization code linked to exactly one registered client.

    ``issued_at`` is the application clock at creation; ``expires_in`` is the
    configured lifetime in seconds, so expiration is a comparison against that
    age rather than a fixed wall-clock instant (build_guidance).
    """

    id: str
    code: str = ""
    client_id: str = ""
    redirect_uri: str = ""
    state: str = ""
    issued_at: float = 0.0
    expires_in: int = 600


__all__ = ["OAuthClient", "AuthorizationCode"]
