"""Packet integrity and lifecycle evidence, not automated scoring of reasoning."""

import copy
import json
import unittest

from router.handoff_review import REVIEW_FIELDS, review_handoff
from scripts.validate_schema_instances import instance_paths, load_catalog, validator_for
from state.state import context_fingerprint, verification_context_fingerprint
from tests.evaluation.replay_integration_reviews import CASES, ROOT, PACKETS, folder_for, inputs, replay
from tests.evaluation.replay_integration_controls import replay as replay_controls
from tests.evaluation.governance_expectations import add_integrated_governance_diagnostics


class IntegratedReviewPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.packets = {case: replay(case) for case in CASES}

    def test_retained_packets_replay_with_only_explicit_governance_diagnostics(self):
        for case, packet in self.packets.items():
            with self.subTest(case=case):
                stored = {name: json.loads((folder_for(case) / f"{name}.json").read_text(encoding="utf-8")) for name in packet}
                add_integrated_governance_diagnostics(stored, case)
                self.assertEqual(stored, packet)
                self.assertEqual(packet, replay(case))

    def test_schema_inventory_includes_all_eight_draft_state_and_handoff_files(self):
        discovered = dict(instance_paths())
        for case, packet in self.packets.items():
            for name in ("state", "handoff"):
                self.assertEqual(discovered[folder_for(case) / f"{name}.json"], f"{name}.schema.json")
                validator_for(f"{name}.schema.json", self.catalog).validate(packet[name])

    def test_actual_reviews_remain_blocked_bound_and_non_executable(self):
        bundles = {"cad": "cadcam-design-handoff", "cnc": "cnc-milling-planning",
                   "additive": "additive-print-prep", "laser": "laser-cut-preflight"}
        for case, packet in self.packets.items():
            state, handoff, observed = (packet[k] for k in ("state", "handoff", "observed"))
            consumer, route = observed["handoff_result"], observed["route_result"]
            self.assertEqual(route["skillset"], bundles[case])
            self.assertEqual(route["consequence_level"], "execution_adjacent")
            self.assertEqual(consumer["handoff"], handoff)
            self.assertEqual(handoff["context_fingerprint"], context_fingerprint(state))
            self.assertEqual(handoff["verification"], state["verification_results"])
            self.assertEqual(state["setup"]["handoff_review"], {k: handoff[k] for k in REVIEW_FIELDS})
            for record in state["verification_results"]:
                self.assertNotEqual(record["status"], "passed")
                self.assertEqual(record["context_binding"], {"version": 1, "fingerprint": verification_context_fingerprint(state)})
                self.assertTrue(record["evidence"])
            for result in (handoff, consumer):
                self.assertEqual(result["status"], "blocked")
                self.assertTrue(result["review_required"])
                self.assertFalse(result["execution_allowed"])
                self.assertTrue(set(route["blockers"]).issubset(result["blockers"]))
            self.assertEqual(consumer["approval_state"], "not_requested")
            self.assertIsNone(consumer["approval_record"])
            self.assertIsNone(handoff["approval_id"])

    def test_missing_readiness_context_is_not_filled_with_test_only_values(self):
        cad = self.packets["cad"]["state"]
        self.assertIsNone(cad["setup"]["cad_handoff"]["manufacturing_context"])
        additive = self.packets["additive"]["state"]
        self.assertIsNone(additive["setup"]["additive_preflight"]["slicer_profile"])
        self.assertNotIn("slicer_profile_id", additive["setup"]["additive_preflight"]["job"])
        laser = self.packets["laser"]["state"]
        self.assertEqual(laser["setup"]["laser_preflight"]["process"]["settings"], {})
        for case, key, schema in (("cad", "cad_handoff", "cad-handoff-input"),
                                  ("additive", "additive_preflight", "additive-preflight"),
                                  ("laser", "laser_preflight", "laser-preflight")):
            self.assertFalse(validator_for(f"{schema}.schema.json", self.catalog).is_valid(self.packets[case]["state"]["setup"][key]))
        for case in ("cnc", "additive", "laser"):
            state = self.packets[case]["state"]
            for key in ("machine_profile", "material"):
                self.assertEqual(state[key]["lifecycle"]["verification"]["status"], "unverified")
        for case in CASES:
            packet = self.packets[case]
            original, contexts, artifacts, _, _ = inputs(case)
            self.assertEqual(contexts, packet["observed"]["contexts"])
            self.assertEqual(artifacts, packet["handoff"]["artifacts"])
            for key in original:
                if key not in ("setup", "simulation_status", "verification_results"):
                    self.assertEqual(original[key], packet["state"][key])

    def test_raw_checks_are_not_presented_as_fresh_integrated_parser_results(self):
        self.assertEqual(self.packets["cad"]["observed"]["raw_checks"]["fixture_review"]["blockers"], [])
        self.assertEqual(self.packets["cad"]["observed"]["route_result"]["cad_review"]["file_checks"], [])
        for case, key in (("cnc", "nc_review"), ("additive", "additive_review"), ("laser", "laser_review")):
            self.assertIsNone(self.packets[case]["observed"]["route_result"][key]["report"])
        for case in ("additive", "laser"):
            raw = self.packets[case]["observed"]["raw_checks"]["preflight"]
            self.assertEqual(raw["file_review"]["status"], "checked_partial_geometry")

    def test_cnc_conflicting_revision_and_required_simulation_are_preserved(self):
        packet = self.packets["cnc"]
        self.assertEqual(packet["state"]["revision"], "B")
        self.assertEqual({a["revision"] for a in packet["handoff"]["artifacts"]}, {"A", "B"})
        self.assertEqual(packet["observed"]["contexts"]["job"]["simulation_status"], "not_run")
        self.assertEqual(packet["state"]["simulation_status"], "required")
        self.assertIn("handoff artifact revision or units conflict with current state", packet["observed"]["handoff_result"]["findings"])

    def test_changed_packet_review_cannot_borrow_current_state_binding(self):
        for case, packet in self.packets.items():
            handoff = copy.deepcopy(packet["handoff"])
            handoff["human_review"]["action"] = "Different unreviewed action"
            byte_inputs = inputs(case)[-1]
            before = copy.deepcopy((handoff, packet["state"]))
            result = review_handoff(handoff, packet["state"], **byte_inputs)
            self.assertEqual((handoff, packet["state"]), before)
            self.assertIn("handoff human_review differs from the state-bound review details", result["findings"])
            self.assertIn("SOURCE_VERIFICATION_REQUIRED", result["blockers"])
            self.assertTrue(set(packet["handoff"]["blockers"]).issubset(result["blockers"]))

    def test_only_fixed_cases_can_be_replayed(self):
        for case in ("../cnc", "positive", "unknown", "C:/private"):
            with self.assertRaises(ValueError):
                inputs(case)


class IntegratedApprovalControlTests(unittest.TestCase):
    def test_retained_test_only_lifecycle_transitions_match_all_four_families(self):
        actual = replay_controls()
        # Phase 7 controls add test-only governance and source assessments before
        # rebinding records. Earlier historical snapshots are not rewritten.
        stored = json.loads((ROOT / "docs/evaluation/source-evidence-runs/approval-controls.json").read_text(encoding="utf-8"))
        self.assertEqual(actual, stored)
        self.assertEqual(len(actual["observations"]), 4)
        for family, cases in actual["observations"].items():
            with self.subTest(family=family):
                baseline = cases["matching_test_record"]
                for name, result in cases.items():
                    self.assertTrue(result["review_required"])
                    self.assertFalse(result["execution_allowed"])
                    self.assertEqual(result["validation_errors"], [])
                    self.assertEqual(result["returned_handoff_fingerprint"], result["supplied_handoff_fingerprint"])
                    self.assertEqual(result["returned_approval_fingerprint"], result["supplied_approval_fingerprint"])
                    if name in ("matching_test_record", "renewed_test_verification_and_record"):
                        self.assertEqual(result["status"], "review_required")
                        self.assertEqual(result["approval_state"], "approved")
                        self.assertEqual(result["blockers"], [])
                    else:
                        self.assertEqual(result["status"], "blocked")
                        self.assertEqual(result["approval_state"], "invalidated")
                        self.assertIn("BLOCK_EXECUTION" if name == "live_execution" else "SOURCE_VERIFICATION_REQUIRED", result["blockers"])
                stale = cases["changed_review_stale_packet_and_record"]
                self.assertEqual(stale["supplied_approval_fingerprint"], baseline["supplied_approval_fingerprint"])
                self.assertNotEqual(stale["current_fingerprint"], stale["supplied_approval_fingerprint"])
                renewed_record = cases["new_test_record_stale_verification"]
                self.assertEqual(renewed_record["current_fingerprint"], renewed_record["supplied_approval_fingerprint"])


if __name__ == "__main__":
    unittest.main()
