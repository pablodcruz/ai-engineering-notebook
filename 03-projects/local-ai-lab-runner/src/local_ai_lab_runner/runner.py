from __future__ import annotations

from dataclasses import dataclass

from .checks import Finding, Severity
from .labs import LabDocument


@dataclass(frozen=True)
class Checkpoint:
    name: str
    status: Severity
    detail: str


def build_checkpoints(lab: LabDocument, findings: list[Finding]) -> list[Checkpoint]:
    failures = {finding.check for finding in findings if finding.severity == Severity.FAIL}
    warnings = {finding.check for finding in findings if finding.severity == Severity.WARN}

    return [
        Checkpoint(
            "Read the lab goal",
            Severity.PASS if lab.title else Severity.FAIL,
            lab.title or "Missing title.",
        ),
        Checkpoint(
            "Confirm local environment",
            Severity.FAIL if any(check.startswith("runtime.") or check.startswith("package.") for check in failures) else Severity.PASS,
            "Runtime and package checks are ready.",
        ),
        Checkpoint(
            "Confirm credentials",
            Severity.FAIL if any(check.startswith("credential.") for check in failures) else Severity.PASS,
            "Credential checks are ready.",
        ),
        Checkpoint(
            "Review lab instructions",
            Severity.WARN if any(check.startswith("lab.section.") for check in warnings) else Severity.PASS,
            "Recommended lab sections are present." if not warnings else "Some recommended sections are missing.",
        ),
        Checkpoint(
            "Run known-good baseline",
            Severity.FAIL if "sample.local" in failures else Severity.PASS,
            "Local sample gives a baseline before changing prompts, parsing, or API calls.",
        ),
    ]


def summarize(findings: list[Finding]) -> dict[str, int]:
    return {
        "pass": sum(1 for finding in findings if finding.severity == Severity.PASS),
        "warn": sum(1 for finding in findings if finding.severity == Severity.WARN),
        "fail": sum(1 for finding in findings if finding.severity == Severity.FAIL),
    }

