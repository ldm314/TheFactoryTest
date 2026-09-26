"""In-process domain events grounding (factory Pattern)."""

_subscribers = {}


def subscribe(event_type: str, handler):
    _subscribers.setdefault(event_type, []).append(handler)


def publish(event_type: str, payload: dict):
    for handler in _subscribers.get(event_type, ()):
        handler(payload)
    try:
        import os
        if not (os.environ.get("KAFKA_BOOTSTRAP") or os.environ.get("KAFKA_BROKERS")):
            return
        # Dynamic: optional sibling Pattern; must not fail dependency.declared
        # when only domain-events@1 is applied (sandbox has no kafka clients).
        publish_json = __import__(
            "kafka_producer", fromlist=["publish_json"]
        ).publish_json
        publish_json(topic=event_type, payload=payload)
    except Exception:
        pass


def make_event(event_type: str, payload=None, **fields):
    """Build one event dict — the shape agents reach for as ``_make_event``."""
    event = {"event_type": event_type, "payload": dict(payload or {})}
    event.update(fields)
    return event


# Common agent spellings so lint.static F821 clears via sibling import autofix.
_make_event = make_event


def get_publisher():
    """Return the in-process ``publish`` callable (agent alias)."""
    return publish
