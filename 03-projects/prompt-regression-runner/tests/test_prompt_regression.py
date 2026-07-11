from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from prompt_regression.contract import OUTPUT_SCHEMA, validate_output
from prompt_regression.dataset import DEFAULT_CASES, DEFAULT_RECORDED_DIR, load_cases, load_recording
from prompt_regression.live_openai import build_request
from prompt_regression.scoring import compare_candidates, evaluate_candidate, score_case


class PromptRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = load_cases(DEFAULT_CASES)
        cls.baseline = load_recording(DEFAULT_RECORDED_DIR / "baseline-v1.json")
        cls.structured = load_recording(DEFAULT_RECORDED_DIR / "structured-v2.json")

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
        self.assertGreater(reports["structured-v2"]["score"] - reports["baseline-v1"]["score"], 0.25)

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


if __name__ == "__main__":
    unittest.main()
