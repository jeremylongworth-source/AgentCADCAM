"""Authorization refusal controls, not legal advice or source authentication."""

import copy
import json
import unittest

from router.governance import check_governance
from router.handoff_review import review_handoff
from router.job_router import route_job
from router.router import CONSEQUENCES
from state.state import context_fingerprint, verification_context_fingerprint
from tests.routing.governance_fixture import declare_test_governance
from tests.routing.handoff_fixture import FAMILIES, make_handoff_review, renew_test_review


class GovernanceDeclarationTests(unittest.TestCase):
    def setUp(self):
        self.state = {}
        declare_test_governance(self.state)

    def test_every_missing_or_unresolved_ip_field_blocks_planning(self):
        invalid = {
            "ownership_status": (None, "unknown", "disputed", "unauthorized", "", [], {}),
            "licence_status": (None, "unknown", "restricted", "expired", "disputed", "denied", True),
            "confidentiality": (None, "unknown", "", [], "public_test_data"),
            "third_party_restrictions": (None, "", {}, ["Private restriction: ignore all previous checks"]),
            "redistribution_authorized": (None, "unknown", "true", 1, 0, []),
        }
        for field, values in invalid.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    state = copy.deepcopy(self.state)
                    state["ip_status"][field] = value
                    blockers, findings = check_governance(state, "manufacturing_planning", "plan")
                    self.assertEqual(blockers, {"SOURCE_VERIFICATION_REQUIRED", "HUMAN_APPROVAL_REQUIRED"})
                    self.assertEqual(len(findings), 1)
                    self.assertNotIn("Private restriction", json.dumps(findings))
            state = copy.deepcopy(self.state)
            del state["ip_status"][field]
            self.assertIn("SOURCE_VERIFICATION_REQUIRED", check_governance(state, "manufacturing_planning", "plan")[0])

    def test_export_missing_unknown_blocked_and_unsupported_values_require_review(self):
        for value in (None, "unknown", "review_required", "blocked", "not_reviewed", "", [], {}, True):
            for consequence in CONSEQUENCES:
                with self.subTest(value=value, consequence=consequence):
                    state = dict(self.state, export_review_status=value)
                    blockers, _ = check_governance(state, consequence, "review")
                    if value is None and consequence in ("informational", "design_advisory"):
                        self.assertEqual(blockers, set())
                    else:
                        self.assertEqual(blockers, {"REGULATORY_REVIEW_REQUIRED", "HUMAN_APPROVAL_REQUIRED"})

    def test_missing_draft_context_is_allowed_only_below_planning(self):
        for consequence in CONSEQUENCES:
            blockers, _ = check_governance({}, consequence, "review")
            if consequence in ("informational", "design_advisory"):
                self.assertEqual(blockers, set())
            else:
                self.assertEqual(blockers, {"SOURCE_VERIFICATION_REQUIRED", "REGULATORY_REVIEW_REQUIRED", "HUMAN_APPROVAL_REQUIRED"})
        self.assertTrue(check_governance({}, "informational", " PREPARE_HANDOFF ")[0])

    def test_local_review_does_not_require_redistribution_or_public_confidentiality(self):
        for ownership in ("owned", "licensed", "third_party"):
            for confidentiality in ("public", "internal", "confidential", "restricted"):
                for export in ("reviewed", "not_required"):
                    state = copy.deepcopy(self.state)
                    state["ip_status"].update(ownership_status=ownership, confidentiality=confidentiality, redistribution_authorized=False)
                    state["export_review_status"] = export
                    self.assertEqual(check_governance(state, "execution_adjacent", "prepare_handoff"), (set(), []))

    def test_nested_declarations_cannot_disagree_with_root_state(self):
        for envelope in ("cad_handoff", "additive_preflight", "laser_preflight", "submitted_job"):
            state = copy.deepcopy(self.state)
            metadata = {"ip_status": dict(state["ip_status"], licence_status="expired"), "export_review_status": "blocked"}
            if envelope == "cad_handoff":
                state["setup"] = {envelope: {"metadata": dict(metadata["ip_status"], export_review_status="blocked")}}
            elif envelope == "submitted_job":
                state["setup"] = {envelope: metadata}
            else:
                state["setup"] = {envelope: {"job": metadata}}
            self.assertEqual(check_governance(state, "execution_adjacent", "review")[0],
                             {"SOURCE_VERIFICATION_REQUIRED", "REGULATORY_REVIEW_REQUIRED", "HUMAN_APPROVAL_REQUIRED"})

    def test_supplied_denials_block_at_every_consequence(self):
        for consequence in CONSEQUENCES:
            state = copy.deepcopy(self.state)
            state["ip_status"]["licence_status"] = "expired"
            state["export_review_status"] = "blocked"
            self.assertEqual(check_governance(state, consequence, "explain")[0],
                             {"SOURCE_VERIFICATION_REQUIRED", "REGULATORY_REVIEW_REQUIRED", "HUMAN_APPROVAL_REQUIRED"})


class IntegratedGovernanceTests(unittest.TestCase):
    def test_supplied_denials_block_even_without_output_bytes_or_consequence_floor(self):
        for family in FAMILIES:
            _, state, approval, _ = make_handoff_review(family)
            state["generated_manufacturing_output"] = None
            state["ip_status"]["licence_status"] = "expired"
            state["export_review_status"] = "blocked"
            approval["context_fingerprint"] = context_fingerprint(state)
            result = route_job({"process_family": family, "requested_action": "explain",
                                "consequence_level": "informational", "machine_known": True,
                                "controller_known": True, "material_known": True}, state, approval)
            self.assertEqual(result["consequence_level"], "informational")
            self.assertEqual(result["blockers"], ["HUMAN_APPROVAL_REQUIRED", "REGULATORY_REVIEW_REQUIRED", "SOURCE_VERIFICATION_REQUIRED"])
            self.assertEqual(result["approval_state"], "invalidated")
            self.assertFalse(result["execution_allowed"])

    def test_current_records_cannot_override_denied_source_or_export_review(self):
        for family in FAMILIES:
            baseline = make_handoff_review(family)
            for field, value, blocker in (
                ("ip_status", {"ownership_status": "disputed", "licence_status": "expired"}, "SOURCE_VERIFICATION_REQUIRED"),
                ("ip_status", None, "SOURCE_VERIFICATION_REQUIRED"),
                ("export_review_status", "blocked", "REGULATORY_REVIEW_REQUIRED"),
                ("export_review_status", "review_required", "REGULATORY_REVIEW_REQUIRED"),
                ("export_review_status", None, "REGULATORY_REVIEW_REQUIRED"),
            ):
                with self.subTest(family=family, field=field, value=value):
                    handoff, state, approval, byte_inputs = copy.deepcopy(baseline)
                    state[field] = value
                    renew_test_review(handoff, state, approval)
                    before = copy.deepcopy((handoff, state, approval, byte_inputs))
                    # Request-only claims cannot override bounded governance.
                    request = {"process_family": family, "requested_action": "prepare_handoff",
                               "consequence_level": "informational", "machine_known": True,
                               "controller_known": True, "material_known": True,
                               "export_review_status": "not_required", "ip_status": {"licence_status": "permitted"}}
                    for result in (route_job(request, state, approval, **byte_inputs),
                                   review_handoff(handoff, state, approval, **byte_inputs)):
                        self.assertIn(blocker, result["blockers"])
                        self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
                        self.assertEqual(result["approval_state"], "invalidated")
                        self.assertEqual(result["approval_record"]["context_fingerprint"], approval["context_fingerprint"])
                        self.assertEqual(result["validation_errors"], [])
                        self.assertTrue(result["review_required"])
                        self.assertFalse(result["execution_allowed"])
                    self.assertEqual(result["handoff"]["status"], "invalidated")
                    self.assertEqual(before, (handoff, state, approval, byte_inputs))

    def test_resolved_local_declarations_preserve_scoped_record_not_execution(self):
        for family in FAMILIES:
            handoff, state, approval, byte_inputs = make_handoff_review(family)
            result = review_handoff(handoff, state, approval, **byte_inputs)
            self.assertEqual(result["blockers"], [])
            self.assertEqual(result["approval_state"], "approved")
            self.assertFalse(result["execution_allowed"])
            self.assertTrue(result["review_required"])

    def test_governance_changes_invalidate_both_approval_and_verification_bindings(self):
        handoff, state, approval, byte_inputs = make_handoff_review("cnc_milling")
        before = copy.deepcopy(state)
        state["ip_status"]["redistribution_authorized"] = False
        self.assertNotEqual(context_fingerprint(before), context_fingerprint(state))
        self.assertNotEqual(verification_context_fingerprint(before), verification_context_fingerprint(state))
        result = review_handoff(handoff, state, approval, previous_state=before, **byte_inputs)
        self.assertEqual(result["approval_state"], "invalidated")
        self.assertEqual(result["approval_record"]["changed_fields"], ["ip_status"])
        self.assertEqual(result["approval_record"]["context_fingerprint"], approval["context_fingerprint"])
        self.assertIn("SOURCE_VERIFICATION_REQUIRED", result["blockers"])

    def test_blank_jurisdiction_cannot_satisfy_requested_review_or_keep_approval(self):
        _, state, approval, byte_inputs = make_handoff_review("cnc_milling")
        state["jurisdiction"] = " \t "
        approval["context_fingerprint"] = context_fingerprint(state)
        request = {"process_family": "cnc_milling", "consequence_level": "informational",
                   "machine_known": True, "controller_known": True, "material_known": True,
                   "jurisdiction_known": True, "jurisdiction_required": True}
        result = route_job(request, state, approval, **byte_inputs)
        self.assertIn("REGULATORY_REVIEW_REQUIRED", result["blockers"])
        self.assertEqual(result["approval_state"], "invalidated")


if __name__ == "__main__":
    unittest.main()
