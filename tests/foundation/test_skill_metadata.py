"""Repository metadata requirements layered on AgentSkills string metadata."""

from __future__ import annotations

import copy
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from scripts.validate_foundation import validate_skill_metadata


ROOT = Path(__file__).resolve().parents[2]


class SkillMetadataTests(unittest.TestCase):
    def setUp(self):
        self.path = ROOT / "skills/cadcam-intake-and-scope/SKILL.md"
        self.content = self.path.read_text(encoding="utf-8")
        _, frontmatter, self.body = self.content.split("---", 2)
        self.frontmatter = yaml.safe_load(frontmatter)
        # Independent complete record for mutation tests, not fabricated job approval.
        self.frontmatter["metadata"].update({
            "version": "0.1.0", "owner": "AgentCADCAM maintainers",
            "supported-consequence-levels": "informational design_advisory manufacturing_planning execution_adjacent",
        })

    def errors_for(self, frontmatter):
        content = "---\n" + yaml.safe_dump(frontmatter) + "---" + self.body
        read_text = Path.read_text
        def changed(path, *args, **kwargs):
            return content if path == self.path else read_text(path, *args, **kwargs)
        errors = []
        with patch.object(Path, "read_text", changed):
            validate_skill_metadata(errors)
        return errors

    def test_repository_metadata_conforms(self):
        errors = []
        validate_skill_metadata(errors)
        self.assertEqual(errors, [])

    def test_router_defaults_are_supported_by_selected_skills(self):
        routes = yaml.safe_load((ROOT / "router/routes.yaml").read_text(encoding="utf-8"))["routes"]
        for route in routes:
            if route["skillset"] is None:
                continue
            bundle = yaml.safe_load((ROOT / f"skillsets/{route['skillset']}.yaml").read_text(encoding="utf-8"))
            for name in bundle["skills"]:
                with self.subTest(route=route["id"], skill=name):
                    content = (ROOT / f"skills/{name}/SKILL.md").read_text(encoding="utf-8")
                    metadata = yaml.safe_load(content.split("---", 2)[1])["metadata"]
                    self.assertIn(route["default_consequence"], metadata["supported-consequence-levels"].split())

    def test_required_metadata_fields_cannot_be_omitted(self):
        for field in ("version", "owner", "supported-consequence-levels"):
            with self.subTest(field=field):
                data = copy.deepcopy(self.frontmatter)
                del data["metadata"][field]
                self.assertTrue(self.errors_for(data))

    def test_metadata_must_remain_string_to_string_mapping(self):
        for value in (None, [], "text", {"owner": ["team"]}, {1: "value"}):
            with self.subTest(value=value):
                data = dict(self.frontmatter, metadata=value)
                self.assertTrue(self.errors_for(data))

    def test_versions_have_numeric_triplet_and_no_placeholders(self):
        for version in ("", "TBD", "1", "1.2", "01.2.3", "1.2.3.4", "v1.2.3", "1.2.3-01", 1):
            with self.subTest(version=version):
                data = copy.deepcopy(self.frontmatter)
                data["metadata"]["version"] = version
                self.assertTrue(self.errors_for(data))

    def test_supported_levels_are_explicit_unique_review_levels(self):
        for levels in ("", "unknown", "live_execution", "execution_adjacent live_execution", "execution_adjacent execution_adjacent", "design_advisory, execution_adjacent", ["design_advisory"]):
            with self.subTest(levels=levels):
                data = copy.deepcopy(self.frontmatter)
                data["metadata"]["supported-consequence-levels"] = levels
                self.assertTrue(self.errors_for(data))

    def test_known_owner_is_required(self):
        for owner in ("", " ", "TBD", "TODO", "unknown"):
            with self.subTest(owner=owner):
                data = copy.deepcopy(self.frontmatter)
                data["metadata"]["owner"] = owner
                self.assertTrue(self.errors_for(data))

    def test_names_descriptions_and_top_level_fields_are_validated(self):
        for mutation in ({"name": "bad--name"}, {"name": "a" * 65}, {"description": "x" * 1025}, {"description": " "}, {"owner": "wrong-layer"}):
            with self.subTest(mutation=mutation):
                self.assertTrue(self.errors_for(dict(self.frontmatter, **mutation)))

    def test_valid_metadata_extensions_and_prerelease_versions_are_allowed(self):
        data = copy.deepcopy(self.frontmatter)
        data["metadata"].update({"version": "1.2.3-rc.1+build.4", "custom-field": "retained"})
        self.assertEqual(self.errors_for(data), [])
