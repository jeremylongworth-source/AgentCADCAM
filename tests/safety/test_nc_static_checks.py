from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from scripts.nc_static_checks import apply_mutation, load_contexts, review_program


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "fixtures/cnc/mill-bracket"


class NcStaticChecksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.program = (FIXTURE_ROOT / "programs/positive.nc").read_text(encoding="utf-8")
        cls.contexts = load_contexts(FIXTURE_ROOT / "contexts")

    def test_positive_program_is_blocked_only_by_simulation_and_approval(self):
        result = review_program(self.program, self.contexts)
        self.assertEqual(result["blockers"], ["HUMAN_APPROVAL_REQUIRED", "SIMULATION_REQUIRED"])
        self.assertFalse(result["execution_allowed"])

    def test_declared_mutations_trigger_expected_hard_blocks(self):
        expected = yaml.safe_load((FIXTURE_ROOT / "expected/outcomes.yaml").read_text(encoding="utf-8"))
        for case in expected["negative"]:
            mutation = yaml.safe_load((FIXTURE_ROOT / "mutations" / f"{case['mutation']}.yaml").read_text(encoding="utf-8"))
            result = review_program(apply_mutation(self.program, mutation), self.contexts)
            with self.subTest(mutation=case["mutation"]):
                self.assertTrue(set(case["expected_blockers"]).issubset(result["blockers"]))

    def test_static_review_never_authorizes_execution(self):
        result = review_program(self.program, self.contexts)
        self.assertTrue(result["review_required"])
        self.assertFalse(result["execution_allowed"])

    def test_missing_tool_context_blocks_where_tool_reference_is_present(self):
        contexts = {key: value.copy() for key, value in self.contexts.items()}
        contexts["tool"]["tool_number"] = None
        self.assertIn("MISSING_CONTEXT", review_program(self.program, contexts)["blockers"])

    def test_unverified_post_validation_blocks(self):
        contexts = {key: value.copy() for key, value in self.contexts.items()}
        contexts["post"]["validation_state"] = "unverified"
        self.assertIn("SOURCE_VERIFICATION_REQUIRED", review_program(self.program, contexts)["blockers"])


if __name__ == "__main__":
    unittest.main()
