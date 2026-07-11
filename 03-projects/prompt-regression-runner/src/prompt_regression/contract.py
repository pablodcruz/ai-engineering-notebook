from __future__ import annotations

from typing import Any


PRODUCT_AREAS = {"authentication", "billing", "integrations", "performance", "account", "unknown"}
URGENCY_LEVELS = {"low", "medium", "high"}
REQUIRED_FIELDS = {
    "customer_problem",
    "product_area",
    "urgency",
    "missing_information",
    "recommended_response",
}

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "customer_problem": {"type": "string"},
        "product_area": {"type": "string", "enum": sorted(PRODUCT_AREAS)},
        "urgency": {"type": "string", "enum": sorted(URGENCY_LEVELS)},
        "missing_information": {"type": "array", "items": {"type": "string"}},
        "recommended_response": {"type": "string"},
    },
    "required": sorted(REQUIRED_FIELDS),
}


def validate_output(payload: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["output is not a JSON object"]
    missing = sorted(REQUIRED_FIELDS - set(payload))
    extra = sorted(set(payload) - REQUIRED_FIELDS)
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    if extra:
        errors.append(f"unexpected fields: {', '.join(extra)}")
    if not isinstance(payload.get("customer_problem"), str) or not str(payload.get("customer_problem", "")).strip():
        errors.append("customer_problem must be a non-empty string")
    if payload.get("product_area") not in PRODUCT_AREAS:
        errors.append(f"product_area must be one of {sorted(PRODUCT_AREAS)}")
    if payload.get("urgency") not in URGENCY_LEVELS:
        errors.append(f"urgency must be one of {sorted(URGENCY_LEVELS)}")
    missing_information = payload.get("missing_information")
    if not isinstance(missing_information, list) or not all(isinstance(item, str) for item in missing_information):
        errors.append("missing_information must be a list of strings")
    if not isinstance(payload.get("recommended_response"), str) or not str(payload.get("recommended_response", "")).strip():
        errors.append("recommended_response must be a non-empty string")
    return errors
