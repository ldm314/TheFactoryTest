"""In-process domain events grounding (factory Pattern)."""

_subscribers = {}


def subscribe(event_type: str, handler):
    _subscribers.setdefault(event_type, []).append(handler)


def publish(event_type: str, payload: dict):
    for handler in _subscribers.get(event_type, ()):
        handler(payload)
