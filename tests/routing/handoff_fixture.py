"""Four-family package consistency controls, never actual manufacturing approval."""

import copy

from router.handoff_review import REVIEW_FIELDS
from state.state import context_fingerprint, verification_context_fingerprint
from tests.routing.cad_fixture import make_cad_review
from tests.routing.cnc_fixture import make_cnc_review
from tests.routing.additive_fixture import make_additive_review
from tests.routing.laser_fixture import make_laser_review
from tests.evaluation.replay_laser_reviews import inputs as laser_inputs


FAMILIES = ("cad_handoff", "cnc_milling", "additive", "laser_cutting")


def renew_test_review(handoff, state, approval):
    """Bind changed test declarations only; do not use as an evidence-review API."""
    state.setdefault("setup", {})["handoff_review"] = {key: copy.deepcopy(handoff[key]) for key in REVIEW_FIELDS}
    for record in state["verification_results"]:
        if "context_binding" in record:
            record["context_binding"] = {"version": 1, "fingerprint": verification_context_fingerprint(state)}
    handoff["verification"] = copy.deepcopy(state["verification_results"])
    handoff["context_fingerprint"] = context_fingerprint(state)
    approval["context_fingerprint"] = handoff["context_fingerprint"]


def make_handoff_review(family):
    factory, argument = {"cad_handoff": (make_cad_review, "cad_artifacts"),
                         "cnc_milling": (make_cnc_review, "nc_program"),
                         "additive": (make_additive_review, "additive_mesh"),
                         "laser_cutting": (make_laser_review, "laser_drawing")}[family]
    state, _, approval, data = factory()
    if family == "cad_handoff":
        binding = state["setup"]["cad_handoff"]["derivation"]
        artifacts = [binding["source"]] + [entry["artifact"] for entry in binding["derivatives"]]
    elif family == "laser_cutting":
        artifacts = laser_inputs("positive")[2]
    elif family == "additive":
        artifacts = [state["setup"]["additive_preflight"]["source_artifact"], state["generated_manufacturing_output"]]
    else:
        # Existing CNC routing control binds this dummy source hash. This is
        # intentionally not a declaration about the real revision-A CAD source.
        artifacts = [{"artifact_id": "test-only-source", "path": "test-only:cnc-source",
                      "kind": "native_cad_source", "sha256": state["source_artifact_hashes"][0],
                      "revision": state["revision"], "units": state["units"], "authority": "authoritative"},
                     state["generated_manufacturing_output"]]
    simulation = {"status": "verified" if family == "cnc_milling" else "not_required",
                  "reason": "Test-only simulation disposition, not a qualified requirement assessment",
                  "required_checks": ["Test-only simulation"] if family == "cnc_milling" else [],
                  "evidence": ["test-only:simulation-disposition"]}
    state["simulation_status"] = simulation["status"]
    handoff = {"handoff_id": f"test-only-{family}", "job_id": state["job_id"], "revision": state["revision"],
               "process_family": family, "consequence_level": "execution_adjacent", "units": state["units"],
               "status": "approved", "context_fingerprint": None, "context_fingerprint_version": 2,
               "artifacts": copy.deepcopy(artifacts), "assumptions": [], "verification": [], "simulation": simulation,
               "human_review": {"action": "Test-only record; obtain actual applicable review before any use",
                                "scope": ["manufacturing_handoff"], "reviewer_role": "Test-only reviewer"},
               "blockers": [], "approval_id": approval["approval_id"], "review_required": True, "execution_allowed": False}
    renew_test_review(handoff, state, approval)
    return handoff, state, approval, {argument: data}
