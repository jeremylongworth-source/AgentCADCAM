"""In-memory laser routing declarations, never actual process settings or approval."""

import copy

from state.state import context_fingerprint, verification_context_fingerprint
from tests.evaluation.replay_laser_reviews import inputs, ROOT
from tests.schema.test_profile_lifecycle import synthetic_review
from tests.routing.governance_fixture import declare_test_governance
import json


CHECKS = ("laser_design", "laser_paths", "laser_process", "laser_beam", "laser_emissions", "laser_output")


def rebind(state):
    for record in state["verification_results"]:
        if "context_binding" in record:
            record["context_binding"] = {"version": 1, "fingerprint": verification_context_fingerprint(state)}


def make_laser_review(case="positive"):
    contexts, drawing, artifacts, _ = inputs(case)
    state = json.loads((ROOT / "docs/evaluation/laser-runs/2026-09-17-positive/state.json").read_text(encoding="utf-8"))
    state["machine_profile"] = synthetic_review(copy.deepcopy(contexts["machine"]))
    state["material"] = synthetic_review(copy.deepcopy(contexts["material"]))
    process = copy.deepcopy(contexts["process"])
    process["settings"] = {"test_only_non_operational_marker": "not a machine parameter"}
    state["setup"] = {"laser_preflight": {"job": copy.deepcopy(contexts["job"]),
                                          "process": process, "source_artifact": artifacts[1]}}
    state["generated_manufacturing_output"] = artifacts[-1]
    state["source_artifact_hashes"] = [a["sha256"] for a in artifacts[:2]]
    state["verification_results"] = [
        {"check_id": key, "kind": "verification", "status": "passed", "context_binding": {},
         "summary": "Test-only evidence declaration, not qualified review", "evidence": [f"test-only:{key}"]}
        for key in CHECKS]
    declare_test_governance(state)
    rebind(state)
    request = {"process_family": "laser_cutting", "artifact_class": "two_d_cutting",
               "consequence_level": "execution_adjacent", "machine_known": True, "material_known": True}
    approval = {"approval_id": "synthetic-laser-approval", "status": "approved", "scope": ["manufacturing_handoff"],
                "reviewer": "test-reviewer", "reviewed_at": "2026-09-17T12:00:00Z",
                "context_fingerprint": context_fingerprint(state)}
    return state, request, approval, drawing
