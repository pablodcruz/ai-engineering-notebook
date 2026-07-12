from __future__ import annotations

import json
from typing import Any

from .contract import validate_output

CHECK_NAMES = (
    "json_valid",
    "schema_valid",
    "product_area_correct",
    "urgency_correct",
    "problem_terms_present",
    "missing_information_covered",
    "grounded",
    "recommended_response_actionable",
)


def evaluate_candidate(cases: list[dict[str, Any]], recording: dict[str, Any]) -> dict[str, Any]:
    outputs = {str(item["case_id"]): item.get("output") for item in recording["outputs"]}
    results = []
    for case in cases:
        case_id = str(case["id"])
        results.append(score_case(case, outputs.get(case_id)))

    total_checks = len(results) * len(CHECK_NAMES)
    passed_checks = sum(
        sum(1 for passed in result["checks"].values() if passed) for result in results
    )
    return {
        "candidate": str(recording["candidate"]),
        "prompt_file": str(recording["prompt_file"]),
        "source": str(recording.get("source", "recorded")),
        "model": recording.get("model"),
        "case_count": len(results),
        "cases_passed": sum(1 for result in results if result["passed"]),
        "checks_passed": passed_checks,
        "total_checks": total_checks,
        "score": round(passed_checks / max(total_checks, 1), 4),
        "results": results,
    }


def score_case(case: dict[str, Any], raw_output: object) -> dict[str, Any]:
    diagnostics: list[str] = []
    parsed: object = raw_output
    json_valid = True
    if isinstance(raw_output, str):
        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            json_valid = False
            parsed = None
            diagnostics.append(f"invalid JSON: {exc.msg}")

    schema_errors = (
        validate_output(parsed) if json_valid else ["schema check skipped because JSON is invalid"]
    )
    schema_valid = not schema_errors
    diagnostics.extend(schema_errors)
    payload = parsed if isinstance(parsed, dict) else {}
    problem = str(payload.get("customer_problem", "")).lower()
    missing_information = " ".join(
        str(value) for value in payload.get("missing_information", [])
    ).lower()
    serialized = json.dumps(payload, sort_keys=True).lower()
    response = str(payload.get("recommended_response", ""))

    required_problem_terms = [
        str(value).lower() for value in case.get("required_problem_terms", [])
    ]
    expected_missing = [
        str(value).lower() for value in case.get("expected_missing_information", [])
    ]
    forbidden = [str(value).lower() for value in case.get("forbidden_terms", [])]

    checks = {
        "json_valid": json_valid,
        "schema_valid": schema_valid,
        "product_area_correct": payload.get("product_area") == case["expected_product_area"],
        "urgency_correct": payload.get("urgency") == case["expected_urgency"],
        "problem_terms_present": all(term in problem for term in required_problem_terms),
        "missing_information_covered": all(
            term in missing_information for term in expected_missing
        ),
        "grounded": json_valid and not any(term in serialized for term in forbidden),
        "recommended_response_actionable": len(response.split()) >= 5,
    }

    for name, passed in checks.items():
        if not passed and name not in {"json_valid", "schema_valid"}:
            diagnostics.append(f"failed {name}")
    return {
        "case_id": str(case["id"]),
        "title": str(case["title"]),
        "category": str(case["category"]),
        "passed": all(checks.values()),
        "score": round(sum(checks.values()) / len(checks), 4),
        "checks": checks,
        "diagnostics": diagnostics,
        "output": raw_output,
    }


def compare_candidates(
    cases: list[dict[str, Any]], recordings: list[dict[str, Any]]
) -> dict[str, Any]:
    reports = [evaluate_candidate(cases, recording) for recording in recordings]
    reports.sort(key=lambda report: (report["score"], report["cases_passed"]), reverse=True)
    return {
        "winner": reports[0]["candidate"] if reports else None,
        "candidates": reports,
        "teaching_note": (
            "A higher aggregate score is a starting point, not the whole decision. "
            "Inspect case-level failures before promoting a prompt."
        ),
    }
