"""What this component reports about itself (docs/15 §2).

A Pattern rather than something each component invents: docs/15 derives SLOs
from what is emitted, and SLOs derived from three components that count
differently are three unrelated numbers.

Deliberately small — a counter per outcome and nothing else. The point is that
every component counts the same things under the same names, not that this is a
metrics system.
"""

import threading

_lock = threading.Lock()
counters = {}


def count(name, amount=1):
    with _lock:
        counters[name] = counters.get(name, 0) + amount


def snapshot():
    """Every counter, for the health endpoint."""
    with _lock:
        return dict(counters)


def reset():
    """For tests. Production never calls it."""
    with _lock:
        counters.clear()
