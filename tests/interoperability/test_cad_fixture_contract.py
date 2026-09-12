from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from scripts.validate_cad_fixture_step import validate
from scripts.validate_cad_fixture_mesh import validate as validate_mesh
from scripts.validate_cad_fixture_design import validate as validate_design


ROOT = Path(__file__).resolve().parents[2]


class CadFixtureContractTests(unittest.TestCase):
    def test_fixture_manifest_points_to_existing_bundle(self):
        manifest = yaml.safe_load((ROOT / "fixtures/manifest.yaml").read_text(encoding="utf-8"))
        entry = next(item for item in manifest["fixtures"] if item["id"] == "cad-bracket-basic")
        self.assertTrue((ROOT / "fixtures" / entry["path"]).is_file())

    def test_fixture_preserves_authoritative_source_and_derived_mesh_roles(self):
        fixture = yaml.safe_load((ROOT / "fixtures/cad/bracket/fixture.yaml").read_text(encoding="utf-8"))
        self.assertEqual(fixture["authoritative_artifact"], "source/bracket.scad")
        roles = {item["path"]: item["authority"] for item in fixture["artifacts"]}
        self.assertEqual(roles["source/bracket.scad"], "authoritative")
        self.assertEqual(roles["source/bracket.stl"], "derived")
        self.assertEqual(fixture["step_artifact"]["status"], "generated")
        step = ROOT / "fixtures/cad/bracket/source/bracket.step"
        self.assertTrue(step.is_file())
        step_text = step.read_text(encoding="utf-8")
        self.assertTrue(step_text.startswith("ISO-10303-21;"))
        self.assertTrue(step_text.rstrip().endswith("END-ISO-10303-21;"))
        self.assertEqual(validate(step), [])
        self.assertEqual(validate_mesh(ROOT / "fixtures/cad/bracket/source/bracket.stl"), [])
        self.assertEqual(validate_design(ROOT / "fixtures/cad/bracket"), [])

    def test_negative_mutations_have_blocking_outcomes(self):
        expected = yaml.safe_load((ROOT / "fixtures/cad/bracket/expected/outcomes.yaml").read_text(encoding="utf-8"))
        for case in expected["negative"]:
            with self.subTest(mutation=case["mutation"]):
                self.assertTrue(case["expected_blockers"])


if __name__ == "__main__":
    unittest.main()
