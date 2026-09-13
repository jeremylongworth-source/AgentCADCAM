from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from state.state import changed_fields, context_fingerprint, invalidate_approval


class StateInvalidationTests(unittest.TestCase):
    def setUp(self):
        self.previous = {"revision": "A", "units": "mm", "machine_profile": {"machine_id": "m1"}, "approval_status": "approved"}

    def test_fingerprint_changes_when_revision_changes(self):
        current = dict(self.previous, revision="B")
        self.assertNotEqual(context_fingerprint(self.previous), context_fingerprint(current))
        self.assertEqual(changed_fields(self.previous, current), ["revision"])

    def test_approved_record_is_invalidated_by_consequential_change(self):
        current = dict(self.previous, units="inch")
        approval = {"status": "approved", "approval_id": "a1"}
        result = invalidate_approval(self.previous, current, approval)
        self.assertEqual(result["status"], "invalidated")
        self.assertEqual(result["changed_fields"], ["units"])

    def test_nonapproved_record_is_not_rewritten(self):
        current = dict(self.previous, units="inch")
        approval = {"status": "pending", "approval_id": "a1"}
        self.assertEqual(invalidate_approval(self.previous, current, approval), approval)

    def test_each_consequential_field_invalidates_approved_record(self):
        approval = {"status": "approved", "approval_id": "a1"}
        for field in (
            "source_artifact_hashes", "revision", "units", "process_family", "material",
            "machine_profile", "controller_profile", "setup", "work_coordinate_system",
            "tool_library", "postprocessor", "post_version", "generated_manufacturing_output",
        ):
            current = dict(self.previous)
            current[field] = {"changed": True} if field not in {"revision", "units", "process_family", "post_version"} else "changed"
            with self.subTest(field=field):
                self.assertEqual(invalidate_approval(self.previous, current, approval)["status"], "invalidated")

    def test_declared_and_runtime_invalidation_fields_agree(self):
        from state.state import INVALIDATING_FIELDS
        path = Path(__file__).resolve().parents[2] / "state/invalidation-rules.yaml"
        rules = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(set(INVALIDATING_FIELDS), {rule["field"] for rule in rules["approval_invalidation"]})

    def test_verification_and_authorization_changes_invalidate(self):
        for field in ("job_id", "workholding", "simulation_status", "verification_results", "cam_system", "jurisdiction", "ip_status", "export_review_status"):
            with self.subTest(field=field):
                current = dict(self.previous, **{field: "changed"})
                self.assertNotEqual(context_fingerprint(self.previous), context_fingerprint(current))
                self.assertEqual(invalidate_approval(self.previous, current, {"status": "approved"})["status"], "invalidated")

    def test_unsupported_values_are_not_stringified_into_fingerprints(self):
        for value in (object(), float("nan"), float("inf"), {1: "ambiguous key"}):
            with self.subTest(value=type(value)):
                with self.assertRaises((TypeError, ValueError)):
                    context_fingerprint(dict(self.previous, material=value))

    def test_boolean_and_number_changes_are_not_equal(self):
        previous = dict(self.previous, material={"verified": True})
        current = dict(self.previous, material={"verified": 1})
        self.assertEqual(changed_fields(previous, current), ["material"])

    def test_key_order_is_irrelevant_but_review_status_does_not_resign_context(self):
        previous = dict(self.previous, material={"id": "m1", "grade": "g1"})
        current = dict(previous, material={"grade": "g1", "id": "m1"}, approval_status="invalidated")
        self.assertEqual(context_fingerprint(previous), context_fingerprint(current))
        self.assertEqual(changed_fields(previous, current), [])


if __name__ == "__main__":
    unittest.main()
