from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT / "03-projects" / "prompt-regression-runner"
DEFAULT_INPUT = PROJECT_ROOT / "feedback" / "recorded" / "support-triage-reviews.json"
DEFAULT_OUTPUT = ROOT / "docs" / "feedback-candidate-data.json"

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from prompt_regression.dataset import load_cases  # noqa: E402
from prompt_regression.feedback import (  # noqa: E402
    load_feedback_export,
    prepare_feedback_candidates,
)


def build_payload() -> dict[str, object]:
    cases = load_cases(PROJECT_ROOT / "data" / "cases.jsonl")
    export = load_feedback_export(DEFAULT_INPUT)
    package = prepare_feedback_candidates(export, cases)
    return {
        "metadata": {
            "project": "Support Triage Feedback Pipeline",
            "source": "committed synthetic Review Console export",
            "permanent_golden_set_modified": False,
        },
        "candidate_package": package,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export synthetic feedback candidate evidence.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = json.dumps(build_payload(), indent=2) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            print(f"Feedback candidate export is stale: {args.output}")
            print("Run: python scripts/export_feedback_candidates.py")
            return 1
        print(f"Feedback candidate export is current: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Wrote feedback candidate evidence to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
