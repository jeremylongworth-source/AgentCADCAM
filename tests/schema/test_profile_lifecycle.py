"""Profile lifecycle shape and explicit review-state declarations."""

import copy
import json
import unittest
from pathlib import Path

from scripts.validate_schema_instances import load_catalog, validator_for


ROOT = Path(__file__).resolve().parents[2]


def synthetic_review(profile):
    """Test-only declaration; never write a verified fixture back to disk."""
    profile["lifecycle"]["verification"] = {
        "status": "verified", "reviewed_revision": profile["lifecycle"]["revision"],
        "reviewer": "synthetic-test-reviewer", "reviewed_at": "2026-09-13T12:00:00Z",
        "evidence": ["fixture:synthetic-review"], "notes": "Test declaration only; no practitioner review.",
    }
    return profile


class ProfileLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()

    def profile(self, name):
        return json.loads((ROOT / f"fixtures/cnc/mill-bracket/contexts/{name}.json").read_text(encoding="utf-8"))

    def test_all_five_schemas_require_lifecycle(self):
        for name in ("machine", "controller", "material", "tool", "post"):
            value = self.profile(name)
            validator = validator_for(f"{name}.schema.json", self.catalog)
            self.assertTrue(validator.is_valid(value))
            value.pop("lifecycle", None)
            with self.subTest(profile=name):
                self.assertFalse(validator.is_valid(value))

    def test_fixture_profiles_are_not_marked_practitioner_verified(self):
        for path in (ROOT / "fixtures").glob("**/contexts/*.json"):
            if path.stem not in {"machine", "printer", "controller", "material", "tool", "post"}:
                continue
            profile = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(path=path):
                self.assertEqual(profile["lifecycle"]["verification"]["status"], "unverified")
                self.assertIsNone(profile["lifecycle"]["verification"]["reviewer"])

    def test_lifecycle_fields_and_review_fields_are_required(self):
        value = self.profile("machine")
        validator = validator_for("machine.schema.json", self.catalog)
        for field in ("revision", "applicability", "units", "verification"):
            mutation = copy.deepcopy(value)
            mutation["lifecycle"].pop(field, None)
            self.assertFalse(validator.is_valid(mutation))
        for field in ("status", "reviewed_revision", "reviewer", "reviewed_at", "evidence", "notes"):
            mutation = copy.deepcopy(value)
            mutation["lifecycle"]["verification"].pop(field, None)
            self.assertFalse(validator.is_valid(mutation))

    def test_unknown_revision_and_review_are_representable(self):
        value = self.profile("machine")
        value["lifecycle"]["revision"] = None
        value["lifecycle"]["verification"]["status"] = "unknown"
        validator_for("machine.schema.json", self.catalog).validate(value)

    def test_verified_requires_revision_reviewer_timestamp_and_evidence(self):
        value = synthetic_review(self.profile("machine"))
        validator = validator_for("machine.schema.json", self.catalog)
        validator.validate(value)
        for field, replacement in (("reviewer", None), ("reviewer", " "), ("reviewed_revision", None),
                                   ("reviewed_at", None), ("reviewed_at", "not-a-date"), ("evidence", [])):
            mutation = copy.deepcopy(value)
            mutation["lifecycle"]["verification"][field] = replacement
            self.assertFalse(validator.is_valid(mutation))
        value["lifecycle"]["revision"] = None
        self.assertFalse(validator.is_valid(value))

    def test_bad_status_empty_applicability_and_unknown_fields_fail(self):
        validator = validator_for("machine.schema.json", self.catalog)
        for mutation in ({"revision": " "}, {"applicability": ""}, {"applicability": None},
                         {"units": []}, {"units": {"": "mm"}}, {"units": {"length": " "}},
                         {"unexpected": True}):
            value = self.profile("machine")
            value["lifecycle"].update(mutation)
            self.assertFalse(validator.is_valid(value))
        value = self.profile("machine")
        value["lifecycle"]["verification"]["status"] = "approved"
        self.assertFalse(validator.is_valid(value))

    def test_nonverified_states_preserve_evidence_without_claiming_current_review(self):
        for status in ("unknown", "unverified", "conflicted", "rejected"):
            value = synthetic_review(self.profile("machine"))
            value["lifecycle"]["verification"]["status"] = status
            validator_for("machine.schema.json", self.catalog).validate(value)


if __name__ == "__main__":
    unittest.main()
