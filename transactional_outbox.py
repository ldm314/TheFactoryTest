"""Transactional outbox grounding (factory Pattern).

Persist intent with the business write; flush to Kafka when
``KAFKA_BOOTSTRAP`` is set, otherwise mark published in-process.
"""

import os


def outbox_row(*, aggregate_type: str, aggregate_id: str, event_type: str, payload: dict):
    return {
        "aggregate_type": aggregate_type,
        "aggregate_id": aggregate_id,
        "event_type": event_type,
        "payload": payload,
        "published": False,
    }


def kafka_enabled() -> bool:
    return bool(os.environ.get("KAFKA_BOOTSTRAP") or os.environ.get("KAFKA_BROKERS"))


def flush_row(row: dict) -> dict:
    """Best-effort publish; returns the row with published=True on success."""
    if kafka_enabled():
        try:
            # Dynamic load so SBOM does not treat kafka_producer as required
            # when this Pattern ships without the kafka-producer sibling file.
            publish_json = __import__(
                "kafka_producer", fromlist=["publish_json"]
            ).publish_json
            publish_json(
                topic=str(row.get("event_type") or "domain.events"),
                payload=row.get("payload") or {},
                key=str(row.get("aggregate_id") or ""),
            )
        except Exception:
            return row
    row = dict(row)
    row["published"] = True
    return row
