from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from scripts.laser_preflight import apply_mutation, load_contexts, preflight
from scripts.validate_laser_fixture_geometry import validate


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "fixtures/laser/cut-bracket"


class LaserPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contexts = load_contexts(FIXTURE_ROOT / "contexts")
        cls.drawing = (FIXTURE_ROOT / "source/bracket.dxf").read_bytes()

    def test_positive_job_requires_only_human_approval(self):
        result = preflight(**self.contexts, drawing_bytes=self.drawing, source_revision="A")
        self.assertEqual(result["blockers"], ["HUMAN_APPROVAL_REQUIRED"])
        self.assertFalse(result["execution_allowed"])

    def test_declared_mutations_trigger_expected_blocks(self):
        expected = yaml.safe_load((FIXTURE_ROOT / "expected/outcomes.yaml").read_text(encoding="utf-8"))
        for case in expected["negative"]:
            mutation = yaml.safe_load((FIXTURE_ROOT / "mutations" / f"{case['mutation']}.yaml").read_text(encoding="utf-8"))
            result = preflight(**apply_mutation(self.contexts, mutation), drawing_bytes=self.drawing, source_revision="A")
            with self.subTest(mutation=case["mutation"]):
                self.assertTrue(set(case["expected_blockers"]).issubset(result["blockers"]))

    def test_beam_and_emission_risks_are_separate_findings(self):
        findings = " ".join(preflight(**self.contexts, drawing_bytes=self.drawing, source_revision="A")["findings"])
        self.assertIn("beam activation", findings)
        self.assertIn("process-emission", findings)

    def test_paired_dxf_and_svg_fixture_geometry_is_valid(self):
        self.assertEqual(validate(FIXTURE_ROOT), [])


if __name__ == "__main__":
    unittest.main()
