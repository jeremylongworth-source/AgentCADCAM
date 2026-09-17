"""Phase 6 acceptance matrix; synthetic consistency records, never approval."""

import copy
import json
import unittest

from router.handoff_review import review_handoff
from router.job_router import route_job
from router.router import CONSEQUENCES, LIVE_ACTIONS, load_routes, route
from scripts.validate_schema_instances import load_catalog, validator_for
from state.state import changed_fields, context_fingerprint
from tests.routing.handoff_fixture import FAMILIES, make_handoff_review


STATE_FIELDS = {
    "job_id", "revision", "source_artifact_hashes", "units", "process_family",
    "material", "machine_profile", "controller_profile", "setup",
    "work_coordinate_system", "tool_library", "cam_system", "postprocessor",
    "post_version", "simulation_status", "verification_results", "jurisdiction",
    "ip_status", "export_review_status", "approval_status",
}
REQUIRED_CHANGES = (
    "revision", "source_artifact_hashes", "units", "machine_profile",
    "controller_profile", "setup", "tool_library", "postprocessor", "material",
)
BUNDLES = {
    "cad_handoff": "cadcam-design-handoff", "cnc_milling": "cnc-milling-planning",
    "additive": "additive-print-prep", "laser_cutting": "laser-cut-preflight",
}


def request_for(family):
    return {"process_family": family, "artifact_class": "handoff", "requested_action": "prepare_handoff",
            "consequence_level": "execution_adjacent", "machine_known": True,
            "controller_known": True, "material_known": True, "jurisdiction_known": True}


def change_one(state, field, fallback):
    """One schema-valid declared input change, never repair dependent evidence."""
    current = copy.deepcopy(state)
    if field == "revision":
        current[field] += "-changed"
    elif field == "source_artifact_hashes":
        current[field][0] = "1" * 64
    elif field == "units":
        current[field] = "inch"
    elif field == "setup":
        current[field]["handoff_review"]["human_review"]["action"] += " Changed test-only setup review."
    elif field == "tool_library":
        if current[field] is None:
            current[field] = copy.deepcopy(fallback[field])
        else:
            current[field]["tools"][0]["tool_id"] += "-changed"
    else:
        identity = {"machine_profile": "machine_id", "controller_profile": "controller_id",
                    "postprocessor": "post_id", "material": "material_id"}[field]
        if current[field] is None:
            current[field] = copy.deepcopy(fallback[field])
        else:
            current[field][identity] += "-changed"
    return current


class IntegrationGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.controls = {family: make_handoff_review(family) for family in FAMILIES}

    def test_state_contract_represents_every_roadmap_field_but_not_free_form_memory(self):
        schema = self.catalog[0]["state.schema.json"]
        self.assertTrue(STATE_FIELDS.issubset(schema["properties"]))
        self.assertIs(schema["additionalProperties"], False)
        for _, state, _, _ in self.controls.values():
            validator_for("state.schema.json", self.catalog).validate(state)
            self.assertTrue(STATE_FIELDS.issubset(state))
            unbounded = dict(state, agent_memory="unstructured manufacturing authority")
            self.assertFalse(validator_for("state.schema.json", self.catalog).is_valid(unbounded))

    def test_all_four_current_controls_are_deterministic_under_object_key_reordering(self):
        def reorder(value):
            if isinstance(value, dict):
                return {key: reorder(value[key]) for key in reversed(value)}
            if isinstance(value, list):
                return [reorder(item) for item in value]
            return value

        for family, (handoff, state, approval, byte_inputs) in self.controls.items():
            with self.subTest(family=family):
                request = request_for(family)
                before = copy.deepcopy((request, handoff, state, approval, byte_inputs))
                result = route_job(request, state, approval, **byte_inputs)
                self.assertEqual(result, route_job(reorder(request), reorder(state), reorder(approval), **reorder(byte_inputs)))
                self.assertEqual(result["skillset"], BUNDLES[family])
                self.assertEqual(result["blockers"], [])
                self.assertEqual(result["approval_state"], "approved")
                consumer = review_handoff(handoff, state, approval, **byte_inputs)
                self.assertEqual(consumer, review_handoff(reorder(handoff), reorder(state), reorder(approval), **reorder(byte_inputs)))
                self.assertEqual(consumer["blockers"], [])
                self.assertTrue(consumer["review_required"])
                self.assertFalse(consumer["execution_allowed"])
                self.assertEqual(before, (request, handoff, state, approval, byte_inputs))
                json.dumps(result, allow_nan=False)

    def test_each_required_change_invalidates_downstream_approval_in_every_family(self):
        fallback = self.controls["cnc_milling"][1]
        for family, (handoff, state, approval, byte_inputs) in self.controls.items():
            baseline = review_handoff(handoff, state, approval, **byte_inputs)
            self.assertEqual(baseline["blockers"], [])
            self.assertEqual(baseline["approval_state"], "approved")
            for field in REQUIRED_CHANGES:
                current = change_one(state, field, fallback)
                self.assertEqual(changed_fields(state, current), [field])
                self.assertNotEqual(context_fingerprint(current), approval["context_fingerprint"])
                validator_for("state.schema.json", self.catalog).validate(current)
                for previous in (state, None):
                    with self.subTest(family=family, field=field, previous_supplied=previous is not None):
                        before = copy.deepcopy((handoff, current, approval))
                        result = review_handoff(handoff, current, approval, previous_state=previous, **byte_inputs)
                        self.assertEqual(result["validation_errors"], [])
                        self.assertEqual(result["approval_state"], "invalidated")
                        self.assertEqual(result["handoff"]["status"], "invalidated")
                        record = result["approval_record"]
                        self.assertEqual(record["invalidation_reason"], "approval fingerprint does not match current context (version 2)")
                        self.assertEqual(record["context_fingerprint"], approval["context_fingerprint"])
                        self.assertEqual(result["handoff"]["context_fingerprint"], handoff["context_fingerprint"])
                        if previous is not None:
                            self.assertEqual(record["changed_fields"], [field])
                        self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
                        self.assertFalse(result["execution_allowed"])
                        self.assertTrue(result["review_required"])
                        validator_for("approval.schema.json", self.catalog).validate(record)
                        validator_for("handoff.schema.json", self.catalog).validate(result["handoff"])
                        self.assertEqual(before, (handoff, current, approval))

    def test_all_consequence_levels_and_live_actions_have_explicit_classification(self):
        self.assertEqual(CONSEQUENCES, ("informational", "design_advisory", "manufacturing_planning",
                                       "execution_adjacent", "live_execution"))
        actions = {"jog", "upload_program", "change_offsets", "activate_spindle", "activate_laser",
                   "start_cycle", "control_machine", "bypass_guard", "disable_interlock", "disable_safety_system"}
        self.assertEqual(LIVE_ACTIONS, actions)
        for family in (*FAMILIES, "unknown"):
            for level in CONSEQUENCES:
                request = dict(request_for(family), requested_action="explain", artifact_class="unknown",
                               consequence_level=level, approval_state="approved")
                result = route(request)
                self.assertEqual(result["consequence_level"], level)
                self.assertFalse(result["execution_allowed"])
                for action in sorted(actions):
                    live = route(dict(request, requested_action=f"  {action.upper()}  "))
                    self.assertEqual(live["consequence_level"], "live_execution")
                    self.assertIn("BLOCK_EXECUTION", live["blockers"])
                    self.assertFalse(live["execution_allowed"])

    def test_actual_bytes_cannot_be_down_classified_at_the_integrated_boundary(self):
        for family, (_, state, approval, byte_inputs) in self.controls.items():
            for level in CONSEQUENCES:
                with self.subTest(family=family, level=level):
                    request = dict(request_for(family), consequence_level=level, requested_action="explain")
                    result = route_job(request, state, approval, **byte_inputs)
                    self.assertEqual(result["consequence_level"], "live_execution" if level == "live_execution" else "execution_adjacent")
                    if level == "live_execution":
                        self.assertIn("BLOCK_EXECUTION", result["blockers"])
                    else:
                        self.assertEqual(result["blockers"], [])
                    self.assertTrue(result["review_required"])
                    self.assertFalse(result["execution_allowed"])

    def test_route_register_has_exact_initial_families_and_unknown_refusal(self):
        routes = load_routes()
        self.assertEqual({item["process_family"] for item in routes}, set(FAMILIES) | {"unknown"})
        self.assertEqual(len(routes), 5)
        for family in ("unknown", "unsupported-process"):
            result = route(dict(request_for(family), approval_state="approved"))
            self.assertEqual(result["process_family"], "unknown")
            self.assertIsNone(result["skillset"])
            self.assertIn("MISSING_CONTEXT", result["blockers"])
            self.assertFalse(result["execution_allowed"])


if __name__ == "__main__":
    unittest.main()
