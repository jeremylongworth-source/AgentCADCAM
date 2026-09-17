"""Phase 3 gates with unrelated synthetic review prerequisites kept current.

Never promote retained fixture profiles or evidence. In-memory declarations are
deliberately artificial, including the renewed verification and approval records.
"""

import copy
import hashlib
import unittest

import yaml

from router.job_router import route_job
from router.router import LIVE_ACTIONS
from state.state import context_fingerprint
from tests.routing.cnc_fixture import CNC, make_cnc_review, rebind_synthetic_verification


class CncGateMatrixTests(unittest.TestCase):
    def setUp(self):
        self.state, self.request, self.approval, self.program = make_cnc_review()

    def current_test_review(self, state=None, program=None):
        state = copy.deepcopy(self.state if state is None else state)
        program = self.program if program is None else program
        state["generated_manufacturing_output"]["sha256"] = hashlib.sha256(program).hexdigest()
        rebind_synthetic_verification(state)
        approval = dict(self.approval, context_fingerprint=context_fingerprint(state))
        result = route_job(self.request, state, approval, nc_program=program)
        self.assertFalse(result["execution_allowed"])
        self.assertTrue(result["review_required"])
        # Verify these negatives did not pass just because an unrelated binding
        # was stale after changing the test inputs.
        self.assertFalse(any("evidence binding does not match" in item for item in result["findings"]))
        return result

    def assert_rejected(self, result, blocker):
        self.assertIn(blocker, result["blockers"])
        self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
        self.assertNotEqual(result["approval_state"], "approved")

    def test_control_has_no_blockers_but_never_authorizes_execution(self):
        result = self.current_test_review()
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["approval_state"], "approved")
        self.assertEqual(result["nc_review"]["report"]["coordinate_review"]["status"], "checked_declared_bounds")

    def test_all_eight_roadmap_mutations_fail_fresh_composed_review(self):
        expected = yaml.safe_load((CNC / "expected/outcomes.yaml").read_text(encoding="utf-8"))["negative"]
        self.assertEqual({case["mutation"] for case in expected}, {
            "wrong-units", "wrong-post", "wrong-controller", "missing-wcs", "unknown-tool",
            "revision-mismatch", "machine-limit-conflict", "incorrect-tool-number"})
        self.assertEqual(len(expected), 8)
        for case in expected:
            with self.subTest(case=case["mutation"]):
                mutation = yaml.safe_load((CNC / "mutations" / (case["mutation"] + ".yaml")).read_text(encoding="utf-8"))
                program = self.program
                for replacement in mutation["replacements"]:
                    old, new = replacement["from"].encode(), replacement["to"].encode()
                    self.assertEqual(program.count(old), 1)
                    program = program.replace(old, new)
                self.assertNotEqual(program, self.program)
                result = self.current_test_review(program=program)
                for blocker in case["expected_blockers"]:
                    self.assert_rejected(result, blocker)
                    self.assertIn(blocker, result["nc_review"]["blockers"])
                self.assertIsNotNone(result["nc_review"]["report"])
                self.assertEqual(result["nc_review"]["report"]["status"], "blocked")

    def test_each_nc_target_identity_mismatch_is_detected(self):
        for field, target, blocker in (
            ("MACHINE", "fixture-mill-3axis", "MACHINE_CONTEXT_REQUIRED"),
            ("CONTROLLER", "fixture-controller", "MACHINE_CONTEXT_REQUIRED"),
            ("POST", "fixture-post-v1", "SOURCE_VERIFICATION_REQUIRED"),
        ):
            with self.subTest(field=field):
                old = f"( {field}: {target} )".encode()
                self.assertEqual(self.program.count(old), 1)
                result = self.current_test_review(program=self.program.replace(old, f"( {field}: other-target )".encode()))
                self.assert_rejected(result, blocker)
                self.assertIn(blocker, result["nc_review"]["blockers"])

    def test_post_target_chain_and_validation_gate_are_independent(self):
        for field in ("machine_id", "controller_id", "cam_system", "post_version", "validation_state"):
            with self.subTest(field=field):
                state = copy.deepcopy(self.state)
                state["postprocessor"][field] = "unknown"
                result = self.current_test_review(state)
                self.assert_rejected(result, "SOURCE_VERIFICATION_REQUIRED")
                self.assertTrue(any("postprocessor" in item for item in result["findings"]))

    def test_missing_mandatory_context_cannot_be_hidden_by_current_records(self):
        for field, blocker in (
            ("machine_profile", "MACHINE_CONTEXT_REQUIRED"),
            ("controller_profile", "MACHINE_CONTEXT_REQUIRED"),
            ("setup", "MISSING_CONTEXT"), ("tool_library", "MISSING_CONTEXT"),
            ("postprocessor", "SOURCE_VERIFICATION_REQUIRED"),
            ("work_coordinate_system", "MISSING_CONTEXT"),
        ):
            with self.subTest(field=field):
                result = self.current_test_review(dict(self.state, **{field: None}))
                self.assert_rejected(result, blocker)

    def test_each_consequential_tool_field_blocks_independently(self):
        for field in ("holder", "reach", "availability", "tool_number", "geometry"):
            with self.subTest(field=field):
                state = copy.deepcopy(self.state)
                state["tool_library"]["tools"][0][field] = None
                self.assert_rejected(self.current_test_review(state), "MISSING_CONTEXT")

    def test_unverified_wcs_and_simulation_status_block_current_evidence(self):
        for status in ("defined", "unknown"):
            with self.subTest(wcs_status=status):
                state = copy.deepcopy(self.state)
                state["work_coordinate_system"]["status"] = status
                self.assert_rejected(self.current_test_review(state), "MISSING_CONTEXT")
        for status in ("not_run", "failed", "unknown"):
            with self.subTest(simulation_status=status):
                self.assert_rejected(self.current_test_review(dict(self.state, simulation_status=status)), "SIMULATION_REQUIRED")

    def test_every_prohibited_action_is_refused_with_complete_context(self):
        for action in sorted(LIVE_ACTIONS):
            with self.subTest(action=action):
                request = dict(self.request, requested_action=action, consequence_level="informational")
                result = route_job(request, self.state, self.approval, nc_program=self.program)
                self.assertEqual(result["consequence_level"], "live_execution")
                self.assertIn("BLOCK_EXECUTION", result["blockers"])
                self.assertFalse(result["execution_allowed"])
                self.assertTrue(result["review_required"])


if __name__ == "__main__":
    unittest.main()
