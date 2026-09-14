"""Review-package fields and declared-status consistency, not safety approval."""

import copy
import json
import unittest
from pathlib import Path

from scripts.validate_schema_instances import validator_for


ROOT = Path(__file__).resolve().parents[2]


class HandoffContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = validator_for("handoff.schema.json")

    def setUp(self):
        self.complete = {
            "handoff_id": "synthetic-handoff", "job_id": "synthetic-job", "revision": "A",
            "process_family": "cnc_milling", "consequence_level": "execution_adjacent",
            "units": "mm", "status": "approved", "context_fingerprint": "a" * 64,
            "context_fingerprint_version": 2,
            "artifacts": [{"artifact_id": "source", "path": "synthetic.step", "kind": "STEP",
                           "sha256": "b" * 64, "revision": "A", "authority": "authoritative"}],
            "assumptions": [],
            "verification": [{"check_id": "fixture-check", "status": "passed",
                              "summary": "Synthetic check declaration only", "evidence": ["fixture:test-report"]}],
            "simulation": {"status": "verified", "reason": "Synthetic simulation declaration only",
                           "required_checks": ["Synthetic machine/fixture simulation"],
                           "evidence": ["fixture:simulation-report"]},
            "human_review": {"action": "Confirm the stated scope and applicable operating procedure before use.",
                             "scope": ["manufacturing_handoff"], "reviewer_role": "Qualified job reviewer"},
            "blockers": [], "review_required": True, "execution_allowed": False,
            "approval_id": "synthetic-review-record",
        }

    def test_complete_declared_review_package_is_schema_valid_not_authenticated(self):
        self.validator.validate(self.complete)
        # Dummy hashes and references demonstrate this is not an authenticity check.
        self.assertFalse(self.complete["execution_allowed"])

    def test_repository_example_is_an_explicit_incomplete_review_package(self):
        value = json.loads((ROOT / "contexts/examples/handoff.example.json").read_text(encoding="utf-8"))
        self.validator.validate(value)
        self.assertIsNone(value["context_fingerprint"])
        self.assertTrue(value["blockers"])
        self.assertTrue(value["human_review"]["action"])

    def test_all_handoff_fields_are_required_even_when_incomplete(self):
        for field in self.complete:
            with self.subTest(field=field):
                value = copy.deepcopy(self.complete)
                del value[field]
                self.assertFalse(self.validator.is_valid(value))

    def test_no_status_can_enable_execution_or_remove_review(self):
        for status in ("draft", "review_required", "blocked", "approved", "invalidated"):
            baseline = dict(self.complete, status=status)
            if status in {"blocked", "invalidated"}:
                baseline["blockers"] = ["HUMAN_APPROVAL_REQUIRED"]
            self.validator.validate(baseline)
            for mutation in ({"execution_allowed": True}, {"review_required": False}):
                with self.subTest(status=status, mutation=mutation):
                    value = dict(baseline, **mutation)
                    self.assertFalse(self.validator.is_valid(value))

    def test_approved_requires_identity_source_artifacts_and_review_reference(self):
        for mutation in ({"context_fingerprint": None}, {"context_fingerprint": "bad"},
                         {"context_fingerprint": "a" * 64 + "\n"},
                         {"context_fingerprint_version": 1}, {"units": None},
                         {"process_family": "unknown"}, {"approval_id": None},
                         {"approval_id": " "}, {"artifacts": []}):
            with self.subTest(mutation=mutation):
                self.assertFalse(self.validator.is_valid(dict(self.complete, **mutation)))
        value = copy.deepcopy(self.complete)
        value["artifacts"][0]["authority"] = "derived"
        self.assertFalse(self.validator.is_valid(value))

    def test_approved_cannot_hide_blockers_or_unresolved_assumptions(self):
        self.assertFalse(self.validator.is_valid(dict(self.complete, blockers=["MISSING_CONTEXT"])))
        for status in ("unresolved", "rejected"):
            value = copy.deepcopy(self.complete)
            value["assumptions"] = [{"statement": "Synthetic assumption", "status": status, "evidence": []}]
            self.assertFalse(self.validator.is_valid(value))

    def test_resolved_assumptions_require_evidence(self):
        value = copy.deepcopy(self.complete)
        value["assumptions"] = [{"statement": "Synthetic assumption", "status": "resolved", "evidence": ["fixture:review"]}]
        self.validator.validate(value)
        value["assumptions"][0]["evidence"] = []
        self.assertFalse(self.validator.is_valid(value))

    def test_approved_requires_nonempty_passed_verification_with_evidence(self):
        self.assertFalse(self.validator.is_valid(dict(self.complete, verification=[])))
        for field, replacement in (("status", "not_run"), ("status", "failed"),
                                   ("status", "inconclusive"), ("evidence", [])):
            value = copy.deepcopy(self.complete)
            value["verification"][0][field] = replacement
            self.assertFalse(self.validator.is_valid(value))

    def test_simulation_not_required_needs_reason_and_cannot_bypass_cnc_gate(self):
        value = copy.deepcopy(self.complete)
        value["simulation"] = {"status": "not_required", "reason": "Design-only review scope", "required_checks": [], "evidence": []}
        self.assertFalse(self.validator.is_valid(value))
        value.update(process_family="cad_handoff", consequence_level="design_advisory")
        self.validator.validate(value)
        value["simulation"]["reason"] = " "
        self.assertFalse(self.validator.is_valid(value))

    def test_unverified_simulation_cannot_receive_approved_status(self):
        for status in ("unknown", "required", "failed"):
            value = copy.deepcopy(self.complete)
            value["simulation"]["status"] = status
            self.assertFalse(self.validator.is_valid(value))
        value = copy.deepcopy(self.complete)
        value["simulation"]["evidence"] = []
        self.assertFalse(self.validator.is_valid(value))

    def test_incomplete_and_failed_findings_are_representable_with_blockers(self):
        value = copy.deepcopy(self.complete)
        value.update(status="review_required", approval_id=None, context_fingerprint=None,
                     units=None, artifacts=[], verification=[], blockers=["MISSING_CONTEXT"])
        value["simulation"] = {"status": "unknown", "reason": "Scope requires assessment", "required_checks": [], "evidence": []}
        value["assumptions"] = [{"statement": "Unknown unit context", "status": "unresolved", "evidence": []}]
        self.validator.validate(value)
        value["verification"] = [{"check_id": "failed-check", "status": "failed", "summary": "Synthetic failure", "evidence": []}]
        self.validator.validate(value)
        value["blockers"] = []
        self.assertFalse(self.validator.is_valid(value))

    def test_blocked_and_invalidated_states_require_blockers(self):
        for status in ("blocked", "invalidated"):
            self.assertFalse(self.validator.is_valid(dict(self.complete, status=status)))
            self.validator.validate(dict(self.complete, status=status, blockers=["HUMAN_APPROVAL_REQUIRED"]))

    def test_live_execution_is_only_representable_as_a_blocked_refusal(self):
        value = dict(self.complete, consequence_level="live_execution")
        self.assertFalse(self.validator.is_valid(value))
        value.update(status="blocked", blockers=["BLOCK_EXECUTION"])
        self.validator.validate(value)
        value["blockers"] = ["MISSING_CONTEXT"]
        self.assertFalse(self.validator.is_valid(value))

    def test_human_review_action_role_and_scope_cannot_be_empty(self):
        for field, value in (("action", " "), ("reviewer_role", ""), ("scope", []),
                             ("scope", [""]), ("scope", ["same", "same"])):
            handoff = copy.deepcopy(self.complete)
            handoff["human_review"][field] = value
            self.assertFalse(self.validator.is_valid(handoff))

    def test_nested_unknown_properties_and_malformed_evidence_are_rejected(self):
        for section in ("simulation", "human_review"):
            value = copy.deepcopy(self.complete)
            value[section]["unexpected"] = "ignored context"
            self.assertFalse(self.validator.is_valid(value))
        for evidence in (None, "report", [""], [" \t"], [1], ["same", "same"]):
            value = copy.deepcopy(self.complete)
            value["verification"][0]["evidence"] = evidence
            self.assertFalse(self.validator.is_valid(value))

    def test_each_incomplete_declaration_requires_a_blocker_even_in_draft(self):
        for mutation in (
            {"context_fingerprint": None}, {"units": None}, {"process_family": "unknown"},
            {"artifacts": []}, {"verification": []},
            {"verification": [{"check_id": "pending", "status": "not_run", "summary": "Not inspected", "evidence": []}]},
            {"assumptions": [{"statement": "Not established", "status": "unresolved", "evidence": []}]},
            {"simulation": {"status": "required", "reason": "Run declared checks", "required_checks": ["machine simulation"], "evidence": []}},
        ):
            with self.subTest(mutation=mutation):
                value = dict(self.complete, status="draft", **mutation)
                self.assertFalse(self.validator.is_valid(value))
                value["blockers"] = ["MISSING_CONTEXT"]
                self.validator.validate(value)

    def test_required_nested_fields_cannot_be_silently_omitted(self):
        for section in ("simulation", "human_review"):
            for field in self.complete[section]:
                value = copy.deepcopy(self.complete)
                del value[section][field]
                with self.subTest(section=section, field=field):
                    self.assertFalse(self.validator.is_valid(value))
        for field in self.complete["verification"][0]:
            value = copy.deepcopy(self.complete)
            del value["verification"][0][field]
            self.assertFalse(self.validator.is_valid(value))

    def test_required_simulation_lists_cannot_be_empty_or_contradict_not_required(self):
        value = copy.deepcopy(self.complete)
        value["simulation"]["required_checks"] = []
        self.assertFalse(self.validator.is_valid(value))
        value = copy.deepcopy(self.complete)
        value.update(process_family="cad_handoff", consequence_level="design_advisory")
        value["simulation"]["status"] = "not_required"
        self.assertFalse(self.validator.is_valid(value))

    def test_passed_claims_without_evidence_are_invalid_before_approval_too(self):
        for section in ("verification", "simulation"):
            value = copy.deepcopy(self.complete)
            value["status"] = "draft"
            record = value[section][0] if section == "verification" else value[section]
            record["evidence"] = []
            self.assertFalse(self.validator.is_valid(value))

    def test_each_initial_family_can_carry_a_declared_review_package(self):
        for family in ("cad_handoff", "cnc_milling", "additive", "laser_cutting"):
            with self.subTest(family=family):
                self.validator.validate(dict(self.complete, process_family=family))


if __name__ == "__main__":
    unittest.main()
