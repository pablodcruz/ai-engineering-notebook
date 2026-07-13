from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import asdict, dataclass
from typing import Any, Protocol

SUPPORTED_EVENT = "ticket.created"
SUPPORTED_CASE_IDS = {"T001", "T002", "T003"}
MAX_BODY_BYTES = 12_000
EVENT_FIELDS = {
    "schema_version",
    "event_id",
    "event_type",
    "occurred_at",
    "account_subdomain",
    "demo_case_id",
    "ticket",
}
TICKET_FIELDS = {
    "id",
    "subject",
    "description",
    "status",
    "priority",
    "requester",
    "tags",
}
REQUESTER_FIELDS = {"name", "email"}
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)")


class TriageEngine(Protocol):
    def triage(self, case_id: str, ticket: str) -> dict[str, Any]: ...


@dataclass(frozen=True)
class NormalizedTicket:
    source: str
    external_ticket_id: str
    event_id: str
    case_id: str
    subject: str
    description: str
    status: str
    priority: str | None
    tags: tuple[str, ...]
    requester_reference: str
    redactions: dict[str, int]


class InMemoryEventStore:
    """Demo-only replay store; production needs shared storage and expiry."""

    def __init__(self) -> None:
        self._claimed: set[str] = set()

    def claim(self, event_id: str) -> bool:
        if event_id in self._claimed:
            return False
        self._claimed.add(event_id)
        return True


class SupportWebhookAdapter:
    def __init__(self, signing_secret: str, triage_engine: TriageEngine) -> None:
        if not signing_secret:
            raise ValueError("A webhook signing secret is required")
        self.signing_secret = signing_secret
        self.triage_engine = triage_engine

    def process(
        self,
        raw_body: bytes,
        signature: str,
        event_store: InMemoryEventStore,
    ) -> dict[str, Any]:
        trace: list[dict[str, Any]] = []
        if not raw_body or len(raw_body) > MAX_BODY_BYTES:
            return _rejected("invalid_body", "Webhook body size is invalid.", trace)

        trace.append(_step("authenticate_webhook", "started", {"body_bytes": len(raw_body)}))
        if not verify_signature(self.signing_secret, raw_body, signature):
            trace[-1] = _step("authenticate_webhook", "rejected", {"reason": "signature_mismatch"})
            return _rejected("invalid_signature", "Webhook authentication failed.", trace)
        trace[-1] = _step("authenticate_webhook", "passed", {"signature_logged": False})

        try:
            payload = json.loads(raw_body)
            event = validate_event(payload)
        except (json.JSONDecodeError, ValueError) as exc:
            trace.append(_step("validate_contract", "rejected", {"reason": str(exc)}))
            return _rejected("invalid_event", str(exc), trace)
        trace.append(
            _step(
                "validate_contract",
                "passed",
                {"event_id": event["event_id"], "event_type": event["event_type"]},
            )
        )

        if not event_store.claim(event["event_id"]):
            trace.append(
                _step(
                    "claim_event",
                    "ignored",
                    {"event_id": event["event_id"], "reason": "duplicate_delivery"},
                )
            )
            return {
                "status": "ignored",
                "reason": "duplicate_delivery",
                "external_ticket_id": str(event["ticket"]["id"]),
                "trace": trace,
                "external_mutation_performed": False,
            }
        trace.append(_step("claim_event", "passed", {"event_id": event["event_id"]}))

        normalized = normalize_ticket(event)
        trace.append(
            _step(
                "normalize_and_redact",
                "passed",
                {
                    "external_ticket_id": normalized.external_ticket_id,
                    "case_id": normalized.case_id,
                    "redactions": normalized.redactions,
                    "requester_email_retained": False,
                },
            )
        )

        triage = self.triage_engine.triage(
            normalized.case_id,
            f"{normalized.subject}\n{normalized.description}",
        )
        _validate_triage_decision(triage)
        trace.append(
            _step(
                "run_triage",
                "passed",
                {
                    "product_area": triage["product_area"],
                    "urgency": triage["urgency"],
                },
            )
        )

        proposal = build_update_proposal(normalized, triage)
        trace.append(
            _step(
                "propose_ticket_update",
                "awaiting_approval",
                {
                    "external_ticket_id": normalized.external_ticket_id,
                    "update_mode": "proposed_only",
                },
            )
        )
        return {
            "status": "proposal_ready",
            "normalized_ticket": asdict(normalized),
            "triage_decision": triage,
            "proposed_update": proposal,
            "trace": trace,
            "external_mutation_performed": False,
        }


def sign_payload(secret: str, raw_body: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()


def verify_signature(secret: str, raw_body: bytes, supplied: object) -> bool:
    if not isinstance(supplied, str) or len(supplied) != 64:
        return False
    expected = sign_payload(secret, raw_body)
    return hmac.compare_digest(expected, supplied.lower())


def validate_event(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Webhook payload must be an object.")
    _require_exact_fields(payload, EVENT_FIELDS, "event")
    if payload.get("schema_version") != "zendesk-style-webhook-v1":
        raise ValueError("Unsupported webhook schema_version.")
    if payload.get("event_type") != SUPPORTED_EVENT:
        raise ValueError("Only ticket.created events are supported.")
    for field in ("event_id", "occurred_at", "account_subdomain"):
        _require_string(payload.get(field), f"event.{field}")
    if payload.get("demo_case_id") not in SUPPORTED_CASE_IDS:
        raise ValueError("The event does not reference a supported synthetic case.")

    ticket = payload.get("ticket")
    if not isinstance(ticket, dict):
        raise ValueError("event.ticket must be an object.")
    _require_exact_fields(ticket, TICKET_FIELDS, "event.ticket")
    if not isinstance(ticket.get("id"), int) or ticket["id"] < 1:
        raise ValueError("event.ticket.id must be a positive integer.")
    for field in ("subject", "description", "status"):
        _require_string(ticket.get(field), f"event.ticket.{field}")
    if len(ticket["description"]) > 1_000:
        raise ValueError("event.ticket.description exceeds 1000 characters.")
    if ticket.get("priority") is not None and ticket.get("priority") not in {
        "low",
        "normal",
        "high",
        "urgent",
    }:
        raise ValueError("event.ticket.priority is unsupported.")
    tags = ticket.get("tags")
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        raise ValueError("event.ticket.tags must be a list of strings.")
    requester = ticket.get("requester")
    if not isinstance(requester, dict):
        raise ValueError("event.ticket.requester must be an object.")
    _require_exact_fields(requester, REQUESTER_FIELDS, "event.ticket.requester")
    _require_string(requester.get("name"), "event.ticket.requester.name")
    _require_string(requester.get("email"), "event.ticket.requester.email")
    return payload


def normalize_ticket(event: dict[str, Any]) -> NormalizedTicket:
    ticket = event["ticket"]
    subject, subject_redactions = redact_sensitive_text(ticket["subject"])
    description, description_redactions = redact_sensitive_text(ticket["description"])
    redactions = {
        key: subject_redactions[key] + description_redactions[key] for key in subject_redactions
    }
    requester_reference = hashlib.sha256(
        ticket["requester"]["email"].strip().lower().encode("utf-8")
    ).hexdigest()[:12]
    return NormalizedTicket(
        source="zendesk_style_mock",
        external_ticket_id=str(ticket["id"]),
        event_id=event["event_id"],
        case_id=event["demo_case_id"],
        subject=subject,
        description=description,
        status=ticket["status"],
        priority=ticket["priority"],
        tags=tuple(ticket["tags"]),
        requester_reference=f"requester_{requester_reference}",
        redactions=redactions,
    )


def redact_sensitive_text(text: str) -> tuple[str, dict[str, int]]:
    email_count = len(EMAIL_PATTERN.findall(text))
    phone_count = len(PHONE_PATTERN.findall(text))
    redacted = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
    redacted = PHONE_PATTERN.sub("[REDACTED_PHONE]", redacted)
    return redacted, {"email": email_count, "phone": phone_count}


def build_update_proposal(ticket: NormalizedTicket, triage: dict[str, Any]) -> dict[str, Any]:
    priority = {"high": "high", "medium": "normal", "low": "low"}[triage["urgency"]]
    tags = sorted(
        set(ticket.tags)
        | {
            "ai_triage_proposed",
            f"product_area_{triage['product_area']}",
            f"urgency_{triage['urgency']}",
        }
    )
    return {
        "external_ticket_id": ticket.external_ticket_id,
        "update_mode": "proposed_only",
        "requires_human_approval": True,
        "fields": {
            "priority": priority,
            "tags": tags,
            "internal_note": triage["recommended_response"],
        },
    }


def _validate_triage_decision(decision: object) -> None:
    if not isinstance(decision, dict):
        raise ValueError("Triage engine returned an invalid decision.")
    required = {"product_area", "urgency", "recommended_response"}
    if not required.issubset(decision):
        raise ValueError("Triage decision is missing proposal fields.")
    if decision["urgency"] not in {"low", "medium", "high"}:
        raise ValueError("Triage decision urgency is unsupported.")
    _require_string(decision["product_area"], "triage.product_area")
    _require_string(decision["recommended_response"], "triage.recommended_response")


def _rejected(code: str, message: str, trace: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "rejected",
        "error": {"code": code, "message": message},
        "trace": trace,
        "external_mutation_performed": False,
    }


def _step(name: str, status: str, detail: dict[str, Any]) -> dict[str, Any]:
    return {"step": name, "status": status, "detail": detail}


def _require_exact_fields(value: dict[str, Any], expected: set[str], context: str) -> None:
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        raise ValueError(f"{context} missing fields: {', '.join(missing)}.")
    if extra:
        raise ValueError(f"{context} unexpected fields: {', '.join(extra)}.")


def _require_string(value: object, context: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context} must be a non-empty string.")
