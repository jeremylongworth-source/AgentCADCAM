"""A passed label must not stand in for current, scoped CNC verification."""

import copy
import hashlib
import unittest

from router.job_router import route_job
from router.cnc_verification import check_cnc_verification
from scripts.validate_schema_instances import load_catalog
from state.state import INVALIDATING_FIELDS, context_fingerprint, verification_context_fingerprint
from tests.routing.cnc_fixture import make_cnc_review, rebind_synthetic_verification


class CncVerificationBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()

    def setUp(self):
        self.state, self.request, self.approval, self.program = make_cnc_review()

    def route(self):
        self.approval["context_fingerprint"] = context_fingerprint(self.state)
        return route_job(self.request, self.state, self.approval, nc_program=self.program)

    def assert_blocked(self, result, blocker):
        self.assertEqual(result["approval_state"], "invalidated")
        self.assertIn(blocker, result["blockers"])
        self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
        self.assertFalse(result["execution_allowed"])
        self.assertTrue(result["review_required"])

    def test_other_job_simulation_cannot_be_accepted_as_passed(self):
        self.state["verification_results"] = [{"status": "passed", "kind": "simulation", "nc_sha256": "0" * 64,
                                               "revision": "wrong-job", "machine_id": "other-machine"}]
        self.assert_blocked(self.route(), "SIMULATION_REQUIRED")

    def test_bare_passed_status_is_not_verification_context(self):
        self.state["verification_results"] = [{"status": "passed"}]
        self.assert_blocked(self.route(), "MISSING_CONTEXT")

    def test_current_complete_synthetic_records_remain_nonexecuting(self):
        before = copy.deepcopy(self.state)
        result = self.route()
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["approval_state"], "approved")
        self.assertFalse(result["execution_allowed"])
        self.assertEqual(self.state, before)

    def test_nc_byte_change_invalidates_verification_even_with_new_approval(self):
        self.program += b"(new harmless artifact bytes)\n"
        self.state["generated_manufacturing_output"]["sha256"] = hashlib.sha256(self.program).hexdigest()
        self.assert_blocked(self.route(), "SIMULATION_REQUIRED")

    def test_machine_evidence_change_invalidates_verification_even_with_new_approval(self):
        self.state["machine_profile"]["lifecycle"]["verification"]["notes"] = "changed declared applicability evidence"
        self.assert_blocked(self.route(), "SIMULATION_REQUIRED")

    def test_every_consequential_input_changes_the_verification_basis(self):
        original = verification_context_fingerprint(self.state)
        for field in INVALIDATING_FIELDS:
            if field in ("simulation_status", "verification_results"):
                continue
            with self.subTest(field=field):
                changed = copy.deepcopy(self.state)
                # Fingerprinting is shape-independent; the router validates shape.
                changed[field] = {"changed-test-value": changed.get(field)}
                self.assertNotEqual(original, verification_context_fingerprint(changed))
                blockers, _ = check_cnc_verification(changed, self.catalog)
                self.assertIn("SIMULATION_REQUIRED", blockers)
                self.assertIn("SOURCE_VERIFICATION_REQUIRED", blockers)

    def test_outcomes_do_not_create_circular_binding_but_still_invalidate_approval(self):
        original = verification_context_fingerprint(self.state)
        approval_basis = context_fingerprint(self.state)
        for field, value in (("simulation_status", "failed"), ("verification_results", [])):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.state)
                changed[field] = value
                self.assertEqual(original, verification_context_fingerprint(changed))
                self.assertNotEqual(approval_basis, context_fingerprint(changed))
        self.state["approval_status"] = "invalidated"
        self.assertEqual(original, verification_context_fingerprint(self.state))
        self.assertNotEqual(original, approval_basis)

    def test_basis_is_canonical_and_rejects_nonfinite_or_nonjson_inputs(self):
        reverse = dict(reversed(list(self.state.items())))
        self.assertEqual(verification_context_fingerprint(self.state), verification_context_fingerprint(reverse))
        for invalid in (float("nan"), float("inf"), {1: "not-string-key"}, {"set"}):
            with self.subTest(type=type(invalid)):
                changed = dict(self.state, setup=invalid)
                with self.assertRaises((TypeError, ValueError)):
                    verification_context_fingerprint(changed)

    def test_missing_or_malformed_record_fields_fail_closed(self):
        baseline = copy.deepcopy(self.state)
        mutations = [(field, None) for field in baseline["verification_results"][0]]
        mutations += [("evidence", []), ("evidence", [" "]), ("evidence", ["same", "same"]),
                      ("kind", "static-only"), ("summary", " "), ("context_binding", {}),
                      ("context_binding", {"version": True, "fingerprint": "a" * 64}),
                      ("context_binding", {"version": 2, "fingerprint": "a" * 64}),
                      ("context_binding", {"version": 1, "fingerprint": "a" * 64 + "\n"}),
                      ("context_binding", {"version": 1, "fingerprint": "a" * 64, "extra": True})]
        for field, value in mutations:
            with self.subTest(field=field, value=value):
                self.state = copy.deepcopy(baseline)
                record = self.state["verification_results"][0]
                if value is None:
                    record.pop(field)
                else:
                    record[field] = value
                blockers, findings = check_cnc_verification(self.state, self.catalog)
                self.assertIn("MISSING_CONTEXT", blockers)
                self.assertIn("SIMULATION_REQUIRED", blockers)
                self.assertTrue(findings)

    def test_failed_inconclusive_and_not_run_records_never_satisfy_gate(self):
        baseline = copy.deepcopy(self.state)
        for index in (0, 1):
            for status in ("failed", "inconclusive", "not_run"):
                with self.subTest(index=index, status=status):
                    self.state = copy.deepcopy(baseline)
                    self.state["verification_results"][index]["status"] = status
                    self.assert_blocked(self.route(), "SIMULATION_REQUIRED" if index == 0 else "MISSING_CONTEXT")

    def test_neither_kind_can_substitute_for_the_other(self):
        baseline = copy.deepcopy(self.state["verification_results"])
        for index in (0, 1):
            self.state["verification_results"] = [copy.deepcopy(baseline[index])]
            self.assert_blocked(self.route(), "MISSING_CONTEXT" if index == 0 else "SIMULATION_REQUIRED")

    def test_duplicate_ids_and_extra_bad_records_cannot_be_ignored(self):
        baseline = copy.deepcopy(self.state["verification_results"])
        duplicate = copy.deepcopy(baseline[0])
        stale = copy.deepcopy(baseline[0])
        stale.update(check_id="stale-extra")
        stale["context_binding"]["fingerprint"] = "0" * 64
        failed = dict(baseline[1], check_id="failed-extra", status="failed")
        for extra in (duplicate, stale, failed, {"status": "passed"}):
            with self.subTest(extra=extra):
                self.state["verification_results"] = copy.deepcopy(baseline + [extra])
                self.assert_blocked(self.route(), "MISSING_CONTEXT")

    def test_renewed_test_only_verification_requires_separate_new_approval(self):
        self.state["machine_profile"]["lifecycle"]["verification"]["notes"] = "new test declaration"
        rebind_synthetic_verification(self.state)
        result = route_job(self.request, self.state, self.approval, nc_program=self.program)
        self.assert_blocked(result, "HUMAN_APPROVAL_REQUIRED")
        self.assertEqual(self.route()["blockers"], [])

    def test_changing_evidence_locator_invalidates_approval_even_with_same_inputs(self):
        basis = verification_context_fingerprint(self.state)
        self.state["verification_results"][0]["evidence"] = ["test-only:new-evidence"]
        self.assertEqual(basis, verification_context_fingerprint(self.state))
        result = route_job(self.request, self.state, self.approval, nc_program=self.program)
        self.assert_blocked(result, "HUMAN_APPROVAL_REQUIRED")

    def test_invalid_verification_does_not_suppress_independent_static_findings(self):
        self.program = self.program.replace(b"S5000", b"S99999")
        self.state["generated_manufacturing_output"]["sha256"] = hashlib.sha256(self.program).hexdigest()
        result = self.route()
        self.assert_blocked(result, "SIMULATION_REQUIRED")
        self.assertIn("MACHINE_CONTEXT_REQUIRED", result["nc_review"]["blockers"])

    def test_context_only_planning_does_not_require_simulation_records(self):
        self.state.update(generated_manufacturing_output=None, verification_results=[], simulation_status="not_run")
        self.request.update(artifact_class="handoff", consequence_level="manufacturing_planning")
        self.approval["context_fingerprint"] = context_fingerprint(self.state)
        result = route_job(self.request, self.state, self.approval)
        self.assertEqual(result["blockers"], [])
        self.assertFalse(result["execution_allowed"])

    def test_invalid_route_preserves_supplied_state_record_and_private_values(self):
        self.state["verification_results"][0]["private_unknown_field"] = "private-packet-value"
        self.approval["context_fingerprint"] = context_fingerprint(self.state)
        before = copy.deepcopy((self.state, self.approval))
        result = route_job(self.request, self.state, self.approval, nc_program=self.program)
        self.assert_blocked(result, "SIMULATION_REQUIRED")
        self.assertEqual((self.state, self.approval), before)
        self.assertEqual(result["approval_record"]["context_fingerprint"], self.approval["context_fingerprint"])
        self.assertNotIn("private-packet-value", str(result["findings"]))


if __name__ == "__main__":
    unittest.main()
