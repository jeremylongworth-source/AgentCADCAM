"""Current CAD byte/context and scoped-review gates, never manufacturing approval."""

import copy
import hashlib
import json
import struct
import unittest
from unittest.mock import patch

from router import cad_evidence
from router.job_router import route_job
from router.router import LIVE_ACTIONS
from scripts.validate_schema_instances import validator_for
from state.state import context_fingerprint
from tests.routing.cad_fixture import CHECKS, make_cad_review, rebind


class CadArtifactGateTests(unittest.TestCase):
    def setUp(self):
        self.state, self.request, self.approval, self.artifacts = make_cad_review()
        self.inputs = self.state["setup"]["cad_handoff"]

    def renew(self):
        rebind(self.state)
        self.approval["context_fingerprint"] = context_fingerprint(self.state)

    def route(self, **kwargs):
        before = copy.deepcopy((self.state, self.request, self.approval, self.artifacts))
        result = route_job(self.request, self.state, self.approval, cad_artifacts=self.artifacts, **kwargs)
        self.assertEqual(before, (self.state, self.request, self.approval, self.artifacts))
        self.assertTrue(result["review_required"])
        self.assertFalse(result["execution_allowed"])
        json.dumps(result, allow_nan=False)
        return result

    def blocked(self, result, blocker="MISSING_CONTEXT"):
        self.assertIn(blocker, result["blockers"], result)
        self.assertIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
        self.assertNotEqual(result["approval_state"], "approved")
        self.assertEqual(result["approval_record"]["context_fingerprint"], self.approval["context_fingerprint"])

    def refresh_bytes(self):
        binding = self.inputs["derivation"]
        descriptors = [binding["source"]] + [a["artifact"] for a in binding["derivatives"]]
        for descriptor in descriptors:
            descriptor["sha256"] = hashlib.sha256(self.artifacts[descriptor["path"]]).hexdigest()
        self.state["source_artifact_hashes"] = [a["sha256"] for a in descriptors]
        self.renew()

    def test_positive_is_deterministic_nonexecuting_and_does_not_require_machine_profiles(self):
        for profiles in (True, False):
            if not profiles:
                self.state.update(machine_profile=None, material=None)
                self.renew()
            result = self.route()
            self.assertEqual(result, self.route())
            self.assertEqual(result["blockers"], [])
            self.assertEqual(result["approval_state"], "approved")
            self.assertFalse(result["cad_review"]["geometry_equivalence_verified"])
            self.assertEqual([r["status"] for r in result["cad_review"]["file_checks"]], ["passed"] * 3)
            validator_for("cad-handoff-input.schema.json").validate(self.inputs)

    def test_every_byte_is_required_and_no_paths_are_read(self):
        for path in self.artifacts:
            self.setUp()
            del self.artifacts[path]
            self.blocked(self.route())
        for value in (None, {}, "D:/private/job", {"../../private": b"secret"}):
            self.setUp()
            self.artifacts = value
            self.blocked(self.route())
        for value in (None, "file.stl", b"", bytearray(b"not bytes")):
            self.setUp()
            self.artifacts["source/bracket.stl"] = value
            self.blocked(self.route())

    def test_changed_bytes_require_new_identity_and_fresh_geometry_review(self):
        for path in self.artifacts:
            self.setUp()
            self.artifacts[path] += b"\n"
            self.blocked(self.route(), "SOURCE_VERIFICATION_REQUIRED")
        for path, before, after in (
            ("source/bracket.svg", b"BASE: 60 x 40 x 6", b"BASE: 61 x 40 x 6"),
            ("source/bracket.svg", b"REV A", b"REV B"),
            ("source/bracket.scad", b"hole_diameter = 6;", b"hole_diameter = 8;"),
            ("source/bracket.step", b"ISO-10303-21;", b"INVALID;"),
        ):
            self.setUp()
            self.assertIn(before, self.artifacts[path])
            self.artifacts[path] = self.artifacts[path].replace(before, after, 1)
            self.refresh_bytes()
            self.blocked(self.route())

    def test_all_six_roadmap_failures_block_with_current_test_records(self):
        for case in ("revision", "units", "stale", "mesh-master", "missing-intent", "dimensions"):
            with self.subTest(case=case):
                self.setUp()
                if case == "revision":
                    self.inputs["derivation"]["derivatives"][-1]["artifact"]["revision"] = "B"
                elif case == "units":
                    self.inputs["metadata"]["units"] = ""
                elif case == "stale":
                    self.artifacts["source/bracket.scad"] = self.artifacts["source/bracket.scad"].replace(b"hole_diameter = 6;", b"hole_diameter = 8;")
                elif case == "mesh-master":
                    self.inputs["metadata"]["authoritative_artifact"] = "source/bracket.stl"
                elif case == "missing-intent":
                    self.inputs["manufacturing_context"]["requirements"] = []
                else:
                    self.artifacts["source/bracket.svg"] = self.artifacts["source/bracket.svg"].replace(b"BASE: 60 x 40 x 6", b"BASE: 61 x 40 x 6")
                self.renew()
                self.blocked(self.route(), "SOURCE_VERIFICATION_REQUIRED" if case in ("stale", "mesh-master") else "MISSING_CONTEXT")

    def test_metadata_context_source_and_descriptor_contracts_are_required(self):
        for key in self.inputs:
            self.setUp()
            del self.inputs[key]
            self.renew()
            self.blocked(self.route())
        for key, value in (("job_id", "other"), ("revision", "B"), ("units", "inch"), ("pmi_status", "unknown"), ("pmi_status", "present")):
            self.setUp()
            self.inputs["metadata"][key] = value
            self.renew()
            self.blocked(self.route())
        for key, value in (("requirements", []), ("drawing_pmi_basis", ""), ("sources", []),
                           ("sources", [{}]), ("material_id", "other"), ("process_family", "additive")):
            self.setUp()
            self.inputs["manufacturing_context"][key] = value
            self.renew()
            self.blocked(self.route())
        self.setUp()
        self.state["machine_profile"] = None
        self.state["material"]["process_family"] = "additive"
        self.renew()
        result = self.route()
        self.blocked(result)
        self.assertIn("CAD selected process conflicts with supplied material profile", result["findings"])

    def test_unsupported_profile_cannot_borrow_fixture_checks(self):
        self.inputs["review_profile"] = "arbitrary-cad-engine"
        self.renew()
        result = self.route()
        self.blocked(result, "SOURCE_VERIFICATION_REQUIRED")
        self.assertEqual(result["cad_review"]["file_checks"], [])

    def test_derivation_roles_inventory_and_state_hashes_must_agree(self):
        for key, value in (("kind", "mesh_derivative"), ("path", "../source.scad"), ("sha256", "0" * 64)):
            self.setUp()
            self.inputs["derivation"]["source"][key] = value
            self.renew()
            self.blocked(self.route(), "SOURCE_VERIFICATION_REQUIRED")
        for mutation in ("missing", "duplicate-id", "extra-hash"):
            self.setUp()
            if mutation == "missing":
                self.inputs["derivation"]["derivatives"].pop()
            elif mutation == "duplicate-id":
                self.inputs["derivation"]["derivatives"][0]["artifact"]["artifact_id"] = self.inputs["derivation"]["source"]["artifact_id"]
            else:
                self.state["source_artifact_hashes"].append("0" * 64)
            self.renew()
            self.blocked(self.route(), "SOURCE_VERIFICATION_REQUIRED")
        self.setUp()
        self.inputs["derivation"]["derivatives"][0]["relationship"] = "export"
        self.renew()
        self.blocked(self.route(), "SOURCE_VERIFICATION_REQUIRED")

    def test_selected_output_must_be_an_exact_reviewed_descriptor(self):
        for entry in self.inputs["derivation"]["derivatives"]:
            self.state["generated_manufacturing_output"] = copy.deepcopy(entry["artifact"])
            self.renew()
            self.assertEqual(self.route()["blockers"], [])
        self.state["generated_manufacturing_output"]["artifact_id"] = "unreviewed-output"
        self.renew()
        self.blocked(self.route())

    def test_every_role_failed_duplicate_and_stale_evidence_blocks(self):
        for identity in CHECKS:
            self.setUp()
            self.state["verification_results"] = [r for r in self.state["verification_results"] if r["check_id"] != identity]
            self.renew()
            self.blocked(self.route())
        for key, value in (("status", "failed"), ("evidence", []), ("kind", "simulation"),
                           ("context_binding", {"version": 1, "fingerprint": "0" * 64})):
            self.setUp()
            self.state["verification_results"][0][key] = value
            self.approval["context_fingerprint"] = context_fingerprint(self.state)
            self.blocked(self.route())
        self.setUp()
        self.state["verification_results"].append(copy.deepcopy(self.state["verification_results"][0]))
        self.renew()
        self.blocked(self.route())

    def test_new_approval_cannot_renew_old_evidence(self):
        self.inputs["manufacturing_context"]["requirements"].append("Changed test-only requirement")
        self.approval["context_fingerprint"] = context_fingerprint(self.state)
        self.blocked(self.route(), "SOURCE_VERIFICATION_REQUIRED")

    def test_changed_context_invalidates_old_review_without_resigning_it(self):
        previous = copy.deepcopy(self.state)
        self.inputs["manufacturing_context"]["drawing_pmi_basis"] = "New test-only basis"
        rebind(self.state)
        result = self.route(previous_state=previous)
        self.assertEqual(result["approval_state"], "invalidated")
        self.assertEqual(result["approval_record"]["context_fingerprint"], self.approval["context_fingerprint"])
        self.assertEqual(result["approval_record"]["changed_fields"], ["setup", "verification_results"])

    def test_handoff_action_bytes_and_selected_output_cannot_be_down_classified(self):
        self.request.update(consequence_level="informational", artifact_class="unknown", requested_action=" PREPARE_HANDOFF ")
        self.artifacts = None
        self.renew()
        result = self.route()
        self.assertEqual(result["consequence_level"], "execution_adjacent")
        self.blocked(result)
        self.setUp()
        self.state["process_family"] = "additive"
        self.request["process_family"] = "additive"
        self.renew()
        self.blocked(self.route())

    def test_all_live_actions_stay_blocked(self):
        for action in LIVE_ACTIONS:
            self.request.update(requested_action=action, consequence_level="informational")
            result = self.route()
            self.assertEqual(result["consequence_level"], "live_execution")
            self.assertIn("BLOCK_EXECUTION", result["blockers"])

    def test_raw_flags_and_wrong_scope_do_not_authorize(self):
        self.request["approval_state"] = "approved"
        self.state["approval_status"] = "approved"
        self.assertEqual(route_job(self.request, self.state, cad_artifacts=self.artifacts)["approval_state"], "not_requested")
        self.approval["scope"] = ["unrelated"]
        self.assertEqual(self.route()["approval_state"], "not_requested")

    def test_advisory_without_artifacts_does_not_require_invented_files(self):
        self.request.update(requested_action="explain", consequence_level="design_advisory")
        self.artifacts = None
        self.state["setup"] = None
        self.renew()
        self.assertEqual(self.route()["blockers"], [])

    def test_resource_limits_malformed_and_nonfinite_bytes_are_blocked(self):
        with patch.object(cad_evidence, "MAX_FILE_BYTES", 10):
            result = self.route()
            self.blocked(result, "SOURCE_VERIFICATION_REQUIRED")
            self.assertEqual(result["cad_review"]["sha256"], {})
        with patch.object(cad_evidence, "MAX_TOTAL_BYTES", 10):
            self.blocked(self.route(), "SOURCE_VERIFICATION_REQUIRED")
        for path in self.artifacts:
            self.setUp()
            self.artifacts[path] = b"\xff\xfe"
            self.refresh_bytes()
            self.blocked(self.route())
        for value in (float("nan"), float("inf"), float("-inf")):
            self.setUp()
            mesh = bytearray(self.artifacts["source/bracket.stl"])
            struct.pack_into("<f", mesh, 96, value)
            self.artifacts["source/bracket.stl"] = bytes(mesh)
            self.refresh_bytes()
            self.blocked(self.route())
        self.setUp()
        self.artifacts["source/bracket.step"] += b"\n#999999=CARTESIAN_POINT('',(1e999,0.,0.));\n"
        self.refresh_bytes()
        result = self.route()
        self.blocked(result)
        self.assertIn("STEP fixture contains nonfinite coordinates", result["cad_review"]["file_checks"][1]["findings"])


if __name__ == "__main__":
    unittest.main()
