"""Cross-package identity, evidence and approval checks across all four families."""

import copy
import json
import unittest
from pathlib import Path

from router.handoff_review import review_handoff
from scripts.validate_schema_instances import validator_for
from state.state import context_fingerprint
from tests.routing.handoff_fixture import FAMILIES, make_handoff_review, renew_test_review
from tests.evaluation.replay_additive_reviews import inputs as additive_inputs


class HandoffReviewTests(unittest.TestCase):
    def select(self, family="additive"):
        self.handoff, self.state, self.approval, self.kwargs = make_handoff_review(family)

    def check(self):
        before = copy.deepcopy((self.handoff, self.state, self.approval, self.kwargs))
        result = review_handoff(self.handoff, self.state, self.approval, **self.kwargs)
        self.assertEqual(before, (self.handoff, self.state, self.approval, self.kwargs))
        self.assertTrue(result["review_required"])
        self.assertFalse(result["execution_allowed"])
        json.dumps(result, allow_nan=False)
        if result["handoff"] is not None:
            validator_for("handoff.schema.json").validate(result["handoff"])
        return result

    def blocked(self, result, blocker="MISSING_CONTEXT"):
        self.assertEqual(result["status"], "blocked", result)
        self.assertIn(blocker, result["blockers"], result)
        self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
        self.assertNotEqual(result["approval_state"], "approved")
        if result["approval_record"] is not None:
            self.assertEqual(result["approval_record"]["context_fingerprint"], self.approval["context_fingerprint"])

    def test_all_four_consistent_controls_are_review_only_and_deterministic(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                self.select(family)
                result = self.check()
                self.assertEqual(result["blockers"], [], result)
                self.assertEqual(result["approval_state"], "approved")
                self.assertEqual(result["status"], "review_required")
                self.assertEqual(result, self.check())
                self.assertEqual(result["handoff"], self.handoff)
                validator_for("handoff-review.schema.json").validate(self.state["setup"]["handoff_review"])

    def test_schema_valid_identity_and_classification_conflicts_are_rejected(self):
        for family in FAMILIES:
            for key, value in (("job_id", "other-job"), ("revision", "different"), ("units", "inch"),
                               ("process_family", "cad_handoff" if family != "cad_handoff" else "additive"),
                               ("consequence_level", "informational")):
                self.select(family)
                self.handoff[key] = value
                validator_for("handoff.schema.json").validate(self.handoff)
                self.blocked(self.check())

    def test_changed_snapshot_fields_cannot_borrow_the_approval_fingerprint(self):
        for field in ("handoff_id", "artifacts", "assumptions", "simulation", "human_review"):
            self.select()
            if field == "handoff_id":
                self.handoff[field] = "another-package"
            elif field == "artifacts":
                self.handoff[field][0]["path"] = "substituted-source"
            elif field == "assumptions":
                self.handoff[field] = [{"statement": "New unsupported conclusion", "status": "resolved", "evidence": ["test-only:new"]}]
            elif field == "simulation":
                self.handoff[field]["reason"] = "Different requirement assessment"
            else:
                self.handoff[field]["action"] = "Different downstream instruction"
            validator_for("handoff.schema.json").validate(self.handoff)
            result = self.check()
            self.blocked(result, "SOURCE_VERIFICATION_REQUIRED")
            self.assertIn(f"handoff {field} differs from the state-bound review details", result["findings"])

    def test_absent_or_malformed_snapshot_is_not_repaired_from_the_handoff(self):
        for value in (None, {}, {"handoff_id": "partial"}):
            self.select()
            self.state["setup"]["handoff_review"] = value
            self.approval["context_fingerprint"] = context_fingerprint(self.state)
            self.handoff["context_fingerprint"] = self.approval["context_fingerprint"]
            self.blocked(self.check())

    def test_verification_records_are_exactly_bound_to_the_state(self):
        for family in FAMILIES:
            self.select(family)
            self.handoff["verification"][0]["summary"] = "Changed conclusion"
            self.blocked(self.check(), "SOURCE_VERIFICATION_REQUIRED")

    def test_new_packet_and_approval_cannot_reuse_old_verification(self):
        self.select()
        self.handoff["human_review"]["action"] = "Changed test-only handoff instruction"
        self.state["setup"]["handoff_review"]["human_review"] = copy.deepcopy(self.handoff["human_review"])
        self.handoff["context_fingerprint"] = context_fingerprint(self.state)
        self.approval["context_fingerprint"] = self.handoff["context_fingerprint"]
        self.blocked(self.check(), "SOURCE_VERIFICATION_REQUIRED")

    def test_stale_packet_and_approval_keep_original_review_identity(self):
        for family in FAMILIES:
            self.select(family)
            original = self.handoff["context_fingerprint"]
            self.state["revision"] = "changed"
            result = self.check()
            self.blocked(result, "SOURCE_VERIFICATION_REQUIRED")
            self.assertEqual(result["handoff"]["context_fingerprint"], original)
            self.assertEqual(result["handoff"]["status"], "invalidated")

    def test_current_output_bytes_are_checked_not_just_package_hashes(self):
        for family in FAMILIES:
            self.select(family)
            argument = next(iter(self.kwargs))
            if family == "cad_handoff":
                self.kwargs[argument]["source/bracket.svg"] += b"\n"
            else:
                self.kwargs[argument] += b"\n"
            result = self.check()
            self.blocked(result, "SOURCE_VERIFICATION_REQUIRED")
            self.assertTrue(set(result["routing"]["blockers"]).issubset(result["handoff"]["blockers"]))

    def test_package_cannot_omit_route_blockers_even_with_matching_review_details(self):
        for family in FAMILIES:
            self.select(family)
            self.kwargs = {}
            result = self.check()
            self.blocked(result)
            self.assertIn("handoff omits current routing blockers", result["findings"])

    def test_simulation_and_assumptions_are_independent_blockers(self):
        self.select()
        self.handoff["simulation"].update(status="unknown", reason="Requirement unresolved")
        self.handoff.update(status="blocked", blockers=["test-only:unresolved"])
        self.state["simulation_status"] = "unknown"
        renew_test_review(self.handoff, self.state, self.approval)
        self.blocked(self.check(), "SIMULATION_REQUIRED")
        self.select()
        self.state["simulation_status"] = "verified"
        renew_test_review(self.handoff, self.state, self.approval)
        self.blocked(self.check(), "SIMULATION_REQUIRED")
        self.select()
        self.handoff["assumptions"] = [{"statement": "Unknown fixture condition", "status": "unresolved", "evidence": []}]
        self.handoff.update(status="blocked", blockers=["test-only:unresolved"])
        renew_test_review(self.handoff, self.state, self.approval)
        self.blocked(self.check())

    def test_inventory_unique_identity_and_source_output_coverage_are_required(self):
        for mutation in ("duplicate", "missing-output", "extra-hash", "source-identity", "source-units"):
            self.select()
            if mutation == "duplicate":
                self.handoff["artifacts"].append(copy.deepcopy(self.handoff["artifacts"][0]))
            elif mutation == "missing-output":
                self.handoff["artifacts"].pop()
            elif mutation == "extra-hash":
                extra = dict(self.handoff["artifacts"][0], artifact_id="extra", path="extra", sha256="1" * 64)
                self.handoff["artifacts"].append(extra)
            elif mutation == "source-identity":
                self.handoff["artifacts"][0]["artifact_id"] = "unreviewed-source"
            else:
                self.handoff["artifacts"][0]["units"] = "inch"
            renew_test_review(self.handoff, self.state, self.approval)
            self.blocked(self.check(), "MISSING_CONTEXT" if mutation in ("duplicate", "source-units") else "SOURCE_VERIFICATION_REQUIRED")

    def test_id_scope_or_missing_approval_cannot_authorize(self):
        for mutation in ("id", "scope", "extra-scope", "missing"):
            self.select()
            if mutation == "id":
                self.handoff["approval_id"] = "another-review"
            elif mutation == "scope":
                self.approval["scope"] = ["unrelated"]
            elif mutation == "extra-scope":
                self.handoff["human_review"]["scope"].append("additional-review")
                renew_test_review(self.handoff, self.state, self.approval)
            else:
                self.approval = None
            self.blocked(self.check(), "HUMAN_APPROVAL_REQUIRED")

    def test_cnc_source_derivative_cannot_be_promoted_by_new_review_details(self):
        for key, value in (("kind", "mesh_derivative"), ("path", "test-only:model.stl")):
            self.select("cnc_milling")
            self.handoff["artifacts"][0][key] = value
            renew_test_review(self.handoff, self.state, self.approval)
            result = self.check()
            self.blocked(result, "SOURCE_VERIFICATION_REQUIRED")
            self.assertIn("handoff manufacturing derivative cannot become an authoritative design source", result["findings"])

    def test_draft_is_never_promoted_by_an_existing_record(self):
        for family in FAMILIES:
            self.select(family)
            self.handoff.update(status="draft", approval_id=None)
            result = self.check()
            self.assertEqual(result["blockers"], [])
            self.assertEqual(result["handoff"]["status"], "draft")
            self.assertEqual(result["approval_state"], "not_requested")

    def test_live_handoffs_remain_explicit_blocked_refusals(self):
        for family in FAMILIES:
            self.select(family)
            self.handoff.update(status="blocked", consequence_level="live_execution", blockers=["BLOCK_EXECUTION"])
            result = self.check()
            self.blocked(result, "BLOCK_EXECUTION")
            self.assertEqual(result["handoff"]["status"], "blocked")

    def test_malformed_inputs_fail_without_leaking_values_or_returning_a_package(self):
        for value in (None, [], {"private": "sensitive sentinel"}):
            self.select()
            self.handoff = value
            result = self.check()
            self.blocked(result)
            self.assertIsNone(result["handoff"])
            self.assertNotIn("sensitive sentinel", json.dumps(result))
        self.select()
        self.state = []
        self.blocked(self.check())
        self.handoff.update(status="blocked", blockers=["REGULATORY_REVIEW_REQUIRED"])
        result = self.check()
        self.blocked(result, "REGULATORY_REVIEW_REQUIRED")
        self.assertIn("REGULATORY_REVIEW_REQUIRED", result["handoff"]["blockers"])

    def test_historical_packets_remain_blocked_without_rewriting_any_review(self):
        root = Path(__file__).resolve().parents[2]
        folders = {"cad_handoff": "cad-runs/2026-09-17-manufacturing-intent",
                   "cnc_milling": "cnc-runs/2026-09-17-positive",
                   "additive": "additive-runs/2026-09-17-positive",
                   "laser_cutting": "laser-runs/2026-09-17-positive"}
        for family, folder in folders.items():
            with self.subTest(family=family):
                self.select(family)
                directory = root / "docs/evaluation" / folder
                originals = {path: path.read_bytes() for path in directory.iterdir() if path.is_file()}
                self.handoff = json.loads((directory / "handoff.json").read_text(encoding="utf-8"))
                self.state = json.loads((directory / "state.json").read_text(encoding="utf-8"))
                self.approval = None
                if family == "additive":
                    self.kwargs = {"additive_mesh": additive_inputs("positive")[1]}
                result = self.check()
                self.blocked(result)
                self.assertEqual(result["approval_state"], "not_requested")
                self.assertEqual(result["handoff"]["context_fingerprint"], self.handoff["context_fingerprint"])
                self.assertTrue(set(self.handoff["blockers"]).issubset(result["blockers"]))
                for key in ("artifacts", "assumptions", "verification", "simulation", "human_review"):
                    self.assertEqual(result["handoff"][key], self.handoff[key])
                self.assertEqual(originals, {path: path.read_bytes() for path in originals})


if __name__ == "__main__":
    unittest.main()
