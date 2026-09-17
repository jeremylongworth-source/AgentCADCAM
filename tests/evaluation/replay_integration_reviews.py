"""Replay fixed integrated packets; never regenerate reasoning or issue approval."""

import argparse
import copy
import hashlib
import json
from pathlib import Path

import yaml

from router.handoff_review import review_handoff
from router.job_router import route_job
from scripts.additive_preflight import preflight as additive_preflight
from scripts.cad_handoff_checks import review_fixture
from scripts.laser_preflight import preflight as laser_preflight
from state.state import context_fingerprint, verification_context_fingerprint
from tests.evaluation.replay_additive_reviews import inputs as additive_inputs
from tests.evaluation.replay_cnc_reviews import replay as cnc_replay
from tests.evaluation.replay_laser_reviews import inputs as laser_inputs


ROOT = Path(__file__).resolve().parents[2]
PACKETS = ROOT / "docs/evaluation/integration-runs"
CASES = ("cad", "cnc", "additive", "laser")
CAD_PATHS = ("source/bracket.scad", "source/bracket.step", "source/bracket.stl", "source/bracket.svg")


def folder_for(case):
    if case not in CASES:
        raise ValueError("unknown fixed integration case")
    return PACKETS / f"2026-09-17-{case}"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def review_text_hash(path):
    # Review/contract text identity is LF-normalized for Windows/Linux checkout
    # portability. Manufacturing artifact identity remains raw-byte SHA-256.
    return sha256(path.read_text(encoding="utf-8").encode("utf-8"))


def draft_state(job_id, revision, units, family, artifacts, output=None, machine=None, material=None):
    return {
        "job_id": job_id, "revision": revision, "units": units, "process_family": family,
        "source_artifact_hashes": [a["sha256"] for a in artifacts if a != output],
        "material": material, "machine_profile": machine, "controller_profile": None,
        "setup": {}, "workholding": None, "work_coordinate_system": None,
        "tool_library": None, "cam_system": None, "postprocessor": None, "post_version": None,
        "generated_manufacturing_output": output, "simulation_status": "unknown",
        "jurisdiction": None,
        "ip_status": {"ownership_status": "repository_authored_synthetic",
                      "licence_status": "CC0-1.0 fixture", "confidentiality": "public_test_data",
                      "redistribution_authorized": True},
        "export_review_status": "not_reviewed", "approval_status": "not_requested",
        "verification_results": [],
    }


def inputs(case):
    """Use actual fixture declarations; no approved routing-test factories."""
    folder_for(case)  # Reject arbitrary paths before reading anything.
    if case == "cad":
        root = ROOT / "fixtures/cad/bracket"
        metadata = read_json(root / "metadata/revision.json")
        derivation = read_json(root / "metadata/derivation.json")
        artifacts = [derivation["source"]] + [a["artifact"] for a in derivation["derivatives"]]
        state = draft_state(metadata["job_id"], metadata["revision"], metadata["units"], "cad_handoff", artifacts)
        state["ip_status"] = {key: metadata[key] for key in (
            "ownership_status", "licence_status", "confidentiality", "third_party_restrictions", "redistribution_authorized")}
        state["export_review_status"] = metadata["export_review_status"]
        state["setup"] = {"cad_handoff": {
            "review_profile": "cad-bracket-basic-v2", "metadata": metadata,
            "derivation": derivation, "manufacturing_context": None,
        }}
        contexts = {"metadata": metadata, "derivation": derivation}
        raw = {"fixture_review": review_fixture(root)}
        byte_inputs = {"cad_artifacts": {path: (root / path).read_bytes() for path in CAD_PATHS}}
    elif case == "cnc":
        supplied = cnc_replay("positive")
        state, contexts, artifacts = supplied["state"], supplied["contexts"], supplied["artifacts"]
        raw = {key: supplied[key] for key in ("raw_fixture_report", "coordinate_report")}
        byte_inputs = {"nc_program": (ROOT / "fixtures/cnc/mill-bracket/programs/positive.nc").read_bytes()}
    elif case == "additive":
        contexts, mesh, source, output, _ = additive_inputs("positive")
        job = contexts["job"]
        artifacts = [source, output]
        state = draft_state(job["job_id"], job["revision"], job["mesh_units"], "additive", artifacts,
                            output, contexts["printer"], contexts["material"])
        state["setup"] = {"additive_preflight": {
            "job": copy.deepcopy(job), "source_artifact": source, "slicer_profile": None,
        }}
        raw = {"preflight": additive_preflight(**contexts, mesh_bytes=mesh, source_revision=source["revision"])}
        byte_inputs = {"additive_mesh": mesh}
    else:
        contexts, drawing, artifacts, _ = laser_inputs("positive")
        job = contexts["job"]
        state = draft_state(job["job_id"], job["revision"], job["units"], "laser_cutting", artifacts,
                            artifacts[-1], contexts["machine"], contexts["material"])
        state["setup"] = {"laser_preflight": {
            "job": copy.deepcopy(job), "source_artifact": artifacts[1], "process": copy.deepcopy(contexts["process"]),
        }}
        raw = {"preflight": laser_preflight(**contexts, drawing_bytes=drawing, source_revision=artifacts[1]["revision"])}
        byte_inputs = {"laser_drawing": drawing}
    return state, contexts, artifacts, raw, byte_inputs


def replay(case):
    folder = folder_for(case)
    decisions = read_json(folder / "decisions.json")
    state, contexts, artifacts, raw, byte_inputs = inputs(case)
    evidence = [f"{folder.relative_to(ROOT).as_posix()}/review.md"]
    review = {
        "handoff_id": f"integration-{case}-2026-09-17", "artifacts": copy.deepcopy(artifacts),
        "assumptions": [{"statement": statement, "status": "unresolved", "evidence": evidence}
                        for statement in decisions["unresolved_assumptions"]],
        "simulation": dict(copy.deepcopy(decisions["simulation"]), evidence=evidence),
        "human_review": copy.deepcopy(decisions["human_review"]),
    }
    state["setup"]["handoff_review"] = review
    state["simulation_status"] = review["simulation"]["status"]
    binding = {"version": 1, "fingerprint": verification_context_fingerprint(state)}
    state["verification_results"] = [dict(copy.deepcopy(item), context_binding=binding, evidence=evidence)
                                     for item in decisions["verification"]]
    request = {"process_family": state["process_family"], "artifact_class": "handoff",
               "consequence_level": "execution_adjacent", "requested_action": "prepare_handoff",
               "generated_manufacturing_artifact": True,
               "machine_known": True, "controller_known": True, "material_known": True, "jurisdiction_known": True}
    route = route_job(request, state, **byte_inputs)
    handoff = dict(copy.deepcopy(review), job_id=state["job_id"], revision=state["revision"], units=state["units"],
                   process_family=state["process_family"], consequence_level=route["consequence_level"],
                   context_fingerprint=context_fingerprint(state), context_fingerprint_version=2,
                   status="blocked", verification=copy.deepcopy(state["verification_results"]),
                   blockers=sorted(set(route["blockers"]) | set(decisions["blockers"])),
                   review_required=True, execution_allowed=False, approval_id=None)
    consumed = review_handoff(handoff, state, **byte_inputs)
    route.pop("job_state")
    manifest = ROOT / f"skillsets/{route['skillset']}.yaml"
    skillset = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    skill_paths = [ROOT / f"skills/{name}/SKILL.md" for name in skillset["skills"]]
    observed = {
        "case": case, "scope": "Fixed synthetic input replay, not agent reasoning, authenticated evidence or manufacturing approval",
        "contexts": contexts, "artifacts": artifacts, "raw_checks": raw,
        "byte_inputs": {key: ({path: {"sha256": sha256(data), "size": len(data)} for path, data in value.items()}
                              if isinstance(value, dict) else {"sha256": sha256(value), "size": len(value)})
                        for key, value in byte_inputs.items()},
        "review_input_hash_policy": "sha256-utf8-universal-newlines-to-lf",
        "review_inputs": {path.relative_to(ROOT).as_posix(): review_text_hash(path)
                          for path in (PACKETS / "protocol.md", folder / "decisions.json", folder / "review.md",
                                       manifest, *skill_paths)},
        "request": request, "route_result": route, "handoff_result": consumed,
    }
    return {"state": state, "handoff": handoff, "observed": observed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=(*CASES, "all"))
    args = parser.parse_args()
    results = {case: replay(case) for case in CASES} if args.case == "all" else replay(args.case)
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
