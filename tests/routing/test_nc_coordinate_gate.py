"""Reviewed translation arithmetic is required, not inferred zero offsets."""

import copy
import hashlib
import unittest

from router.job_router import route_job
from scripts.validate_schema_instances import validator_for
from state.state import context_fingerprint
from tests.routing.cnc_fixture import make_cnc_review, rebind_synthetic_verification


class NcCoordinateGateTests(unittest.TestCase):
    def setUp(self):
        self.state, self.request, self.approval, self.program = make_cnc_review()

    def route(self, resign=True):
        if resign:
            self.state["generated_manufacturing_output"]["sha256"] = hashlib.sha256(self.program).hexdigest()
            rebind_synthetic_verification(self.state)
            self.approval["context_fingerprint"] = context_fingerprint(self.state)
        return route_job(self.request, self.state, self.approval, nc_program=self.program)

    def assert_blocked(self, result, blocker):
        self.assertNotEqual(result["approval_state"], "approved")
        self.assertIn(blocker, result["blockers"])
        self.assertFalse(result["execution_allowed"])
        self.assertTrue(result["review_required"])

    def test_missing_coordinate_model_blocks_matching_approval(self):
        self.state["setup"].pop("coordinate_model")
        self.assert_blocked(self.route(), "MISSING_CONTEXT")

    def test_translation_exposes_machine_limit_conflict_hidden_by_raw_coordinates(self):
        self.state["setup"]["coordinate_model"]["translation"]["x"] = 10
        result = self.route()
        self.assert_blocked(result, "MACHINE_CONTEXT_REQUIRED")
        self.assertTrue(any("machine-axis bound" in finding for finding in result["findings"]))

    def test_translated_in_bounds_program_is_not_compared_to_raw_machine_bounds(self):
        model = self.state["setup"]["coordinate_model"]
        model["translation"]["x"] = 10
        model["initial_machine_position"]["x"] = 10
        self.state["machine_profile"]["limits"]["x"] = {"min": 10, "max": 70}
        result = self.route()
        self.assertEqual(result["blockers"], [])
        coordinate = result["nc_review"]["report"]["coordinate_review"]
        self.assertEqual(coordinate["status"], "checked_declared_bounds")
        self.assertTrue(any(point["machine_target"]["x"] == "70" for point in coordinate["targets"]))

    def test_unknown_or_out_of_bounds_initial_position_blocks(self):
        self.state["setup"]["coordinate_model"]["initial_machine_position"]["z"] = 31
        self.assert_blocked(self.route(), "MACHINE_CONTEXT_REQUIRED")
        self.state["setup"]["coordinate_model"].pop("initial_machine_position")
        self.assert_blocked(self.route(), "MISSING_CONTEXT")

    def test_unreviewed_or_stale_model_cannot_be_approved(self):
        review = self.state["setup"]["coordinate_model"]["lifecycle"]["verification"]
        review["status"] = "unverified"
        self.assert_blocked(self.route(), "SOURCE_VERIFICATION_REQUIRED")
        review.update(status="verified", reviewed_revision="old")
        self.assert_blocked(self.route(), "SOURCE_VERIFICATION_REQUIRED")

    def test_model_identities_and_units_must_match_state(self):
        original = copy.deepcopy(self.state)
        for field, value in (("machine_id", "other"), ("controller_id", "other"), ("setup_id", "other"),
                             ("tool_id", "other"), ("wcs", "G55"), ("units", "in")):
            with self.subTest(field=field):
                self.state = copy.deepcopy(original)
                self.state["setup"]["coordinate_model"][field] = value
                self.assert_blocked(self.route(), "MISSING_CONTEXT")

    def test_coordinate_frame_and_axis_model_are_explicit(self):
        original = copy.deepcopy(self.state)
        for field, value in (("coordinate_frame", None), ("coordinate_frame", "workpiece")):
            self.state = copy.deepcopy(original)
            self.state["machine_profile"]["limits"][field] = value
            self.assert_blocked(self.route(), "MACHINE_CONTEXT_REQUIRED")
        self.state = copy.deepcopy(original)
        self.state["machine_profile"]["capabilities"]["axes"] = 5
        self.assert_blocked(self.route(), "MACHINE_CONTEXT_REQUIRED")

    def test_schema_rejects_incomplete_vectors_and_unimplemented_model_kinds(self):
        for field, value in (("translation", {"x": 0, "y": 0}), ("translation", {"x": False, "y": 0, "z": 0}),
                             ("kind", "rotated_scaled")):
            with self.subTest(field=field):
                setup = copy.deepcopy(self.state["setup"])
                setup["coordinate_model"][field] = value
                self.assertFalse(validator_for("setup.schema.json").is_valid(setup))

    def test_coordinate_change_invalidates_prior_fingerprint(self):
        self.state["setup"]["coordinate_model"]["translation"]["x"] = 1
        result = self.route(resign=False)
        self.assertEqual(result["approval_state"], "invalidated")
        self.assertEqual(result["approval_record"]["context_fingerprint"], self.approval["context_fingerprint"])

    def test_implicit_axis_values_preserve_previous_machine_position(self):
        result = self.route()
        points = result["nc_review"]["report"]["coordinate_review"]["targets"]
        self.assertEqual(points[-1]["machine_target"], {"x": "0", "y": "0", "z": "25"})
        self.assertTrue(any(point["machine_target"] == {"x": "60", "y": "40", "z": "0"} for point in points))

    def test_offset_changing_code_cannot_use_fixed_translation(self):
        self.program = self.program.replace(b"G1 X60 Y40", b"G92X0\nG1 X60 Y40")
        self.assert_blocked(self.route(), "SOURCE_VERIFICATION_REQUIRED")

    def test_additional_tool_change_requires_new_initial_position_evidence(self):
        self.program = self.program.replace(b"G0 Z25", b"M5\nT1M6\nS5000M3\nG0 Z25")
        self.assert_blocked(self.route(), "SOURCE_VERIFICATION_REQUIRED")

    def test_negative_fractional_translation_checks_exact_boundary(self):
        model = self.state["setup"]["coordinate_model"]
        model["translation"]["x"] = -10.25
        model["initial_machine_position"]["x"] = -10.25
        self.state["machine_profile"]["limits"]["x"] = {"min": -10.25, "max": 49.75}
        result = self.route()
        self.assertEqual(result["blockers"], [])
        points = result["nc_review"]["report"]["coordinate_review"]["targets"]
        self.assertTrue(any(point["machine_target"]["x"] == "49.75" for point in points))
        self.program = self.program.replace(b"X60", b"X60.000000000000000000000000000001")
        result = self.route()
        self.assert_blocked(result, "MACHINE_CONTEXT_REQUIRED")
        self.assertTrue(any("49.750000000000000000000000000001" in finding for finding in result["findings"]))

    def test_first_partial_move_retains_declared_initial_axes(self):
        self.state["setup"]["coordinate_model"]["initial_machine_position"].update(x=7, y=8)
        self.program = self.program.replace(b"G0 X0 Y0 Z25", b"G0 Z25")
        result = self.route()
        self.assertEqual(result["blockers"], [])
        first = result["nc_review"]["report"]["coordinate_review"]["targets"][0]
        self.assertEqual(first["machine_target"], {"x": "7", "y": "8", "z": "25"})

    def test_review_evidence_and_source_cannot_be_omitted(self):
        original = copy.deepcopy(self.state)
        for field, value in (("evidence", []), ("reviewer", None), ("reviewed_at", "not-a-date")):
            with self.subTest(field=field):
                self.state = copy.deepcopy(original)
                self.state["setup"]["coordinate_model"]["lifecycle"]["verification"][field] = value
                self.assert_blocked(self.route(), "MISSING_CONTEXT")
        self.state = copy.deepcopy(original)
        self.state["setup"]["coordinate_model"].pop("source")
        self.assert_blocked(self.route(), "MISSING_CONTEXT")

    def test_model_lifecycle_units_must_match(self):
        self.state["setup"]["coordinate_model"]["lifecycle"]["units"]["length"] = "in"
        self.assert_blocked(self.route(), "MISSING_CONTEXT")


if __name__ == "__main__":
    unittest.main()
