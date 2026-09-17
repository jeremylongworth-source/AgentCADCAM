"""Roadmap Phase 7 named-case matrix; synthetic declarations, never job approval."""

import copy
from dataclasses import dataclass
from pathlib import Path
import unittest

from router.handoff_review import review_handoff
from router.job_router import route_job
from scripts.validate_schema_instances import load_catalog, validator_for
from state.state import context_fingerprint, verification_context_fingerprint
from tests.routing.handoff_fixture import FAMILIES, make_handoff_review, renew_test_review
from tests.routing.test_integration_gate import request_for


ROOT = Path(__file__).resolve().parents[2]
MANUFACTURING = ("cnc_milling", "additive", "laser_cutting")
LIVE_CASES = {
    "bypass-guard": "bypass_guard",
    "disable-safety": "disable_safety_system",
    "start-machine": "start_cycle",
}


@dataclass(frozen=True)
class SafetyCase:
    identifier: str
    roadmap_text: str
    families: tuple[str, ...]
    blocker: str


CASES = (
    SafetyCase("missing-machine", "missing machine", MANUFACTURING, "MACHINE_CONTEXT_REQUIRED"),
    SafetyCase("unknown-controller", "unknown controller", ("cnc_milling",), "MACHINE_CONTEXT_REQUIRED"),
    SafetyCase("incorrect-post", "incorrect postprocessor", ("cnc_milling",), "SOURCE_VERIFICATION_REQUIRED"),
    SafetyCase("conflicting-units", "conflicting units", FAMILIES, "MISSING_CONTEXT"),
    SafetyCase("unauthorized-source", "unauthorized source file", FAMILIES, "SOURCE_VERIFICATION_REQUIRED"),
    SafetyCase("unknown-material", "unknown material", MANUFACTURING, "MISSING_CONTEXT"),
    SafetyCase("missing-safety", "missing safety context", MANUFACTURING, "MISSING_CONTEXT"),
    SafetyCase("bypass-guard", "request to bypass guard", FAMILIES, "BLOCK_EXECUTION"),
    SafetyCase("disable-safety", "request to disable safety system", FAMILIES, "BLOCK_EXECUTION"),
    SafetyCase("start-machine", "request to directly start machine", FAMILIES, "BLOCK_EXECUTION"),
    SafetyCase("no-verification", "request to produce production-ready output without verification", FAMILIES, "MISSING_CONTEXT"),
    SafetyCase("export-sensitive", "export-sensitive technical data", FAMILIES, "REGULATORY_REVIEW_REQUIRED"),
    SafetyCase("conflicting-revisions", "conflicting revisions", FAMILIES, "MISSING_CONTEXT"),
)


def adverse_control(case, family, baseline):
    """Change test declarations and rebind test records, not evidence or real approval."""
    handoff, state, approval, byte_inputs = copy.deepcopy(baseline)
    request = request_for(family)
    # An optimistic request must not override the bounded context or byte evidence.
    request.update(consequence_level="informational", approval_state="approved")
    name = case.identifier
    if name == "missing-machine":
        state["machine_profile"] = None
    elif name == "unknown-controller":
        state["controller_profile"] = None
    elif name == "incorrect-post":
        state["postprocessor"]["controller_id"] = "test-only-other-controller"
    elif name == "conflicting-units":
        state["units"] = "inch" if state["units"] == "mm" else "mm"
        handoff["units"] = state["units"]
    elif name == "unauthorized-source":
        state["ip_status"]["licence_status"] = "restricted"
    elif name == "unknown-material":
        state["material"] = None
    elif name == "missing-safety":
        if family == "cnc_milling":
            state["setup"]["workholding"]["clamps_clear"] = None
        elif family == "additive":
            state["setup"]["additive_preflight"]["job"]["environment_status"] = "unknown"
        else:
            state["setup"]["laser_preflight"]["job"]["ventilation_status"] = "unknown"
    elif name in LIVE_CASES:
        request["requested_action"] = LIVE_CASES[name]
        # Serialized handoffs carry consequence, not an action command field.
        handoff.update(consequence_level="live_execution", status="blocked", blockers=["BLOCK_EXECUTION"])
    elif name == "no-verification":
        state["verification_results"] = []
        # A schema-valid draft still cannot borrow the matching approved record.
        handoff.update(status="draft", blockers=["MISSING_CONTEXT"])
    elif name == "export-sensitive":
        state["export_review_status"] = "review_required"
    elif name == "conflicting-revisions":
        state["revision"] += "-conflict"
        handoff["revision"] = state["revision"]
    else:
        raise ValueError("unknown curated safety case")
    # Keep all remaining verification current to isolate the adverse condition.
    # This helper does not supply missing records or change their outcomes.
    renew_test_review(handoff, state, approval)
    return request, handoff, state, approval, byte_inputs


class PublicAlphaSafetyCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.controls = {family: make_handoff_review(family) for family in FAMILIES}

    def test_case_register_matches_every_named_roadmap_safety_case(self):
        phase = (ROOT / "ROADMAP.md").read_text(encoding="utf-8").split("# PHASE 7 -", 1)[1]
        section = phase.split("## Safety tests", 1)[1].split("## Regulatory architecture", 1)[0]
        required = [line[2:] for line in section.splitlines() if line.startswith("* ")]
        self.assertEqual([case.roadmap_text for case in CASES], required)
        self.assertEqual(len({case.identifier for case in CASES}), 13)
        self.assertEqual(sum(len(case.families) for case in CASES), 43)
        for case in CASES:
            self.assertTrue(set(case.families).issubset(FAMILIES))
            self.assertEqual(len(case.families), len(set(case.families)))

    def test_all_four_positive_controls_recognize_records_without_execution(self):
        for family, control in self.controls.items():
            with self.subTest(family=family):
                handoff, state, approval, byte_inputs = control
                before = copy.deepcopy(control)
                results = (route_job(request_for(family), state, approval, **byte_inputs),
                           review_handoff(handoff, state, approval, **byte_inputs))
                for result in results:
                    self.assertEqual(result["validation_errors"], [])
                    self.assertEqual(result["blockers"], [])
                    self.assertEqual(result["approval_state"], "approved")
                    self.assertIs(result["execution_allowed"], False)
                    self.assertIs(result["review_required"], True)
                self.assertEqual(control, before)

    def test_named_adverse_cases_block_at_both_boundaries_with_current_records(self):
        checked = set()
        for case in CASES:
            for family in case.families:
                with self.subTest(case=case.identifier, family=family):
                    inputs = adverse_control(case, family, self.controls[family])
                    request, handoff, state, approval, byte_inputs = inputs
                    before = copy.deepcopy(inputs)
                    for schema, value in (("state.schema.json", state), ("handoff.schema.json", handoff),
                                          ("approval.schema.json", approval)):
                        validator_for(schema, self.catalog).validate(value)
                    fingerprint = context_fingerprint(state)
                    self.assertEqual(approval["context_fingerprint"], fingerprint)
                    self.assertEqual(handoff["context_fingerprint"], fingerprint)
                    for record in state["verification_results"]:
                        self.assertEqual(record["status"], "passed")
                        self.assertEqual(record["context_binding"]["fingerprint"], verification_context_fingerprint(state))
                    results = {"router": route_job(request, state, approval, **byte_inputs)}
                    # The three live actions serialize to one identical live packet.
                    # Count that consumer input once per family, not three times.
                    if case.identifier not in LIVE_CASES or case.identifier == "bypass-guard":
                        results["handoff"] = review_handoff(handoff, state, approval, **byte_inputs)
                    for boundary, result in results.items():
                        with self.subTest(boundary=boundary):
                            self.assertEqual(result["validation_errors"], [])
                            self.assertIn(case.blocker, result["blockers"])
                            self.assertIs(result["execution_allowed"], False)
                            self.assertIs(result["review_required"], True)
                            self.assertEqual(result["approval_record"]["context_fingerprint"], fingerprint)
                            if boundary == "handoff" or case.identifier not in LIVE_CASES:
                                self.assertEqual(result["approval_state"], "invalidated")
                                self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
                            if case.identifier in LIVE_CASES:
                                routing = result["routing"] if boundary == "handoff" else result
                                self.assertEqual(routing["consequence_level"], "live_execution")
                                self.assertIn("BLOCK_EXECUTION", routing["blockers"])
                            if boundary == "handoff":
                                self.assertIn(case.blocker, result["routing"]["blockers"])
                                self.assertEqual(result["status"], "blocked")
                                self.assertIn(result["handoff"]["status"], ("invalidated", "blocked"))
                            checked.add((case.identifier, family, boundary))
                    self.assertEqual(inputs, before)
        self.assertEqual(len(checked), 78)
        self.assertEqual(sum(boundary == "router" for _, _, boundary in checked), 43)
        self.assertEqual(sum(boundary == "handoff" for _, _, boundary in checked), 35)

    def test_forged_approved_live_or_unverified_packets_fail_schema_and_consumer(self):
        for name in ("bypass-guard", "no-verification"):
            case = next(case for case in CASES if case.identifier == name)
            for family in FAMILIES:
                with self.subTest(case=name, family=family):
                    _, handoff, state, approval, byte_inputs = adverse_control(case, family, self.controls[family])
                    handoff.update(status="approved", blockers=[])
                    self.assertFalse(validator_for("handoff.schema.json", self.catalog).is_valid(handoff))
                    before = copy.deepcopy((handoff, state, approval, byte_inputs))
                    result = review_handoff(handoff, state, approval, **byte_inputs)
                    self.assertTrue(any(error.startswith("handoff/") for error in result["validation_errors"]))
                    self.assertIn(case.blocker, result["blockers"])
                    self.assertEqual(result["approval_state"], "invalidated")
                    self.assertEqual(result["approval_record"]["context_fingerprint"], approval["context_fingerprint"])
                    self.assertIsNone(result["handoff"])
                    self.assertIs(result["execution_allowed"], False)
                    self.assertIs(result["review_required"], True)
                    self.assertEqual(before, (handoff, state, approval, byte_inputs))


if __name__ == "__main__":
    unittest.main()
