from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .evals import DEFAULT_CASES, evaluate_cases
from .tools import TOOL_SPECS
from .workflow import DEFAULT_BACKLOG, run_workflow


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        result = run_workflow(
            args.request,
            approved=args.approve,
            backlog_path=args.backlog,
            max_tool_calls=args.max_tool_calls,
        )
        if args.as_json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(f"Status: {result.status}")
            print(result.answer)
            if result.sources:
                print("Sources:")
                for source in result.sources:
                    print(f"- {source}")
            print("Trace:")
            for step in result.trace:
                print(
                    f"{step.step}. {step.event} {step.name} [{step.status}] {step.duration_ms:.3f}ms"
                )
        return {"completed": 0, "approval_required": 3, "refused": 2}.get(result.status, 1)

    if args.command == "tools":
        payload = [spec.to_dict() for spec in TOOL_SPECS]
        if args.as_json:
            print(json.dumps(payload, indent=2))
        else:
            for spec in TOOL_SPECS:
                mode = "read-only" if spec.read_only else "mutation; approval required"
                print(f"{spec.name}: {spec.description} ({mode})")
        return 0

    if args.command == "eval":
        results, failures = evaluate_cases(args.cases)
        for result in results:
            status = "PASS" if result["passed"] else "FAIL"
            print(
                f"{status} {result['name']}: {result['status']} tools={','.join(result['tools']) or 'none'}"
            )
        print()
        print(f"{len(results) - failures}/{len(results)} passed")
        return 0 if failures == 0 else 1

    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="backlog-agent", description="Run a constrained backlog workflow."
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run one request and print its trace.")
    run_parser.add_argument("request")
    run_parser.add_argument(
        "--approve", action="store_true", help="Approve the proposed simulated mutation."
    )
    run_parser.add_argument("--backlog", type=Path, default=DEFAULT_BACKLOG)
    run_parser.add_argument("--max-tool-calls", type=int, default=8)
    run_parser.add_argument("--json", action="store_true", dest="as_json")

    tools_parser = subparsers.add_parser("tools", help="List allowed tool contracts.")
    tools_parser.add_argument("--json", action="store_true", dest="as_json")

    eval_parser = subparsers.add_parser("eval", help="Run behavioral workflow evals.")
    eval_parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    return parser


if __name__ == "__main__":
    sys.exit(main())
