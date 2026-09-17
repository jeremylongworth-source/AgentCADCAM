"""Byte identity is evidence of unchanged files, never proof of derivation truth."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.cad_handoff_checks import review_fixture
from scripts.validate_cad_derivation import validate
from scripts.validate_schema_instances import load_catalog, validator_for


ROOT = Path(__file__).resolve().parents[2]


class CadDerivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.fixture = ROOT / "fixtures/cad/bracket"
        cls.binding = json.loads((cls.fixture / "metadata/derivation.json").read_text(encoding="utf-8"))

    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="cad-binding-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name) / "bracket"
        shutil.copytree(self.fixture, self.root)
        self.path = self.root / "metadata/derivation.json"

    def write_binding(self, value):
        self.path.write_text(json.dumps(value), encoding="utf-8")

    def assert_binding_blocks(self):
        result = review_fixture(self.root)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("SOURCE_VERIFICATION_REQUIRED", result["blockers"])
        self.assertFalse(result["execution_allowed"])
        self.assertFalse(result["geometry_equivalence_verified"])
        return result

    def test_required_binding_fields_and_hash_shapes(self):
        validator = validator_for("derivation.schema.json", self.catalog)
        validator.validate(self.binding)
        for field in self.binding:
            with self.subTest(field=field):
                mutation = copy.deepcopy(self.binding)
                mutation.pop(field)
                self.assertFalse(validator.is_valid(mutation))
        for value in ("", "a" * 63, "g" * 64, None):
            with self.subTest(hash=value):
                mutation = copy.deepcopy(self.binding)
                mutation["source"]["sha256"] = value
                self.assertFalse(validator.is_valid(mutation))

    def test_schema_rejects_authority_reversal_unknown_units_and_execution(self):
        validator = validator_for("derivation.schema.json", self.catalog)
        for field, value in (("authority", "derived"), ("units", None), ("units", " ")):
            mutation = copy.deepcopy(self.binding)
            mutation["source"][field] = value
            self.assertFalse(validator.is_valid(mutation))
        for field, value in (("review_required", False), ("execution_allowed", True), ("hash_policy", "sha256-normalized")):
            mutation = dict(self.binding, **{field: value})
            self.assertFalse(validator.is_valid(mutation))
        mutation = copy.deepcopy(self.binding)
        mutation["derivatives"][0]["artifact"]["authority"] = "authoritative"
        self.assertFalse(validator.is_valid(mutation))

    def test_missing_malformed_and_incomplete_binding_blocks(self):
        self.path.unlink()
        self.assert_binding_blocks()
        for text in ("not JSON", "[]", "{}", "null"):
            with self.subTest(text=text):
                self.path.write_text(text, encoding="utf-8")
                self.assert_binding_blocks()

    def test_binding_coverage_and_identity_cannot_be_replaced(self):
        mutations = []
        missing = copy.deepcopy(self.binding)
        missing["derivatives"].pop()
        mutations.append(missing)
        duplicate = copy.deepcopy(self.binding)
        duplicate["derivatives"][1] = copy.deepcopy(duplicate["derivatives"][0])
        mutations.append(duplicate)
        duplicate_id = copy.deepcopy(self.binding)
        duplicate_id["derivatives"][0]["artifact"]["artifact_id"] = duplicate_id["source"]["artifact_id"]
        mutations.append(duplicate_id)
        escape = copy.deepcopy(self.binding)
        escape["source"]["path"] = "../outside.scad"
        mutations.append(escape)
        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                self.write_binding(mutation)
                self.assert_binding_blocks()

    def test_every_bound_artifact_hash_revision_units_and_kind_are_checked(self):
        for index in range(4):
            for field, value in (("sha256", "0" * 64), ("revision", "B"), ("units", "inch"), ("kind", "other")):
                with self.subTest(index=index, field=field):
                    mutation = copy.deepcopy(self.binding)
                    item = mutation["source"] if index == 0 else mutation["derivatives"][index - 1]["artifact"]
                    item[field] = value
                    self.write_binding(mutation)
                    before = self.path.read_bytes()
                    self.assert_binding_blocks()
                    self.assertEqual(self.path.read_bytes(), before)

    def test_revision_metadata_must_agree_even_if_all_hashes_match(self):
        bundle = yaml.safe_load((self.root / "fixture.yaml").read_text(encoding="utf-8"))
        metadata = json.loads((self.root / "metadata/revision.json").read_text(encoding="utf-8"))
        self.assertEqual(validate(self.root, bundle, metadata), [])
        for field, value in (("revision", "B"), ("units", "inch"), ("authoritative_artifact", "source/bracket.stl")):
            with self.subTest(field=field):
                self.assertTrue(validate(self.root, bundle, dict(metadata, **{field: value})))

    def test_raw_byte_policy_does_not_silently_normalize_line_endings(self):
        target = self.root / "source/bracket.scad"
        data = target.read_bytes()
        self.assertNotIn(b"\r", data)
        target.write_bytes(data.replace(b"\n", b"\r\n"))
        self.assert_binding_blocks()


if __name__ == "__main__":
    unittest.main()
