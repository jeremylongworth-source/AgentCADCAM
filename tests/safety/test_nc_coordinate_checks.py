"""Direct static evidence utility must also fail closed on coordinate inputs."""

import copy
import unittest

from scripts.nc_static_checks import load_contexts, review_program
from tests.safety.test_nc_static_checks import FIXTURE_ROOT
from tests.schema.test_profile_lifecycle import synthetic_review


class NcCoordinateChecksTests(unittest.TestCase):
    def setUp(self):
        self.contexts = load_contexts(FIXTURE_ROOT / "contexts")
        self.program = (FIXTURE_ROOT / "programs/positive.nc").read_text(encoding="utf-8")
        self.model = synthetic_review(copy.deepcopy(self.contexts["setup"]["coordinate_model"]))

    def review(self):
        return review_program(self.program, self.contexts, selected_wcs="G54", coordinate_model=self.model)

    def test_finite_numbers_required_for_both_vectors(self):
        original = copy.deepcopy(self.model)
        for field in ("translation", "initial_machine_position"):
            for value in (None, True, "0", float("nan"), float("inf"), -float("inf")):
                with self.subTest(field=field, value=value):
                    self.model = copy.deepcopy(original)
                    self.model[field]["x"] = value
                    result = self.review()
                    self.assertIn("MISSING_CONTEXT", result["blockers"])
                    self.assertNotEqual(result["coordinate_review"]["status"], "checked_declared_bounds")

    def test_missing_context_returns_findings_not_an_exception(self):
        original = copy.deepcopy(self.contexts)
        for field in ("machine", "setup", "tool", "controller", "job"):
            with self.subTest(field=field):
                self.contexts = copy.deepcopy(original)
                self.contexts.pop(field)
                result = self.review()
                self.assertTrue(result["blockers"])
                self.assertNotEqual(result["coordinate_review"]["status"], "checked_declared_bounds")

    def test_offline_review_keeps_inputs_and_other_gates_unchanged(self):
        original = copy.deepcopy((self.contexts, self.model))
        result = self.review()
        self.assertEqual(result["blockers"], ["HUMAN_APPROVAL_REQUIRED", "SIMULATION_REQUIRED"])
        self.assertEqual(result["coordinate_review"]["status"], "checked_declared_bounds")
        self.assertEqual((self.contexts, self.model), original)
        self.assertTrue(result["review_required"])
        self.assertFalse(result["execution_allowed"])

    def test_standalone_legacy_report_does_not_claim_coordinate_review(self):
        result = review_program(self.program, self.contexts)
        self.assertIsNone(result["coordinate_review"])
        self.assertTrue(result["review_required"])
        self.assertFalse(result["execution_allowed"])


if __name__ == "__main__":
    unittest.main()
