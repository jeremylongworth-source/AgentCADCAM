from __future__ import annotations

import unittest

from router.router import route


class FixtureRoutingTests(unittest.TestCase):
    def test_known_initial_fixtures_route_as_execution_adjacent_review(self):
        cases = {
            "cad_handoff": ("design", "cadcam-design-handoff", {}),
            "cnc_milling": ("nc_program", "cnc-milling-planning", {"machine_known": True, "controller_known": True, "material_known": True}),
            "additive": ("mesh", "additive-print-prep", {"machine_known": True, "material_known": True}),
            "laser_cutting": ("two_d_cutting", "laser-cut-preflight", {"machine_known": True, "material_known": True}),
        }
        for family, (artifact, skillset, context) in cases.items():
            request = {"process_family": family, "artifact_class": artifact, "consequence_level": "execution_adjacent", "approval_state": "not_requested", **context}
            result = route(request)
            with self.subTest(family=family):
                self.assertEqual(result["skillset"], skillset)
                self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
                self.assertNotIn("BLOCK_EXECUTION", result["blockers"])
                self.assertFalse(result["execution_allowed"])

    def test_live_execution_request_blocks_for_every_initial_family(self):
        for family in ("cad_handoff", "cnc_milling", "additive", "laser_cutting"):
            result = route({"process_family": family, "artifact_class": "unknown", "consequence_level": "live_execution", "approval_state": "approved"})
            with self.subTest(family=family):
                self.assertIn("BLOCK_EXECUTION", result["blockers"])
                self.assertFalse(result["execution_allowed"])


if __name__ == "__main__":
    unittest.main()
