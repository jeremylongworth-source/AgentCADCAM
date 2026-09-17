"""Laser integration failures cannot be hidden by freshly matching records."""

import copy
import hashlib
import json
import unittest

from router.job_router import route_job
from router.router import LIVE_ACTIONS
from scripts.validate_schema_instances import validator_for
from state.state import context_fingerprint
from tests.evaluation.replay_laser_reviews import CASES
from tests.routing.laser_fixture import CHECKS, make_laser_review, rebind


class LaserArtifactGateTests(unittest.TestCase):
    def setUp(self):
        self.state, self.request, self.approval, self.drawing = make_laser_review()

    def renew(self):
        rebind(self.state)
        self.approval["context_fingerprint"] = context_fingerprint(self.state)

    def route(self, **kwargs):
        before = copy.deepcopy((self.state, self.request, self.approval))
        result = route_job(self.request, self.state, self.approval, laser_drawing=self.drawing, **kwargs)
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

    def test_current_records_and_both_formats_get_fresh_nonexecuting_review(self):
        for case in ("positive", "svg-positive"):
            self.state, self.request, self.approval, self.drawing = make_laser_review(case)
            result = self.route()
            self.assertEqual(result["blockers"], [], result)
            self.assertEqual(result["approval_state"], "approved")
            self.assertEqual(result["laser_review"]["sha256"], hashlib.sha256(self.drawing).hexdigest())
            self.assertEqual(result["laser_review"]["report"]["file_review"]["status"], "checked_partial_geometry")
            validator_for("laser-preflight.schema.json").validate(self.state["setup"]["laser_preflight"])

    def test_all_retained_negatives_block_even_with_new_bound_evidence_and_approval(self):
        for case in CASES:
            if case in ("positive", "svg-positive"):
                continue
            with self.subTest(case=case):
                self.state, self.request, self.approval, self.drawing = make_laser_review(case)
                self.assert_blocked_approval(self.route(), "SOURCE_VERIFICATION_REQUIRED" if "unsupported" in case else "MISSING_CONTEXT")

    def test_missing_wrong_type_or_changed_bytes_cannot_reuse_approval(self):
        for drawing in (None, "path.svg", b"", self.drawing + b"\n"):
            with self.subTest(kind=type(drawing)):
                self.state, self.request, self.approval, _ = make_laser_review()
                self.drawing = drawing
                self.assert_blocked_approval(self.route(), "SOURCE_VERIFICATION_REQUIRED" if type(drawing) is bytes and drawing else "MISSING_CONTEXT")

    def test_missing_or_conflicting_descriptor_and_input_contract_block(self):
        for field in ("setup", "generated_manufacturing_output"):
            for value in (None, {}):
                self.setUp()
                self.state[field] = value
                self.renew()
                self.assert_blocked_approval(self.route())
        for field, value in (("kind", "drawing"), ("authority", "reference"), ("revision", "B"), ("units", "inch")):
            self.setUp()
            self.state["generated_manufacturing_output"][field] = value
            self.renew()
            self.assert_blocked_approval(self.route())

    def test_inner_job_must_match_outer_job_and_authoritative_source(self):
        for key in ("job_id", "revision", "units"):
            self.setUp()
            self.state["setup"]["laser_preflight"]["job"][key] = "conflict"
            self.renew()
            self.assert_blocked_approval(self.route())
        for key, value in (("sha256", "0" * 64), ("authority", "unknown"), ("revision", "B"), ("units", "inch")):
            self.setUp()
            self.state["setup"]["laser_preflight"]["source_artifact"][key] = value
            self.renew()
            self.assert_blocked_approval(self.route(), "SOURCE_VERIFICATION_REQUIRED")

    def test_empty_settings_or_missing_source_cannot_be_verified_by_status_only(self):
        for key, value in (("settings", {}), ("settings", None), ("source", {}), ("source", None)):
            self.setUp()
            self.state["setup"]["laser_preflight"]["process"][key] = value
            self.renew()
            self.assert_blocked_approval(self.route())

    def test_each_evidence_role_is_required_independently(self):
        for identity in CHECKS:
            with self.subTest(identity=identity):
                self.setUp()
                self.state["verification_results"] = [r for r in self.state["verification_results"] if r["check_id"] != identity]
                self.renew()
                result = self.route()
                self.assert_blocked_approval(result)
                self.assertIn(f"{identity}: a current passed context-bound evidence record is required", result["findings"])

    def test_failed_malformed_duplicate_and_stale_records_cannot_be_hidden(self):
        for key, value in (("status", "failed"), ("status", "inconclusive"), ("evidence", []),
                           ("kind", "simulation"), ("context_binding", {"version": 1, "fingerprint": "0" * 64})):
            self.setUp()
            self.state["verification_results"][0][key] = value
            self.approval["context_fingerprint"] = context_fingerprint(self.state)
            self.assert_blocked_approval(self.route())
        for record in ({"status": "passed"}, copy.deepcopy(self.state["verification_results"][-1])):
            self.setUp()
            self.state["verification_results"].append(record)
            self.approval["context_fingerprint"] = context_fingerprint(self.state)
            self.assert_blocked_approval(self.route())

    def test_changed_process_needs_new_verification_not_just_new_approval(self):
        self.state["setup"]["laser_preflight"]["process"]["settings"]["test_only_non_operational_marker"] = "changed test declaration"
        self.approval["context_fingerprint"] = context_fingerprint(self.state)
        self.assert_blocked_approval(self.route(), "SOURCE_VERIFICATION_REQUIRED")

    def test_old_approval_fingerprint_is_preserved_after_context_change(self):
        previous = copy.deepcopy(self.state)
        self.state["setup"]["laser_preflight"]["process"]["settings"]["test_only_non_operational_marker"] = "changed test declaration"
        rebind(self.state)
        result = self.route(previous_state=previous)
        self.assertEqual(result["approval_state"], "invalidated")
        self.assertIn("setup", result["approval_record"]["changed_fields"])
        self.assertEqual(result["approval_record"]["context_fingerprint"], self.approval["context_fingerprint"])

    def test_raw_approval_flags_never_replace_scoped_records(self):
        self.state["setup"]["laser_preflight"]["job"]["approval_status"] = "approved"
        self.request["approval_state"] = "approved"
        self.state["approval_status"] = "approved"
        rebind(self.state)
        result = route_job(self.request, self.state, laser_drawing=self.drawing)
        self.assertEqual(result["approval_state"], "not_requested")
        self.assertIn("HUMAN_APPROVAL_REQUIRED", result["laser_review"]["blockers"])

    def test_supplied_bytes_and_declared_output_cannot_be_down_classified(self):
        self.request.update(consequence_level="informational", artifact_class="unknown")
        self.assertEqual(self.route()["consequence_level"], "execution_adjacent")
        self.state["generated_manufacturing_output"] = None
        self.renew()
        result = self.route()
        self.assertEqual(result["consequence_level"], "execution_adjacent")
        self.assert_blocked_approval(result)
        self.setUp()
        self.state["process_family"] = "cad_handoff"
        self.request["process_family"] = "cad_handoff"
        self.renew()
        self.assert_blocked_approval(self.route())

    def test_every_live_action_remains_blocked(self):
        for action in LIVE_ACTIONS:
            self.request["requested_action"] = action
            self.request["consequence_level"] = "informational"
            result = self.route()
            self.assertEqual(result["consequence_level"], "live_execution")
            self.assertIn("BLOCK_EXECUTION", result["blockers"])

    def test_advisory_context_without_output_does_not_require_a_nonexistent_drawing(self):
        self.state["generated_manufacturing_output"] = None
        self.state["setup"] = None
        self.drawing = None
        self.request.update(consequence_level="manufacturing_planning", artifact_class="unknown")
        self.renew()
        self.assertEqual(self.route()["blockers"], [])


if __name__ == "__main__":
    unittest.main()
