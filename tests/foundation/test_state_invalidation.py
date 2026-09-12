from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
