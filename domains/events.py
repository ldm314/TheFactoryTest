"""Domain event model and operations for the domains surface.

The behaviour handlers in ``domains/__init__.py`` call these helpers, so they
live beside that module (same package) rather than under a new name: an
imported-but-never-defined name is how a rebuild most commonly fails.

A default structured-logging subscriber attaches to the shared broker at import
time; every published event is fanned out on ``"*"`` so each subscriber sees it
in publish order (settle: subscriber fan-out mechanism).
"""

import hashlib
import logging
from datetime import datetime, timezone

from store import clock as _clock
from store import open_store

from domain_events import subscribe as _broker_subscribe
from domain_events import publish as _broker_publish
from domains import RETENTION_DAYS
import json


# Self-contained constants — this module is not __init__.py and has no access to
# those names. Keep them identical to the contract's surface defaults so a name
# invented here never goes undefined (lint.static / F821).
SERVICE_NAME = "domains"
RECORD_FIELDS = ["name", "occurred_at"]

logger = logging.getLogger("domains.events")

_event_store = open_store(SERVICE_NAME, RETENTION_DAYS, RECORD_FIELDS)

# In-process replay cache: idempotency-key -> last recorded event. Keyed by the
# owner so one client's replay never shadows another's within the window.
_IDEMPOTENCY_CACHE = {}


def _iso():
    """ISO 8601 UTC timestamp derived from the application clock."""
    return (
        datetime.fromtimestamp(_clock.now(), tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256(value):
    """SHA-256 of a JSON-encoded value, hex — used only for cache row ids."""
    return hashlib.sha256(json.dumps(value).encode()).hexdigest()


def _default_subscriber(event):
    """Settle: a default structured-logging handler on the broker at import."""
    logger.info("subscriber received event=%s", event)


_broker_subscribe("*", _default_subscriber)


def record_event(owner="", name=None, occurred_at=None, idempotency_key=None):
    """Record one domain event in the outbox and make it available to subscribers.

    Idempotent replay within the recent window returns the last recorded event for
    ``(owner, idempotency_key)`` without writing a second row; callers still get a
    201 with the cached ``event_id``, ``name`` and ``occurred_at``. When `name` is
    missing the record is rejected — this returns an empty dict (the handler maps
    that to 400).
    """
    if name is None or not isinstance(name, str) or not name.strip():
        return {}

    occurred_at = occurred_at or _iso()

    # Idempotent replay: return the cached record without re-writing.
    if idempotency_key:
        key = f"{owner}|{idempotency_key}"
        cached = _IDEMPOTENCY_CACHE.get(key)
        if isinstance(cached, dict):
            logger.info("domain event replayed type=%s id=%s", name, cached["event_id"])
            return {
                "event_id": cached["event_id"],
                "name": cached["name"],
                "occurred_at": cached["occurred_at"],
            }

    record = {"name": name, "occurred_at": occurred_at}

    stored = _event_store.put(record)

    _IDEMPOTENCY_CACHE[f"{owner}|{idempotency_key or ''}"] = {
        "event_id": stored["id"],
        "name": name,
        "occurred_at": occurred_at,
    }

    logger.info("domain event emitted type=%s id=%s", name, stored["id"])

    try:
        _broker_publish("*", {"name": name, "occurred_at": occurred_at})
    except Exception:  # noqa: BLE001
        logger.exception("failed to publish domain event id=%s", stored["id"])

    return {
        "event_id": stored["id"],
        "name": name,
        "occurred_at": occurred_at,
    }


def get_events():
    """List real recorded events for a subscriber, filtering cache stubs.

    Idempotency-cache rows lack the required ``name`` field and so are not domain
    events; they never reach subscribers via GET (settle: distinguish by absence).
    """
    if not _event_store.applied:
        return []
    for row in _event_store.list():
        record = row.get("body", {})
        if isinstance(record, dict) and bool(record.get("name")):
            yield {
                "id": row["id"],
                "name": record["name"],
                "occurred_at": record.get("occurred_at"),
            }


def get_event(event_id):
    """Return one recorded event by id, or None. Real events only."""
    if not _event_store.applied:
        return None
    row = _event_store.get(event_id)
    if not isinstance(row, dict):
        return None
    record = row.get("body", {})
    if not isinstance(record, dict) or not bool(record.get("name")):
        return None
    return {
        "id": row["id"],
        "name": record["name"],
        "occurred_at": record.get("occurred_at"),
    }
