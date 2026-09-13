"""In-memory token-bucket rate limit grounding (factory Pattern)."""

import time


class TokenBucket:
    def __init__(self, rate_per_s: float, capacity: float):
        self.rate = rate_per_s
        self.capacity = capacity
        self.tokens = capacity
        self.updated = time.monotonic()

    def allow(self, cost: float = 1.0) -> bool:
        now = time.monotonic()
        self.tokens = min(
            self.capacity,
            self.tokens + (now - self.updated) * self.rate,
        )
        self.updated = now
        if self.tokens < cost:
            return False
        self.tokens -= cost
        return True
