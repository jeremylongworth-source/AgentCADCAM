"""In-memory reviewed declarations for router tests, never practitioner approval."""

import hashlib
import json
from pathlib import Path

from state.state import context_fingerprint, verification_context_fingerprint
from tests.schema.test_profile_lifecycle import synthetic_review


ROOT = Path(__file__).resolve().parents[2]
CNC = ROOT / "fixtures/cnc/mill-bracket"


def rebind_synthetic_verification(state):
    """Test-only rebinding of existing declarations, never a real evidence review.

    Do not replace records or promote failed/unknown outcomes.
    """
    fingerprint = verification_context_fingerprint(state)
    for record in state.get("verification_results", []):
        if "context_binding" in record:
            record["context_binding"] = {"version": 1, "fingerprint": fingerprint}


def make_cnc_review():
    def read(name):
        return json.loads((CNC / f"contexts/{name}.json").read_text(encoding="utf-8"))

    program = (CNC / "programs/positive.nc").read_bytes()
    job = read("job")
    state = json.loads((ROOT / "state/state.example.json").read_text(encoding="utf-8"))
    state.update(job_id=job["job_id"], revision=job["revision"], process_family="cnc_milling",
                 simulation_status="verified", verification_results=[])
    for target, name in (("machine_profile", "machine"), ("controller_profile", "controller"), ("material", "material")):
        state[target] = synthetic_review(read(name))
    state["setup"] = read("setup")
    state["setup"]["wcs_status"] = "verified"
    state["setup"]["workholding"]["clamps_clear"] = True
    synthetic_review(state["setup"]["coordinate_model"])
    state["work_coordinate_system"] = {"code": "G54", "status": "verified"}
    tool = synthetic_review(read("tool"))
    tool["availability"] = "available"
    state["tool_library"] = {"tools": [tool]}
    state["postprocessor"] = synthetic_review(read("post"))
    state["cam_system"] = state["postprocessor"]["cam_system"]
    state["post_version"] = state["postprocessor"]["post_version"]
    state["generated_manufacturing_output"] = {
        "artifact_id": "synthetic-nc", "path": "fixtures/cnc/mill-bracket/programs/positive.nc",
        "kind": "nc_program", "sha256": hashlib.sha256(program).hexdigest(),
        "revision": state["revision"], "units": state["units"], "authority": "derived",
    }
    state["verification_results"] = [
        {"check_id": f"synthetic-{kind}", "kind": kind, "status": "passed",
         "summary": "Test-only declaration, not actual job verification",
         "evidence": [f"test-only:{kind}"], "context_binding": {}}
        for kind in ("simulation", "verification")
    ]
    rebind_synthetic_verification(state)
    request = {"process_family": "cnc_milling", "artifact_class": "nc_program", "consequence_level": "execution_adjacent",
               "machine_known": True, "controller_known": True, "material_known": True}
    approval = {"approval_id": "synthetic-approval", "status": "approved", "scope": ["manufacturing_handoff"],
                "reviewer": "test-reviewer", "reviewed_at": "2026-09-17T12:00:00Z",
                "context_fingerprint": context_fingerprint(state)}
    return state, request, approval, program
