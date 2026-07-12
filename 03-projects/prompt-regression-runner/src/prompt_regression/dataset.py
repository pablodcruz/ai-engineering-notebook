from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES = PROJECT_ROOT / "data" / "cases.jsonl"
DEFAULT_RECORDED_DIR = PROJECT_ROOT / "recorded"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on {path}:{line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"Expected an object on {path}:{line_number}")
        rows.append(value)
    return rows


def load_cases(path: Path = DEFAULT_CASES) -> list[dict[str, Any]]:
    cases = load_jsonl(path)
    ids = [str(case["id"]) for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("Case ids must be unique")
    return cases


def load_recording(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("outputs"), list):
        raise ValueError(f"Invalid recording: {path}")
    return payload
