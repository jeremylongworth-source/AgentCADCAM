from __future__ import annotations

import tempfile
import unittest
import json
from pathlib import Path

import yaml

from scripts.evaluate_pilot_gate import aggregate
from scripts.validate_pilot_packet import REQUIRED_DIRS, validate


def _write_packet(root: Path, name: str, family: str, **overrides: object) -> None:
    # Fabricated unit-test data exercises the evaluator contract, never the real pilot gate.
    packet_root = root / name
    for directory in REQUIRED_DIRS:
        (packet_root / directory).mkdir(parents=True)
        if directory != "final-verdict":
            (packet_root / directory / "evidence.txt").write_text("Synthetic test evidence only.", encoding="utf-8")
    packet = packet_root / "final-verdict"
    verdict = {
        "packet_status": "completed",
        "workflow_family": family,
        "participant_role": "qualified reviewer",
        "qualified_reviewer": True,
        "reviewer_id": "test-reviewer",
        "reviewer_experience": "Synthetic test qualification declaration",
        "input_origin": "sanitized_real",
        "consent_recorded": True,
        "sanitized": True,
        "schema_valid": True,
        "router_correct": True,
        "revision_provenance_detected": True,
        "interoperability_recommendation_accurate": True,
        "handoff_complete": True,
        "critical_safety_cases": 2,
        "critical_safety_cases_detected": 2,
        "machine_post_mismatch_detected": True if family == "cnc_milling" else None,
        "safety_regulatory_claims": 2,
        "authoritatively_sourced_claims": 2,
        "false_ready_decision": False,
        "usable_with_minor_or_no_edits": True,
        "reviewer_edit_burden": {"baseline_count": 10, "skill_count": 5},
        "unsupported_assumption_count": 0,
        "unsupported_assumption_opportunities": 10,
        "usefulness_rating": 5,
        "safety_findings": [],
        "required_edits": [],
        "verdict": "proceed",
        "evidence": {directory: [f"{directory}/evidence.txt"] for directory in REQUIRED_DIRS[:-1]},
    }
    verdict.update(overrides)
    (packet / "final-verdict.yaml").write_text(yaml.safe_dump(verdict, sort_keys=False), encoding="utf-8")


class PilotGateTests(unittest.TestCase):
    def test_empty_root_cannot_claim_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            report = aggregate(Path(directory))
        self.assertEqual(report["status"], "not_ready")
        self.assertIn("no completed pilot packets found", report["blockers"])

    def test_all_workflows_and_targets_can_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, family in enumerate(("cad_handoff", "cnc_milling", "additive", "laser_cutting")):
                _write_packet(root, f"packet-{index}", family)
            report = aggregate(root)
        self.assertEqual(report["status"], "thresholds_met")
        self.assertFalse(report["gate_awarded"])
        self.assertEqual(report["packet_count"], 4)
        self.assertEqual(report["metrics"]["reviewer_edit_burden"]["reduction"], 0.5)

    def test_failed_safety_case_blocks_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, family in enumerate(("cad_handoff", "cnc_milling", "additive", "laser_cutting")):
                _write_packet(root, f"packet-{index}", family, critical_safety_cases_detected=1 if index == 0 else 2)
            report = aggregate(root)
        self.assertEqual(report["status"], "not_ready")
        self.assertTrue(any("critical safety detection" in item for item in report["blockers"]))

    def report_with(self, **overrides):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, family in enumerate(("cad_handoff", "cnc_milling", "additive", "laser_cutting")):
                _write_packet(root, f"packet-{index}", family, **overrides)
            return aggregate(root)

    def test_unsourced_claim_blocks_mandatory_target(self):
        report = self.report_with(authoritatively_sourced_claims=1)
        self.assertEqual(report["status"], "not_ready")
        self.assertEqual(report["metrics"]["authoritative_sourcing"]["rate"], 0.5)
        self.assertTrue(any("authoritative sourcing" in item for item in report["blockers"]))

    def test_unsupported_rate_reports_failures_and_strict_boundary(self):
        for count, status in ((1, "thresholds_met"), (2, "not_ready")):
            with self.subTest(count=count):
                report = self.report_with(unsupported_assumption_count=count, unsupported_assumption_opportunities=100)
                self.assertEqual(report["status"], status)
                self.assertEqual(report["metrics"]["unsupported_assumption_rate"]["rate"], count / 100)

    def test_edit_reduction_boundary_is_inclusive(self):
        for edits, status in ((7, "thresholds_met"), (8, "not_ready")):
            with self.subTest(edits=edits):
                report = self.report_with(reviewer_edit_burden={"baseline_count": 10, "skill_count": edits})
                self.assertEqual(report["status"], status)

    def test_zero_denominators_are_json_safe_and_do_not_imply_detection(self):
        report = self.report_with(
            unsupported_assumption_opportunities=0,
            critical_safety_cases=0, critical_safety_cases_detected=0,
            safety_regulatory_claims=0, authoritatively_sourced_claims=0,
            reviewer_edit_burden={"baseline_count": 0, "skill_count": 0},
        )
        json.dumps(report, allow_nan=False)
        self.assertEqual(report["status"], "not_ready")
        self.assertIsNone(report["metrics"]["critical_safety_detection"]["rate"])

    def test_invalid_packets_fail_closed(self):
        for overrides in (
            {"input_origin": "synthetic"}, {"consent_recorded": False},
            {"sanitized": False}, {"qualified_reviewer": False},
            {"packet_status": "template"}, {"packet_status": "unknown"},
            {"workflow_family": []}, {"verdict": {}},
            {"router_correct": "true"}, {"reviewer_id": ""},
            {"safety_regulatory_claims": True},
            {"authoritatively_sourced_claims": 3}, {"evidence": {}},
            {"critical_safety_cases_detected": -1}, {"required_edits": None},
        ):
            with self.subTest(overrides=overrides):
                report = self.report_with(**overrides)
                self.assertEqual(report["status"], "not_ready")
                self.assertEqual(report["packet_count"], 0)

    def test_negative_reviewer_and_measure_results_block_readiness(self):
        for overrides in (
            {"verdict": "stop"}, {"verdict": "revise"},
            {"false_ready_decision": True}, {"schema_valid": False},
            {"router_correct": False}, {"handoff_complete": False},
            {"revision_provenance_detected": False},
            {"interoperability_recommendation_accurate": False},
            {"usable_with_minor_or_no_edits": False},
            {"machine_post_mismatch_detected": False},
        ):
            with self.subTest(overrides=overrides):
                self.assertEqual(self.report_with(**overrides)["status"], "not_ready")

    def test_missing_verdict_directory_is_reported_not_silently_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "incomplete-packet").mkdir()
            report = aggregate(root)
        self.assertTrue(any("incomplete-packet" in item for item in report["blockers"]))

    def test_evidence_must_be_nonempty_and_confined(self):
        for ref in ("../outside.txt", "final-verdict/final-verdict.yaml", "input/missing.txt"):
            with tempfile.TemporaryDirectory() as directory, self.subTest(ref=ref):
                root = Path(directory)
                _write_packet(root, "packet", "cad_handoff", evidence={"input": [ref]})
                self.assertTrue(any("invalid evidence" in error for error in validate(root / "packet")))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_packet(root, "packet", "cad_handoff")
            (root / "packet/input/evidence.txt").write_text("", encoding="utf-8")
            self.assertTrue(any("empty" in error for error in validate(root / "packet")))


if __name__ == "__main__":
    unittest.main()
