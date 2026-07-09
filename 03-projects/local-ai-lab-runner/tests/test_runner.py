from __future__ import annotations

from pathlib import Path
import os
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from local_ai_lab_runner.checks import Severity, has_failures, profile_for_lab, run_checks
from local_ai_lab_runner.labs import discover_labs, load_lab
from local_ai_lab_runner.runner import build_checkpoints, summarize


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "labs"


class LocalLabRunnerTests(unittest.TestCase):
    def test_discovers_markdown_labs(self) -> None:
        labs = discover_labs(FIXTURE_ROOT)

        self.assertEqual([path.name for path in labs], ["credential-lab.md", "good-lab.md"])

    def test_good_lab_has_no_failures(self) -> None:
        lab = load_lab(FIXTURE_ROOT / "good-lab.md", root=FIXTURE_ROOT)
        findings = run_checks(lab)
        counts = summarize(findings)

        self.assertFalse(has_failures(findings))
        self.assertGreater(counts["pass"], 0)

    def test_credential_lab_requires_key_when_credentials_are_mentioned(self) -> None:
        old_key = os.environ.pop("OPENAI_API_KEY", None)
        try:
            lab = load_lab(FIXTURE_ROOT / "credential-lab.md", root=FIXTURE_ROOT)
            findings = run_checks(lab, profile=profile_for_lab(lab))
        finally:
            if old_key is not None:
                os.environ["OPENAI_API_KEY"] = old_key

        self.assertTrue(any(finding.check == "credential.OPENAI_API_KEY" for finding in findings))
        self.assertTrue(has_failures(findings))

    def test_simulated_missing_package_fails(self) -> None:
        lab = load_lab(FIXTURE_ROOT / "good-lab.md", root=FIXTURE_ROOT)
        findings = run_checks(lab, simulate={"missing-package"})

        self.assertTrue(any(finding.check.startswith("package.") and finding.severity == Severity.FAIL for finding in findings))

    def test_builds_checkpoints_from_findings(self) -> None:
        lab = load_lab(FIXTURE_ROOT / "good-lab.md", root=FIXTURE_ROOT)
        findings = run_checks(lab)
        checkpoints = build_checkpoints(lab, findings)

        self.assertEqual(checkpoints[0].name, "Read the lab goal")
        self.assertTrue(all(checkpoint.status in {Severity.PASS, Severity.WARN, Severity.FAIL} for checkpoint in checkpoints))


if __name__ == "__main__":
    unittest.main()

