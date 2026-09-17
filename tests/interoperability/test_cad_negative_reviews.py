"""Audit actual replay evidence and retained decisions, not agent reasoning quality."""

import copy
import json
import unittest

from scripts.cad_handoff_checks import review_fixture
from scripts.validate_schema_instances import load_catalog, validator_for
from state.state import context_fingerprint
from tests.interoperability.replay_cad_negative_cases import CASES, FIXTURE, ROOT, replay


class CadNegativeReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.runs = {}
        for case in CASES:
            folder = ROOT / f"docs/evaluation/cad-runs/2026-09-17-{case}"
            cls.runs[case] = {name: json.loads((folder / f"{name}.json").read_text(encoding="utf-8"))
                              for name in ("observed", "state", "handoff")}

    def test_replayed_inputs_and_tool_findings_match_retained_observations(self):
        for case, run in self.runs.items():
            with self.subTest(case=case):
                self.assertEqual(replay(case), run["observed"])

    def test_replay_does_not_change_positive_fixture(self):
        before = {str(p.relative_to(FIXTURE)): p.read_bytes() for p in FIXTURE.rglob("*") if p.is_file()}
        for case in CASES:
            replay(case)
        after = {str(p.relative_to(FIXTURE)): p.read_bytes() for p in FIXTURE.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(review_fixture(FIXTURE)["blockers"], [])

    def test_unknown_case_is_rejected_before_any_copy(self):
        with self.assertRaises(ValueError):
            replay("../arbitrary-input")

    def test_all_retained_states_and_handoffs_conform_and_agree(self):
        for case, run in self.runs.items():
            with self.subTest(case=case):
                state, handoff = run["state"], run["handoff"]
                validator_for("state.schema.json", self.catalog).validate(state)
                validator_for("handoff.schema.json", self.catalog).validate(handoff)
                self.assertEqual(context_fingerprint(state), handoff["context_fingerprint"])
                for field in ("job_id", "revision", "units", "process_family"):
                    self.assertEqual(state[field], handoff[field])
                self.assertEqual(state["verification_results"], handoff["verification"])
                self.assertEqual(state["source_artifact_hashes"], [a["sha256"] for a in handoff["artifacts"]])

    def test_handoff_preserves_observed_identities_without_mesh_promotion(self):
        for case, run in self.runs.items():
            with self.subTest(case=case):
                supplied, output = run["observed"]["inventory"], run["handoff"]["artifacts"]
                self.assertEqual(len(supplied), len(output))
                for original, reviewed in zip(supplied, output):
                    self.assertEqual(original["locator"], reviewed["path"])
                    for field in ("kind", "sha256", "revision", "units"):
                        self.assertEqual(original[field], reviewed[field])
                    authority = "unknown" if case == "stl-treated-as-design-master" else original["authority"]
                    self.assertEqual(reviewed["authority"], authority)

    def test_missing_units_and_conflicting_revision_are_not_silently_resolved(self):
        missing = self.runs["missing-units"]["handoff"]
        self.assertIsNone(missing["units"])
        self.assertIsNone(next(a for a in missing["artifacts"] if a["kind"] == "mesh_derivative")["units"])
        revision = self.runs["revision-mismatch"]["handoff"]
        self.assertEqual(revision["revision"], "A")
        self.assertEqual(next(a for a in revision["artifacts"] if a["kind"] == "drawing_reference")["revision"], "B")

    def test_every_negative_stays_blocked_and_cannot_be_promoted(self):
        for case, run in self.runs.items():
            with self.subTest(case=case):
                handoff = run["handoff"]
                self.assertEqual(run["observed"]["tool_result"]["status"], "blocked")
                self.assertEqual(handoff["status"], "blocked")
                self.assertTrue(handoff["review_required"])
                self.assertFalse(handoff["execution_allowed"])
                self.assertIsNone(handoff["approval_id"])
                self.assertTrue(set(run["observed"]["tool_result"]["blockers"]).issubset(handoff["blockers"]))
                value = copy.deepcopy(handoff)
                value.update(status="approved", blockers=[], approval_id="synthetic-not-real")
                self.assertFalse(validator_for("handoff.schema.json", self.catalog).is_valid(value))


if __name__ == "__main__":
    unittest.main()
