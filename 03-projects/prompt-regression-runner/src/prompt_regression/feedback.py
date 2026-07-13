from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contract import PRODUCT_AREAS, URGENCY_LEVELS

EXPORT_SCHEMA = "support-triage-review-export-v1"
REVIEW_SCHEMA = "review-v1"
CANDIDATE_SCHEMA = "feedback-candidate-package-v1"
APPROVAL_SCHEMA = "feedback-approval-v1"
SUPPORTED_SAMPLE_IDS = {"T001", "T002", "T003"}
EXECUTION_MODES = {"live", "recorded"}
OUTCOMES = {"accepted", "overridden"}
OVERRIDE_REASONS = {
    "taxonomy_correction",
    "urgency_correction",
    "response_improvement",
    "policy_or_safety",
    "other",
}

EXPORT_FIELDS = {
    "schema_version",
    "synthetic_data_only",
    "exported_at",
    "review_count",
    "reviews",
}
REVIEW_FIELDS = {
    "schema_version",
    "review_id",
    "sample_id",
    "execution_mode",
    "source_request_id",
    "prompt_version",
    "outcome",
    "override_reason",
    "model_decision",
    "final_decision",
    "reviewed_at",
}
DECISION_FIELDS = {"product_area", "urgency", "recommended_response"}


def load_feedback_export(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid feedback JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Feedback export must be a JSON object")
    return payload


def prepare_feedback_candidates(
    payload: dict[str, Any], cases: list[dict[str, Any]]
) -> dict[str, Any]:
    reviews = validate_feedback_export(payload)
    case_by_id = {str(case["id"]): case for case in cases}
    missing_cases = SUPPORTED_SAMPLE_IDS - set(case_by_id)
    if missing_cases:
        raise ValueError(
            f"Base dataset is missing supported cases: {', '.join(sorted(missing_cases))}"
        )

    accepted = 0
    corrected = 0
    duplicate_corrections = 0
    reasons: Counter[str] = Counter()
    candidates: list[dict[str, Any]] = []
    correction_fingerprints: set[str] = set()

    for review in reviews:
        if review["outcome"] == "accepted":
            accepted += 1
            continue
        corrected += 1
        reason = str(review["override_reason"])
        reasons[reason] += 1
        fingerprint = _correction_fingerprint(review)
        if fingerprint in correction_fingerprints:
            duplicate_corrections += 1
            continue
        correction_fingerprints.add(fingerprint)
        candidates.append(
            _build_candidate(review, case_by_id[str(review["sample_id"])], fingerprint)
        )

    return {
        "schema_version": CANDIDATE_SCHEMA,
        "synthetic_data_only": True,
        "promotion_status": "awaiting_human_review",
        "source_exported_at": payload["exported_at"],
        "summary": {
            "review_count": len(reviews),
            "accepted_count": accepted,
            "corrected_count": corrected,
            "candidate_count": len(candidates),
            "duplicate_corrections_omitted": duplicate_corrections,
            "override_reasons": dict(sorted(reasons.items())),
        },
        "candidates": candidates,
        "review_instructions": [
            "Confirm the human decision reflects the intended support policy.",
            "Confirm deterministic expectations remain sufficient for this case.",
            "Create an approval artifact for selected candidate ids.",
            "Merge approved cases into permanent eval data only through a reviewed code change.",
        ],
    }


def validate_feedback_export(payload: dict[str, Any]) -> list[dict[str, Any]]:
    _require_exact_fields(payload, EXPORT_FIELDS, "feedback export")
    if payload.get("schema_version") != EXPORT_SCHEMA:
        raise ValueError(f"Unsupported feedback schema: {payload.get('schema_version')!r}")
    if payload.get("synthetic_data_only") is not True:
        raise ValueError("Feedback export must declare synthetic_data_only as true")
    _parse_timestamp(payload.get("exported_at"), "exported_at")

    reviews = payload.get("reviews")
    if not isinstance(reviews, list):
        raise ValueError("reviews must be a list")
    if type(payload.get("review_count")) is not int or payload["review_count"] != len(reviews):
        raise ValueError("review_count must exactly match the number of reviews")

    validated: list[dict[str, Any]] = []
    review_ids: set[str] = set()
    for index, raw_review in enumerate(reviews):
        if not isinstance(raw_review, dict):
            raise ValueError(f"reviews[{index}] must be an object")
        _validate_review(raw_review, index)
        review_id = str(raw_review["review_id"])
        if review_id in review_ids:
            raise ValueError(f"Duplicate review_id: {review_id}")
        review_ids.add(review_id)
        validated.append(raw_review)
    return validated


def build_approval_artifact(
    package: dict[str, Any], *, reviewer: str, approved_ids: list[str]
) -> dict[str, Any]:
    if package.get("schema_version") != CANDIDATE_SCHEMA:
        raise ValueError("Unsupported candidate package schema")
    if package.get("synthetic_data_only") is not True:
        raise ValueError("Candidate package must remain synthetic-only")
    if not reviewer.strip():
        raise ValueError("Reviewer name is required")
    if not approved_ids:
        raise ValueError("At least one candidate id must be explicitly approved")
    if len(approved_ids) != len(set(approved_ids)):
        raise ValueError("Approved candidate ids must be unique")

    candidates = package.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("Candidate package candidates must be a list")
    by_id = {
        str(candidate.get("candidate_id")): candidate
        for candidate in candidates
        if isinstance(candidate, dict)
    }
    unknown = sorted(set(approved_ids) - set(by_id))
    if unknown:
        raise ValueError(f"Unknown candidate ids: {', '.join(unknown)}")

    return {
        "schema_version": APPROVAL_SCHEMA,
        "synthetic_data_only": True,
        "reviewer": reviewer.strip(),
        "approved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_schema_version": CANDIDATE_SCHEMA,
        "approved_candidate_ids": approved_ids,
        "approved_candidates": [by_id[candidate_id] for candidate_id in approved_ids],
        "promotion_note": (
            "This artifact records review approval. The permanent golden set was not modified; "
            "promotion still requires a reviewed code change."
        ),
    }


def render_feedback_report(package: dict[str, Any]) -> str:
    summary = package["summary"]
    reason_lines = [
        f"- `{reason}`: {count}" for reason, count in summary["override_reasons"].items()
    ] or ["- No override reasons recorded."]
    candidate_sections = []
    for candidate in package["candidates"]:
        changed = ", ".join(candidate["changed_fields"])
        candidate_sections.append(
            "\n".join(
                [
                    f"### {candidate['candidate_id']}",
                    "",
                    f"- Source case: `{candidate['source_case_id']}`",
                    f"- Source review: `{candidate['source_review_id']}`",
                    f"- Override reason: `{candidate['override_reason']}`",
                    f"- Changed fields: {changed}",
                    "- Promotion status: **awaiting human review**",
                ]
            )
        )
    if not candidate_sections:
        candidate_sections.append("No corrected decisions produced candidate cases.")

    return "\n".join(
        [
            "# Support Triage Feedback Candidate Report",
            "",
            "> Synthetic data only. Candidate cases are not part of the permanent golden set.",
            "",
            "## Summary",
            "",
            f"- Reviews: {summary['review_count']}",
            f"- Accepted: {summary['accepted_count']}",
            f"- Corrected: {summary['corrected_count']}",
            f"- Candidate cases: {summary['candidate_count']}",
            f"- Duplicate corrections omitted: {summary['duplicate_corrections_omitted']}",
            "",
            "## Override Reasons",
            "",
            *reason_lines,
            "",
            "## Candidate Review Queue",
            "",
            *candidate_sections,
            "",
            "## Promotion Boundary",
            "",
            "An approval artifact records a review decision, but it does not edit the permanent ",
            "evaluation dataset. Promotion requires a separate reviewed code change.",
            "",
        ]
    )


def _validate_review(review: dict[str, Any], index: int) -> None:
    context = f"reviews[{index}]"
    _require_exact_fields(review, REVIEW_FIELDS, context)
    if review.get("schema_version") != REVIEW_SCHEMA:
        raise ValueError(f"{context}.schema_version must be {REVIEW_SCHEMA}")
    _require_non_empty_string(review.get("review_id"), f"{context}.review_id")
    sample_id = review.get("sample_id")
    if sample_id not in SUPPORTED_SAMPLE_IDS:
        raise ValueError(f"{context}.sample_id is unsupported: {sample_id!r}")
    if review.get("execution_mode") not in EXECUTION_MODES:
        raise ValueError(f"{context}.execution_mode is unsupported")
    _require_non_empty_string(review.get("source_request_id"), f"{context}.source_request_id")
    _require_non_empty_string(review.get("prompt_version"), f"{context}.prompt_version")
    outcome = review.get("outcome")
    if outcome not in OUTCOMES:
        raise ValueError(f"{context}.outcome is unsupported")
    _parse_timestamp(review.get("reviewed_at"), f"{context}.reviewed_at")
    model = _validate_decision(review.get("model_decision"), f"{context}.model_decision")
    final = _validate_decision(review.get("final_decision"), f"{context}.final_decision")

    reason = review.get("override_reason")
    if outcome == "accepted":
        if reason is not None:
            raise ValueError(f"{context}.override_reason must be null for accepted reviews")
        if model != final:
            raise ValueError(f"{context} accepted review cannot change the model decision")
    else:
        if reason not in OVERRIDE_REASONS:
            raise ValueError(f"{context}.override_reason is unsupported")
        if model == final:
            raise ValueError(f"{context} overridden review must change at least one decision field")


def _validate_decision(value: object, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be an object")
    _require_exact_fields(value, DECISION_FIELDS, context)
    if value.get("product_area") not in PRODUCT_AREAS:
        raise ValueError(f"{context}.product_area is unsupported")
    if value.get("urgency") not in URGENCY_LEVELS:
        raise ValueError(f"{context}.urgency is unsupported")
    response = value.get("recommended_response")
    _require_non_empty_string(response, f"{context}.recommended_response")
    if len(str(response)) > 1200:
        raise ValueError(f"{context}.recommended_response exceeds 1200 characters")
    return value


def _build_candidate(
    review: dict[str, Any], base_case: dict[str, Any], fingerprint: str
) -> dict[str, Any]:
    model = review["model_decision"]
    final = review["final_decision"]
    changed_fields = [field for field in sorted(DECISION_FIELDS) if model[field] != final[field]]
    candidate_id = f"F-{review['sample_id']}-{fingerprint[:8]}"
    regression_case = dict(base_case)
    regression_case.update(
        {
            "id": candidate_id,
            "title": f"Human-corrected {base_case['title']}",
            "expected_product_area": final["product_area"],
            "expected_urgency": final["urgency"],
            "human_expected_response": final["recommended_response"],
            "source_review_id": review["review_id"],
        }
    )
    return {
        "candidate_id": candidate_id,
        "source_case_id": review["sample_id"],
        "source_review_id": review["review_id"],
        "execution_mode": review["execution_mode"],
        "prompt_version": review["prompt_version"],
        "reviewed_at": review["reviewed_at"],
        "override_reason": review["override_reason"],
        "changed_fields": changed_fields,
        "model_decision": model,
        "human_decision": final,
        "regression_case": regression_case,
    }


def _correction_fingerprint(review: dict[str, Any]) -> str:
    stable = {
        "sample_id": review["sample_id"],
        "override_reason": review["override_reason"],
        "final_decision": review["final_decision"],
    }
    rendered = json.dumps(stable, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def _require_exact_fields(value: dict[str, Any], expected: set[str], context: str) -> None:
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        raise ValueError(f"{context} missing fields: {', '.join(missing)}")
    if extra:
        raise ValueError(f"{context} unexpected fields: {', '.join(extra)}")


def _require_non_empty_string(value: object, context: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context} must be a non-empty string")


def _parse_timestamp(value: object, context: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{context} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{context} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{context} must include a timezone")
    return parsed
