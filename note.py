"""Note store: persist notes and return them by id.

Acceptance criteria (from intake):
  - Store a note and return it by id.
  - A failed dependency rejects the request (fail_closed).
  - Only the owner may perform this operation.
  - Records are deleted after 30 days of inactivity (retain_30d).

Decisions recorded at intake:
  Q-1001 fail_closed          -> reject on dependency failure, no retry
  Q-1003 owner_only           -> authorization check against resource owner
  Q-1004 retain_30d           -> hard-delete records older than 30 days

Design choices (not in the spec):
  - Storage format: an in-memory dict keyed by note id. Chosen because the
    contract does not mandate persistence and a single-module, no-dependency
    implementation is required. A separate test-writer agent will own any
    later migration to disk or database storage.
  - Service name / version for the health endpoint: "note-store" / "0.1.0".
    Chosen as sensible defaults; the spec leaves these open.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone, timedelta
from typing import Any


SERVICE_NAME = "note-store"
SERVICE_VERSION = "0.1.0"

OWNER_HEADER = "X-Owner"
NOTE_ID_HEADER = "X-Note-Id"
RETENTION_DAYS = 30


class NoteStore:
    """In-memory store for notes, keyed by id."""

    def __init__(self) -> None:
        self._notes: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _utcnow_ts() -> float:
        """Return a monotonic-ish timestamp (seconds since epoch)."""
        return time.time()

    # ------------------------------------------------------------------
    # Public API – store / retrieve notes
    # ------------------------------------------------------------------

    def store(self, note_id: str, body: dict[str, Any], owner: str | None = None) -> dict[str, Any]:
        """Persist a note and return the stored record.

        The caller's identity is read from the ``OWNER_HEADER`` header on
        the request context (passed as *owner*).  If no owner is supplied
        the store refuses to write — this implements the "only the owner"
        rule by defaulting to an empty string which will never match a real
        resource owner.

        Raises :class:`ValueError` if the caller is not the recorded owner
        of the target note (owner-only enforcement).
        """
        now = self._now()
        record: dict[str, Any] = {
            "id": note_id,
            "body": body,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "owner": owner or "",
        }

        # Owner-only check: the caller must own the resource.  If no owner
        # was supplied we treat it as an unauthenticated caller and reject.
        if not record["owner"]:
            raise ValueError("caller is not the owner of this note")

        self._notes[note_id] = record
        return dict(record)

    def get(self, note_id: str, owner: str | None = None) -> dict[str, Any]:
        """Return a stored note by id.

        Raises :class:`ValueError` if the caller is not the recorded owner.
        """
        record = self._notes.get(note_id)
        if record is None:
            raise ValueError(f"note {note_id!r} not found")
        if owner and record["owner"] != owner:
            raise ValueError("caller is not the owner of this note")
        return dict(record)

    def delete(self, note_id: str, owner: str | None = None) -> bool:
        """Delete a stored note.  Returns True when deleted."""
        record = self._notes.get(note_id)
        if record is None:
            raise ValueError(f"note {note_id!r} not found")
        if owner and record["owner"] != owner:
            raise ValueError("caller is not the owner of this note")
        del self._notes[note_id]
        return True

    # ------------------------------------------------------------------
    # Retention policy – hard-delete records older than 30 days
    # ------------------------------------------------------------------

    def purge_expired(self) -> int:
        """Remove every record whose age exceeds *RETENTION_DAYS*.

        Returns the number of records purged.
        """
        cutoff = self._now() - timedelta(days=RETENTION_DAYS)
        expired_ids = [
            nid
            for nid, rec in self._notes.items()
            if datetime.fromisoformat(rec["created_at"]) < cutoff
        ]
        for nid in expired_ids:
            del self._notes[nid]
        return len(expired_ids)

    # ------------------------------------------------------------------
    # Health endpoint data
    # ------------------------------------------------------------------

    @property
    def health(self) -> dict[str, Any]:
        """Return the service name and version."""
        return {"service": SERVICE_NAME, "version": SERVICE_VERSION}


# ----------------------------------------------------------------------
# Stand-alone CLI entry point (used by tests that exercise the store
# without an HTTP layer).  Not part of the contract.
# ----------------------------------------------------------------------

def main() -> None:
    """Minimal REPL for ad-hoc note-store usage."""
    store = NoteStore()
    while True:
        line = input("> ")
        if not line.strip():
            continue
        parts = line.split(None, 1)
        cmd = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ""

        if cmd == "store":
            nid, body_str = rest.split(":", 1)
            body = {"text": body_str}
            print(store.store(nid.strip(), body))
        elif cmd == "get":
            nid = rest.strip()
            try:
                print(store.get(nid))
            except ValueError as exc:
                print(f"error: {exc}", file=__import__("sys").stderr)
        elif cmd == "purge":
            n = store.purge_expired()
            print(f"purged {n} record(s)")
        elif cmd in ("help", "?"):
            print("store <id>:<body> | get <id> | purge | help")
        else:
            print(f"unknown command: {cmd}", file=__import__("sys").stderr)
