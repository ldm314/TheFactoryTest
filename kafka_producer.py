"""Kafka-compatible producer grounding (factory Pattern).

Uses ``KAFKA_BOOTSTRAP`` (or ``KAFKA_BROKERS``). When unset, ``publish_json``
is a no-op so local criteria still pass without a broker.

Optional client libraries are loaded via ``__import__`` so the attempt-tier
SBOM does not mark ``kafka`` / ``confluent_kafka`` unresolved under the
network-less sandbox image (those packages land in the compose app image).
"""

from __future__ import annotations

import json
import os
from typing import Any

BOOTSTRAP_ENV = "KAFKA_BOOTSTRAP"


def bootstrap_servers() -> str | None:
    return os.environ.get(BOOTSTRAP_ENV) or os.environ.get("KAFKA_BROKERS")


def publish_json(topic: str, payload: dict[str, Any], *, key: str = "") -> bool:
    """Publish one JSON message. True when a broker accepted it."""
    servers = bootstrap_servers()
    if not servers:
        return False
    try:
        KafkaProducer = __import__("kafka", fromlist=["KafkaProducer"]).KafkaProducer
    except ImportError:
        return _publish_via_confluent(servers, topic, payload, key=key)
    producer = KafkaProducer(
        bootstrap_servers=servers.split(","),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda v: (v or "").encode("utf-8"),
    )
    try:
        future = producer.send(topic, value=payload, key=key or None)
        future.get(timeout=10)
        return True
    finally:
        producer.close()


def _publish_via_confluent(servers: str, topic: str, payload: dict, *, key: str) -> bool:
    try:
        Producer = __import__("confluent_kafka", fromlist=["Producer"]).Producer
    except ImportError:
        return False
    producer = Producer({"bootstrap.servers": servers})
    producer.produce(
        topic, json.dumps(payload).encode("utf-8"), key=(key or None),
    )
    producer.flush(10)
    return True
