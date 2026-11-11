import copy
import json
import unittest
from pathlib import Path

from scripts.validate_feedback import validate_report

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = json.loads((ROOT / "evals/example_feedback.json").read_text(encoding="utf-8"))


class FeedbackValidationTests(unittest.TestCase):
    def setUp(self):
        self.r = copy.deepcopy(ORIGINAL)

    def assert_problem(self, expected):
        problems = validate_report(self.r)
        self.assertTrue(any(expected in x for x in problems), problems)

    def test_valid_example(self):
        self.assertEqual(validate_report(self.r), [])

    def test_invented_evidence_is_rejected(self):
        self.r["evidence"][0]["quote"] = "This quotation is not in the essay."
        self.assert_problem("not verbatim")

    def test_invented_priority_quote_is_rejected(self):
        self.r["priorities"][0]["quote"] = "Imaginary student sentence."
        self.assert_problem("not verbatim")

    def test_missing_task_prompt_withheld_score(self):
        self.r["prompt"] = ""
        self.r["scores"]["TR"] = None
        self.r["scores"]["overall"] = None
        self.r["evidence"] = [e for e in self.r["evidence"] if e["criterion"] != "TR"]
        self.assertEqual(validate_report(self.r), [])

    def test_missing_task_prompt_cannot_receive_overall(self):
        self.r["prompt"] = ""
        self.assert_problem("TR must be null")

    def test_missing_chart_cannot_receive_task_band(self):
        self.r["task_type"] = "academic_task1"
        self.r["scores"]["TA"] = self.r["scores"].pop("TR")
        for item in self.r["evidence"]:
            if item["criterion"] == "TR":
                item["criterion"] = "TA"
        self.assert_problem("TA must be null")

    def test_invalid_band(self):
        self.r["scores"]["CC"] = 7.3
        self.assert_problem("Invalid band")

    def test_boolean_band_is_invalid(self):
        self.r["scores"]["CC"] = True
        self.assert_problem("Invalid band")

    def test_missing_scored_criterion_evidence(self):
        self.r["evidence"] = [e for e in self.r["evidence"] if e["criterion"] != "LR"]
        self.assert_problem("Scored criterion LR")

    def test_no_overall_with_partial_four_criteria(self):
        self.r["scores"]["GRA"] = None
        self.assert_problem("overall requires")

    def test_too_many_priorities(self):
        self.r["priorities"] = self.r["priorities"] * 4
        self.assert_problem("at most three")

    def test_official_claim_is_rejected(self):
        self.r["score_label"] = "official"
        self.assert_problem("unofficial_training_estimate")

    def test_ai_model_is_not_independent_student(self):
        self.r["draft_kind"] = "model"
        self.assert_problem("Do not assign student-performance")

    def test_behavioral_suite_integrity(self):
        cases = json.loads((ROOT / "evals/behavioral_cases.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 8)
        self.assertEqual(len(set(c["id"] for c in cases)), len(cases))
        for case in cases:
            self.assertTrue(case["essay"].strip())
            self.assertTrue(case["expected_primary_issue"].strip())
            self.assertTrue(case["must_not_claim"].strip())


if __name__ == "__main__":
    unittest.main()
