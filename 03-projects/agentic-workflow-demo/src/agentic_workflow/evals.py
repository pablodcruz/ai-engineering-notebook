from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .workflow import run_workflow


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES = PROJECT_ROOT / "evals" / "cases.jsonl"


def load_cases(path: Path = DEFAULT_CASES) -> list[dict[str, Any]]:
    cases = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            cases.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on {path}:{line_number}: {exc}") from exc
    return cases


def evaluate_cases(path: Path = DEFAULT_CASES) -> tuple[list[dict[str, Any]], int]:
    results = []
    failures = 0
    for case in load_cases(path):
        result = run_workflow(str(case["request"]), approved=bool(case.get("approve", False)))
        tool_names = [step.name for step in result.trace if step.event == "tool_call"]
        expected_tools = list(case.get("expected_tools", []))
        forbidden_tools = list(case.get("forbidden_tools", []))
        expected_sources = list(case.get("expected_sources", []))
        checks = {
            "status": result.status == case["expected_status"],
            "tools": all(tool in tool_names for tool in expected_tools),
            "forbidden_tools": not any(tool in tool_names for tool in forbidden_tools),
            "sources": all(any(expected in source for source in result.sources) for expected in expected_sources),
        }
        passed = all(checks.values())
        failures += 0 if passed else 1
        results.append(
            {
                "name": case["name"],
                "request": case["request"],
                "passed": passed,
                "checks": checks,
                "status": result.status,
                "tools": tool_names,
                "sources": result.sources,
            }
        )
    return results, failures
