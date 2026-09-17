"""In-memory reviewed test declarations; no real slicer settings or approval."""

import copy
import json

from state.state import context_fingerprint, verification_context_fingerprint
from tests.evaluation.replay_additive_reviews import inputs, ROOT
from tests.schema.test_profile_lifecycle import synthetic_review
from tests.routing.governance_fixture import declare_test_governance
from tests.routing.source_fixture import declare_test_source_review


CHECKS = ("additive_design", "additive_geometry", "additive_orientation", "additive_supports",
          "additive_slicer", "additive_environment", "additive_output")


def rebind(state):
    for record in state["verification_results"]:
        if "context_binding" in record:
            record["context_binding"] = {"version": 1, "fingerprint": verification_context_fingerprint(state)}


def make_additive_review(case="3mf-positive"):
    contexts, mesh, source, derivative, _ = inputs(case)
    state = json.loads((ROOT / "docs/evaluation/additive-runs/2026-09-17-positive/state.json").read_text(encoding="utf-8"))
    job = copy.deepcopy(contexts["job"])
    job["slicer_profile_id"] = "fixture-pla-profile"
    state.update(job_id=job["job_id"], revision=job["revision"], units=job["mesh_units"])
    state["machine_profile"] = synthetic_review(copy.deepcopy(contexts["printer"]))
    state["material"] = synthetic_review(copy.deepcopy(contexts["material"]))
    profile = {"profile_id": "fixture-pla-profile", "revision": "test-1", "slicer_id": "test-only-slicer",
               "slicer_version": "test-only-version", "printer_id": contexts["printer"]["machine_id"],
               "material_id": contexts["material"]["material_id"],
               "settings": {"non_operational_test_marker": "not a printing parameter"},
               "source": {"title": "Synthetic slicer declaration", "publisher": "AgentCADCAM tests",
                          "locator": "test-only:slicer", "published_at": None, "accessed_at": "2026-09-17",
                          "scope": "Router tests only, not an applicable slicer configuration",
                          "claims": ["This is a non-operational test marker, not a print setting."]}}
    declare_test_source_review(profile["source"], "slicer_profile")
    state["setup"] = {"additive_preflight": {"job": job, "slicer_profile": profile, "source_artifact": source}}
    state["generated_manufacturing_output"] = derivative
    state["source_artifact_hashes"] = [source["sha256"]]
    state["verification_results"] = [
        {"check_id": key, "kind": "verification", "status": "passed", "context_binding": {},
         "summary": "Test-only evidence declaration, not qualified review", "evidence": [f"test-only:{key}"]}
        for key in CHECKS]
    declare_test_governance(state)
    rebind(state)
    request = {"process_family": "additive", "artifact_class": "mesh", "consequence_level": "execution_adjacent",
               "machine_known": True, "material_known": True}
    approval = {"approval_id": "synthetic-additive-approval", "status": "approved", "scope": ["manufacturing_handoff"],
                "reviewer": "test-reviewer", "reviewed_at": "2026-09-17T12:00:00Z",
                "context_fingerprint": context_fingerprint(state)}
    return state, request, approval, mesh
