from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from streamflow.producer import generate_events, write_jsonl
from streamflow.quality import (
    mark_duplicate_events,
    parse_event_json,
    split_valid_rejected,
    validate_event,
)


class StreamFlowQualityTests(unittest.TestCase):
    def test_valid_event_passes(self) -> None:
        event = {
            "event_id": "evt_001",
            "event_type": "purchase",
            "event_ts": "2026-06-30T14:30:00Z",
            "source": "simulator",
            "entity_id": "user_123",
            "payload": {"amount": 19.99, "currency": "USD"},
        }

        result = validate_event(event)

        self.assertTrue(result.valid)
        self.assertEqual(result.reasons, ())
        self.assertEqual(result.event["event_ts"], "2026-06-30T14:30:00Z")

    def test_missing_required_field_is_rejected(self) -> None:
        result = validate_event(
            {
                "event_type": "purchase",
                "event_ts": "2026-06-30T14:30:00Z",
                "source": "simulator",
                "payload": {"amount": 19.99},
            }
        )

        self.assertFalse(result.valid)
        self.assertIn("missing_event_id", result.reasons)

    def test_invalid_timestamp_source_and_type_are_rejected(self) -> None:
        result = validate_event(
            {
                "event_id": "evt_001",
                "event_type": "refund",
                "event_ts": "yesterday",
                "source": "unknown",
                "payload": {"amount": 19.99},
            }
        )

        self.assertFalse(result.valid)
        self.assertIn("invalid_event_ts", result.reasons)
        self.assertIn("unsupported_event_type", result.reasons)
        self.assertIn("unsupported_source", result.reasons)

    def test_duplicate_ids_are_marked(self) -> None:
        event = {
            "event_id": "evt_001",
            "event_type": "page_view",
            "event_ts": "2026-06-30T14:30:00Z",
            "source": "web",
            "payload": {"page": "home"},
        }
        results = mark_duplicate_events([validate_event(event), validate_event(dict(event))])

        self.assertEqual(len(results), 2)
        self.assertTrue(all("duplicate_event_id" in result.reasons for result in results))
        self.assertTrue(all(not result.valid for result in results))

    def test_split_valid_rejected(self) -> None:
        valid_event = {
            "event_id": "evt_001",
            "event_type": "page_view",
            "event_ts": "2026-06-30T14:30:00Z",
            "source": "web",
            "payload": {"page": "home"},
        }
        invalid_event = {**valid_event, "event_id": "evt_002", "payload": "bad"}

        valid, rejected = split_valid_rejected([valid_event, invalid_event])

        self.assertEqual(len(valid), 1)
        self.assertEqual(len(rejected), 1)
        self.assertIn("payload_not_object", rejected[0]["rejection_reasons"])

    def test_parse_event_json_rejects_invalid_json(self) -> None:
        result = parse_event_json("{not json")

        self.assertFalse(result.valid)
        self.assertEqual(result.reasons, ("invalid_json",))

    def test_generate_events_and_write_jsonl(self) -> None:
        events = generate_events(5, seed=1, invalid_rate=0)
        out = Path(__file__).parent / "tmp_events.jsonl"
        try:
            write_jsonl(events, out)
            lines = out.read_text(encoding="utf-8").splitlines()
        finally:
            if out.exists():
                out.unlink()

        self.assertEqual(len(lines), 5)
        self.assertEqual(json.loads(lines[0])["event_id"], "evt_00001")


if __name__ == "__main__":
    unittest.main()
