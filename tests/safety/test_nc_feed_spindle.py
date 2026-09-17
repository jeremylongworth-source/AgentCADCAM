"""Synthetic numeric-context and ordered feed/spindle review regressions."""

import copy
import unittest

from scripts.nc_static_checks import load_contexts, review_program
from tests.safety.test_nc_static_checks import FIXTURE_ROOT


class NcFeedSpindleTests(unittest.TestCase):
    def setUp(self):
        self.program = (FIXTURE_ROOT / "programs/positive.nc").read_text(encoding="utf-8")
        self.contexts = load_contexts(FIXTURE_ROOT / "contexts")

    def change(self, old, new):
        self.assertIn(old, self.program)
        return self.program.replace(old, new)

    def assert_issue(self, program, blocker, finding):
        result = review_program(program, self.contexts)
        self.assertIn(blocker, result["blockers"])
        self.assertTrue(any(finding in text for text in result["findings"]), result)
        self.assertFalse(result["execution_allowed"])
        self.assertTrue(result["review_required"])

    def test_supported_modes_and_boundary_values(self):
        for speed in (500, 12000):
            for feed in (0.01, 1000):
                with self.subTest(speed=speed, feed=feed):
                    program = self.change("S5000", f"S{speed}").replace("F100", f"F{feed}").replace("F200", f"F{feed}")
                    self.assertEqual(review_program(program, self.contexts)["blockers"],
                                     ["HUMAN_APPROVAL_REQUIRED", "SIMULATION_REQUIRED"])

    def test_missing_or_late_feed_mode_blocks(self):
        for program in (self.change("G94", "(G94)"), self.change("G94", "").replace("G0 Z25", "G94\nG0 Z25")):
            self.assert_issue(program, "MISSING_CONTEXT", "feed mode")

    def test_missing_or_late_rpm_mode_blocks(self):
        for program in (self.change("G97", "(G97)"), self.change("G97", "").replace("G0 Z25", "G97\nG0 Z25")):
            self.assert_issue(program, "MISSING_CONTEXT", "spindle mode")

    def test_missing_zero_negative_and_excessive_feed(self):
        self.assert_issue(self.change("F100", "(F100)"), "MISSING_CONTEXT", "feed rate")
        for rate in (0, -1, 1001):
            with self.subTest(rate=rate):
                self.assert_issue(self.change("F100", f"F{rate}"), "MACHINE_CONTEXT_REQUIRED", "feed rate")

    def test_missing_zero_negative_and_out_of_range_speed(self):
        self.assert_issue(self.change("S5000", "(S5000)"), "MISSING_CONTEXT", "spindle speed")
        for speed in (0, -1, 499, 12001):
            with self.subTest(speed=speed):
                self.assert_issue(self.change("S5000", f"S{speed}"), "MACHINE_CONTEXT_REQUIRED", "spindle speed")

    def test_feed_motion_requires_commanded_spindle_on(self):
        for program in (self.change("M3", "(M3)"), self.change("G1 Z0 F100", "M5\nG1 Z0 F100")):
            self.assert_issue(program, "MISSING_CONTEXT", "spindle-on")

    def test_speed_change_while_on_is_checked(self):
        self.assert_issue(self.change("G1 X60 Y40", "S12001\nG1 X60 Y40"),
                          "MACHINE_CONTEXT_REQUIRED", "spindle speed")

    def test_explicit_spindle_stop_required_at_end(self):
        self.assert_issue(self.change("M5", "(M5)"), "MISSING_CONTEXT", "spindle stop")

    def test_tool_change_while_spindle_commanded_on_blocks(self):
        self.assert_issue(self.change("G0 Z25", "T1 M6\nG0 Z25"), "MISSING_CONTEXT", "tool change while spindle")

    def test_same_block_values_and_separate_modal_values(self):
        for program in (self.change("S5000 M3", "M3 S5000"), self.change("S5000 M3", "S5000\nM3"),
                        self.change("G1 Z0 F100", "F100\nG1 Z0")):
            self.assertEqual(review_program(program, self.contexts)["blockers"],
                             ["HUMAN_APPROVAL_REQUIRED", "SIMULATION_REQUIRED"])

    def test_unsupported_feed_spindle_modes_stay_blocking(self):
        for old, new in (("G94", "G93"), ("G94", "G95"), ("G97", "G96")):
            with self.subTest(new=new):
                self.contexts["controller"]["supported_commands"].append(new)
                self.assert_issue(self.change(old, new), "SOURCE_VERIFICATION_REQUIRED", "outside static reviewer")

    def test_conflicting_feed_or_spindle_modes_are_not_silently_selected(self):
        for old, new in (("G94", "G93G94"), ("G97", "G96G97")):
            self.assert_issue(self.change(old, new), "SOURCE_VERIFICATION_REQUIRED", "conflicting modal")

    def test_missing_and_malformed_feed_limit_blocks(self):
        for limit in (None, {}, [], {"max": True, "units": "mm/min"}, {"max": "NaN", "units": "mm/min"},
                      {"max": -1, "units": "mm/min"}, {"max": 1000, "units": "in/min"}):
            with self.subTest(limit=limit):
                self.contexts["machine"]["limits"]["feed_rate"] = limit
                self.assert_issue(self.program, "MACHINE_CONTEXT_REQUIRED", "feed limit")

    def test_missing_nonfinite_or_reversed_spindle_bounds_block(self):
        for minimum, maximum in ((None, 12000), (500, None), (True, 12000), ("NaN", 12000),
                                 (500, float("inf")), (12000, 500), (-1, 12000)):
            with self.subTest(minimum=minimum, maximum=maximum):
                self.contexts["machine"]["capabilities"].update(spindle_rpm_min=minimum, spindle_rpm_max=maximum)
                self.assert_issue(self.program, "MACHINE_CONTEXT_REQUIRED", "spindle limits")

    def test_machine_length_and_spindle_units_cannot_be_inferred(self):
        original = copy.deepcopy(self.contexts)
        for field, wrong in (("length", "in"), ("length", None), ("spindle_speed", None), ("spindle_speed", "rad/s")):
            with self.subTest(field=field, wrong=wrong):
                self.contexts = copy.deepcopy(original)
                self.contexts["machine"]["lifecycle"]["units"][field] = wrong
                self.assert_issue(self.program, "MACHINE_CONTEXT_REQUIRED", "machine units")

    def test_missing_nonfinite_or_reversed_axis_bounds_block(self):
        for limit in (None, {}, [], {"min": 0}, {"min": 100, "max": 0}, {"min": True, "max": 60},
                      {"min": "NaN", "max": 60}, {"min": 0, "max": float("inf")}):
            with self.subTest(limit=limit):
                self.contexts["machine"]["limits"]["x"] = limit
                self.assert_issue(self.program, "MACHINE_CONTEXT_REQUIRED", "X coordinate bounds")

    def test_approval_declarations_cannot_suppress_numeric_failures(self):
        self.contexts["job"].update(simulation_status="verified", approval_status="approved")
        self.assert_issue(self.change("S5000", "S99999"), "MACHINE_CONTEXT_REQUIRED", "spindle speed")

    def test_controller_units_must_support_the_job(self):
        for units in (None, [], ["in"], "mm"):
            with self.subTest(units=units):
                self.contexts["controller"]["supported_units"] = units
                self.assert_issue(self.program, "MACHINE_CONTEXT_REQUIRED", "controller units")

    def test_malformed_job_units_are_reported_not_used_as_mapping_keys(self):
        for units in (None, {}, [], True):
            with self.subTest(units=units):
                self.contexts["job"]["units"] = units
                self.assert_issue(self.program, "MISSING_CONTEXT", "program units")

    def test_initial_spindle_state_is_unknown_until_explicit_stop(self):
        program = self.program.replace("M5\nT1 M6", "T1 M6")
        self.assert_issue(program, "MISSING_CONTEXT", "tool change while spindle")
        self.assert_issue(program.replace("T1 M6", "T1 M6 M5"), "MISSING_CONTEXT", "tool change while spindle")

    def test_missing_numeric_context_containers_fail_closed(self):
        original = copy.deepcopy(self.contexts)
        for field, finding in (("limits", "coordinate bounds"), ("capabilities", "spindle limits"), ("lifecycle", "machine units")):
            for value in (None, [], "invalid"):
                with self.subTest(field=field, value=value):
                    self.contexts = copy.deepcopy(original)
                    self.contexts["machine"][field] = value
                    self.assert_issue(self.program, "MACHINE_CONTEXT_REQUIRED", finding)

    def test_inputs_are_not_repaired_or_approved_by_review(self):
        original = copy.deepcopy(self.contexts)
        result = review_program(self.program, self.contexts)
        self.assertEqual(self.contexts, original)
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["execution_allowed"])
        self.assertTrue(result["review_required"])


if __name__ == "__main__":
    unittest.main()
