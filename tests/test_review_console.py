from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "docs" / "support-triage.html").read_text(encoding="utf-8")


class ReviewConsoleContractTests(unittest.TestCase):
    def test_review_workflow_controls_are_present(self) -> None:
        for control_id in (
            "review-form",
            "accept-review",
            "save-override",
            "review-reason",
            "review-metrics",
            "export-reviews",
            "reset-reviews",
        ):
            self.assertIn(f'id="{control_id}"', HTML)

    def test_demo_access_request_is_manual_email_only(self) -> None:
        self.assertIn('id="request-demo-access"', HTML)
        self.assertIn("mailto:pablo.de.la.cruz.pro@gmail.com", HTML)
        self.assertIn("no code is issued automatically", HTML)

    def test_saved_record_excludes_ticket_and_credentials(self) -> None:
        match = re.search(
            r"const record = \{(?P<body>.*?)\n\s*\};\n\s*reviews\.push",
            HTML,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        record_source = match.group("body")
        for forbidden in ("accessCode", "access-code", "ticketEl", "OPENAI_API_KEY"):
            self.assertNotIn(forbidden, record_source)
        self.assertIn('schema_version: "review-v1"', record_source)
        self.assertIn("model_decision", record_source)
        self.assertIn("final_decision", record_source)

    def test_override_requires_a_change_and_reason(self) -> None:
        self.assertIn("!reviewResponseEl.value.trim()", HTML)
        self.assertIn('outcome === "overridden" && !changed', HTML)
        self.assertIn('outcome === "overridden" && !reviewReasonEl.value', HTML)

    def test_review_actions_do_not_call_the_triage_api(self) -> None:
        match = re.search(
            r"function recordReview\(outcome\) \{(?P<body>.*?)\n\s*\}\n\n\s*function exportReviews",
            HTML,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        self.assertNotIn("fetch(", match.group("body"))


if __name__ == "__main__":
    unittest.main()
