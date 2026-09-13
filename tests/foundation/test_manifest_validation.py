"""Exercise malformed repository contracts without editing the working tree."""

from __future__ import annotations

import copy
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from scripts import validate_foundation as foundation


ROOT = Path(__file__).resolve().parents[2]


class ManifestValidationTests(unittest.TestCase):
    def validate_with(self, relative, mutation):
        target = ROOT / relative
        original = yaml.safe_load(target.read_text(encoding="utf-8"))
        value = mutation(copy.deepcopy(original))
        read_text = Path.read_text

        def replaced(path, *args, **kwargs):
            if path == target:
                return yaml.safe_dump(value)
            return read_text(path, *args, **kwargs)

        errors = []
        with patch.object(Path, "read_text", replaced):
            foundation.validate_manifests(errors)
        return errors

    def test_valid_repository_manifests_pass(self):
        errors = []
        foundation.validate_manifests(errors)
        self.assertEqual(errors, [])

    def test_skillsets_reject_empty_malformed_duplicate_and_unknown_skills(self):
        for value in ([], None, 1, "cadcam-intake-and-scope", [{}], ["nonexistent"], ["cadcam-intake-and-scope"] * 2):
            with self.subTest(value=value):
                errors = self.validate_with("skillsets/cadcam-design-handoff.yaml", lambda data: dict(data, skills=value))
                self.assertTrue(errors)

    def test_route_rows_fail_closed_on_bad_shape_and_duplicates(self):
        for value in ([None], [{}], [1], [], {"not": "a list"}):
            with self.subTest(value=value):
                self.assertTrue(self.validate_with("router/routes.yaml", lambda data: dict(data, routes=value)))
        self.assertTrue(self.validate_with("router/routes.yaml", lambda data: dict(data, routes=data["routes"] + [data["routes"][0]])))

    def test_route_reference_and_family_types_fail_closed(self):
        for field, value in (("process_family", []), ("skillset", {}), ("skillset", "../README"), ("artifact_classes", []), ("default_consequence", "made_up")):
            with self.subTest(field=field, value=value):
                def mutate(data):
                    data["routes"][0][field] = value
                    return data
                self.assertTrue(self.validate_with("router/routes.yaml", mutate))

    def test_fixture_index_rejects_empty_bad_and_duplicate_rows(self):
        for value in ([], [None], [{"id": [], "path": 1}], "not-a-list"):
            with self.subTest(value=value):
                self.assertTrue(self.validate_with("fixtures/manifest.yaml", lambda data: dict(data, fixtures=value)))
        self.assertTrue(self.validate_with("fixtures/manifest.yaml", lambda data: dict(data, fixtures=data["fixtures"] * 2)))

    def test_fixture_descriptors_reject_wrong_root_and_missing_license(self):
        for value in ([], "not-a-mapping", None, {}):
            with self.subTest(value=value):
                self.assertTrue(self.validate_with("fixtures/cnc/mill-bracket/fixture.yaml", lambda _: value))

    def test_fixture_descriptors_reject_malformed_references(self):
        for field, value in (("contexts", []), ("contexts", {"job": {}}), ("program", 1), ("source_job", "../../../README.md"), ("source_job", "missing.yaml")):
            with self.subTest(field=field, value=value):
                self.assertTrue(self.validate_with("fixtures/cnc/mill-bracket/fixture.yaml", lambda data: dict(data, **{field: value})))
        for value in (1, [None], [{}], {"svg": None}):
            with self.subTest(artifacts=value):
                self.assertTrue(self.validate_with("fixtures/laser/cut-bracket/fixture.yaml", lambda data: dict(data, artifacts=value)))

    def test_fixture_index_cannot_read_outside_fixtures(self):
        def mutate(data):
            data["fixtures"][0]["path"] = "../docs/sources/source-registry.yaml"
            return data
        self.assertTrue(self.validate_with("fixtures/manifest.yaml", mutate))

    def test_declared_skills_must_exist_on_disk(self):
        missing = ROOT / "skills/cadcam-intake-and-scope/SKILL.md"
        is_file = Path.is_file
        with patch.object(Path, "is_file", lambda path: False if path == missing else is_file(path)):
            errors = []
            foundation.validate_manifests(errors)
        self.assertTrue(any("referenced file is missing" in error for error in errors))

    def test_references_reject_external_paths_before_file_lookup(self):
        for value in ("../README.md", "/etc/passwd", "C:/outside.yaml", "C:\\outside.yaml", "//server/share/file", None, 1, {}):
            with self.subTest(value=value), patch.object(Path, "is_file", side_effect=AssertionError("must not probe outside files")):
                errors = []
                result = foundation._file_reference(ROOT / "fixtures", value, ROOT / "fixtures", errors, "test reference")
                self.assertIsNone(result)
                self.assertTrue(errors)

    def test_resolved_links_cannot_escape_fixture_boundary(self):
        alias = ROOT / "fixtures/alias.yaml"
        resolve = Path.resolve
        with patch.object(Path, "resolve", lambda path, *args, **kwargs: ROOT / "README.md" if path == alias else resolve(path, *args, **kwargs)):
            errors = []
            self.assertIsNone(foundation._file_reference(ROOT / "fixtures", "alias.yaml", ROOT / "fixtures", errors, "linked fixture"))
        self.assertTrue(any("escapes" in error for error in errors))

    def test_shared_fixture_paths_remain_valid(self):
        errors = []
        result = foundation._file_reference(ROOT / "fixtures/cnc/mill-bracket", "../../cad/bracket/fixture.yaml", ROOT / "fixtures", errors, "source_job")
        self.assertEqual(result, ROOT / "fixtures/cad/bracket/fixture.yaml")
        self.assertEqual(errors, [])

    def test_duplicate_yaml_keys_are_rejected(self):
        errors = []
        with patch.object(Path, "read_text", return_value="skills: []\nskills: [cadcam-intake-and-scope]\n"):
            self.assertIsNone(foundation.load_yaml(ROOT / "skillsets/cadcam-design-handoff.yaml", errors))
        self.assertTrue(errors)


class StructuredFileValidationTests(unittest.TestCase):
    def validate_text(self, path, text, validator):
        read_text = Path.read_text
        def replaced(candidate, *args, **kwargs):
            return text if candidate == path else read_text(candidate, *args, **kwargs)
        errors = []
        with patch.object(Path, "read_text", replaced):
            validator(errors)
        return errors

    def test_json_syntax_duplicate_keys_and_nonfinite_constants_fail(self):
        path = ROOT / "contexts/examples/job.example.json"
        for text in ('{"job_id":', '{"job_id":"a","job_id":"b"}', '{"value":NaN}', '{"value":Infinity}'):
            with self.subTest(text=text):
                errors = self.validate_text(path, text, foundation.validate_structured_files)
                self.assertTrue(any("invalid or ambiguous JSON" in error for error in errors))

    def test_mutation_yaml_syntax_is_checked(self):
        path = ROOT / "fixtures/additive/fdm-bracket/mutations/non-manifold-geometry.yaml"
        self.assertTrue(self.validate_text(path, "broken: [", foundation.validate_structured_files))

    def test_nonmapping_schema_documents_fail_without_crashing(self):
        for relative in ("contexts/schemas/job.schema.json", "state/state.schema.json"):
            for text in ("[]", "null", "1"):
                with self.subTest(relative=relative, text=text):
                    self.assertTrue(self.validate_text(ROOT / relative, text, foundation.validate_schemas))

    def test_missing_safety_document_is_reported_without_crashing(self):
        read_text = Path.read_text
        def missing(path, *args, **kwargs):
            if path == ROOT / "SECURITY.md":
                raise FileNotFoundError
            return read_text(path, *args, **kwargs)
        errors = []
        with patch.object(Path, "read_text", missing):
            foundation.validate_safety_invariants(errors)
        self.assertTrue(any("missing or unreadable" in error for error in errors))

    def test_frontmatter_must_be_unambiguous_mapping_with_text_fields(self):
        path = ROOT / "skills/cadcam-intake-and-scope/SKILL.md"
        for metadata in ("[]", "name: cadcam-intake-and-scope\ndescription: []", "name: wrong\nname: cadcam-intake-and-scope\ndescription: text"):
            with self.subTest(metadata=metadata):
                self.assertTrue(self.validate_text(path, f"---\n{metadata}\n---\n", foundation.validate_skill_metadata))

    def test_inline_markdown_missing_and_external_file_paths_fail(self):
        for target in ("missing.md", "../outside.md", "C:/private.md"):
            with self.subTest(target=target):
                self.assertTrue(self.validate_text(ROOT / "README.md", f"[link]({target})", foundation.validate_markdown_references))

    def test_walk_excludes_dependency_environments(self):
        errors = []
        paths = list(foundation.repository_files({".json", ".md"}, errors))
        self.assertTrue(paths)
        self.assertTrue(all(not {".git", "venv", ".venv", "node_modules"}.intersection(path.relative_to(ROOT).parts) for path in paths))
        self.assertEqual(errors, [])
