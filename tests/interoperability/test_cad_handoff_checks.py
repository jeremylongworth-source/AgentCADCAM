from __future__ import annotations

import copy
import unittest
from pathlib import Path

import yaml

from scripts.cad_handoff_checks import apply_mutation, review_bundle


ROOT = Path(__file__).resolve().parents[2]


class CadHandoffChecksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = yaml.safe_load((ROOT / "fixtures/cad/bracket/fixture.yaml").read_text(encoding="utf-8"))
        cls.fixture["metadata"] = yaml.safe_load((ROOT / "fixtures/cad/bracket/metadata/revision.json").read_text(encoding="utf-8"))

    def test_positive_bundle_remains_review_required_without_false_ready(self):
        result = review_bundle(self.fixture, ROOT / "fixtures/cad/bracket")
        self.assertEqual(result["status"], "review_required")
        self.assertEqual(result["blockers"], [])
        self.assertFalse(result["geometry_equivalence_verified"])

    def test_revision_mismatch_blocks(self):
        bundle = copy.deepcopy(self.fixture)
        bundle["artifacts"][1]["revision"] = "B"
        self.assertIn("MISSING_CONTEXT", review_bundle(bundle)["blockers"])

    def test_missing_units_blocks_without_inference(self):
        bundle = copy.deepcopy(self.fixture)
        bundle["artifacts"][0]["units"] = None
        self.assertIn("MISSING_CONTEXT", review_bundle(bundle)["blockers"])

    def test_mesh_cannot_become_authoritative_design_master(self):
        bundle = copy.deepcopy(self.fixture)
        bundle["authoritative_artifact"] = "source/bracket.stl"
        self.assertIn("SOURCE_VERIFICATION_REQUIRED", review_bundle(bundle)["blockers"])

    def test_missing_pmi_status_blocks(self):
        bundle = copy.deepcopy(self.fixture)
        del bundle["metadata"]["pmi_status"]
        self.assertIn("MISSING_CONTEXT", review_bundle(bundle)["blockers"])

    def test_conflicting_dimensions_block(self):
        bundle = copy.deepcopy(self.fixture)
        bundle["dimension_checks"] = [{"name": "plate_width", "status": "conflict"}]
        self.assertIn("MISSING_CONTEXT", review_bundle(bundle)["blockers"])

    def test_declared_mutation_fixtures_produce_expected_blocks(self):
        expected = yaml.safe_load((ROOT / "fixtures/cad/bracket/expected/outcomes.yaml").read_text(encoding="utf-8"))
        for case in expected["negative"]:
            mutation_path = ROOT / "fixtures/cad/bracket/mutations" / f"{case['mutation']}.yaml"
            mutation = yaml.safe_load(mutation_path.read_text(encoding="utf-8"))
            result = review_bundle(apply_mutation(self.fixture, mutation))
            with self.subTest(mutation=case["mutation"]):
                self.assertTrue(set(case["expected_blockers"]).issubset(result["blockers"]))


if __name__ == "__main__":
    unittest.main()
