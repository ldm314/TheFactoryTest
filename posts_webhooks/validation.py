"""Webhook signature hashing and in-window de-duplication for posts/webhooks.

The route already checks the presented ``X-Signature`` against the registered
secret before this handler runs (see the scaffold guard), so nothing here is a
second authentication decision — it only hashes the raw body for de-duplication
and remembers which signatures have been accepted within the window.
"""

import hashlib
import threading
import time


# How long an accepted signature stays "already seen". A webhook client retries
# delivery; this window lets us answer a repeat with 200 instead of running the
# downstream handler twice. Fixed seconds, not wall-clock epochs: absolute is
# fragile across clock changes, relative to first sight is what de-dup needs.
DEDUP_TTL_SECONDS = 300


def signature_hash(raw_body: bytes) -> str:
    """A stable digest of the raw request body — never the parsed JSON."""
    return hashlib.sha256(raw_body).hexdigest()


class DedupStore:
    """In-window de-duplication keyed by signature hash.

    Kept in memory for this cycle: a signature is only useful as proof once, and
    what is not remembered here is lost the moment we stop looking at it. A
    later cycle can back this with the database without changing the handler.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._seen: dict[str, float] = {}

    def _prune(self, now: float) -> None:
        expired = [key for key, until in self._seen.items() if now > until]
        with self._lock:
            for key in expired:
                del self._seen[key]

    def seen(self, sig_hash: str, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        self._prune(now)
        with self._lock:
            return sig_hash in self._seen

    def record(self, sig_hash: str, now: float | None = None) -> None:
        now = time.time() if now is None else now
        self._prune(now)
        with self._lock:
            self._seen[sig_hash] = now + DEDUP_TTL_SECONDS


_dedup = DedupStore()
