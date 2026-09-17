from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from scripts.additive_preflight import apply_mutation, load_contexts, preflight


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "fixtures/additive/fdm-bracket"


class AdditivePreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contexts = load_contexts(FIXTURE_ROOT / "contexts")
        cls.mesh = (ROOT / "fixtures/cad/bracket/source/bracket.stl").read_bytes()

    def test_positive_job_requires_only_human_approval(self):
        result = preflight(**self.contexts, mesh_bytes=self.mesh, source_revision="A")
        self.assertEqual(result["blockers"], ["HUMAN_APPROVAL_REQUIRED"])
        self.assertFalse(result["execution_allowed"])

    def test_declared_mutations_trigger_expected_blocks(self):
        expected = yaml.safe_load((FIXTURE_ROOT / "expected/outcomes.yaml").read_text(encoding="utf-8"))
        for case in expected["negative"]:
            mutation = yaml.safe_load((FIXTURE_ROOT / "mutations" / f"{case['mutation']}.yaml").read_text(encoding="utf-8"))
            result = preflight(**apply_mutation(self.contexts, mutation), mesh_bytes=self.mesh, source_revision="A")
            with self.subTest(mutation=case["mutation"]):
                self.assertTrue(set(case["expected_blockers"]).issubset(result["blockers"]))


if __name__ == "__main__":
    unittest.main()
