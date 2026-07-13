from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT / "03-projects" / "zendesk-style-support-adapter"
DEFAULT_OUTPUT = ROOT / "docs" / "support-adapter-data.json"
DEMO_SECRET = "synthetic-recorded-signing-key"

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from support_adapter.adapter import (  # noqa: E402
    InMemoryEventStore,
    SupportWebhookAdapter,
    sign_payload,
)
from support_adapter.recorded import RecordedTriageEngine  # noqa: E402


def event(
    event_id: str,
    case_id: str,
    ticket_id: int,
    subject: str,
    description: str,
    *,
    requester_email: str = "synthetic@example.com",
) -> dict[str, Any]:
    return {
        "schema_version": "zendesk-style-webhook-v1",
        "event_id": event_id,
        "event_type": "ticket.created",
        "occurred_at": "2026-07-13T18:00:00Z",
        "account_subdomain": "synthetic-demo",
        "demo_case_id": case_id,
        "ticket": {
            "id": ticket_id,
            "subject": subject,
            "description": description,
            "status": "new",
            "priority": None,
            "requester": {"name": "Synthetic Requester", "email": requester_email},
            "tags": ["public_demo", "synthetic"],
        },
    }


def encode(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def run(
    adapter: SupportWebhookAdapter,
    payload: dict[str, Any],
    store: InMemoryEventStore,
    *,
    valid_signature: bool = True,
) -> dict[str, Any]:
    body = encode(payload)
    signature = sign_payload(DEMO_SECRET, body) if valid_signature else "0" * 64
    return adapter.process(body, signature, store)


def build_payload() -> dict[str, object]:
    adapter = SupportWebhookAdapter(DEMO_SECRET, RecordedTriageEngine())
    valid = event(
        "evt_recorded_valid",
        "T003",
        9003,
        "Production webhook failures",
        "Every production webhook has returned HTTP 500 since this morning.",
    )
    pii = event(
        "evt_recorded_pii",
        "T001",
        9001,
        "Password reset email missing",
        "Reset mail never arrives. Contact pablo@example.com or 212-555-0100.",
        requester_email="pablo@example.com",
    )
    duplicate = event(
        "evt_recorded_duplicate",
        "T002",
        9002,
        "Duplicate card charge",
        "Our company card has two pending charges for one invoice.",
    )
    unsupported = event(
        "evt_recorded_unsupported",
        "T999",
        9999,
        "Unsupported sample",
        "This signed event references a case outside the public demo allowlist.",
    )
    duplicate_store = InMemoryEventStore()
    run(adapter, duplicate, duplicate_store)

    scenarios = [
        {
            "id": "valid_proposal",
            "label": "Valid ticket creates proposal",
            "teaching_point": "Authentication, normalization, triage, and proposal creation all pass.",
            "input_summary": {
                "event_id": valid["event_id"],
                "event_type": valid["event_type"],
                "ticket_id": valid["ticket"]["id"],
                "demo_case_id": valid["demo_case_id"],
                "signature_supplied": True,
                "synthetic_data_only": True,
            },
            "result": run(adapter, valid, InMemoryEventStore()),
        },
        {
            "id": "pii_redaction",
            "label": "PII is removed before triage",
            "teaching_point": "Requester email is replaced by a reference and text PII is redacted.",
            "input_summary": {
                "event_id": pii["event_id"],
                "event_type": pii["event_type"],
                "ticket_id": pii["ticket"]["id"],
                "demo_case_id": pii["demo_case_id"],
                "contains_synthetic_pii": True,
                "signature_supplied": True,
                "synthetic_data_only": True,
            },
            "result": run(adapter, pii, InMemoryEventStore()),
        },
        {
            "id": "duplicate_delivery",
            "label": "Duplicate delivery is ignored",
            "teaching_point": "The same event id cannot create a second proposal.",
            "input_summary": {
                "event_id": duplicate["event_id"],
                "event_type": duplicate["event_type"],
                "ticket_id": duplicate["ticket"]["id"],
                "demo_case_id": duplicate["demo_case_id"],
                "delivery_attempt": 2,
                "signature_supplied": True,
                "synthetic_data_only": True,
            },
            "result": run(adapter, duplicate, duplicate_store),
        },
        {
            "id": "invalid_signature",
            "label": "Invalid signature is rejected",
            "teaching_point": "Untrusted bytes are rejected before ticket details are parsed or logged.",
            "input_summary": {
                "body_bytes": len(encode(valid)),
                "signature_supplied": True,
                "signature_valid": False,
                "synthetic_data_only": True,
            },
            "result": run(adapter, valid, InMemoryEventStore(), valid_signature=False),
        },
        {
            "id": "unsupported_case",
            "label": "Unsupported case fails closed",
            "teaching_point": "A valid signature does not bypass the synthetic case allowlist.",
            "input_summary": {
                "event_id": unsupported["event_id"],
                "event_type": unsupported["event_type"],
                "ticket_id": unsupported["ticket"]["id"],
                "demo_case_id": unsupported["demo_case_id"],
                "signature_supplied": True,
                "synthetic_data_only": True,
            },
            "result": run(adapter, unsupported, InMemoryEventStore()),
        },
    ]
    rendered = json.dumps(scenarios)
    for forbidden in (DEMO_SECRET, "pablo@example.com", "212-555-0100"):
        if forbidden in rendered:
            raise RuntimeError(f"Unsafe value reached the recorded adapter evidence: {forbidden}")
    return {
        "metadata": {
            "project": "Mocked Zendesk-Style Support Adapter",
            "schema_version": "support-adapter-evidence-v1",
            "scenario_count": len(scenarios),
            "synthetic_data_only": True,
            "external_services_required": False,
            "external_mutations_performed": False,
        },
        "contract": {
            "inbound": "signed zendesk-style-webhook-v1",
            "internal": "normalized redacted ticket",
            "outbound": "proposed-only ticket update",
            "approval_required": True,
        },
        "scenarios": scenarios,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export mocked support-adapter trace evidence.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build_payload(), indent=2) + "\n"

    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            print(f"Support adapter export is stale: {args.output}")
            print("Run: python scripts/export_support_adapter.py")
            return 1
        print(f"Support adapter export is current: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Wrote support adapter evidence to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
