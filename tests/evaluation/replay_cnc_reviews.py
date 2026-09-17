"""Read-only replay of fixed CNC review inputs and diagnostics, not agent output."""

import argparse
import copy
import hashlib
import json
from pathlib import Path

import yaml

from router.job_router import route_job
from scripts.nc_static_checks import load_contexts, review_program
from state.state import context_fingerprint


ROOT = Path(__file__).resolve().parents[2]
CNC = ROOT / "fixtures/cnc/mill-bracket"
CAD = ROOT / "fixtures/cad/bracket"
CASES = ("positive", "wrong-units", "wrong-post", "wrong-controller", "missing-wcs",
         "unknown-tool", "revision-mismatch", "machine-limit-conflict", "incorrect-tool-number")


def replay(case):
    if case not in CASES:
        raise ValueError("unknown fixed CNC case")
    program = (CNC / "programs/positive.nc").read_bytes()
    mutation = None
    if case != "positive":
        mutation = yaml.safe_load((CNC / f"mutations/{case}.yaml").read_text(encoding="utf-8"))
        for change in mutation["replacements"]:
            before, after = change["from"].encode("utf-8"), change["to"].encode("utf-8")
            if program.count(before) != 1:
                raise ValueError("CNC mutation anchor changed")
            program = program.replace(before, after, 1)
    contexts = load_contexts(CNC / "contexts")
    job = contexts["job"]
    inventory = []
    bundle = yaml.safe_load((CAD / "fixture.yaml").read_text(encoding="utf-8"))
    for item in bundle["artifacts"]:
        if item["path"] not in ("source/bracket.scad", "source/bracket.stl", "source/bracket.step", "source/bracket.svg"):
            continue
        artifact = {key: item[key] for key in ("kind", "authority", "revision", "units")}
        artifact.update(artifact_id=Path(item["path"]).name, path=f"fixtures/cad/bracket/{item['path']}",
                        sha256=hashlib.sha256((CAD / item["path"]).read_bytes()).hexdigest())
        inventory.append(artifact)
    nc_artifact = {"artifact_id": f"nc-{case}", "path": f"replay:cnc/{case}/program.nc", "kind": "nc_program",
                   "sha256": hashlib.sha256(program).hexdigest(), "revision": job["revision"],
                   "units": job["units"], "authority": "derived"}
    state = {"job_id": job["job_id"], "revision": job["revision"], "units": job["units"],
             "source_artifact_hashes": [a["sha256"] for a in inventory], "process_family": "cnc_milling",
             "material": copy.deepcopy(contexts["material"]), "machine_profile": copy.deepcopy(contexts["machine"]),
             "controller_profile": copy.deepcopy(contexts["controller"]), "setup": copy.deepcopy(contexts["setup"]),
             "work_coordinate_system": {"code": contexts["setup"]["coordinate_model"]["wcs"],
                                        "status": contexts["setup"]["wcs_status"]},
             "tool_library": {"tool_library_id": job["tool_library"]["tool_library_id"], "tools": [copy.deepcopy(contexts["tool"])]},
             "cam_system": job["cam_system"], "postprocessor": copy.deepcopy(contexts["post"]),
             "post_version": contexts["post"]["post_version"], "generated_manufacturing_output": nc_artifact,
             "simulation_status": job["simulation_status"], "jurisdiction": job["jurisdiction"],
             "ip_status": copy.deepcopy(job["ip_status"]), "export_review_status": job["export_review_status"],
             "approval_status": job["approval_status"], "verification_results": [{
                 "check_id": "partial_static_review", "status": "inconclusive",
                 "summary": "Offline reports retained; required context/simulation/review is unresolved. No physical verification.",
                 "evidence": [f"docs/evaluation/cnc-runs/2026-09-17-{case}/observed.json"]}]}
    request = {"process_family": "cnc_milling", "artifact_class": "nc_program", "consequence_level": "execution_adjacent",
               "machine_known": True, "controller_known": True, "material_known": True}
    result = route_job(request, state, nc_program=program)
    result.pop("job_state")
    text = program.decode("utf-8")
    return {"case": case, "mutation": mutation, "program": text, "contexts": contexts,
            "artifacts": inventory + [nc_artifact], "state": state, "context_fingerprint": context_fingerprint(state),
            "cad_source": (CAD / "source/bracket.scad").read_text(encoding="utf-8"),
            "cad_metadata": json.loads((CAD / "metadata/revision.json").read_text(encoding="utf-8")),
            "raw_fixture_report": review_program(text, contexts),
            "coordinate_report": review_program(text, contexts, selected_wcs="G54", coordinate_model=contexts["setup"]["coordinate_model"]),
            "request": request, "route_result": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=(*CASES, "all"))
    args = parser.parse_args()
    results = [replay(case) for case in CASES] if args.case == "all" else [replay(args.case)]
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
