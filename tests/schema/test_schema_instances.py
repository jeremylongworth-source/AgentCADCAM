from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry
from referencing.exceptions import Unresolvable

from scripts.validate_schema_instances import load_catalog, validate_repository, validator_for
from state.state import invalidate_approval


ROOT = Path(__file__).resolve().parents[2]


class SchemaInstanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()

    def test_repository_examples_and_profile_fixtures_conform(self):
        errors, schemas, instances = validate_repository()
        self.assertEqual(errors, [])
        self.assertEqual(schemas, 10)
        self.assertGreaterEqual(instances, 13)

    def test_cross_schema_artifact_validation_rejects_bad_hash(self):
        job = json.loads((ROOT / "contexts/examples/job.example.json").read_text(encoding="utf-8"))
        job["artifacts"] = [{
            "artifact_id": "synthetic-source", "path": "synthetic.step", "kind": "STEP",
            "sha256": "0" * 64, "revision": "A", "authority": "authoritative",
        }]
        validator_for("job.schema.json", self.catalog).validate(job)
        job["artifacts"][0]["sha256"] = "bad-hash"
        errors = list(validator_for("job.schema.json", self.catalog).iter_errors(job))
        self.assertTrue(any(list(error.absolute_path) == ["artifacts", 0, "sha256"] for error in errors))

    def test_profile_source_reference_is_enforced(self):
        machine = json.loads((ROOT / "fixtures/cnc/mill-bracket/contexts/machine.json").read_text(encoding="utf-8"))
        del machine["source"]["publisher"]
        self.assertFalse(validator_for("machine.schema.json", self.catalog).is_valid(machine))

    def test_missing_unknown_and_invalid_state_fields_are_rejected(self):
        original = json.loads((ROOT / "state/state.example.json").read_text(encoding="utf-8"))
        for mutation in ({"job_id": ""}, {"approval_status": "ready"}, {"unexpected": 1}):
            with self.subTest(mutation=mutation):
                state = dict(original, **mutation)
                self.assertFalse(validator_for("state.schema.json", self.catalog).is_valid(state))
        del original["revision"]
        self.assertFalse(validator_for("state.schema.json", self.catalog).is_valid(original))

    def test_runtime_invalidated_approval_conforms_and_preserves_identity(self):
        previous = {"revision": "A"}
        current = {"revision": "B"}
        approval = {
            "approval_id": "synthetic-review", "status": "approved",
            "scope": ["CAD review"], "context_fingerprint": "old-fingerprint",
            "reviewer": "test-reviewer", "reviewed_at": "2026-09-12T12:00:00Z",
        }
        original = copy.deepcopy(approval)
        result = invalidate_approval(previous, current, approval)
        validator = validator_for("approval.schema.json", self.catalog)
        validator.validate(approval)
        validator.validate(result)
        self.assertEqual(result["status"], "invalidated")
        self.assertEqual(result["changed_fields"], ["revision"])
        self.assertEqual(result["context_fingerprint"], "old-fingerprint")
        self.assertEqual(approval, original)

    def test_approval_timestamp_format_is_enforced(self):
        approval = {
            "approval_id": "test", "status": "pending", "scope": ["review"],
            "context_fingerprint": "test", "reviewer": "test", "reviewed_at": "not-a-date",
        }
        self.assertFalse(validator_for("approval.schema.json", self.catalog).is_valid(approval))

    def test_unknown_reference_fails_without_retrieval(self):
        validator = Draft202012Validator({"$ref": "https://example.invalid/schema"}, registry=Registry())
        with self.assertRaises(Unresolvable):
            validator.validate({})

    def test_all_declared_schema_references_resolve_locally(self):
        schemas, registry = self.catalog
        def references(value):
            if isinstance(value, dict):
                if "$ref" in value:
                    yield value["$ref"]
                for child in value.values():
                    yield from references(child)
            elif isinstance(value, list):
                for child in value:
                    yield from references(child)
        for name, schema in schemas.items():
            for reference in references(schema):
                with self.subTest(schema=name, reference=reference):
                    registry.resolver(schema["$id"]).lookup(reference)


if __name__ == "__main__":
    unittest.main()
