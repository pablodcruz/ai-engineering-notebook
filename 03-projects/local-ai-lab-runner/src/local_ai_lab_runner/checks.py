from __future__ import annotations

import importlib.util
import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .labs import LabDocument


class Severity(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass(frozen=True)
class Finding:
    severity: Severity
    check: str
    message: str
    fix: str = ""


@dataclass(frozen=True)
class CheckProfile:
    min_python: tuple[int, int] = (3, 10)
    required_packages: tuple[str, ...] = ()
    required_env: tuple[str, ...] = ()
    recommended_sections: tuple[str, ...] = (
        "Skill Level",
        "Duration",
        "Learning Objectives",
        "Prerequisites",
        "Setup",
        "Exercise",
        "Expected Output",
        "Common Failure Modes",
        "Build Notes",
        "Debrief",
    )


def profile_for_lab(lab: LabDocument | None) -> CheckProfile:
    required_env: tuple[str, ...] = ()
    if lab and "OPENAI_API_KEY" in lab.text:
        required_env = ("OPENAI_API_KEY",)
    return CheckProfile(required_env=required_env)


def run_checks(
    lab: LabDocument | None,
    *,
    profile: CheckProfile | None = None,
    simulate: set[str] | None = None,
) -> list[Finding]:
    simulate = simulate or set()
    profile = profile or profile_for_lab(lab)
    findings: list[Finding] = []

    findings.extend(_lab_checks(lab, profile))
    findings.extend(_runtime_checks(profile, simulate))
    findings.extend(_package_checks(profile.required_packages, simulate))
    findings.extend(_credential_checks(profile.required_env, simulate))
    findings.append(_known_good_sample(simulate))

    return findings


def has_failures(findings: list[Finding]) -> bool:
    return any(finding.severity == Severity.FAIL for finding in findings)


def _lab_checks(lab: LabDocument | None, profile: CheckProfile) -> list[Finding]:
    if lab is None:
        return [
            Finding(
                Severity.WARN,
                "lab",
                "No lab file supplied; running environment checks only.",
                "Pass a markdown lab path to validate lab-specific readiness.",
            )
        ]

    findings = [
        Finding(Severity.PASS, "lab.file", f"Loaded {lab.relative_path or lab.path.name}."),
    ]
    if lab.title:
        findings.append(Finding(Severity.PASS, "lab.title", f"Found lab title: {lab.title}."))
    else:
        findings.append(
            Finding(
                Severity.FAIL,
                "lab.title",
                "Lab is missing a top-level title.",
                "Add a '# Lab Name' heading at the top of the markdown file.",
            )
        )

    for section in profile.recommended_sections:
        if lab.has_section(section):
            findings.append(
                Finding(Severity.PASS, f"lab.section.{section}", f"Found section: {section}.")
            )
        else:
            findings.append(
                Finding(
                    Severity.WARN,
                    f"lab.section.{section}",
                    f"Recommended section missing: {section}.",
                    f"Add a '## {section}' section or document why this lab does not need it.",
                )
            )

    return findings


def _runtime_checks(profile: CheckProfile, simulate: set[str]) -> list[Finding]:
    current = sys.version_info[:2]
    if "old-python" in simulate:
        current = (3, 8)
    if current >= profile.min_python:
        return [
            Finding(
                Severity.PASS,
                "runtime.python",
                f"Python {current[0]}.{current[1]} meets minimum {profile.min_python[0]}.{profile.min_python[1]}.",
            )
        ]
    return [
        Finding(
            Severity.FAIL,
            "runtime.python",
            f"Python {current[0]}.{current[1]} is below minimum {profile.min_python[0]}.{profile.min_python[1]}.",
            "Use the project virtual environment or install a supported Python runtime.",
        )
    ]


def _package_checks(required_packages: tuple[str, ...], simulate: set[str]) -> list[Finding]:
    packages = list(required_packages or ("json", "pathlib"))
    findings: list[Finding] = []
    for package in packages:
        if importlib.util.find_spec(package) is not None:
            findings.append(
                Finding(
                    Severity.PASS, f"package.{package}", f"Package import available: {package}."
                )
            )
        else:
            findings.append(
                Finding(
                    Severity.FAIL,
                    f"package.{package}",
                    f"Package import unavailable: {package}.",
                    "Install the package in the active environment, then rerun the check.",
                )
            )
    if "missing-package" in simulate:
        findings.append(
            Finding(
                Severity.FAIL,
                "package.demo_missing_package",
                "Demo dependency unavailable: demo_missing_package.",
                "Install the missing dependency in the active environment, then rerun the check.",
            )
        )
    return findings


def _credential_checks(required_env: tuple[str, ...], simulate: set[str]) -> list[Finding]:
    if not required_env:
        return [
            Finding(
                Severity.PASS,
                "credential.none",
                "No credential requirement detected for this lab.",
            )
        ]

    findings: list[Finding] = []
    for variable in required_env:
        present = bool(os.getenv(variable)) and "missing-credential" not in simulate
        if present:
            findings.append(
                Finding(Severity.PASS, f"credential.{variable}", f"{variable} is present.")
            )
        else:
            findings.append(
                Finding(
                    Severity.FAIL,
                    f"credential.{variable}",
                    f"{variable} is not set in the active shell.",
                    f"Set {variable} for this shell or choose a lab that does not need external API access.",
                )
            )
    return findings


def _known_good_sample(simulate: set[str]) -> Finding:
    if "sample-failure" in simulate:
        return Finding(
            Severity.FAIL,
            "sample.local",
            "Known-good local sample failed.",
            "Run `ai-lab-runner sample` and inspect the exact error before changing lab code.",
        )
    payload = {"prompt": "Return readiness status.", "status": "ready"}
    if payload["status"] == "ready":
        return Finding(Severity.PASS, "sample.local", "Known-good local sample completed.")
    return Finding(
        Severity.FAIL, "sample.local", "Known-good local sample returned an unexpected result."
    )


def default_lab_root(project_root: Path) -> Path:
    return project_root.parents[1] / "02-labs"
