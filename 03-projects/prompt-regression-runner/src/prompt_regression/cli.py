from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .dataset import DEFAULT_CASES, DEFAULT_RECORDED_DIR, load_cases, load_recording
from .feedback import (
    build_approval_artifact,
    load_feedback_export,
    prepare_feedback_candidates,
    render_feedback_report,
)
from .live_openai import record_live_outputs
from .scoring import compare_candidates, evaluate_candidate


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        cases = load_cases(args.cases)
        if args.command == "evaluate":
            report = evaluate_candidate(cases, load_recording(args.recording))
            print_report(report, as_json=args.as_json)
            return 0
        if args.command == "compare":
            recordings = [load_recording(path) for path in args.recordings]
            comparison = compare_candidates(cases, recordings)
            if args.as_json:
                print(json.dumps(comparison, indent=2))
            else:
                for report in comparison["candidates"]:
                    print(
                        f"{report['candidate']}: {report['score']:.1%} checks, "
                        f"{report['cases_passed']}/{report['case_count']} cases passed"
                    )
                print(f"Winner: {comparison['winner']}")
                print(comparison["teaching_note"])
            return 0
        if args.command == "case":
            comparison = compare_candidates(
                cases, [load_recording(path) for path in args.recordings]
            )
            found = False
            for report in comparison["candidates"]:
                result = next(
                    (item for item in report["results"] if item["case_id"] == args.case_id), None
                )
                if result:
                    found = True
                    print(f"{report['candidate']} · {result['title']} · {result['score']:.1%}")
                    for check, passed in result["checks"].items():
                        print(f"  {'PASS' if passed else 'FAIL'} {check}")
                    for diagnostic in result["diagnostics"]:
                        print(f"  - {diagnostic}")
            return 0 if found else 2
        if args.command == "record-live":
            payload = record_live_outputs(
                cases,
                candidate=args.candidate,
                prompt_file=args.prompt,
                model=args.model,
                output_path=args.output,
            )
            print(f"Recorded {len(payload['outputs'])} outputs to {args.output}")
            return 0
        if args.command == "prepare-feedback":
            package = prepare_feedback_candidates(load_feedback_export(args.export), cases)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            if args.report:
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(render_feedback_report(package), encoding="utf-8")
            summary = package["summary"]
            print(
                f"Validated {summary['review_count']} reviews: "
                f"{summary['accepted_count']} accepted, {summary['corrected_count']} corrected"
            )
            print(f"Wrote {summary['candidate_count']} awaiting-review candidates to {args.output}")
            if args.report:
                print(f"Wrote reviewer report to {args.report}")
            return 0
        if args.command == "approve-feedback":
            package = load_feedback_export(args.package)
            approval = build_approval_artifact(
                package, reviewer=args.reviewer, approved_ids=args.approve
            )
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(approval, indent=2) + "\n", encoding="utf-8")
            print(
                f"Recorded explicit approval for {len(args.approve)} candidate(s) in {args.output}"
            )
            print("The permanent golden set was not modified.")
            return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 2
    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prompt-regression",
        description="Compare prompt candidates against fixed structured-output cases.",
    )
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    subparsers = parser.add_subparsers(dest="command")

    evaluate = subparsers.add_parser("evaluate", help="Score one recorded candidate.")
    evaluate.add_argument("recording", type=Path)
    evaluate.add_argument("--json", action="store_true", dest="as_json")

    compare = subparsers.add_parser("compare", help="Compare two or more recorded candidates.")
    compare.add_argument(
        "recordings",
        nargs="+",
        type=Path,
        default=[
            DEFAULT_RECORDED_DIR / "baseline-v1.json",
            DEFAULT_RECORDED_DIR / "structured-v2.json",
        ],
    )
    compare.add_argument("--json", action="store_true", dest="as_json")

    case = subparsers.add_parser("case", help="Explain one case across candidates.")
    case.add_argument("case_id")
    case.add_argument("recordings", nargs="+", type=Path)

    live = subparsers.add_parser(
        "record-live", help="Generate a recording through the OpenAI Responses API."
    )
    live.add_argument("--candidate", required=True)
    live.add_argument("--prompt", required=True, type=Path)
    live.add_argument(
        "--model", required=True, help="Explicit model id for reproducible recording metadata."
    )
    live.add_argument("--output", required=True, type=Path)

    prepare = subparsers.add_parser(
        "prepare-feedback",
        help="Validate a synthetic Review Console export and create candidate eval cases.",
    )
    prepare.add_argument("export", type=Path)
    prepare.add_argument("--output", required=True, type=Path)
    prepare.add_argument("--report", type=Path)

    approve = subparsers.add_parser(
        "approve-feedback",
        help="Record explicit human approval without editing the permanent golden set.",
    )
    approve.add_argument("package", type=Path)
    approve.add_argument("--reviewer", required=True)
    approve.add_argument("--approve", required=True, action="append")
    approve.add_argument("--output", required=True, type=Path)
    return parser


def print_report(report: dict[str, object], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, indent=2))
        return
    print(
        f"{report['candidate']}: {report['score']:.1%} checks passed; "
        f"{report['cases_passed']}/{report['case_count']} complete cases passed"
    )
    for result in report["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status} {result['case_id']} {result['title']} ({result['score']:.1%})")


if __name__ == "__main__":
    sys.exit(main())
