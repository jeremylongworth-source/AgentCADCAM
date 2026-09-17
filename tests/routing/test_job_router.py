from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from router.job_router import route_job
from scripts.validate_schema_instances import validator_for
from state.state import context_fingerprint
from tests.schema.test_profile_lifecycle import synthetic_review
from tests.routing.cnc_fixture import make_cnc_review
from tests.routing.laser_fixture import make_laser_review
from tests.routing.additive_fixture import make_additive_review


ROOT = Path(__file__).resolve().parents[2]


class JobRouterTests(unittest.TestCase):
    def setUp(self):
        self.state, self.request, self.approval, self.program = make_cnc_review()

    def route(self, request, state, approval=None, **kwargs):
        """Supply fixture bytes explicitly for these context-focused CNC tests."""
        program = self.program if isinstance(state, dict) and state.get("process_family") == "cnc_milling" else None
        return route_job(request, state, approval, nc_program=program, **kwargs)

    def test_current_scoped_approval_routes_without_mutating_inputs(self):
        before = copy.deepcopy((self.request, self.state, self.approval))
        result = self.route(self.request, self.state, self.approval)
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["approval_state"], "approved")
        self.assertFalse(result["execution_allowed"])
        self.assertTrue(result["review_required"])
        self.assertEqual(before, (self.request, self.state, self.approval))
        validator_for("state.schema.json").validate(result["job_state"])
        validator_for("approval.schema.json").validate(result["approval_record"])

    def test_changed_evidence_invalidates_before_routing(self):
        for field, value in (
            ("verification_results", [{"status": "failed"}]), ("simulation_status", "failed"),
            ("workholding", {"fixture_id": "new"}), ("job_id", "other-job"),
        ):
            with self.subTest(field=field):
                current = dict(self.state, **{field: value})
                result = self.route(self.request, current, self.approval, previous_state=self.state)
                self.assertEqual(result["approval_state"], "invalidated")
                self.assertIn(field, result["approval_record"]["changed_fields"])
                self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
                validator_for("approval.schema.json").validate(result["approval_record"])

    def test_stale_approval_is_detected_without_a_previous_snapshot(self):
        self.approval["context_fingerprint"] = "old-v1-fingerprint"
        result = self.route(self.request, self.state, self.approval)
        self.assertEqual(result["approval_record"]["status"], "invalidated")
        self.assertEqual(result["approval_record"]["context_fingerprint"], "old-v1-fingerprint")

    def test_new_review_of_changed_context_remains_valid(self):
        previous = dict(self.state, revision="old")
        result = self.route(self.request, self.state, self.approval, previous_state=previous)
        self.assertEqual(result["approval_state"], "approved")

    def test_request_cannot_fabricate_an_approval(self):
        self.request["approval_state"] = "approved"
        self.state["approval_status"] = "approved"
        result = self.route(self.request, self.state)
        self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
        self.assertEqual(result["approval_state"], "not_requested")

    def test_wrong_scope_and_missing_timestamp_require_review(self):
        for mutation in ({"scope": ["unrelated_scope"]}, {"reviewed_at": None}):
            with self.subTest(mutation=mutation):
                result = self.route(self.request, self.state, dict(self.approval, **mutation))
                self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
                self.assertEqual(result["approval_record"]["status"], "approved")

    def test_malformed_state_and_profiles_fail_closed(self):
        for state in ([], dict(self.state, machine_profile={}), dict(self.state, material={"private": "value"}), dict(self.state, workholding={"x": float("nan")})):
            with self.subTest(state_type=type(state)):
                result = self.route(self.request, state, self.approval)
                self.assertIn("MISSING_CONTEXT", result["blockers"])
                self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
                self.assertFalse(result["execution_allowed"])
                json.dumps(result, allow_nan=False)

    def test_missing_profile_cannot_be_confirmed_by_request_flag(self):
        self.state["machine_profile"] = None
        result = self.route(self.request, self.state)
        self.assertIn("MACHINE_CONTEXT_REQUIRED", result["blockers"])

    def test_incomplete_source_blocks_even_a_matching_approval_record(self):
        for field in ("scope", "claims"):
            with self.subTest(field=field):
                current = copy.deepcopy(self.state)
                current["machine_profile"]["source"].pop(field, None)
                approval = dict(self.approval, context_fingerprint=context_fingerprint(current))
                result = self.route(self.request, current, approval)
                self.assertNotEqual(result["approval_state"], "approved")
                self.assertIn("MISSING_CONTEXT", result["blockers"])
                self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
                self.assertFalse(result["execution_allowed"])

    def test_source_claim_change_requires_renewed_review(self):
        current = copy.deepcopy(self.state)
        current["machine_profile"]["source"]["claims"] = ["Changed synthetic evidence scope"]
        result = self.route(self.request, current, self.approval, previous_state=self.state)
        self.assertEqual(result["approval_state"], "invalidated")
        self.assertIn("machine_profile", result["approval_record"]["changed_fields"])
        self.assertEqual(result["approval_record"]["context_fingerprint"], self.approval["context_fingerprint"])

    def test_conflicting_family_is_explicitly_blocked(self):
        self.request["process_family"] = "cad_handoff"
        result = self.route(self.request, self.state, self.approval)
        self.assertIn("MISSING_CONTEXT", result["blockers"])
        self.assertEqual(result["process_family"], "cnc_milling")

    def test_live_action_stays_blocked_with_matching_approval(self):
        self.request.update(requested_action="start_cycle", consequence_level="informational")
        result = self.route(self.request, self.state, self.approval)
        self.assertEqual(result["consequence_level"], "live_execution")
        self.assertIn("BLOCK_EXECUTION", result["blockers"])

    def test_generated_output_sets_consequence_floor(self):
        self.state["generated_manufacturing_output"] = {"sha256": "0" * 64}
        self.request.update(artifact_class="handoff", consequence_level="informational")
        result = self.route(self.request, self.state)
        self.assertEqual(result["consequence_level"], "execution_adjacent")

    def test_matching_approval_cannot_clear_failed_simulation_or_verification(self):
        self.state.update(simulation_status="failed", verification_results=[{"status": "failed"}])
        self.approval["context_fingerprint"] = context_fingerprint(self.state)
        result = self.route(self.request, self.state, self.approval)
        self.assertIn("SIMULATION_REQUIRED", result["blockers"])
        self.assertIn("MISSING_CONTEXT", result["blockers"])
        self.assertFalse(result["execution_allowed"])
        self.assertEqual(result["approval_state"], "invalidated")
        self.assertEqual(result["approval_record"]["status"], "invalidated")

    def test_nonfinite_previous_snapshot_fails_closed(self):
        previous = dict(self.state, workholding={"x": float("nan")})
        self.approval["context_fingerprint"] = "old"
        result = self.route(self.request, self.state, self.approval, previous_state=previous)
        self.assertIn("MISSING_CONTEXT", result["blockers"])
        self.assertEqual(result["approval_state"], "not_requested")

    def test_all_workflow_families_accept_current_scoped_records(self):
        for family, fixture, machine_file, artifact, skillset in (
            ("cad_handoff", "cnc/mill-bracket", "machine", "drawing", "cadcam-design-handoff"),
            ("cnc_milling", "cnc/mill-bracket", "machine", "nc_program", "cnc-milling-planning"),
            ("additive", "additive/fdm-bracket", "printer", "mesh", "additive-print-prep"),
            ("laser_cutting", "laser/cut-bracket", "machine", "two_d_cutting", "laser-cut-preflight"),
        ):
            with self.subTest(family=family):
                state = copy.deepcopy(self.state)
                state["process_family"] = family
                for target, file in (("machine_profile", machine_file), ("material", "material")):
                    state[target] = synthetic_review(json.loads((ROOT / f"fixtures/{fixture}/contexts/{file}.json").read_text(encoding="utf-8")))
                if family != "cnc_milling":
                    state["controller_profile"] = None
                    state["generated_manufacturing_output"] = None
                approval = dict(self.approval, context_fingerprint=context_fingerprint(state))
                request = dict(self.request, process_family=family, artifact_class=artifact)
                if family == "laser_cutting":
                    state, request, approval, drawing = make_laser_review()
                    result = route_job(request, state, approval, laser_drawing=drawing)
                elif family == "additive":
                    state, request, approval, mesh = make_additive_review()
                    result = route_job(request, state, approval, additive_mesh=mesh)
                else:
                    result = self.route(request, state, approval)
                self.assertEqual(result["blockers"], [])
                self.assertEqual(result["skillset"], skillset)
                self.assertFalse(result["execution_allowed"])

    def test_nc_cannot_be_approved_with_missing_required_context(self):
        for field in ("setup", "tool_library", "postprocessor", "work_coordinate_system", "cam_system", "post_version", "units"):
            with self.subTest(field=field):
                state = dict(self.state, **{field: None})
                approval = dict(self.approval, context_fingerprint=context_fingerprint(state))
                result = self.route(self.request, state, approval)
                self.assertNotEqual(result["approval_state"], "approved")
                self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])

    def test_nc_post_identity_mismatch_is_blocking_even_with_matching_fingerprint(self):
        for field in ("machine_id", "controller_id", "cam_system", "post_version", "validation_state"):
            with self.subTest(field=field):
                state = copy.deepcopy(self.state)
                state["postprocessor"][field] = "mismatched"
                approval = dict(self.approval, context_fingerprint=context_fingerprint(state))
                result = self.route(self.request, state, approval)
                self.assertIn("SOURCE_VERIFICATION_REQUIRED", result["blockers"])
                self.assertNotEqual(result["approval_state"], "approved")

    def test_nc_missing_or_conflicted_tooling_is_blocking(self):
        for mutation in ({"holder": None}, {"reach": None}, {"availability": "unavailable"}, {"tool_number": None}, {"geometry": {}}):
            with self.subTest(mutation=mutation):
                state = copy.deepcopy(self.state)
                state["tool_library"]["tools"][0].update(mutation)
                approval = dict(self.approval, context_fingerprint=context_fingerprint(state))
                result = self.route(self.request, state, approval)
                self.assertIn("MISSING_CONTEXT", result["blockers"])
                self.assertNotEqual(result["approval_state"], "approved")

    def test_nc_wcs_and_workholding_uncertainty_are_blocking(self):
        for field in ("wcs_status", "workholding"):
            state = copy.deepcopy(self.state)
            state["setup"][field] = "missing" if field == "wcs_status" else {"clamps_clear": None}
            approval = dict(self.approval, context_fingerprint=context_fingerprint(state))
            result = self.route(self.request, state, approval)
            self.assertNotEqual(result["approval_state"], "approved")
            self.assertIn("MISSING_CONTEXT", result["blockers"])

    def test_nc_malformed_nested_controller_and_tooling_data_fail_closed(self):
        for field, mutation in (
            ("controller_profile", {"supported_units": 1}),
            ("controller_profile", {"modes_and_offsets": []}),
            ("controller_profile", {"modes_and_offsets": {"wcs": 1}}),
            ("tool_library", {"tools": [None]}),
        ):
            with self.subTest(field=field, mutation=mutation):
                state = copy.deepcopy(self.state)
                state[field].update(mutation)
                approval = dict(self.approval, context_fingerprint=context_fingerprint(state))
                result = self.route(self.request, state, approval)
                self.assertNotEqual(result["approval_state"], "approved")
                self.assertIn("MISSING_CONTEXT", result["blockers"])

    def test_nc_duplicate_tool_identity_or_number_is_blocking(self):
        for field in ("tool_id", "tool_number"):
            with self.subTest(field=field):
                state = copy.deepcopy(self.state)
                second = dict(state["tool_library"]["tools"][0], tool_id="second", tool_number=2)
                second[field] = state["tool_library"]["tools"][0][field]
                state["tool_library"]["tools"].append(second)
                approval = dict(self.approval, context_fingerprint=context_fingerprint(state))
                result = self.route(self.request, state, approval)
                self.assertEqual(result["approval_state"], "invalidated")
                self.assertIn("MISSING_CONTEXT", result["blockers"])

    def test_nc_explicit_empty_or_conflicting_workholding_cannot_fall_back(self):
        for workholding in ({}, {"type": "fixture-only", "clamps_clear": False}, {"type": "other-fixture", "clamps_clear": True}):
            with self.subTest(workholding=workholding):
                state = dict(self.state, workholding=workholding)
                approval = dict(self.approval, context_fingerprint=context_fingerprint(state))
                before = copy.deepcopy((state, approval))
                result = self.route(self.request, state, approval)
                self.assertEqual(result["approval_state"], "invalidated")
                self.assertEqual(result["job_state"]["approval_status"], "invalidated")
                self.assertIn("MISSING_CONTEXT", result["blockers"])
                self.assertEqual(before, (state, approval))
                self.assertEqual(result["approval_record"]["context_fingerprint"], approval["context_fingerprint"])
                validator_for("approval.schema.json").validate(result["approval_record"])

    def test_nc_unresolved_stock_and_wcs_are_blocking(self):
        for field, mutation in (
            ("setup", {"stock": {"x": 60, "y": 40, "z": 6, "units": "inch"}}),
            ("setup", {"stock": {"x": 60, "y": 40, "z": 0, "units": "mm"}}),
            ("setup", {"orientation": {}}),
            ("work_coordinate_system", {"code": "G55"}),
            ("work_coordinate_system", {"status": "defined"}),
        ):
            with self.subTest(field=field, mutation=mutation):
                state = copy.deepcopy(self.state)
                state[field].update(mutation)
                approval = dict(self.approval, context_fingerprint=context_fingerprint(state))
                result = self.route(self.request, state, approval)
                self.assertEqual(result["approval_state"], "invalidated")
                self.assertIn("MISSING_CONTEXT", result["blockers"])

    def test_unverified_profiles_block_matching_approval_for_all_profile_types(self):
        for field in ("machine_profile", "controller_profile", "material", "postprocessor", "tool_library"):
            for status in ("unknown", "unverified", "conflicted", "rejected"):
                with self.subTest(field=field, status=status):
                    state = copy.deepcopy(self.state)
                    profile = state[field]["tools"][0] if field == "tool_library" else state[field]
                    profile["lifecycle"]["verification"]["status"] = status
                    approval = dict(self.approval, context_fingerprint=context_fingerprint(state))
                    before = copy.deepcopy((state, approval))
                    result = self.route(self.request, state, approval)
                    self.assertEqual(result["approval_state"], "invalidated")
                    self.assertIn("SOURCE_VERIFICATION_REQUIRED", result["blockers"])
                    self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
                    self.assertEqual(result["approval_record"]["context_fingerprint"], approval["context_fingerprint"])
                    self.assertEqual(before, (state, approval))

    def test_profile_review_must_identify_the_current_profile_revision(self):
        state = copy.deepcopy(self.state)
        state["machine_profile"]["lifecycle"]["verification"]["reviewed_revision"] = "old-profile"
        approval = dict(self.approval, context_fingerprint=context_fingerprint(state))
        result = self.route(self.request, state, approval)
        self.assertEqual(result["approval_state"], "invalidated")
        self.assertIn("SOURCE_VERIFICATION_REQUIRED", result["blockers"])

    def test_profile_metadata_changes_invalidate_old_fingerprints(self):
        for field in ("machine_profile", "controller_profile", "material", "postprocessor", "tool_library"):
            for change in ("revision", "applicability", "units", "verification"):
                with self.subTest(field=field, change=change):
                    state = copy.deepcopy(self.state)
                    profile = state[field]["tools"][0] if field == "tool_library" else state[field]
                    lifecycle = profile["lifecycle"]
                    if change == "units":
                        lifecycle[change] = {"length": "inch"}
                    elif change == "verification":
                        lifecycle[change]["notes"] = "Changed synthetic findings"
                    else:
                        lifecycle[change] = "changed"
                    result = self.route(self.request, state, self.approval, previous_state=self.state)
                    self.assertEqual(result["approval_state"], "invalidated")
                    self.assertIn(field, result["approval_record"]["changed_fields"])

    def test_unverified_supplied_profiles_block_approval_in_every_family_and_level(self):
        for family in ("cad_handoff", "cnc_milling", "additive", "laser_cutting"):
            for level in ("informational", "design_advisory", "manufacturing_planning", "execution_adjacent"):
                with self.subTest(family=family, level=level):
                    state = copy.deepcopy(self.state)
                    state["process_family"] = family
                    if family != "cnc_milling":
                        state["generated_manufacturing_output"] = None
                    if family != "cad_handoff":
                        state["machine_profile"]["process_family"] = family
                        state["material"]["process_family"] = family
                    request = dict(self.request, process_family=family, consequence_level=level, artifact_class="handoff")
                    approval = dict(self.approval, context_fingerprint=context_fingerprint(state))
                    kwargs = {}
                    if family == "laser_cutting" and level == "execution_adjacent":
                        state, request, approval, drawing = make_laser_review()
                        kwargs["laser_drawing"] = drawing
                    elif family == "additive" and level == "execution_adjacent":
                        state, request, approval, mesh = make_additive_review()
                        kwargs["additive_mesh"] = mesh
                    self.assertEqual(self.route(request, state, approval, **kwargs)["approval_state"], "approved")
                    state["machine_profile"]["lifecycle"]["verification"]["status"] = "unverified"
                    approval["context_fingerprint"] = context_fingerprint(state)
                    result = self.route(request, state, approval, **kwargs)
                    self.assertEqual(result["approval_state"], "invalidated")
                    self.assertIn("SOURCE_VERIFICATION_REQUIRED", result["blockers"])
