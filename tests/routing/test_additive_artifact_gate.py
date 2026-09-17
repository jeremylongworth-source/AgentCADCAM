"""Fresh additive evidence under matching test-only records, never printer use."""

import copy
import hashlib
import json
import unittest
from unittest.mock import patch

from router import additive_evidence
from router.job_router import route_job
from router.router import LIVE_ACTIONS
from scripts.validate_schema_instances import validator_for
from state.state import context_fingerprint
from tests.evaluation.replay_additive_reviews import CASES
from tests.routing.additive_fixture import CHECKS, make_additive_review, rebind
from tests.safety.test_three_mf_review import MESH, model, package


class AdditiveArtifactGateTests(unittest.TestCase):
    def setUp(self):
        self.state, self.request, self.approval, self.mesh = make_additive_review()

    def renew(self):
        rebind(self.state)
        self.approval["context_fingerprint"] = context_fingerprint(self.state)

    def route(self, **kwargs):
        before = copy.deepcopy((self.state, self.request, self.approval))
        result = route_job(self.request, self.state, self.approval, additive_mesh=self.mesh, **kwargs)
        self.assertEqual(before, (self.state, self.request, self.approval))
        self.assertFalse(result["execution_allowed"])
        self.assertTrue(result["review_required"])
        json.dumps(result, allow_nan=False)
        return result

    def assert_blocked_approval(self, result, blocker="MISSING_CONTEXT"):
        self.assertIn(blocker, result["blockers"], result)
        self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
        self.assertNotEqual(result["approval_state"], "approved")
        self.assertEqual(result["approval_record"]["context_fingerprint"], self.approval["context_fingerprint"])

    def test_both_formats_have_fresh_nonexecuting_controls(self):
        for case in ("positive", "3mf-positive"):
            self.state, self.request, self.approval, self.mesh = make_additive_review(case)
            result = self.route()
            self.assertEqual(result["blockers"], [], result)
            self.assertEqual(result["approval_state"], "approved")
            self.assertEqual(result["additive_review"]["sha256"], hashlib.sha256(self.mesh).hexdigest())
            self.assertEqual(result["additive_review"]["report"]["file_review"]["status"], "checked_partial_geometry")
            validator_for("additive-preflight.schema.json").validate(self.state["setup"]["additive_preflight"])

    def test_every_retained_negative_blocks_with_current_test_evidence_and_approval(self):
        for case in CASES:
            if case in ("positive", "3mf-positive"):
                continue
            with self.subTest(case=case):
                self.state, self.request, self.approval, self.mesh = make_additive_review(case)
                blocker = "SOURCE_VERIFICATION_REQUIRED" if case == "3mf-required-extension" else "MACHINE_CONTEXT_REQUIRED" if case in ("unsupported-build-volume", "3mf-build-placement") else "MISSING_CONTEXT"
                self.assert_blocked_approval(self.route(), blocker)

    def test_absent_invalid_or_changed_bytes_cannot_reuse_approval(self):
        for value in (None, "model.3mf", b"", self.mesh + b"\n"):
            self.setUp()
            self.mesh = value
            self.assert_blocked_approval(self.route(), "SOURCE_VERIFICATION_REQUIRED" if type(value) is bytes and value else "MISSING_CONTEXT")

    def test_descriptor_contract_format_and_job_state_must_agree(self):
        for field in ("setup", "generated_manufacturing_output"):
            self.setUp()
            self.state[field] = None
            self.renew()
            self.assert_blocked_approval(self.route())
        for key, value in (("kind", "mesh_derivative"), ("authority", "reference"), ("revision", "B"), ("units", "inch")):
            self.setUp()
            self.state["generated_manufacturing_output"][key] = value
            self.renew()
            self.assert_blocked_approval(self.route())
        for key in ("job_id", "revision", "mesh_units", "mesh_format"):
            self.setUp()
            self.state["setup"]["additive_preflight"]["job"][key] = "conflict"
            self.renew()
            self.assert_blocked_approval(self.route())

    def test_source_hash_authority_revision_and_units_are_bound(self):
        for key, value in (("sha256", "0" * 64), ("authority", "unknown"), ("revision", "B"), ("units", "inch")):
            self.setUp()
            self.state["setup"]["additive_preflight"]["source_artifact"][key] = value
            self.renew()
            self.assert_blocked_approval(self.route(), "SOURCE_VERIFICATION_REQUIRED")

    def test_slicer_settings_source_versions_and_selection_are_required(self):
        for key, value in (("settings", {}), ("settings", None), ("source", {}), ("revision", ""),
                           ("slicer_id", ""), ("slicer_version", ""), ("printer_id", "other"),
                           ("material_id", "other"), ("profile_id", "other")):
            self.setUp()
            self.state["setup"]["additive_preflight"]["slicer_profile"][key] = value
            self.renew()
            self.assert_blocked_approval(self.route())
        self.setUp()
        self.state["setup"]["additive_preflight"]["job"].pop("slicer_profile_id")
        self.renew()
        self.assert_blocked_approval(self.route())

    def test_material_slicer_compatibility_and_environment_cannot_be_overridden(self):
        for field, key, value in (("compatibility", "slicer_profiles", []),
                                   ("compatibility", "slicer_profiles", ["other"]),
                                   ("environmental_requirements", "environment_status", "unknown")):
            self.setUp()
            self.state["material"][field][key] = value
            self.renew()
            self.assert_blocked_approval(self.route())

    def test_each_evidence_role_is_independently_required(self):
        for key in CHECKS:
            self.setUp()
            self.state["verification_results"] = [r for r in self.state["verification_results"] if r["check_id"] != key]
            self.renew()
            result = self.route()
            self.assert_blocked_approval(result)
            self.assertIn(f"{key}: a current passed context-bound evidence record is required", result["findings"])

    def test_failed_malformed_duplicate_and_stale_records_block(self):
        for key, value in (("status", "failed"), ("status", "not_run"), ("evidence", []),
                           ("kind", "simulation"), ("context_binding", {"version": 1, "fingerprint": "0" * 64})):
            self.setUp()
            self.state["verification_results"][0][key] = value
            self.approval["context_fingerprint"] = context_fingerprint(self.state)
            self.assert_blocked_approval(self.route())
        for extra in ({"status": "passed"}, copy.deepcopy(self.state["verification_results"][-1])):
            self.setUp()
            self.state["verification_results"].append(extra)
            self.approval["context_fingerprint"] = context_fingerprint(self.state)
            self.assert_blocked_approval(self.route())

    def test_changed_slicer_requires_new_evidence_not_only_new_approval(self):
        for key, value in (("settings", {"non_operational_test_marker": "changed"}), ("revision", "test-2"),
                           ("slicer_version", "new-test-version"), ("source", {"scope": "incomplete test source"})):
            self.setUp()
            self.state["setup"]["additive_preflight"]["slicer_profile"][key] = value
            self.approval["context_fingerprint"] = context_fingerprint(self.state)
            self.assert_blocked_approval(self.route(), "SOURCE_VERIFICATION_REQUIRED")

    def test_old_review_is_invalidated_without_rewriting_its_fingerprint(self):
        previous = copy.deepcopy(self.state)
        self.state["setup"]["additive_preflight"]["slicer_profile"]["revision"] = "test-2"
        rebind(self.state)
        result = self.route(previous_state=previous)
        self.assertEqual(result["approval_state"], "invalidated")
        self.assertIn("setup", result["approval_record"]["changed_fields"])
        self.assertEqual(result["approval_record"]["context_fingerprint"], self.approval["context_fingerprint"])

    def test_raw_flags_wrong_scope_and_missing_approval_cannot_authorize(self):
        self.state["setup"]["additive_preflight"]["job"]["approval_status"] = "approved"
        self.request["approval_state"] = "approved"
        self.state["approval_status"] = "approved"
        rebind(self.state)
        result = route_job(self.request, self.state, additive_mesh=self.mesh)
        self.assertEqual(result["approval_state"], "not_requested")
        self.assertIn("HUMAN_APPROVAL_REQUIRED", result["additive_review"]["blockers"])
        self.renew()
        self.approval["scope"] = ["unrelated"]
        self.assertEqual(self.route()["approval_state"], "not_requested")

    def test_bytes_and_output_cannot_be_down_classified_or_changed_to_another_family(self):
        self.request.update(consequence_level="informational", artifact_class="unknown")
        self.assertEqual(self.route()["consequence_level"], "execution_adjacent")
        self.state["generated_manufacturing_output"] = None
        self.renew()
        self.assert_blocked_approval(self.route())
        self.setUp()
        self.state["process_family"] = "cad_handoff"
        self.request["process_family"] = "cad_handoff"
        self.renew()
        self.assert_blocked_approval(self.route())

    def test_every_prohibited_live_action_stays_blocked(self):
        for action in LIVE_ACTIONS:
            self.request.update(requested_action=action, consequence_level="informational")
            result = self.route()
            self.assertEqual(result["consequence_level"], "live_execution")
            self.assertIn("BLOCK_EXECUTION", result["blockers"])

    def test_context_only_planning_does_not_require_an_invented_mesh(self):
        self.state.update(setup=None, generated_manufacturing_output=None)
        self.mesh = None
        self.request.update(consequence_level="manufacturing_planning", artifact_class="unknown")
        self.renew()
        self.assertEqual(self.route()["blockers"], [])

    def test_extreme_package_numbers_and_input_limits_are_structured_refusals(self):
        self.mesh = package(model(mesh=MESH.replace('x="1"', 'x="1e999999999999999999999999"', 1)))
        digest = hashlib.sha256(self.mesh).hexdigest()
        self.state["generated_manufacturing_output"]["sha256"] = digest
        self.state["setup"]["additive_preflight"]["job"]["mesh_sha256"] = digest
        self.renew()
        self.assert_blocked_approval(self.route(), "SOURCE_VERIFICATION_REQUIRED")
        self.setUp()
        with patch.object(additive_evidence, "MAX_BYTES", 10):
            result = self.route()
            self.assert_blocked_approval(result, "SOURCE_VERIFICATION_REQUIRED")
            self.assertIsNone(result["additive_review"]["sha256"])


if __name__ == "__main__":
    unittest.main()
