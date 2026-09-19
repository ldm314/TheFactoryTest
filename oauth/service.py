"""OAuth authorization-code flow helpers for oauth_authorize.

Generated from the build plan (build_plan.modules). The handlers in
``oauth_authorize/__init__.py`` call these; they are not a separate surface and
invent no routes or records of their own. Every name here is defined below, so
a helper that is called always resolves to a real function in this package.
"""

import secrets

import telemetry
from store import open_store, clock

# Client registrations live in the oauth_clients schema (R-1387). The authorize
# surface validates client_id and redirect_uri against it; D-30 keeps each
# service's own records here for codes.
CLIENTS_STORE = "oauth_clients"
CODE_STORE = "oauth_authorize"

# Authorization codes are short-lived by design (build_guidance: typically 10
# minutes). A code older than this is rejected rather than exchanged.
CODE_LIFETIME_SECONDS = 600


def validate_client(client_id, redirect_uri):
    """Return the stored registration for ``client_id`` or ``None``.

    Looks up by store id first, then scans every record matching ``client_id``
    exactly — registrations are keyed by a sequential id with client_id as a
    projected field (R-1387). The redirect_uri is returned when present so the
    caller can check it without another round-trip.
    """
    clients = open_store(CLIENTS_STORE)
    record = clients.get(str(client_id))
    if record is not None:
        return record

    for candidate in (clients.list() or []):
        if str(candidate.get("client_id")) == str(client_id):
            return candidate
    return None


def generate_authorization_code():
    """A short-lived, unguessable authorization code."""
    return secrets.token_urlsafe(24)


def store_authorization_code(code, client_id, redirect_uri, state=""):
    """Persist a one-time authorization code linked to exactly one client.

    Records the issue time and lifetime so expiration can be checked later;
    counts issuance for telemetry (build_guidance). Returns what was stored.
    """
    telemetry.count("authorization_issued")
    codes = open_store(CODE_STORE)
    stored = dict(codes.put(
        {
            "id": code,
            "code": code,
            "client_id": str(client_id),
            "redirect_uri": redirect_uri or "",
            "state": state or "",
            "issued_at": clock.now(),
            "expires_in": CODE_LIFETIME_SECONDS,
        },
        owner="",
    ))
    return stored


def is_code_expired(record):
    """True when the code's lifetime has elapsed.

    Uses the application clock so a test can move time forward and force an
    expiration (build_guidance: reject expired codes). A record with no usable
    issue time counts as expired rather than being silently accepted.
    """
    issued_at = record.get("issued_at")
    if not issued_at:
        return True
    try:
        age = clock.now() - float(issued_at)
    except (TypeError, ValueError):
        return True
    return age > CODE_LIFETIME_SECONDS


def revoke_authorization_code(code):
    """A code is single-use; remove it after exchange and count the revocation.

    Returns the stored record if any remained, else ``None``.
    """
    codes = open_store(CODE_STORE)
    result = codes.get(str(code))
    if result is not None:
        telemetry.count("authorization_revoked")
    return result


def _validation_failure():
    """Count a rejected request for telemetry (build_guidance)."""
    telemetry.count("validation_failure")
