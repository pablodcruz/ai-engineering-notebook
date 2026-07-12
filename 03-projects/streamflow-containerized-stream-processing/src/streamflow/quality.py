from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .schemas import ALLOWED_EVENT_TYPES, ALLOWED_SOURCES, REQUIRED_FIELDS


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    event: dict[str, Any]
    reasons: tuple[str, ...]


def parse_event_json(raw: str) -> ValidationResult:
    try:
        event = json.loads(raw)
    except json.JSONDecodeError:
        return ValidationResult(valid=False, event={"raw": raw}, reasons=("invalid_json",))
    if not isinstance(event, dict):
        return ValidationResult(valid=False, event={"raw": raw}, reasons=("event_not_object",))
    return validate_event(event)


def validate_event(
    event: dict[str, Any],
    *,
    allowed_event_types: tuple[str, ...] = ALLOWED_EVENT_TYPES,
    allowed_sources: tuple[str, ...] = ALLOWED_SOURCES,
) -> ValidationResult:
    reasons: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in event or event[field] in (None, ""):
            reasons.append(f"missing_{field}")

    if "event_ts" in event and event.get("event_ts") not in (None, ""):
        if parse_timestamp(str(event["event_ts"])) is None:
            reasons.append("invalid_event_ts")

    if event.get("event_type") and event["event_type"] not in allowed_event_types:
        reasons.append("unsupported_event_type")

    if event.get("source") and event["source"] not in allowed_sources:
        reasons.append("unsupported_source")

    if "payload" in event and not isinstance(event.get("payload"), dict):
        reasons.append("payload_not_object")

    return ValidationResult(valid=not reasons, event=normalize_event(event), reasons=tuple(reasons))


def mark_duplicate_events(results: list[ValidationResult]) -> list[ValidationResult]:
    counts: dict[str, int] = {}
    for result in results:
        event_id = result.event.get("event_id")
        if isinstance(event_id, str) and event_id:
            counts[event_id] = counts.get(event_id, 0) + 1

    marked: list[ValidationResult] = []
    for result in results:
        event_id = result.event.get("event_id")
        if isinstance(event_id, str) and counts.get(event_id, 0) > 1:
            reasons = tuple(dict.fromkeys((*result.reasons, "duplicate_event_id")))
            marked.append(ValidationResult(valid=False, event=result.event, reasons=reasons))
        else:
            marked.append(result)
    return marked


def split_valid_rejected(
    events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    results = mark_duplicate_events([validate_event(event) for event in events])
    valid: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for result in results:
        if result.valid:
            valid.append(result.event)
        else:
            rejected.append({**result.event, "rejection_reasons": list(result.reasons)})
    return valid, rejected


def parse_timestamp(value: str) -> datetime | None:
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(event)
    timestamp = normalized.get("event_ts")
    if isinstance(timestamp, str):
        parsed = parse_timestamp(timestamp)
        if parsed is not None:
            normalized["event_ts"] = parsed.isoformat().replace("+00:00", "Z")
    return normalized
