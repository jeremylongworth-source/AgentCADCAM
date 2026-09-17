"""Isolate Phase 4 evidence failures from the declared human-approval flag.

These are synthetic utility checks, not authenticated approvals or a composed
additive approval workflow. Retained full skill reviews remain blocked.
"""

import copy
import unittest

from scripts.additive_preflight import preflight
from tests.evaluation.replay_additive_reviews import inputs


class AdditiveGateMatrixTests(unittest.TestCase):
    def check(self, contexts, mesh, revision="A"):
        before = copy.deepcopy(contexts)
        result = preflight(**contexts, mesh_bytes=mesh, source_revision=revision)
        self.assertEqual(contexts, before)
        self.assertTrue(result["review_required"])
        self.assertFalse(result["execution_allowed"])
        self.assertNotIn(result["status"], ("approved", "ready", "manufacturing_ready"))
        return result

    def declared_control(self, case="positive"):
        contexts, mesh, *_ = inputs(case)
        # Satisfy only the legacy utility flag, never create a real approval.
        contexts["job"]["approval_status"] = "approved"
        return contexts, mesh

    def test_both_format_controls_are_partial_review_not_approval(self):
        for case in ("positive", "3mf-positive"):
            with self.subTest(case=case):
                result = self.check(*self.declared_control(case))
                self.assertEqual(result["blockers"], [])
                self.assertEqual(result["status"], "review_required")
                self.assertEqual(result["file_review"]["status"], "checked_partial_geometry")

    def test_all_required_negatives_block_without_missing_human_flag(self):
        cases = {
            "non-manifold-geometry": ("MISSING_CONTEXT", "boundary_edges: 3"),
            "unsupported-material": ("MISSING_CONTEXT", "printer/material compatibility is not established"),
            "missing-material-profile": ("MISSING_CONTEXT", "material profile does not match job"),
            "incompatible-printer-profile": ("MACHINE_CONTEXT_REQUIRED", "printer profile does not match job"),
            "revision-mismatch": ("MISSING_CONTEXT", "source revision is missing or conflicts"),
            "unsupported-build-volume": ("MACHINE_CONTEXT_REQUIRED", "build volume on x"),
            "missing-environment": ("MISSING_CONTEXT", "environmental context is unresolved"),
        }
        for case, (blocker, finding) in cases.items():
            with self.subTest(case=case):
                result = self.check(*self.declared_control(case))
                self.assertEqual(result["status"], "blocked")
                self.assertNotIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
                self.assertIn(blocker, result["blockers"])
                self.assertTrue(any(finding in item for item in result["findings"]))
                # A freshly bound derivative must not mask the actual defect.
                self.assertFalse(any("mesh_sha256 identity" in item for item in result["findings"]))

    def test_3mf_semantic_failures_survive_declared_approval(self):
        for case, blocker, finding in (
            ("3mf-unit-conflict", "MISSING_CONTEXT", "embedded/default unit conflicts"),
            ("3mf-build-placement", "MACHINE_CONTEXT_REQUIRED", "transformed build placement exceeds"),
            ("3mf-required-extension", "SOURCE_VERIFICATION_REQUIRED", "required/recommended extensions"),
        ):
            with self.subTest(case=case):
                result = self.check(*self.declared_control(case))
                self.assertEqual(result["status"], "blocked")
                self.assertNotIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
                self.assertIn(blocker, result["blockers"])
                self.assertTrue(any(finding in item for item in result["findings"]))

    def test_missing_planning_declarations_are_independent_blocks(self):
        for field, finding in (
            ("slicer_profile_status", "slicer profile is not ready"),
            ("orientation_status", "orientation is not ready"),
            ("support_status", "support plan is not ready"),
            ("environment_status", "environmental context is unresolved"),
        ):
            for value in (None, "unknown", [], {}):
                with self.subTest(field=field, value=value):
                    contexts, mesh = self.declared_control()
                    contexts["job"][field] = value
                    result = self.check(contexts, mesh)
                    self.assertEqual(result["blockers"], ["MISSING_CONTEXT"])
                    self.assertIn(finding, result["findings"])

    def test_both_compatibility_directions_are_required(self):
        for profile, container, field, blocker in (
            ("printer", "capabilities", "materials", "MISSING_CONTEXT"),
            ("material", "compatibility", "printers", "MACHINE_CONTEXT_REQUIRED"),
        ):
            for value in (None, [], "fixture-pla", {}):
                with self.subTest(profile=profile, value=value):
                    contexts, mesh = self.declared_control()
                    contexts[profile][container][field] = value
                    self.assertEqual(self.check(contexts, mesh)["blockers"], [blocker])

    def test_revision_and_byte_identity_fail_independently(self):
        for case in ("positive", "3mf-positive"):
            contexts, mesh = self.declared_control(case)
            for revision in (None, "", "B"):
                with self.subTest(case=case, revision=revision):
                    result = self.check(contexts, mesh, revision)
                    self.assertEqual(result["blockers"], ["MISSING_CONTEXT"])
                    self.assertIn("source revision is missing or conflicts with job revision", result["findings"])
            contexts["job"]["mesh_sha256"] = "0" * 64
            result = self.check(contexts, mesh)
            self.assertEqual(result["blockers"], ["SOURCE_VERIFICATION_REQUIRED"])
            self.assertEqual(result["file_review"]["status"], "checked_partial_geometry")

    def test_format_labels_cannot_replace_the_other_formats_bytes(self):
        for case, wrong_format in (("positive", "3MF"), ("3mf-positive", "STL")):
            contexts, mesh = self.declared_control(case)
            contexts["job"]["mesh_format"] = wrong_format
            result = self.check(contexts, mesh)
            self.assertEqual(result["status"], "blocked")
            self.assertIn("MISSING_CONTEXT", result["blockers"])
            self.assertNotIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
            self.assertEqual(result["file_review"]["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
