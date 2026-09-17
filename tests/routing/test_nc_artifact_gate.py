"""Actual NC bytes must agree with state and pass fresh static review."""

import copy
import hashlib
import unittest

from router.job_router import route_job
from state.state import context_fingerprint
from scripts.validate_schema_instances import validator_for
from tests.routing.cnc_fixture import make_cnc_review, rebind_synthetic_verification


class NcArtifactGateTests(unittest.TestCase):
    def setUp(self):
        self.state, self.request, self.approval, self.program = make_cnc_review()

    def resign_test_declarations(self, program=None):
        # Simulate a matching record even for faulty content; never a real review.
        if program is not None:
            self.state["generated_manufacturing_output"]["sha256"] = hashlib.sha256(program).hexdigest()
        rebind_synthetic_verification(self.state)
        self.approval["context_fingerprint"] = context_fingerprint(self.state)

    def assert_invalidated(self, result, blocker):
        self.assertEqual(result["approval_state"], "invalidated")
        self.assertIn(blocker, result["blockers"])
        self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
        self.assertEqual(result["approval_record"]["context_fingerprint"], self.approval["context_fingerprint"])
        self.assertFalse(result["execution_allowed"])
        self.assertTrue(result["review_required"])
        validator_for("approval.schema.json").validate(result["approval_record"])

    def test_matching_approval_without_actual_bytes_is_not_sufficient(self):
        result = route_job(self.request, self.state, self.approval)
        self.assert_invalidated(result, "MISSING_CONTEXT")

    def test_matching_bytes_and_context_get_fresh_nonexecuting_review(self):
        before = copy.deepcopy((self.state, self.request, self.approval))
        result = route_job(self.request, self.state, self.approval, nc_program=self.program)
        self.assertEqual(result["approval_state"], "approved")
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["nc_review"]["sha256"], hashlib.sha256(self.program).hexdigest())
        self.assertEqual(result["nc_review"]["report"]["status"], "review_required")
        self.assertEqual(result["nc_review"]["context_fingerprint"], context_fingerprint(self.state))
        self.assertFalse(result["execution_allowed"])
        self.assertTrue(result["review_required"])
        self.assertEqual(before, (self.state, self.request, self.approval))

    def test_changed_bytes_cannot_reuse_matching_metadata_approval(self):
        changed = self.program.replace(b"S5000", b"S99999")
        result = route_job(self.request, self.state, self.approval, nc_program=changed)
        self.assert_invalidated(result, "SOURCE_VERIFICATION_REQUIRED")
        self.assertEqual(result["job_state"]["generated_manufacturing_output"], self.state["generated_manufacturing_output"])
        self.assertEqual(result["nc_review"]["sha256"], hashlib.sha256(changed).hexdigest())

    def test_resigned_bad_program_still_fails_fresh_static_checks(self):
        for old, new, blocker in ((b"S5000", b"S99999", "MACHINE_CONTEXT_REQUIRED"),
                                  (b"G54", b"(G54)", "MISSING_CONTEXT"),
                                  (b"X60 Y0", b"X100Y0", "MACHINE_CONTEXT_REQUIRED"),
                                  (b"T1 M6", b"T9M6", "MISSING_CONTEXT"),
                                  (b"G21", b"G20", "MISSING_CONTEXT"),
                                  (b"fixture-post-v1", b"wrong-post", "SOURCE_VERIFICATION_REQUIRED"),
                                  (b"fixture-controller", b"wrong-controller", "MACHINE_CONTEXT_REQUIRED"),
                                  (b"REVISION: B", b"REVISION: C", "MISSING_CONTEXT"),
                                  (b"T1 M6", b"T2M6", "MISSING_CONTEXT")):
            with self.subTest(new=new):
                changed = self.program.replace(old, new)
                self.resign_test_declarations(changed)
                result = route_job(self.request, self.state, self.approval, nc_program=changed)
                self.assert_invalidated(result, blocker)
                self.assertEqual(result["nc_review"]["report"]["status"], "blocked")

    def test_missing_or_mismatched_artifact_contract_blocks(self):
        original = copy.deepcopy(self.state["generated_manufacturing_output"])
        for descriptor in (None, {}, dict(original, revision="old"), dict(original, units=None),
                           dict(original, kind="mesh"), dict(original, authority="authoritative"),
                           dict(original, sha256="invalid")):
            with self.subTest(descriptor=descriptor):
                self.state["generated_manufacturing_output"] = descriptor
                self.resign_test_declarations()
                result = route_job(self.request, self.state, self.approval, nc_program=self.program)
                self.assert_invalidated(result, "MISSING_CONTEXT")

    def test_byte_identity_does_not_normalize_line_endings(self):
        changed = self.program.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        if changed == self.program:
            changed = self.program.replace(b"\r\n", b"\n")
        result = route_job(self.request, self.state, self.approval, nc_program=changed)
        self.assert_invalidated(result, "SOURCE_VERIFICATION_REQUIRED")

    def test_wrong_input_type_and_invalid_encoding_do_not_skip_review(self):
        for program in ("G21", bytearray(self.program), b"\xff\xfe"):
            with self.subTest(type=type(program)):
                if isinstance(program, bytes):
                    self.resign_test_declarations(program)
                result = route_job(self.request, self.state, self.approval, nc_program=program)
                self.assertNotEqual(result["approval_state"], "approved")
                self.assertTrue(result["blockers"])
                self.assertFalse(result["execution_allowed"])

    def test_supplied_bytes_force_consequence_even_without_artifact_label(self):
        self.request.update(artifact_class="handoff", consequence_level="informational")
        self.state["generated_manufacturing_output"] = None
        self.resign_test_declarations()
        result = route_job(self.request, self.state, self.approval, nc_program=self.program)
        self.assertEqual(result["consequence_level"], "execution_adjacent")
        self.assert_invalidated(result, "MISSING_CONTEXT")

    def test_selected_wcs_not_first_supported_wcs_drives_review(self):
        self.state["controller_profile"]["modes_and_offsets"]["wcs"] = ["G54", "G55"]
        self.state["work_coordinate_system"]["code"] = "G55"
        self.resign_test_declarations()
        result = route_job(self.request, self.state, self.approval, nc_program=self.program)
        self.assert_invalidated(result, "MISSING_CONTEXT")

    def test_additional_tools_are_not_silently_ignored_by_single_tool_reviewer(self):
        tool = dict(self.state["tool_library"]["tools"][0], tool_id="second", tool_number=2)
        self.state["tool_library"]["tools"].append(tool)
        self.resign_test_declarations()
        result = route_job(self.request, self.state, self.approval, nc_program=self.program)
        self.assert_invalidated(result, "SOURCE_VERIFICATION_REQUIRED")

    def test_profile_and_simulation_gates_remain_independent(self):
        for field, value in (("simulation_status", "failed"), ("verification_results", [{"status": "failed"}])):
            with self.subTest(field=field):
                self.state[field] = value
                self.resign_test_declarations()
                result = route_job(self.request, self.state, self.approval, nc_program=self.program)
                self.assertNotEqual(result["approval_state"], "approved")
                self.assertFalse(result["execution_allowed"])

    def test_stale_descriptor_update_cannot_rewrite_old_fingerprint(self):
        changed = self.program + b"(benign source edit)\n"
        self.state["generated_manufacturing_output"]["sha256"] = hashlib.sha256(changed).hexdigest()
        result = route_job(self.request, self.state, self.approval, nc_program=changed)
        self.assert_invalidated(result, "HUMAN_APPROVAL_REQUIRED")

    def test_live_request_cannot_be_authorized_by_static_pass(self):
        self.request["requested_action"] = "start_cycle"
        result = route_job(self.request, self.state, self.approval, nc_program=self.program)
        self.assertIn("BLOCK_EXECUTION", result["blockers"])
        self.assertFalse(result["execution_allowed"])

    def test_unlabeled_execution_adjacent_handoff_cannot_skip_nc_evidence(self):
        self.request["artifact_class"] = "handoff"
        self.state["generated_manufacturing_output"] = None
        self.resign_test_declarations()
        self.assert_invalidated(route_job(self.request, self.state, self.approval), "MISSING_CONTEXT")

    def test_context_only_planning_does_not_require_a_nonexistent_program(self):
        self.request.update(artifact_class="handoff", consequence_level="manufacturing_planning")
        self.state["generated_manufacturing_output"] = None
        self.resign_test_declarations()
        result = route_job(self.request, self.state, self.approval)
        self.assertEqual(result["blockers"], [])
        self.assertIsNone(result["nc_review"])
        self.assertFalse(result["execution_allowed"])

    def test_nc_input_cannot_be_reclassified_as_cad_to_skip_static_review(self):
        self.state["process_family"] = "cad_handoff"
        self.request.update(process_family="cad_handoff", artifact_class="handoff")
        self.resign_test_declarations()
        for program in (None, self.program):
            with self.subTest(supplied_bytes=program is not None):
                result = route_job(self.request, self.state, self.approval, nc_program=program)
                self.assertNotEqual(result["approval_state"], "approved")
                self.assertIn("MISSING_CONTEXT", result["blockers"])
                self.assertTrue(any("another family cannot bypass" in error for error in result["validation_errors"]))

    def test_malformed_declared_output_cannot_lower_consequence(self):
        self.request.update(artifact_class="handoff", consequence_level="informational")
        self.state["generated_manufacturing_output"] = "malformed descriptor"
        self.resign_test_declarations()
        result = route_job(self.request, self.state, self.approval)
        self.assertEqual(result["consequence_level"], "execution_adjacent")
        self.assertIn("MISSING_CONTEXT", result["blockers"])
        self.assertNotEqual(result["approval_state"], "approved")


if __name__ == "__main__":
    unittest.main()
