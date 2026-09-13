from __future__ import annotations

import unittest

from router.router import route


class RouterTests(unittest.TestCase):
    def test_initial_workflow_families_route_to_their_skillsets(self):
        cases = {
            "cad_handoff": "cadcam-design-handoff",
            "cnc_milling": "cnc-milling-planning",
            "additive": "additive-print-prep",
            "laser_cutting": "laser-cut-preflight",
        }
        for family, skillset in cases.items():
            request = {"process_family": family, "artifact_class": "unknown"}
            result = route(request)
            with self.subTest(family=family):
                self.assertEqual(result["skillset"], skillset)
                self.assertEqual(result["process_family"], family)

    def test_live_execution_is_always_blocked(self):
        result = route({"process_family": "cnc_milling", "artifact_class": "nc_program", "consequence_level": "live_execution", "approval_state": "approved"})
        self.assertIn("BLOCK_EXECUTION", result["blockers"])
        self.assertFalse(result["execution_allowed"])

    def test_cnc_execution_adjacent_route_requires_context_and_approval(self):
        result = route({"process_family": "cnc_milling", "artifact_class": "nc_program", "consequence_level": "execution_adjacent"})
        self.assertIn("MACHINE_CONTEXT_REQUIRED", result["blockers"])
        self.assertIn("MISSING_CONTEXT", result["blockers"])
        self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])

    def test_missing_consequence_does_not_default_to_informational(self):
        result = route({"process_family": "cnc_milling", "artifact_class": "nc_program"})
        self.assertEqual(result["consequence_level"], "execution_adjacent")
        self.assertIn("MISSING_CONTEXT", result["blockers"])
        self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])

    def test_unknown_family_returns_unknown_route(self):
        result = route({"process_family": "unknown", "artifact_class": "unknown"})
        self.assertEqual(result["route_id"], "unknown")
        self.assertIn("MISSING_CONTEXT", result["blockers"])

    def test_live_action_overrides_advisory_label(self):
        result = route({"process_family": "cad_handoff", "consequence_level": "informational", "requested_action": "start_cycle"})
        self.assertEqual(result["consequence_level"], "live_execution")
        self.assertIn("BLOCK_EXECUTION", result["blockers"])

    def test_generated_nc_cannot_be_down_classified(self):
        result = route({"process_family": "cnc_milling", "artifact_class": "nc_program", "consequence_level": "informational"})
        self.assertEqual(result["consequence_level"], "execution_adjacent")
        self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])

    def test_malformed_fields_block_without_crashing(self):
        for field in ("process_family", "consequence_level", "requested_action", "approval_state", "artifact_class"):
            with self.subTest(field=field):
                result = route({"process_family": "cad_handoff", "consequence_level": "design_advisory", field: []})
                self.assertIn("MISSING_CONTEXT", result["blockers"])
                self.assertFalse(result["execution_allowed"])


if __name__ == "__main__":
    unittest.main()
