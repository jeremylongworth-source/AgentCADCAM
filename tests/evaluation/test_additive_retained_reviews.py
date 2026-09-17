"""Packet integrity and known-case evidence, not automated grading of reasoning."""

import copy
import json
import unittest

from scripts.validate_schema_instances import instance_paths, load_catalog, validator_for
from state.state import context_fingerprint, invalidate_approval
from tests.evaluation.replay_additive_reviews import CASES, FIXTURE, ROOT, TETRA, inputs, replay, sha256, tetrahedron_mesh
from tests.safety.test_three_mf_review import MESH


class AdditiveRetainedReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.runs = {}
        for case in CASES:
            folder = ROOT / f"docs/evaluation/additive-runs/2026-09-17-{case}"
            cls.runs[case] = {name: json.loads((folder / f"{name}.json").read_text(encoding="utf-8"))
                              for name in ("observed", "state", "handoff")}

    def test_replay_preserves_history_with_only_explicit_new_additive_gate_diagnostics(self):
        for case, run in self.runs.items():
            with self.subTest(case=case):
                # Evaluation wrappers are not typed preflight contexts. Preserve
                # historical packets; permit only the new gate's exact findings.
                expected = copy.deepcopy(run["observed"])
                route = expected["route_result"]
                additions = ["additive setup.additive_preflight requires structured job, versioned slicer settings/source and source artifact"]
                if case in ("revision-mismatch", "3mf-unit-conflict"):
                    additions.append("additive artifact kind, authority, revision or units conflict with bounded state")
                additions += [
                    "actual nonempty additive mesh/package bytes are required; paths and passing labels are insufficient",
                    "additive verification record 0: structured evidence and versioned context binding are required",
                    *[f"{identity}: a current passed context-bound evidence record is required" for identity in
                      ("additive_design", "additive_geometry", "additive_orientation", "additive_supports",
                       "additive_slicer", "additive_environment", "additive_output")],
                ]
                route["additive_review"] = {"status": "blocked", "sha256": None,
                                            "context_fingerprint": route["context_fingerprint"],
                                            "blockers": ["MISSING_CONTEXT"], "findings": additions, "report": None}
                position = route["findings"].index("verification evidence is missing, unresolved, or failed")
                route["findings"][position:position] = additions
                self.assertEqual(replay(case), expected)

    def test_state_handoff_schemas_and_all_input_bindings_agree(self):
        for case, run in self.runs.items():
            with self.subTest(case=case):
                observed, state, handoff = (run[name] for name in ("observed", "state", "handoff"))
                validator_for("state.schema.json", self.catalog).validate(state)
                validator_for("handoff.schema.json", self.catalog).validate(handoff)
                self.assertEqual(state, observed["state"])
                self.assertEqual(handoff["context_fingerprint"], context_fingerprint(state))
                self.assertEqual(observed["route_result"]["context_fingerprint"], handoff["context_fingerprint"])
                self.assertEqual(observed["route_result"]["validation_errors"], [])
                self.assertNotIn("artifact class is not valid for the selected process family", observed["route_result"]["findings"])
                self.assertEqual(state["verification_results"], handoff["verification"])
                self.assertEqual(observed["artifacts"], handoff["artifacts"])
                self.assertEqual(state["generated_manufacturing_output"], handoff["artifacts"][-1])
                self.assertEqual(state["source_artifact_hashes"], [handoff["artifacts"][0]["sha256"]])
                self.assertEqual(state["setup"]["submitted_job"], observed["contexts"]["job"])
                self.assertEqual(state["setup"]["source_revision"], observed["source_revision"])
                for field in ("job_id", "revision", "units", "process_family"):
                    self.assertEqual(state[field], handoff[field])

    def test_actual_source_and_derivative_bytes_are_bound(self):
        for case, run in self.runs.items():
            with self.subTest(case=case):
                contexts, mesh, source, derivative, _ = inputs(case)
                self.assertEqual(sha256((ROOT / source["path"]).read_bytes()), source["sha256"])
                self.assertEqual(sha256(mesh), derivative["sha256"])
                self.assertEqual(sha256(mesh), contexts["job"]["mesh_sha256"])
                self.assertEqual(sha256(mesh), run["observed"]["raw_preflight"]["file_review"]["sha256"])
                self.assertEqual([source, derivative], run["handoff"]["artifacts"])

    def test_named_negatives_have_specific_file_or_context_findings(self):
        expected = {
            "non-manifold-geometry": ("MISSING_CONTEXT", "boundary_edges: 3"),
            "unsupported-material": ("MISSING_CONTEXT", "printer/material compatibility is not established"),
            "missing-material-profile": ("MISSING_CONTEXT", "material profile does not match job"),
            "incompatible-printer-profile": ("MACHINE_CONTEXT_REQUIRED", "printer profile does not match job"),
            "revision-mismatch": ("MISSING_CONTEXT", "source revision is missing or conflicts"),
            "unsupported-build-volume": ("MACHINE_CONTEXT_REQUIRED", "build volume on x"),
            "missing-environment": ("MISSING_CONTEXT", "environmental context is unresolved"),
            "3mf-unit-conflict": ("MISSING_CONTEXT", "embedded/default unit conflicts"),
            "3mf-build-placement": ("MACHINE_CONTEXT_REQUIRED", "transformed build placement exceeds"),
            "3mf-required-extension": ("SOURCE_VERIFICATION_REQUIRED", "required/recommended extensions"),
        }
        for case, (blocker, finding) in expected.items():
            with self.subTest(case=case):
                raw = self.runs[case]["observed"]["raw_preflight"]
                self.assertIn(blocker, raw["blockers"])
                self.assertTrue(any(finding in item for item in raw["findings"]))
                self.assertIn(blocker, self.runs[case]["handoff"]["blockers"])

    def test_positive_geometry_controls_do_not_suppress_full_review_gaps(self):
        for case in ("positive", "3mf-positive"):
            run = self.runs[case]
            self.assertEqual(run["observed"]["raw_preflight"]["blockers"], ["HUMAN_APPROVAL_REQUIRED"])
            self.assertEqual(run["handoff"]["blockers"], ["HUMAN_APPROVAL_REQUIRED", "MISSING_CONTEXT", "SOURCE_VERIFICATION_REQUIRED"])
            self.assertEqual(run["handoff"]["verification"][0]["status"], "inconclusive")
            self.assertTrue(all(item["status"] == "unresolved" for item in run["handoff"]["assumptions"]))

    def test_actual_open_mesh_remains_valid_labeled_and_newly_identified(self):
        baseline = self.runs["positive"]["observed"]
        changed = self.runs["non-manifold-geometry"]["observed"]
        self.assertEqual(changed["contexts"]["job"]["mesh_status"], "valid")
        self.assertNotEqual(changed["artifacts"][-1]["sha256"], baseline["artifacts"][-1]["sha256"])
        self.assertEqual(changed["raw_preflight"]["file_review"]["topology"]["boundary_edges"], 3)
        self.assertEqual(changed["raw_preflight"]["file_review"]["topology"]["nonmanifold_vertices"], 3)
        self.assertEqual(changed["raw_preflight"]["file_review"]["dimensions_exact"], baseline["raw_preflight"]["file_review"]["dimensions_exact"])

    def test_revision_unit_and_material_conflicts_are_preserved(self):
        mismatch = self.runs["revision-mismatch"]
        self.assertEqual(mismatch["state"]["revision"], "B")
        self.assertTrue(all(a["revision"] == "A" for a in mismatch["handoff"]["artifacts"]))
        units = self.runs["3mf-unit-conflict"]
        self.assertEqual(units["state"]["units"], "mm")
        self.assertEqual(units["handoff"]["artifacts"][-1]["units"], "inch")
        self.assertEqual(units["observed"]["raw_preflight"]["file_review"]["unit"], "inch")
        missing = self.runs["missing-material-profile"]
        self.assertIsNone(missing["state"]["setup"]["submitted_job"]["material_id"])
        self.assertEqual(missing["state"]["material"]["material_id"], "fixture-pla")

    def test_no_profile_parameter_or_approval_is_promoted(self):
        for run in self.runs.values():
            state, handoff = run["state"], run["handoff"]
            for field in ("machine_profile", "material"):
                self.assertEqual(state[field]["lifecycle"]["verification"]["status"], "unverified")
                self.assertIsNone(state[field]["lifecycle"]["verification"]["reviewer"])
                self.assertEqual(state[field]["lifecycle"]["verification"]["evidence"], [])
            self.assertEqual(state["material"]["properties"], {})
            self.assertEqual(state["approval_status"], "not_requested")
            self.assertEqual(state["simulation_status"], "not_run")
            self.assertEqual(handoff["status"], "blocked")
            self.assertTrue(handoff["review_required"])
            self.assertFalse(handoff["execution_allowed"])
            self.assertIsNone(handoff["approval_id"])
            for field in ("raw_preflight", "route_result"):
                self.assertTrue(set(run["observed"][field]["blockers"]).issubset(handoff["blockers"]))
            promoted = copy.deepcopy(handoff)
            promoted.update(status="approved", blockers=[], approval_id="fake-review")
            self.assertFalse(validator_for("handoff.schema.json", self.catalog).is_valid(promoted))

    def test_submitted_job_claim_changes_invalidate_the_evaluation_fingerprint(self):
        state = self.runs["positive"]["state"]
        approval = {"status": "approved", "context_fingerprint": context_fingerprint(state)}
        for key, value in (("mesh_units", "inch"), ("mesh_format", "3MF"), ("printer_id", "other"),
                           ("material_id", None), ("slicer_profile_status", "unknown"),
                           ("orientation_status", "unknown"), ("support_status", "unknown"),
                           ("environment_status", "unknown"), ("model_dimensions", {"x": 1, "y": 1, "z": 1})):
            with self.subTest(field=key):
                changed = copy.deepcopy(state)
                changed["setup"]["submitted_job"][key] = value
                self.assertNotEqual(context_fingerprint(changed), approval["context_fingerprint"])
                result = invalidate_approval(state, changed, approval)
                self.assertEqual(result["status"], "invalidated")
                self.assertEqual(result["changed_fields"], ["setup"])
                self.assertEqual(result["context_fingerprint"], approval["context_fingerprint"])
        self.assertEqual(approval["status"], "approved")  # Synthetic original copy is not overwritten.

    def test_changed_derivative_hash_cannot_reuse_retained_context_identity(self):
        state = self.runs["positive"]["state"]
        changed = copy.deepcopy(state)
        changed["generated_manufacturing_output"]["sha256"] = "0" * 64
        self.assertNotEqual(context_fingerprint(state), context_fingerprint(changed))

    def test_explicit_tetrahedron_source_reproduces_prior_reference_geometry(self):
        source = json.loads(TETRA.read_text(encoding="utf-8"))
        self.assertEqual(tetrahedron_mesh(source), MESH)
        self.assertEqual(source["units"], "mm")
        self.assertEqual(source["revision"], "A")
        self.assertEqual(source["license"], "CC0-1.0 synthetic fixture")

    def test_additive_packets_are_in_repository_schema_validation(self):
        selected = {path.relative_to(ROOT).as_posix(): schema for path, schema in instance_paths()}
        for case in CASES:
            for name in ("state", "handoff"):
                self.assertEqual(selected[f"docs/evaluation/additive-runs/2026-09-17-{case}/{name}.json"], f"{name}.schema.json")

    def test_full_contract_sections_are_retained_without_claiming_reasoning_score(self):
        headings = ("Artifact and provenance", "Mesh, units and build volume", "Printer, material and slicer",
                    "Orientation and supports", "Environment and operator context", "Blockers and reviewer action", "Evidence and limits")
        for case in CASES:
            review = (ROOT / f"docs/evaluation/additive-runs/2026-09-17-{case}/review.md").read_text(encoding="utf-8")
            for heading in headings:
                self.assertIn(f"## {heading}", review)
            self.assertIn("REVIEW_REQUIRED", review)
            self.assertIn("additive-job-preflight", review)

    def test_replay_does_not_rewrite_fixtures_or_allow_arbitrary_input_paths(self):
        before = {p.relative_to(FIXTURE): p.read_bytes() for p in FIXTURE.rglob("*") if p.is_file()}
        replay("non-manifold-geometry")
        replay("3mf-unit-conflict")
        after = {p.relative_to(FIXTURE): p.read_bytes() for p in FIXTURE.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        with self.assertRaises(ValueError):
            replay("../../external-job")


if __name__ == "__main__":
    unittest.main()
