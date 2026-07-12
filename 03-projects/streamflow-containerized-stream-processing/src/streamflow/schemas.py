from __future__ import annotations

from dataclasses import dataclass

REQUIRED_FIELDS = ("event_id", "event_type", "event_ts", "source", "payload")
ALLOWED_EVENT_TYPES = ("page_view", "add_to_cart", "purchase", "video_play")
ALLOWED_SOURCES = ("simulator", "web", "mobile", "api")


@dataclass(frozen=True)
class StreamFlowConfig:
    topic: str = "streamflow.events"
    broker: str = "redpanda:9092"
    allowed_event_types: tuple[str, ...] = ALLOWED_EVENT_TYPES
    allowed_sources: tuple[str, ...] = ALLOWED_SOURCES


def event_contract() -> dict[str, dict[str, object]]:
    return {
        "event_id": {"type": "string", "required": True},
        "event_type": {"type": "string", "required": True},
        "event_ts": {"type": "timestamp string", "required": True},
        "source": {"type": "string", "required": True},
        "payload": {"type": "object", "required": True},
        "entity_id": {"type": "string", "required": False},
    }
