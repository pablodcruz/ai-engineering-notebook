from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .checks import default_lab_root, has_failures, profile_for_lab, run_checks
from .labs import discover_labs, load_lab
from .runner import build_checkpoints, summarize

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LAB_ROOT = default_lab_root(PROJECT_ROOT)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "list":
            return list_labs(args)
        if args.command == "doctor":
            return doctor(args)
        if args.command == "check":
            return check(args)
        if args.command == "run":
            return run(args)
        if args.command == "sample":
            return sample(args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 2

    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-lab-runner",
        description="Validate local AI lab readiness before running experiments.",
    )
    parser.add_argument("--lab-root", type=Path, default=DEFAULT_LAB_ROOT)
    parser.add_argument("--json", action="store_true", dest="as_json")

    subparsers = parser.add_subparsers(dest="command")
    list_parser = subparsers.add_parser("list", help="List discoverable markdown labs.")
    _add_json_option(list_parser)
    doctor_parser = subparsers.add_parser("doctor", help="Run environment-only readiness checks.")
    _add_json_option(doctor_parser)

    check_parser = subparsers.add_parser("check", help="Check a lab file and local readiness.")
    _add_json_option(check_parser)
    check_parser.add_argument("lab", type=Path)
    check_parser.add_argument(
        "--simulate",
        action="append",
        default=[],
        choices=["missing-credential", "missing-package", "old-python", "sample-failure"],
        help="Inject a demo failure mode.",
    )

    run_parser = subparsers.add_parser("run", help="Print lab checkpoints after readiness checks.")
    _add_json_option(run_parser)
    run_parser.add_argument("lab", type=Path)
    run_parser.add_argument(
        "--simulate",
        action="append",
        default=[],
        choices=["missing-credential", "missing-package", "old-python", "sample-failure"],
        help="Inject a demo failure mode.",
    )

    sample_parser = subparsers.add_parser("sample", help="Run a known-good local sample.")
    _add_json_option(sample_parser)
    sample_parser.add_argument(
        "--simulate",
        action="append",
        default=[],
        choices=["sample-failure"],
        help="Inject a demo sample failure.",
    )

    return parser


def _add_json_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", dest="as_json", default=argparse.SUPPRESS)


def list_labs(args: argparse.Namespace) -> int:
    labs = discover_labs(args.lab_root)
    if args.as_json:
        print(json.dumps([str(path.relative_to(args.lab_root)) for path in labs], indent=2))
        return 0
    for path in labs:
        print(path.relative_to(args.lab_root))
    return 0


def doctor(args: argparse.Namespace) -> int:
    findings = run_checks(None)
    _print_findings(findings, as_json=args.as_json)
    return 1 if has_failures(findings) else 0


def check(args: argparse.Namespace) -> int:
    lab = load_lab(args.lab, root=args.lab_root)
    findings = run_checks(lab, profile=profile_for_lab(lab), simulate=set(args.simulate))
    _print_findings(findings, as_json=args.as_json)
    return 1 if has_failures(findings) else 0


def run(args: argparse.Namespace) -> int:
    lab = load_lab(args.lab, root=args.lab_root)
    findings = run_checks(lab, profile=profile_for_lab(lab), simulate=set(args.simulate))
    checkpoints = build_checkpoints(lab, findings)

    if args.as_json:
        print(
            json.dumps(
                {
                    "summary": summarize(findings),
                    "findings": [_finding_payload(finding) for finding in findings],
                    "checkpoints": [_checkpoint_payload(checkpoint) for checkpoint in checkpoints],
                },
                indent=2,
            )
        )
        return 1 if has_failures(findings) else 0

    _print_findings(findings, as_json=False)
    print()
    print("Checkpoints:")
    for index, checkpoint in enumerate(checkpoints, start=1):
        print(f"{index}. {checkpoint.status.value} {checkpoint.name}: {checkpoint.detail}")
    return 1 if has_failures(findings) else 0


def sample(args: argparse.Namespace) -> int:
    findings = run_checks(None, simulate=set(args.simulate))
    sample_findings = [finding for finding in findings if finding.check == "sample.local"]
    _print_findings(sample_findings, as_json=args.as_json)
    return 1 if has_failures(sample_findings) else 0


def _print_findings(findings, *, as_json: bool) -> None:
    if as_json:
        print(
            json.dumps(
                {
                    "summary": summarize(findings),
                    "findings": [_finding_payload(finding) for finding in findings],
                },
                indent=2,
            )
        )
        return

    summary = summarize(findings)
    print(f"Summary: {summary['pass']} pass, {summary['warn']} warn, {summary['fail']} fail")
    for finding in findings:
        print(f"{finding.severity.value} {finding.check}: {finding.message}")
        if finding.fix:
            print(f"  Fix: {finding.fix}")


def _finding_payload(finding) -> dict[str, str]:
    return {
        "severity": finding.severity.value,
        "check": finding.check,
        "message": finding.message,
        "fix": finding.fix,
    }


def _checkpoint_payload(checkpoint) -> dict[str, str]:
    return {
        "name": checkpoint.name,
        "status": checkpoint.status.value,
        "detail": checkpoint.detail,
    }


if __name__ == "__main__":
    sys.exit(main())
