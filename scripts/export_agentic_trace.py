from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT / "03-projects" / "agentic-workflow-demo"
DEFAULT_OUTPUT = ROOT / "docs" / "agentic-workflow-data.json"

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from agentic_workflow.tools import TOOL_SPECS  # noqa: E402
from agentic_workflow.workflow import run_workflow  # noqa: E402

SCENARIOS = (
    ("Blocked work", "Summarize blocked work", False),
    ("Approval checkpoint", "Change TASK-103 priority to high", False),
    ("Approved simulation", "Change TASK-103 priority to high", True),
    ("Prohibited action", "Delete TASK-101", False),
)


def build_payload() -> dict[str, object]:
    return {
        "metadata": {
            "project": "Agentic Workflow Demo",
            "planner": "deterministic intent planner",
            "backlog": "03-projects/agentic-workflow-demo/data/backlog.json",
            "baseline_requires_network": False,
        },
        "tools": [spec.to_dict() for spec in TOOL_SPECS],
        "scenarios": [
            {
                "label": label,
                "approved": approved,
                "result": _stable_result(request, approved),
            }
            for label, request, approved in SCENARIOS
        ],
    }


def _stable_result(request: str, approved: bool) -> dict[str, object]:
    payload = run_workflow(request, approved=approved).to_dict()
    for step in payload["trace"]:
        step["duration_ms"] = 0.0
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export agent workflow traces for the static showcase."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = json.dumps(build_payload(), indent=2) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            print(f"Agent trace export is stale: {args.output}")
            print("Run: python scripts/export_agentic_trace.py")
            return 1
        print(f"Agent trace export is current: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Wrote {len(SCENARIOS)} agent traces to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
