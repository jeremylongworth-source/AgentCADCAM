"""Retained CNC evidence integrity, not independent scoring of agent reasoning."""

import copy
import hashlib
import json
import unittest

from router.job_router import route_job
from scripts.validate_schema_instances import load_catalog, validator_for
from state.state import context_fingerprint
from tests.evaluation.replay_cnc_reviews import CASES, CNC, ROOT, replay
from tests.evaluation.governance_expectations import add_governance_diagnostics


class CncRetainedReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.runs = {}
        for case in CASES:
            folder = ROOT / f"docs/evaluation/cnc-runs/2026-09-17-{case}"
            cls.runs[case] = {name: json.loads((folder / f"{name}.json").read_text(encoding="utf-8"))
                              for name in ("observed", "state", "handoff")}

    def test_replay_preserves_history_with_only_explicit_new_binding_findings(self):
        for case, run in self.runs.items():
            with self.subTest(case=case):
                # Original packets predate the binding gate and remain immutable.
                # Permit exactly these added diagnostics, not arbitrary drift in
                # identities, static results, route blockers, or prior findings.
                expected = copy.deepcopy(run["observed"])
                findings = expected["route_result"]["findings"]
                position = findings.index("CNC simulation evidence is not verified")
                findings[position:position] = [
                    "CNC verification record 0: structured evidence and versioned context binding are required",
                    "CNC simulation requires a current passed context-bound evidence record",
                    "CNC verification requires a current passed context-bound evidence record",
                ]
                add_governance_diagnostics(expected["route_result"], "cnc")
                self.assertEqual(replay(case), expected)

    def test_packet_schemas_state_and_handoff_agree(self):
        for case, run in self.runs.items():
            with self.subTest(case=case):
                state, handoff, observed = run["state"], run["handoff"], run["observed"]
                validator_for("state.schema.json", self.catalog).validate(state)
                validator_for("handoff.schema.json", self.catalog).validate(handoff)
                self.assertEqual(state, observed["state"])
                self.assertEqual(context_fingerprint(state), handoff["context_fingerprint"])
                self.assertEqual(observed["route_result"]["context_fingerprint"], handoff["context_fingerprint"])
                self.assertEqual(observed["artifacts"], handoff["artifacts"])
                self.assertEqual(state["verification_results"], handoff["verification"])
                self.assertEqual(state["source_artifact_hashes"], [a["sha256"] for a in handoff["artifacts"][:-1]])
                for field in ("job_id", "revision", "units", "process_family"):
                    self.assertEqual(state[field], handoff[field])

    def test_supplied_nc_bytes_and_source_identities_are_bound(self):
        for case, run in self.runs.items():
            with self.subTest(case=case):
                observed, state = run["observed"], run["state"]
                program = observed["program"].encode("utf-8")
                descriptor = state["generated_manufacturing_output"]
                self.assertEqual(hashlib.sha256(program).hexdigest(), descriptor["sha256"])
                self.assertEqual(observed["route_result"]["nc_review"]["sha256"], descriptor["sha256"])
                self.assertEqual(descriptor, observed["artifacts"][-1])
                self.assertEqual(descriptor["path"], f"replay:cnc/{case}/program.nc")
                for artifact in observed["artifacts"][:-1]:
                    self.assertEqual(hashlib.sha256((ROOT / artifact["path"]).read_bytes()).hexdigest(), artifact["sha256"])

    def test_each_named_negative_has_its_specific_observation_and_blocker(self):
        expected = {
            "wrong-units": ("MISSING_CONTEXT", "program units are missing or conflict"),
            "wrong-post": ("SOURCE_VERIFICATION_REQUIRED", "program post identity does not match"),
            "wrong-controller": ("MACHINE_CONTEXT_REQUIRED", "program controller identity does not match"),
            "missing-wcs": ("MISSING_CONTEXT", "required work coordinate system is missing"),
            "unknown-tool": ("MISSING_CONTEXT", "tool references do not reconcile"),
            "revision-mismatch": ("MISSING_CONTEXT", "program revision does not match"),
            "machine-limit-conflict": ("MACHINE_CONTEXT_REQUIRED", "X100 exceeds declared fixture coordinate bound"),
            "incorrect-tool-number": ("MISSING_CONTEXT", "tool references do not reconcile"),
        }
        for case, (blocker, finding) in expected.items():
            with self.subTest(case=case):
                report = self.runs[case]["observed"]["raw_fixture_report"]
                self.assertIn(blocker, report["blockers"])
                self.assertTrue(any(finding in text for text in report["findings"]))
                self.assertIn(blocker, self.runs[case]["handoff"]["blockers"])

    def test_no_review_or_availability_is_promoted_for_replay(self):
        for case, run in self.runs.items():
            with self.subTest(case=case):
                state = run["state"]
                profiles = [state[key] for key in ("machine_profile", "controller_profile", "material", "postprocessor")]
                profiles += state["tool_library"]["tools"] + [state["setup"]["coordinate_model"]]
                for profile in profiles:
                    self.assertEqual(profile["lifecycle"]["verification"]["status"], "unverified")
                    self.assertIsNone(profile["lifecycle"]["verification"]["reviewer"])
                self.assertEqual(state["tool_library"]["tools"][0]["availability"], "fixture-only")
                self.assertEqual(state["setup"]["wcs_status"], "defined")
                self.assertIsNone(state["setup"]["workholding"]["clamps_clear"])
                self.assertEqual(state["approval_status"], "not_requested")
                self.assertEqual(state["simulation_status"], "not_run")

    def test_positive_control_and_prerequisite_stops_are_not_overclaimed(self):
        positive = self.runs["positive"]["observed"]["raw_fixture_report"]
        self.assertEqual(positive["blockers"], ["HUMAN_APPROVAL_REQUIRED", "SIMULATION_REQUIRED"])
        for run in self.runs.values():
            observed = run["observed"]
            coordinate = observed["coordinate_report"]["coordinate_review"]
            self.assertEqual(coordinate["status"], "not_run")
            self.assertEqual(coordinate["targets"], [])
            self.assertEqual(coordinate["blockers"], ["SOURCE_VERIFICATION_REQUIRED"])
            self.assertIsNone(observed["raw_fixture_report"]["coordinate_review"])
            self.assertEqual(observed["route_result"]["nc_review"]["status"], "not_run")
            self.assertIsNone(observed["route_result"]["nc_review"]["report"])
            self.assertEqual(observed["route_result"]["validation_errors"], [])

    def test_all_handoffs_are_blocked_and_preserve_all_software_blockers(self):
        for case, run in self.runs.items():
            with self.subTest(case=case):
                handoff = run["handoff"]
                self.assertEqual(handoff["status"], "blocked")
                self.assertTrue(handoff["review_required"])
                self.assertFalse(handoff["execution_allowed"])
                self.assertIsNone(handoff["approval_id"])
                for field in ("raw_fixture_report", "coordinate_report", "route_result"):
                    self.assertTrue(set(run["observed"][field]["blockers"]).issubset(handoff["blockers"]))
                promoted = copy.deepcopy(handoff)
                promoted.update(status="approved", blockers=[], approval_id="not-a-real-review")
                self.assertFalse(validator_for("handoff.schema.json", self.catalog).is_valid(promoted))

    def test_conflicting_revision_and_unit_claims_are_retained(self):
        revision = self.runs["revision-mismatch"]
        self.assertIn("( REVISION: C )", revision["observed"]["program"])
        self.assertEqual(revision["state"]["revision"], "B")
        self.assertEqual(revision["handoff"]["artifacts"][0]["revision"], "A")
        units = self.runs["wrong-units"]
        self.assertIn("G20", units["observed"]["program"])
        self.assertIn("( UNITS: mm )", units["observed"]["program"])
        self.assertEqual(units["handoff"]["units"], "mm")

    def test_seven_outputs_are_retained_for_every_case(self):
        skills = ("machine-capability-match", "cnc-setup-planner", "tooling-plan-review", "toolpath-strategy-planner",
                  "postprocessor-readiness-review", "nc-static-safety-review", "simulation-readiness-review")
        for case in CASES:
            review = (ROOT / f"docs/evaluation/cnc-runs/2026-09-17-{case}/review.md").read_text(encoding="utf-8")
            for number, skill in enumerate(skills, 1):
                self.assertIn(f"## {number}. {skill}", review)
            self.assertIn("REVIEW_REQUIRED", review)

    def test_replay_preserves_checked_in_fixture_bytes(self):
        before = {str(p.relative_to(CNC)): p.read_bytes() for p in CNC.rglob("*") if p.is_file()}
        for case in CASES:
            replay(case)
        after = {str(p.relative_to(CNC)): p.read_bytes() for p in CNC.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_unknown_case_cannot_select_an_arbitrary_path(self):
        with self.assertRaises(ValueError):
            replay("../../external-job")

    def test_changed_program_cannot_reuse_retained_artifact_identity(self):
        run = self.runs["positive"]
        program = run["observed"]["program"].replace("X60 Y0", "X100 Y0").encode("utf-8")
        result = route_job(run["observed"]["request"], run["state"], nc_program=program)
        self.assertIn("SOURCE_VERIFICATION_REQUIRED", result["nc_review"]["blockers"])
        self.assertTrue(any("SHA-256" in text for text in result["nc_review"]["findings"]))
        self.assertFalse(result["execution_allowed"])
        self.assertEqual(result["approval_state"], "not_requested")


if __name__ == "__main__":
    unittest.main()
