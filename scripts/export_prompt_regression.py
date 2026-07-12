from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT / "03-projects" / "prompt-regression-runner"
DEFAULT_OUTPUT = ROOT / "docs" / "prompt-regression-data.json"

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from prompt_regression.dataset import load_cases, load_recording  # noqa: E402
from prompt_regression.scoring import compare_candidates  # noqa: E402


def build_payload() -> dict[str, object]:
    cases = load_cases(PROJECT_ROOT / "data" / "cases.jsonl")
    recordings = [
        load_recording(PROJECT_ROOT / "recorded" / "baseline-v1.json"),
        load_recording(PROJECT_ROOT / "recorded" / "structured-v2.json"),
    ]
    comparison = compare_candidates(cases, recordings)
    reports = {report["candidate"]: report for report in comparison["candidates"]}
    baseline_score = reports["baseline-v1"]["score"]
    structured_score = reports["structured-v2"]["score"]
    return {
        "metadata": {
            "project": "Prompt Regression Runner",
            "task": "structured support-ticket triage",
            "case_count": len(cases),
            "check_count_per_case": 8,
            "source": "committed recorded outputs",
        },
        "quality_gate": {
            "passed": (
                comparison["winner"] == "structured-v2"
                and structured_score >= 0.95
                and structured_score - baseline_score >= 0.25
            ),
            "winner": comparison["winner"],
            "minimum_structured_score": 0.95,
            "minimum_improvement": 0.25,
            "actual_improvement": round(structured_score - baseline_score, 4),
        },
        "comparison": comparison,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Prompt Regression Runner evidence.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build_payload()
    if not payload["quality_gate"]["passed"]:
        print("Prompt regression quality gate failed.")
        return 1
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            print(f"Prompt regression export is stale: {args.output}")
            print("Run: python scripts/export_prompt_regression.py")
            return 1
        print(f"Prompt regression export is current: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Wrote prompt comparison evidence to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
