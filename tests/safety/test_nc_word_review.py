"""Literal NC review regressions; all programs are inert synthetic strings."""

import copy
import unittest

from scripts.nc_static_checks import load_contexts, review_program
from tests.safety.test_nc_static_checks import FIXTURE_ROOT


class NcWordReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.program = (FIXTURE_ROOT / "programs/positive.nc").read_text(encoding="utf-8")
        cls.contexts = load_contexts(FIXTURE_ROOT / "contexts")

    def review(self, before, after, contexts=None):
        return review_program(self.program.replace(before, after), contexts or self.contexts)

    def assert_block(self, result, blocker):
        self.assertIn(blocker, result["blockers"])
        self.assertEqual(result["status"], "blocked")
        self.assertTrue(result["review_required"])
        self.assertFalse(result["execution_allowed"])

    def test_compact_out_of_bounds_coordinates_are_not_skipped(self):
        self.assert_block(self.review("G1 X60 Y0 F200", "G1X100Y0F200"), "MACHINE_CONTEXT_REQUIRED")

    def test_comments_cannot_supply_units_wcs_or_tool_change(self):
        for text in ("G21", "G90 G17 G54", "T1 M6"):
            with self.subTest(text=text):
                self.assert_block(self.review(text, f"({text})"), "MISSING_CONTEXT")

    def test_commands_coordinates_and_tools_in_comments_are_not_executable_words(self):
        result = self.review("G21", "G21 (G20 G999 X999 T9 M6) ; G91 X999")
        self.assertEqual(result["blockers"], ["HUMAN_APPROVAL_REQUIRED", "SIMULATION_REQUIRED"])

    def test_case_spacing_and_numeric_spelling_preserve_supported_meaning(self):
        for original, replacement in (("G21", "g021.0"), ("T1 M6", "m06t01"),
                                      ("G1 X60 Y0 F200", "n10g01x+60.y.0f200"),
                                      ("G90 G17 G54", "g 9 0 g17g054")):
            with self.subTest(replacement=replacement):
                self.assertEqual(self.review(original, replacement)["blockers"],
                                 ["HUMAN_APPROVAL_REQUIRED", "SIMULATION_REQUIRED"])

    def test_decimal_wcs_is_not_the_required_g54(self):
        self.assert_block(self.review("G54", "G54.1"), "MISSING_CONTEXT")

    def test_compact_unsupported_command_is_detected(self):
        self.assert_block(self.review("G1 X60 Y0 F200", "G999X60Y0F200"), "MACHINE_CONTEXT_REQUIRED")

    def test_tool_selection_can_precede_change_on_separate_line(self):
        self.assertEqual(self.review("T1 M6", "T1\nM6")["blockers"],
                         ["HUMAN_APPROVAL_REQUIRED", "SIMULATION_REQUIRED"])

    def test_unknown_tool_selection_is_not_hidden_by_an_earlier_valid_change(self):
        self.assert_block(self.review("M5", "T9\nM5"), "MISSING_CONTEXT")

    def test_tool_change_without_selection_is_blocked(self):
        self.assert_block(self.review("T1 M6", "M6"), "MISSING_CONTEXT")

    def test_modes_must_be_established_before_motion(self):
        for text in ("G21", "G90 G17 G54", "T1 M6"):
            with self.subTest(text=text):
                changed = self.program.replace(text + "\n", "").replace("G0 Z25", text + "\nG0 Z25")
                self.assert_block(review_program(changed, self.contexts), "MISSING_CONTEXT")

    def test_missing_absolute_mode_is_blocked(self):
        self.assert_block(self.review("G90 G17 G54", "G17 G54"), "MISSING_CONTEXT")

    def test_incremental_mode_is_not_treated_as_absolute_even_if_profile_allows_it(self):
        contexts = copy.deepcopy(self.contexts)
        contexts["controller"]["supported_commands"].append("G91")
        self.assert_block(self.review("G90", "G91", contexts), "SOURCE_VERIFICATION_REQUIRED")

    def test_modal_axis_only_line_is_checked(self):
        self.assert_block(self.review("G1 X60 Y0 F200", "X100Y0F200"), "MACHINE_CONTEXT_REQUIRED")

    def test_axes_without_motion_mode_are_blocked(self):
        self.assert_block(self.review("G0 X0 Y0 Z25", "X0Y0Z25"), "MISSING_CONTEXT")

    def test_duplicate_words_and_conflicting_modal_groups_are_blocked(self):
        for replacement in ("G0G1X0Y0Z25", "G0X0X1Y0Z25", "G0X0Y0Z25M3M5"):
            with self.subTest(replacement=replacement):
                self.assert_block(self.review("G0 X0 Y0 Z25", replacement), "SOURCE_VERIFICATION_REQUIRED")

    def test_unsupported_syntax_and_malformed_comments_fail_closed(self):
        for suffix in ("X#1", "X[1+2]", "X1e2", "/G0X1", "O100", "A90", "G1X",
                       "(unterminated", "(nested (comment))", "G0X1)", "G0X1.2.3"):
            with self.subTest(suffix=suffix):
                self.assert_block(self.review("M5", suffix + "\nM5"), "SOURCE_VERIFICATION_REQUIRED")

    def test_headers_cannot_be_duplicated_or_declared_after_code(self):
        for replacement in ("( REVISION: C )\n( REVISION: B )", "( REVISION: B )\n( REVISION: B )"):
            self.assert_block(self.review("( REVISION: B )", replacement), "SOURCE_VERIFICATION_REQUIRED")
        self.assert_block(self.review("M5", "( JOB: cnc-mill-bracket )\nM5"), "SOURCE_VERIFICATION_REQUIRED")

    def test_executable_code_after_end_is_not_accepted(self):
        self.assert_block(self.review("M30", "M30\nG0X1"), "SOURCE_VERIFICATION_REQUIRED")

    def test_declared_approval_does_not_hide_unsupported_syntax(self):
        contexts = copy.deepcopy(self.contexts)
        contexts["job"].update(simulation_status="verified", approval_status="approved")
        self.assert_block(self.review("G1 X60 Y0 F200", "G1X#1Y0F200", contexts), "SOURCE_VERIFICATION_REQUIRED")

    def test_comments_between_words_work_but_cannot_split_a_word(self):
        self.assertEqual(self.review("G21", "G21 (units; not code)")["blockers"],
                         ["HUMAN_APPROVAL_REQUIRED", "SIMULATION_REQUIRED"])
        for replacement in ("G(comment)21", "G2(comment)1"):
            self.assert_block(self.review("G21", replacement), "SOURCE_VERIFICATION_REQUIRED")

    def test_active_comment_extensions_require_review(self):
        for replacement in ("G21 (DEBUG,#1)", "G21 ; LOGOPEN,file.txt", "G21 (PROBECLOSE)"):
            self.assert_block(self.review("G21", replacement), "SOURCE_VERIFICATION_REQUIRED")

    def test_delimiter_errors_require_review(self):
        for program in (self.program.rstrip().removesuffix("%"), self.program + "G0X1\n",
                        self.program.replace("G21", "%\nG21")):
            self.assert_block(review_program(program, self.contexts), "SOURCE_VERIFICATION_REQUIRED")

    def test_valid_modal_continuation_and_empty_input(self):
        self.assertEqual(self.review("G1 X60 Y0 F200", "X60Y0F200")["blockers"],
                         ["HUMAN_APPROVAL_REQUIRED", "SIMULATION_REQUIRED"])
        self.assert_block(review_program("", self.contexts), "MISSING_CONTEXT")

    def test_caller_allowlist_cannot_enable_unimplemented_decimal_gcode(self):
        contexts = copy.deepcopy(self.contexts)
        contexts["controller"]["supported_commands"].append("G54.1")
        self.assert_block(self.review("G54", "G54.1", contexts), "SOURCE_VERIFICATION_REQUIRED")


if __name__ == "__main__":
    unittest.main()
