"""Server-Sent Events grounding (factory Pattern).

Helpers and a FastAPI-ready generator for ``text/event-stream``. Not a broker.
"""

from __future__ import annotations

import json
from typing import Any, AsyncIterator, Iterable

CONTENT_TYPE = "text/event-stream"
HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def format_sse(event: str | None, data: str, *, event_id: str | None = None) -> str:
    """One SSE event block ending in a blank line."""
    lines = []
    if event_id is not None:
        lines.append(f"id: {event_id}")
    if event:
        lines.append(f"event: {event}")
    for piece in (data or "").splitlines() or [""]:
        lines.append(f"data: {piece}")
    lines.append("")
    return "\n".join(lines)


def format_sse_json(
    event: str | None, payload: Any, *, event_id: str | None = None,
) -> str:
    return format_sse(event, json.dumps(payload), event_id=event_id)


async def stream_events(
    events: Iterable[tuple[str | None, Any]],
) -> AsyncIterator[str]:
    """Yield formatted SSE blocks from ``(event_name, payload)`` pairs."""
    for index, (name, payload) in enumerate(events):
        if isinstance(payload, (dict, list)):
            yield format_sse_json(name, payload, event_id=str(index))
        else:
            yield format_sse(name, str(payload), event_id=str(index))
