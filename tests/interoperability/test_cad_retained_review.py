"""Audit the retained synthetic review record, not the quality of model reasoning."""

import copy
import hashlib
import json
import unittest
from pathlib import Path

from scripts.cad_handoff_checks import review_fixture
from scripts.validate_schema_instances import load_catalog, validator_for
from state.state import context_fingerprint


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "docs/evaluation/cad-runs/2026-09-17-manufacturing-intent"


class RetainedCadReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.state = json.loads((PACKET / "state.json").read_text(encoding="utf-8"))
        cls.handoff = json.loads((PACKET / "handoff.json").read_text(encoding="utf-8"))

    def test_retained_state_handoff_and_scoped_source_conform(self):
        validator_for("state.schema.json", self.catalog).validate(self.state)
        validator_for("handoff.schema.json", self.catalog).validate(self.handoff)
        schema_id = self.catalog[0]["handoff.schema.json"]["$id"]
        source_validator = validator_for("handoff.schema.json", self.catalog).evolve(schema={"$ref": schema_id + "#/$defs/source"})
        source_validator.validate(json.loads((PACKET / "source.json").read_text(encoding="utf-8")))

    def test_fingerprint_and_reviewed_context_agree(self):
        self.assertEqual(self.handoff["context_fingerprint"], context_fingerprint(self.state))
        for field in ("job_id", "revision", "process_family", "units"):
            self.assertEqual(self.handoff[field], self.state[field])
        self.assertEqual(self.handoff["verification"], self.state["verification_results"])
        self.assertEqual(self.state["approval_status"], "not_requested")

    def test_actual_artifact_bytes_and_source_roles_are_preserved(self):
        self.assertEqual(len(self.handoff["artifacts"]), 4)
        self.assertEqual(self.state["source_artifact_hashes"], [item["sha256"] for item in self.handoff["artifacts"]])
        for item in self.handoff["artifacts"]:
            with self.subTest(artifact=item["artifact_id"]):
                path = (ROOT / item["path"]).resolve()
                self.assertTrue(path.is_relative_to(ROOT))
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item["sha256"])
                self.assertEqual(item["authority"], "authoritative" if path.suffix == ".scad" else "derived")
                self.assertEqual(item["units"], "mm")

    def test_passing_file_checks_do_not_erase_failed_manufacturing_intent(self):
        portable = review_fixture(ROOT / "fixtures/cad/bracket")
        self.assertEqual(portable["status"], "review_required")
        self.assertEqual(portable["blockers"], [])
        # This is a retained decision, not an automated PMI inference engine.
        self.assertEqual(self.handoff["status"], "blocked")
        self.assertIn("MISSING_CONTEXT", self.handoff["blockers"])
        self.assertIn("HUMAN_APPROVAL_REQUIRED", self.handoff["blockers"])
        findings = {item["check_id"]: item["status"] for item in self.handoff["verification"]}
        self.assertEqual(findings["portable_fixture_checks"], "passed")
        self.assertEqual(findings["native_generator_probe"], "passed")
        self.assertEqual(findings["manufacturing_intent"], "failed")
        self.assertTrue(self.handoff["review_required"])
        self.assertFalse(self.handoff["execution_allowed"])
        self.assertIsNone(self.handoff["approval_id"])

    def test_promoting_retained_blocked_record_to_approved_is_invalid(self):
        value = copy.deepcopy(self.handoff)
        value.update(status="approved", approval_id="synthetic-not-real", blockers=[])
        self.assertFalse(validator_for("handoff.schema.json", self.catalog).is_valid(value))

    def test_removing_review_findings_changes_fingerprint(self):
        value = copy.deepcopy(self.state)
        value["verification_results"] = [item for item in value["verification_results"] if item["check_id"] != "manufacturing_intent"]
        self.assertNotEqual(context_fingerprint(value), self.handoff["context_fingerprint"])

    def test_local_evidence_files_exist_without_fetching_sources(self):
        references = []
        for item in self.handoff["verification"] + self.handoff["assumptions"]:
            references.extend(item["evidence"])
        for reference in references:
            with self.subTest(reference=reference):
                path = (ROOT / reference.split("#", 1)[0]).resolve()
                self.assertTrue(path.is_relative_to(ROOT))
                self.assertTrue(path.is_file())


if __name__ == "__main__":
    unittest.main()
