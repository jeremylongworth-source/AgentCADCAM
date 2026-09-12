from __future__ import annotations

import unittest
from pathlib import Path

import yaml


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
        self.assertEqual(fixture["step_artifact"]["status"], "planned")

    def test_negative_mutations_have_blocking_outcomes(self):
        expected = yaml.safe_load((ROOT / "fixtures/cad/bracket/expected/outcomes.yaml").read_text(encoding="utf-8"))
        for case in expected["negative"]:
            with self.subTest(mutation=case["mutation"]):
                self.assertTrue(case["expected_blockers"])


if __name__ == "__main__":
    unittest.main()
