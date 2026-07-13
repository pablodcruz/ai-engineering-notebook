from __future__ import annotations

import sys
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from prompt_regression.contract import OUTPUT_SCHEMA, validate_output
from prompt_regression.dataset import (
    DEFAULT_CASES,
    DEFAULT_RECORDED_DIR,
    load_cases,
    load_recording,
)
from prompt_regression.feedback import (
    APPROVAL_SCHEMA,
    CANDIDATE_SCHEMA,
    build_approval_artifact,
    load_feedback_export,
    prepare_feedback_candidates,
    render_feedback_report,
)
from prompt_regression.live_openai import build_request
from prompt_regression.scoring import compare_candidates, evaluate_candidate, score_case


class PromptRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = load_cases(DEFAULT_CASES)
        cls.baseline = load_recording(DEFAULT_RECORDED_DIR / "baseline-v1.json")
        cls.structured = load_recording(DEFAULT_RECORDED_DIR / "structured-v2.json")
        cls.feedback_export = load_feedback_export(
            DEFAULT_CASES.parent.parent / "feedback" / "recorded" / "support-triage-reviews.json"
        )

    def test_schema_rejects_missing_and_extra_fields(self) -> None:
        errors = validate_output({"customer_problem": "Example", "unexpected": True})

        self.assertTrue(any("missing fields" in error for error in errors))
        self.assertTrue(any("unexpected fields" in error for error in errors))

    def test_invalid_json_produces_actionable_diagnostics(self) -> None:
        result = score_case(self.cases[0], "not json")

        self.assertFalse(result["checks"]["json_valid"])
        self.assertTrue(any("invalid JSON" in message for message in result["diagnostics"]))

    def test_dataset_has_fifteen_balanced_cases(self) -> None:
        categories = {case["category"] for case in self.cases}

        self.assertEqual(len(self.cases), 15)
        self.assertGreaterEqual(len(categories), 5)

    def test_structured_candidate_passes_every_case(self) -> None:
        report = evaluate_candidate(self.cases, self.structured)

        self.assertEqual(report["cases_passed"], len(self.cases))
        self.assertEqual(report["score"], 1.0)

    def test_comparison_exposes_baseline_gap(self) -> None:
        comparison = compare_candidates(self.cases, [self.baseline, self.structured])
        reports = {report["candidate"]: report for report in comparison["candidates"]}

        self.assertEqual(comparison["winner"], "structured-v2")
        self.assertGreater(
            reports["structured-v2"]["score"] - reports["baseline-v1"]["score"], 0.25
        )

    def test_regression_changes_case_result(self) -> None:
        recording = deepcopy(self.structured)
        recording["outputs"][0]["output"]["urgency"] = "low"
        report = evaluate_candidate(self.cases, recording)
        first = next(result for result in report["results"] if result["case_id"] == "T001")

        self.assertFalse(first["passed"])
        self.assertFalse(first["checks"]["urgency_correct"])

    def test_live_request_uses_explicit_model_and_strict_schema(self) -> None:
        request = build_request("Prompt", "Ticket", "explicit-model-id")

        self.assertEqual(request["model"], "explicit-model-id")
        self.assertEqual(request["text"]["format"]["schema"], OUTPUT_SCHEMA)
        self.assertTrue(request["text"]["format"]["strict"])
        self.assertEqual(request["max_output_tokens"], 300)
        self.assertFalse(request["store"])

    def test_feedback_pipeline_summarizes_accepted_and_corrected_reviews(self) -> None:
        package = prepare_feedback_candidates(self.feedback_export, self.cases)

        self.assertEqual(package["schema_version"], CANDIDATE_SCHEMA)
        self.assertEqual(package["promotion_status"], "awaiting_human_review")
        self.assertEqual(package["summary"]["review_count"], 4)
        self.assertEqual(package["summary"]["accepted_count"], 1)
        self.assertEqual(package["summary"]["corrected_count"], 3)

    def test_feedback_pipeline_converts_correction_to_regression_candidate(self) -> None:
        package = prepare_feedback_candidates(self.feedback_export, self.cases)
        candidate = next(item for item in package["candidates"] if item["source_case_id"] == "T003")

        self.assertEqual(candidate["human_decision"]["urgency"], "high")
        self.assertEqual(candidate["model_decision"]["urgency"], "medium")
        self.assertIn("urgency", candidate["changed_fields"])
        self.assertEqual(candidate["regression_case"]["expected_urgency"], "high")
        self.assertEqual(candidate["source_review_id"], "review_example_T003")

    def test_feedback_pipeline_omits_duplicate_corrections(self) -> None:
        package = prepare_feedback_candidates(self.feedback_export, self.cases)

        self.assertEqual(package["summary"]["candidate_count"], 2)
        self.assertEqual(package["summary"]["duplicate_corrections_omitted"], 1)

    def test_feedback_pipeline_rejects_duplicate_review_ids(self) -> None:
        payload = deepcopy(self.feedback_export)
        payload["reviews"][1]["review_id"] = payload["reviews"][0]["review_id"]

        with self.assertRaisesRegex(ValueError, "Duplicate review_id"):
            prepare_feedback_candidates(payload, self.cases)

    def test_feedback_pipeline_rejects_non_synthetic_export(self) -> None:
        payload = deepcopy(self.feedback_export)
        payload["synthetic_data_only"] = False

        with self.assertRaisesRegex(ValueError, "synthetic_data_only"):
            prepare_feedback_candidates(payload, self.cases)

    def test_feedback_pipeline_rejects_unsupported_sample(self) -> None:
        payload = deepcopy(self.feedback_export)
        payload["reviews"][0]["sample_id"] = "T999"

        with self.assertRaisesRegex(ValueError, "sample_id is unsupported"):
            prepare_feedback_candidates(payload, self.cases)

    def test_feedback_approval_requires_explicit_candidate_ids(self) -> None:
        package = prepare_feedback_candidates(self.feedback_export, self.cases)

        with self.assertRaisesRegex(ValueError, "explicitly approved"):
            build_approval_artifact(package, reviewer="Pablo", approved_ids=[])

        candidate_id = package["candidates"][0]["candidate_id"]
        approval = build_approval_artifact(package, reviewer="Pablo", approved_ids=[candidate_id])
        self.assertEqual(approval["schema_version"], APPROVAL_SCHEMA)
        self.assertEqual(approval["approved_candidate_ids"], [candidate_id])
        self.assertIn("not modified", approval["promotion_note"])

    def test_feedback_report_marks_candidates_as_awaiting_review(self) -> None:
        package = prepare_feedback_candidates(self.feedback_export, self.cases)
        report = render_feedback_report(package)

        self.assertIn("Synthetic data only", report)
        self.assertIn("Candidate cases: 2", report)
        self.assertIn("awaiting human review", report)


if __name__ == "__main__":
    unittest.main()
