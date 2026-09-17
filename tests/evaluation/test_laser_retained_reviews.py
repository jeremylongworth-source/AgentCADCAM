"""Known-case packet integrity, not automatic grading or manufacturing approval."""

import copy
import json
import unittest
from unittest.mock import patch

from scripts.laser_preflight import preflight
from scripts.validate_schema_instances import instance_paths, load_catalog, validator_for
from state.state import context_fingerprint, invalidate_approval
from tests.evaluation import replay_laser_reviews as reviews
from tests.evaluation.replay_laser_reviews import CASES, FILE_CASES, FIXTURE, ROOT, inputs, replay, sha256


class LaserRetainedReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.runs = {}
        for case in CASES:
            folder = ROOT / f"docs/evaluation/laser-runs/2026-09-17-{case}"
            cls.runs[case] = {name: json.loads((folder / f"{name}.json").read_text(encoding="utf-8"))
                              for name in ("observed", "state", "handoff")}

    def test_replay_preserves_history_with_only_explicit_new_laser_gate_diagnostics(self):
        self.assertEqual(len(self.runs), 16)
        for case, run in self.runs.items():
            with self.subTest(case=case):
                # Original evaluation wrappers are not production preflight
                # contexts. Preserve their packets; allow exactly this new gate
                # output, never arbitrary drift in bytes, state or raw checks.
                expected = copy.deepcopy(run["observed"])
                route = expected["route_result"]
                additions = ["laser setup.laser_preflight requires structured job, nonempty process settings/source and source artifact"]
                if case in ("wrong-units", "svg-wrong-units"):
                    additions.append("laser drawing kind, authority, revision or units conflict with bounded state")
                additions += [
                    "actual nonempty laser drawing bytes are required; paths and passing labels are insufficient",
                    "laser verification record 0: structured evidence and versioned context binding are required",
                    *[f"{identity}: a current passed context-bound evidence record is required" for identity in
                      ("laser_design", "laser_paths", "laser_process", "laser_beam", "laser_emissions", "laser_output")],
                ]
                route["laser_review"] = {"status": "blocked", "sha256": None,
                                         "context_fingerprint": route["context_fingerprint"],
                                         "blockers": ["MISSING_CONTEXT"], "findings": additions, "report": None}
                position = route["findings"].index("verification evidence is missing, unresolved, or failed")
                route["findings"][position:position] = additions
                self.assertEqual(replay(case), expected)

    def test_schemas_and_all_input_bindings_agree(self):
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
                self.assertEqual(state["source_artifact_hashes"], [a["sha256"] for a in handoff["artifacts"][:2]])
                self.assertEqual(state["setup"]["submitted_job"], observed["contexts"]["job"])
                self.assertEqual(state["setup"]["submitted_process"], observed["contexts"]["process"])
                self.assertEqual(state["setup"]["source_revision"], observed["source_revision"])
                for field in ("job_id", "revision", "units", "process_family"):
                    self.assertEqual(state[field], handoff[field])

    def test_original_inventory_source_and_derivative_hashes_match_actual_bytes(self):
        for case, run in self.runs.items():
            with self.subTest(case=case):
                contexts, drawing, artifacts, _ = inputs(case)
                for artifact in artifacts[:2]:
                    self.assertEqual(sha256((ROOT / artifact["path"]).read_bytes()), artifact["sha256"])
                self.assertEqual(sha256(drawing), artifacts[-1]["sha256"])
                self.assertEqual(sha256(drawing), contexts["job"]["drawing_sha256"])
                self.assertEqual(sha256(drawing), run["observed"]["raw_preflight"]["file_review"]["sha256"])
                self.assertEqual(artifacts, run["handoff"]["artifacts"])

    def test_named_negatives_are_specific_and_independent_of_missing_approval(self):
        expected = {
            "duplicate-contours": ("MISSING_CONTEXT", "duplicate_circles: 1"),
            "open-contours": ("MISSING_CONTEXT", "open_contours: 1"),
            "unsupported-entity": ("SOURCE_VERIFICATION_REQUIRED", "unsupported entity or attribute"),
            "wrong-units": ("MISSING_CONTEXT", "unit declaration conflicts"),
            "scale-mismatch": ("MISSING_CONTEXT", "physical dimension conflicts"),
            "unknown-material": ("MISSING_CONTEXT", "material identity is unknown"),
            "prohibited-unsafe-material": ("MISSING_CONTEXT", "material safety status is unresolved or unsafe"),
            "missing-ventilation": ("MISSING_CONTEXT", "ventilation and fume context is unresolved"),
            "machine-material-incompatibility": ("MACHINE_CONTEXT_REQUIRED", "machine/material compatibility is not established"),
            "svg-duplicate-contours": ("MISSING_CONTEXT", "duplicate_circles: 1"),
            "svg-open-contours": ("MISSING_CONTEXT", "open_contours: 1"),
            "svg-unsupported-entity": ("SOURCE_VERIFICATION_REQUIRED", "curved/unsupported path commands"),
            "svg-wrong-units": ("MACHINE_CONTEXT_REQUIRED", "placement exceeds declared zero-origin working area on x"),
            "svg-scale-mismatch": ("MISSING_CONTEXT", "physical dimension conflicts"),
        }
        for case, (blocker, finding) in expected.items():
            with self.subTest(case=case):
                run = self.runs[case]
                contexts, drawing, artifacts, _ = inputs(case)
                contexts["job"]["approval_status"] = "approved"  # Isolate, not authenticate, the other blockers.
                isolated = preflight(**contexts, drawing_bytes=drawing, source_revision=artifacts[1]["revision"])
                self.assertNotIn("HUMAN_APPROVAL_REQUIRED", isolated["blockers"])
                for result in (run["observed"]["raw_preflight"], isolated):
                    self.assertIn(blocker, result["blockers"])
                    self.assertTrue(any(finding in item for item in result["findings"]))
                    self.assertEqual(result["status"], "blocked")
                    self.assertFalse(result["execution_allowed"])
                self.assertIn(blocker, run["handoff"]["blockers"])

    def test_positive_geometry_does_not_suppress_full_review_gaps(self):
        for case in ("positive", "svg-positive"):
            run = self.runs[case]
            self.assertEqual(run["observed"]["raw_preflight"]["blockers"], ["HUMAN_APPROVAL_REQUIRED"])
            self.assertEqual(run["observed"]["raw_preflight"]["file_review"]["dimensions_mm"], {"x": "60", "y": "40"})
            self.assertEqual(run["handoff"]["blockers"], ["HUMAN_APPROVAL_REQUIRED", "MISSING_CONTEXT", "SOURCE_VERIFICATION_REQUIRED"])
            self.assertEqual(run["handoff"]["verification"][0]["status"], "inconclusive")
            self.assertTrue(all(item["status"] == "unresolved" for item in run["handoff"]["assumptions"]))

    def test_altered_files_keep_optimistic_labels_but_bind_new_test_hashes(self):
        for prefix in ("", "svg-"):
            baseline = self.runs[prefix + "positive"]["observed"]
            for case in FILE_CASES:
                with self.subTest(case=prefix + case):
                    observed = self.runs[prefix + case]["observed"]
                    job = observed["contexts"]["job"]
                    for key in ("geometry_status", "scale_status", "duplicate_geometry", "open_contours", "unsupported_entities", "model_dimensions"):
                        self.assertEqual(job[key], baseline["contexts"]["job"][key])
                    self.assertNotEqual(observed["artifacts"][-1]["sha256"], baseline["artifacts"][-1]["sha256"])
                    self.assertEqual(observed["artifacts"][:2], baseline["artifacts"][:2])

    def test_mixed_svg_units_preserve_dimensions_but_change_placement(self):
        run = self.runs["svg-wrong-units"]
        drawing = run["observed"]["raw_preflight"]["file_review"]
        self.assertEqual(drawing["dimensions_mm"], {"x": "60", "y": "40"})
        self.assertEqual(drawing["bounds_mm"], {"min": ["859", "5"], "max": ["919", "45"]})
        self.assertIsNone(run["handoff"]["artifacts"][-1]["units"])
        self.assertEqual(run["state"]["units"], "mm")
        self.assertEqual(self.runs["wrong-units"]["handoff"]["artifacts"][-1]["units"], "inch")

    def test_actual_scale_changes_and_unsupported_geometry_are_retained(self):
        expected = {"scale-mismatch": ({"x": "120", "y": "80"}, "6"),
                    "svg-scale-mismatch": ({"x": "30", "y": "20"}, "3/2")}
        for case, (dimensions, radius) in expected.items():
            drawing = self.runs[case]["observed"]["raw_preflight"]["file_review"]
            self.assertEqual(drawing["dimensions_mm"], dimensions)
            self.assertEqual([c["radius"] for c in drawing["contours_mm"] if c["kind"] == "circle"], [radius, radius])
        for case in ("unsupported-entity", "svg-unsupported-entity"):
            drawing = self.runs[case]["observed"]["raw_preflight"]["file_review"]
            self.assertIsNone(drawing["geometry"])
            self.assertIsNone(drawing["bounds_mm"])

    def test_context_mutations_preserve_conflicting_candidate_evidence(self):
        unsafe = self.runs["prohibited-unsafe-material"]["observed"]["contexts"]
        self.assertEqual(unsafe["job"]["unsafe_material_status"], "unsafe")
        self.assertEqual(unsafe["material"]["environmental_requirements"]["unsafe_material_status"], "not_indicated")
        vent = self.runs["missing-ventilation"]["observed"]["contexts"]
        self.assertEqual(vent["job"]["ventilation_status"], "unknown")
        self.assertEqual(vent["material"]["environmental_requirements"]["ventilation_status"], "known")
        unknown = self.runs["unknown-material"]["observed"]["contexts"]
        self.assertEqual(unknown["job"]["material_id"], "unknown-material")
        self.assertEqual(unknown["material"]["material_id"], "fixture-plywood")
        incompatible = self.runs["machine-material-incompatibility"]["observed"]
        self.assertEqual(incompatible["contexts"]["material"]["compatibility"], {"machines": ["other-laser"]})
        self.assertIn("material/process profile compatibility is not established", incompatible["raw_preflight"]["findings"])

    def test_no_profile_parameters_or_approval_are_promoted(self):
        for run in self.runs.values():
            state, handoff = run["state"], run["handoff"]
            for field in ("machine_profile", "material"):
                lifecycle = state[field]["lifecycle"]["verification"]
                self.assertEqual(lifecycle["status"], "unverified")
                self.assertIsNone(lifecycle["reviewer"])
                self.assertEqual(lifecycle["evidence"], [])
            self.assertEqual(state["setup"]["submitted_process"]["settings"], {})
            self.assertEqual(state["material"]["properties"], {})
            self.assertEqual(state["approval_status"], "not_requested")
            self.assertEqual(state["simulation_status"], "not_run")
            self.assertEqual(handoff["status"], "blocked")
            self.assertEqual(handoff["simulation"]["status"], "required")
            self.assertTrue(handoff["review_required"])
            self.assertFalse(handoff["execution_allowed"])
            self.assertIsNone(handoff["approval_id"])
            for field in ("raw_preflight", "route_result"):
                self.assertTrue(set(run["observed"][field]["blockers"]).issubset(handoff["blockers"]))
            promoted = copy.deepcopy(handoff)
            promoted.update(status="approved", blockers=[], approval_id="fake-review")
            self.assertFalse(validator_for("handoff.schema.json", self.catalog).is_valid(promoted))

    def assert_setup_change_invalidates(self, group, key, value):
        state = self.runs["positive"]["state"]
        approval = {"status": "approved", "context_fingerprint": context_fingerprint(state)}
        changed = copy.deepcopy(state)
        changed["setup"][group][key] = value
        self.assertNotEqual(context_fingerprint(changed), approval["context_fingerprint"])
        result = invalidate_approval(state, changed, approval)
        self.assertEqual(result["status"], "invalidated")
        self.assertEqual(result["changed_fields"], ["setup"])
        self.assertEqual(result["context_fingerprint"], approval["context_fingerprint"])
        self.assertEqual(approval["status"], "approved")

    def test_submitted_job_changes_invalidate_retained_context(self):
        for key, value in (("units", "inch"), ("format", "SVG"), ("machine_id", "other"),
                           ("material_id", None), ("process_profile_status", "unknown"),
                           ("path_intent", "mark"), ("placement_frame", "other"),
                           ("ventilation_status", "unknown"), ("unsafe_material_status", "unsafe"),
                           ("model_dimensions", {"x": 1, "y": 1}), ("scale_status", "unknown")):
            with self.subTest(field=key):
                self.assert_setup_change_invalidates("submitted_job", key, value)

    def test_process_settings_identity_target_and_source_changes_invalidate(self):
        for key, value in (("settings", {"test_only_setting": "changed"}), ("settings_status", "unknown"),
                           ("process_profile_id", "other"), ("machine_id", "other"),
                           ("material_id", "other"), ("source", {"scope": "changed test claim"})):
            with self.subTest(field=key):
                self.assert_setup_change_invalidates("submitted_process", key, value)

    def test_source_and_derivative_changes_cannot_reuse_context_fingerprint(self):
        state = self.runs["positive"]["state"]
        for field in ("source_artifact_hashes", "generated_manufacturing_output"):
            changed = copy.deepcopy(state)
            if field == "source_artifact_hashes":
                changed[field][0] = "0" * 64
            else:
                changed[field]["sha256"] = "0" * 64
            self.assertNotEqual(context_fingerprint(state), context_fingerprint(changed))

    def test_source_inventory_drift_or_redirect_requires_review(self):
        original = json.loads(reviews.MANIFEST.read_bytes())
        for field, value in (("sha256", "0" * 64), ("revision", "B"), ("path", "../external.dxf")):
            with self.subTest(field=field):
                changed = copy.deepcopy(original)
                changed["sources"]["DXF"][field] = value
                with patch.object(reviews, "MANIFEST") as manifest:
                    manifest.read_bytes.return_value = json.dumps(changed).encode()
                    with self.assertRaises(ValueError):
                        replay("positive")

    def test_full_review_sections_and_separate_safety_gaps_are_retained(self):
        headings = ("Artifact and provenance", "Geometry, units and scale", "Path intent and placement",
                    "Machine, material and process", "Beam risk", "Process-emission and ventilation risk",
                    "Blockers and reviewer action", "Evidence and limits")
        for case, run in self.runs.items():
            review = (ROOT / f"docs/evaluation/laser-runs/2026-09-17-{case}/review.md").read_text(encoding="utf-8")
            for heading in headings:
                self.assertIn(f"## {heading}", review)
            self.assertIn("REVIEW_REQUIRED", review)
            self.assertIn("laser-job-preflight", review)
            assumptions = run["handoff"]["assumptions"]
            self.assertTrue(any(a["statement"].startswith("Beam-risk") and a["status"] == "unresolved" for a in assumptions))
            self.assertTrue(any(a["statement"].startswith("Process-emission") and a["status"] == "unresolved" for a in assumptions))

    def test_all_thirty_two_state_handoff_instances_are_in_repository_validation(self):
        selected = {p.relative_to(ROOT).as_posix(): schema for p, schema in instance_paths()}
        for case in CASES:
            for name in ("state", "handoff"):
                self.assertEqual(selected[f"docs/evaluation/laser-runs/2026-09-17-{case}/{name}.json"], f"{name}.schema.json")

    def test_replay_leaves_fixtures_unchanged_and_rejects_unknown_cases(self):
        before = {p.relative_to(FIXTURE): p.read_bytes() for p in FIXTURE.rglob("*") if p.is_file()}
        for case in CASES:
            replay(case)
        after = {p.relative_to(FIXTURE): p.read_bytes() for p in FIXTURE.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        with self.assertRaises(ValueError):
            replay("../../external-job")


if __name__ == "__main__":
    unittest.main()
