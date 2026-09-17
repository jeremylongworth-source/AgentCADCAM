"""Isolated laser gate edges; synthetic flags are not authenticated approval."""

import copy
import json
import unittest

from scripts.laser_preflight import preflight
from tests.evaluation.replay_laser_reviews import inputs


class LaserGateMatrixTests(unittest.TestCase):
    def control(self, format="DXF"):
        contexts, drawing, artifacts, _ = inputs("svg-positive" if format == "SVG" else "positive")
        contexts["job"]["approval_status"] = "approved"
        return contexts, drawing, artifacts[1]["revision"]

    def check(self, contexts, drawing, revision, blocker=None, finding=None):
        before = copy.deepcopy(contexts)
        result = preflight(**contexts, drawing_bytes=drawing, source_revision=revision)
        self.assertEqual(contexts, before)
        self.assertTrue(result["review_required"])
        self.assertFalse(result["execution_allowed"])
        self.assertNotIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
        self.assertEqual(contexts["process"]["settings"], {})
        self.assertEqual(contexts["material"]["properties"], {})
        if blocker:
            self.assertIn(blocker, result["blockers"], result)
            self.assertEqual(result["status"], "blocked")
        else:
            self.assertEqual(result["blockers"], [], result)
            self.assertEqual(result["status"], "review_required")
        if finding:
            self.assertTrue(any(finding in item for item in result["findings"]), result)
        json.dumps(result, allow_nan=False)
        return result

    def test_two_format_controls_are_partial_nonexecuting_reviews(self):
        for format in ("DXF", "SVG"):
            with self.subTest(format=format):
                result = self.check(*self.control(format))
                self.assertEqual(result["file_review"]["status"], "checked_partial_geometry")
                self.assertEqual(result["file_review"]["dimensions_mm"], {"x": "60", "y": "40"})

    def test_format_labels_cannot_substitute_for_actual_bytes(self):
        for format, wrong in (("DXF", "SVG"), ("SVG", "DXF")):
            contexts, drawing, revision = self.control(format)
            contexts["job"]["format"] = wrong
            result = self.check(contexts, drawing, revision, "MISSING_CONTEXT")
            # Identity still matches: failure must come from parsing semantics.
            self.assertEqual(result["file_review"]["sha256"], contexts["job"]["drawing_sha256"])
            self.assertIsNone(result["file_review"]["geometry"])

    def test_unsafe_and_uncertain_statuses_block_in_either_context(self):
        for owner in ("job", "material"):
            for status in (None, "", "unknown", "unsafe", "prohibited", True, [], {}):
                with self.subTest(owner=owner, status=status):
                    contexts, drawing, revision = self.control()
                    target = contexts["job"] if owner == "job" else contexts["material"]["environmental_requirements"]
                    if status is None:
                        target.pop("unsafe_material_status")
                    else:
                        target["unsafe_material_status"] = status
                    self.check(contexts, drawing, revision, "MISSING_CONTEXT", "material safety status is unresolved or unsafe")

    def test_job_or_material_ventilation_uncertainty_blocks_independently(self):
        for owner in ("job", "material"):
            for status in (None, "", "unknown", True, [], {}):
                with self.subTest(owner=owner, status=status):
                    contexts, drawing, revision = self.control("SVG")
                    target = contexts["job"] if owner == "job" else contexts["material"]["environmental_requirements"]
                    if status is None:
                        target.pop("ventilation_status")
                    else:
                        target["ventilation_status"] = status
                    self.check(contexts, drawing, revision, "MISSING_CONTEXT", "ventilation and fume context is unresolved")

    def test_machine_and_process_compatibility_are_separate_requirements(self):
        for field, blocker, finding in (
            ("machines", "MACHINE_CONTEXT_REQUIRED", "machine/material compatibility is not established"),
            ("process_profiles", "MISSING_CONTEXT", "material/process profile compatibility is not established"),
        ):
            for value in (None, [], ["other"], "fixture-laser-40w", {}):
                with self.subTest(field=field, value=value):
                    contexts, drawing, revision = self.control()
                    contexts["material"]["compatibility"][field] = value
                    result = self.check(contexts, drawing, revision, blocker, finding)
                    self.assertEqual(result["blockers"], [blocker])

    def test_each_unresolved_process_review_flag_blocks_without_guessing_settings(self):
        for owner, key in (("job", "process_profile_status"), ("process", "settings_status")):
            for value in (None, "unknown", "rejected", True):
                with self.subTest(owner=owner, status=value):
                    contexts, drawing, revision = self.control()
                    contexts[owner][key] = value
                    result = self.check(contexts, drawing, revision, "SOURCE_VERIFICATION_REQUIRED")
                    self.assertEqual(result["blockers"], ["SOURCE_VERIFICATION_REQUIRED"])

    def test_cut_intent_and_explicit_placement_cannot_be_inferred_from_geometry(self):
        for key, value, blocker in (("path_intent", None, "MISSING_CONTEXT"),
                                    ("path_intent", "score", "MISSING_CONTEXT"),
                                    ("path_intent", "mark", "MISSING_CONTEXT"),
                                    ("placement_frame", None, "MACHINE_CONTEXT_REQUIRED"),
                                    ("placement_frame", "centered", "MACHINE_CONTEXT_REQUIRED")):
            with self.subTest(field=key, value=value):
                contexts, drawing, revision = self.control()
                contexts["job"][key] = value
                result = self.check(contexts, drawing, revision, blocker)
                self.assertEqual(result["blockers"], [blocker])

    def test_beam_and_emission_findings_remain_distinct_for_both_controls(self):
        for format in ("DXF", "SVG"):
            result = self.check(*self.control(format))
            self.assertIn("beam activation is outside project boundary and requires human control", result["findings"])
            self.assertIn("process-emission risk remains subject to operator review", result["findings"])
            self.assertIn("ventilation has known-status declarations; applicable site evidence still requires review", result["findings"])


if __name__ == "__main__":
    unittest.main()
