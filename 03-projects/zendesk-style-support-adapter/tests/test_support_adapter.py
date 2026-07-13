from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from support_adapter.adapter import (
    InMemoryEventStore,
    SupportWebhookAdapter,
    build_update_proposal,
    normalize_ticket,
    redact_sensitive_text,
    sign_payload,
    validate_event,
    verify_signature,
)
from support_adapter.recorded import RecordedTriageEngine

SECRET = "synthetic-test-key"


def event(
    *,
    event_id: str = "evt_001",
    case_id: str = "T003",
    description: str = "Every production webhook returns HTTP 500.",
) -> dict:
    return {
        "schema_version": "zendesk-style-webhook-v1",
        "event_id": event_id,
        "event_type": "ticket.created",
        "occurred_at": "2026-07-13T18:00:00Z",
        "account_subdomain": "synthetic-demo",
        "demo_case_id": case_id,
        "ticket": {
            "id": 9003,
            "subject": "Production webhook failures",
            "description": description,
            "status": "new",
            "priority": None,
            "requester": {"name": "Synthetic User", "email": "person@example.com"},
            "tags": ["webhook", "production"],
        },
    }


def encoded(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


class SupportAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = SupportWebhookAdapter(SECRET, RecordedTriageEngine())

    def test_valid_webhook_produces_proposed_update_without_mutation(self) -> None:
        body = encoded(event())
        result = self.adapter.process(body, sign_payload(SECRET, body), InMemoryEventStore())

        self.assertEqual(result["status"], "proposal_ready")
        self.assertFalse(result["external_mutation_performed"])
        self.assertEqual(result["proposed_update"]["update_mode"], "proposed_only")
        self.assertTrue(result["proposed_update"]["requires_human_approval"])
        self.assertEqual(result["proposed_update"]["fields"]["priority"], "high")
        self.assertIn("product_area_integrations", result["proposed_update"]["fields"]["tags"])

    def test_invalid_signature_is_rejected_before_payload_details_are_exposed(self) -> None:
        body = encoded(event(description="private@example.com called 212-555-0100"))
        result = self.adapter.process(body, "0" * 64, InMemoryEventStore())

        self.assertEqual(result["error"]["code"], "invalid_signature")
        self.assertEqual(len(result["trace"]), 1)
        self.assertNotIn("private@example.com", json.dumps(result))
        self.assertNotIn("212-555-0100", json.dumps(result))

    def test_duplicate_delivery_is_idempotently_ignored(self) -> None:
        body = encoded(event())
        signature = sign_payload(SECRET, body)
        store = InMemoryEventStore()

        first = self.adapter.process(body, signature, store)
        duplicate = self.adapter.process(body, signature, store)

        self.assertEqual(first["status"], "proposal_ready")
        self.assertEqual(duplicate["status"], "ignored")
        self.assertEqual(duplicate["reason"], "duplicate_delivery")
        self.assertFalse(duplicate["external_mutation_performed"])

    def test_pii_is_redacted_and_requester_email_is_not_retained(self) -> None:
        payload = event(description="Contact ops@example.com or 212-555-0100 about the webhook.")
        body = encoded(payload)
        result = self.adapter.process(body, sign_payload(SECRET, body), InMemoryEventStore())
        rendered = json.dumps(result)

        self.assertIn("[REDACTED_EMAIL]", rendered)
        self.assertIn("[REDACTED_PHONE]", rendered)
        self.assertNotIn("ops@example.com", rendered)
        self.assertNotIn("person@example.com", rendered)
        self.assertEqual(result["normalized_ticket"]["redactions"], {"email": 1, "phone": 1})

    def test_unsupported_case_and_extra_fields_fail_contract_validation(self) -> None:
        unsupported = event(case_id="T999")
        with self.assertRaisesRegex(ValueError, "supported synthetic case"):
            validate_event(unsupported)

        extra = event()
        extra["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "unexpected fields"):
            validate_event(extra)

    def test_signature_helpers_are_deterministic_and_constant_contract(self) -> None:
        body = encoded(event())
        signature = sign_payload(SECRET, body)

        self.assertEqual(len(signature), 64)
        self.assertTrue(verify_signature(SECRET, body, signature))
        self.assertFalse(verify_signature(SECRET, body + b" ", signature))
        self.assertFalse(verify_signature(SECRET, body, None))

    def test_redaction_and_proposal_functions_are_independently_testable(self) -> None:
        redacted, counts = redact_sensitive_text("Email a@b.com or call +1 212-555-0100")
        normalized = normalize_ticket(event())
        proposal = build_update_proposal(
            normalized,
            {
                "product_area": "integrations",
                "urgency": "medium",
                "recommended_response": "Collect a delivery id.",
            },
        )

        self.assertEqual(counts, {"email": 1, "phone": 1})
        self.assertNotIn("a@b.com", redacted)
        self.assertEqual(proposal["fields"]["priority"], "normal")

    def test_malformed_json_is_rejected_without_triage(self) -> None:
        body = b"{not-json"
        result = self.adapter.process(body, sign_payload(SECRET, body), InMemoryEventStore())

        self.assertEqual(result["error"]["code"], "invalid_event")
        self.assertFalse(result["external_mutation_performed"])


if __name__ == "__main__":
    unittest.main()
