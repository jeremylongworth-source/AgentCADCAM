from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


class SkillsetIntegrityTests(unittest.TestCase):
    def test_cad_handoff_skillset_references_existing_skill_contracts(self):
        manifest = yaml.safe_load((ROOT / "skillsets/cadcam-design-handoff.yaml").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "cadcam-design-handoff")
        self.assertEqual(len(manifest["skills"]), 5)
        for skill in manifest["skills"]:
            with self.subTest(skill=skill):
                self.assertTrue((ROOT / "skills" / skill / "SKILL.md").is_file())

    def test_every_router_skillset_manifest_exists(self):
        routes = yaml.safe_load((ROOT / "router/routes.yaml").read_text(encoding="utf-8"))
        for route in routes["routes"]:
            with self.subTest(route=route["id"]):
                skillset = route.get("skillset")
                if skillset:
                    self.assertTrue((ROOT / "skillsets" / f"{skillset}.yaml").is_file())


if __name__ == "__main__":
    unittest.main()
