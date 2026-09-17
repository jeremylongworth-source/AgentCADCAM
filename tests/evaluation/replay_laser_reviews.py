"""Reconstruct fixed laser evidence without generating reviews or running equipment."""

import argparse
import copy
import hashlib
import json
from pathlib import Path

import yaml

from router.job_router import route_job
from scripts.laser_preflight import apply_mutation, load_contexts, preflight


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures/laser/cut-bracket"
MANIFEST = FIXTURE / "source-manifest.json"
FILE_CASES = ("duplicate-contours", "open-contours", "unsupported-entity", "wrong-units", "scale-mismatch")
CASES = ("positive", *FILE_CASES, "unknown-material", "prohibited-unsafe-material",
         "missing-ventilation", "machine-material-incompatibility", "svg-positive",
         *(f"svg-{case}" for case in FILE_CASES))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def replace_once(data, before, after):
    if data.count(before) != 1:
        raise ValueError("fixed mutation no longer matches its single expected input")
    return data.replace(before, after, 1)


def drawing_mutation(data, format, case):
    if format == "SVG":
        substitutions = {
            "duplicate-contours": (b"</g>", b'<circle cx="17" cy="25" r="3"/></g>'),
            "open-contours": (b'<rect x="5" y="5" width="60" height="40" />', b'<polyline points="5,5 65,5 65,45 5,45"/>'),
            "unsupported-entity": (b"</g>", b'<path d="M5 5C10 10 20 20 30 30Z"/></g>'),
            "wrong-units": (b'width="70mm"', b'width="70in"'),
            "scale-mismatch": (b'viewBox="0 0 70 50"', b'viewBox="0 0 140 100"'),
        }
        return replace_once(data, *substitutions[case])
    if case == "wrong-units":
        return replace_once(data, b"$INSUNITS\n 70\n4\n", b"$INSUNITS\n 70\n1\n")
    head, tail = data.split(b"  2\nENTITIES\n", 1)
    body, rest = tail.split(b"  0\nENDSEC", 1)
    if case == "duplicate-contours":
        body += b"0\nCIRCLE\n8\n0\n10\n17\n20\n25\n40\n3\n"
    elif case == "open-contours":
        body = replace_once(body, b" 70\n1\n", b" 70\n0\n")
    elif case == "unsupported-entity":
        body += b"0\nARC\n8\n0\n10\n17\n20\n25\n40\n3\n50\n0\n51\n90\n"
    elif case == "scale-mismatch":
        # Fixed fixture coordinates/radii only; do not reinterpret arbitrary DXF.
        for value in (5, 65, 45, 17, 25, 53, 3):
            body = body.replace(f"\n{value}.0\n".encode(), f"\n{2*value}.0\n".encode())
    return head+b"  2\nENTITIES\n"+body+b"  0\nENDSEC"+rest


def inputs(case):
    if case not in CASES:
        raise ValueError("unknown fixed laser review case")
    manifest_bytes = MANIFEST.read_bytes()
    manifest = json.loads(manifest_bytes)
    format = "SVG" if case.startswith("svg-") else "DXF"
    source = copy.deepcopy(manifest["sources"][format])
    expected_path = f"fixtures/laser/cut-bracket/source/bracket.{format.lower()}"
    if source["path"] != expected_path:
        raise ValueError("source inventory cannot redirect fixed fixture inputs")
    data = (ROOT / expected_path).read_bytes()
    if sha256(data) != source["sha256"] or source["revision"] != manifest["revision"]:
        raise ValueError("source inventory identity/revision drift requires review")
    contexts = load_contexts(FIXTURE / "contexts")
    contexts["job"]["format"] = format
    base_case = case.removeprefix("svg-")
    mutation = None
    if base_case in FILE_CASES:
        data = drawing_mutation(data, format, base_case)
        mutation = {"kind": "drawing_bytes", "case": base_case, "format": format,
                    "metadata_geometry_and_scale_labels_unchanged": True}
    elif base_case != "positive":
        mutation = yaml.safe_load((FIXTURE / f"mutations/{base_case}.yaml").read_text(encoding="utf-8"))
        contexts = apply_mutation(contexts, mutation)
    # Controlled derivative identity, never repair or overwrite a source/approval.
    contexts["job"]["drawing_sha256"] = sha256(data)
    inventory = {"artifact_id": "laser-source-manifest", "path": MANIFEST.relative_to(ROOT).as_posix(),
                 "kind": "synthetic_source_inventory", "authority": "reference", "revision": manifest["revision"],
                 "units": "mm", "sha256": sha256(manifest_bytes)}
    derivative = {"artifact_id": f"laser-{case}", "path": f"replay:laser/{case}/input.{format.lower()}",
                  "kind": "two_d_cutting", "authority": "derived", "revision": source["revision"],
                  "units": (None if format == "SVG" else "inch") if base_case == "wrong-units" else "mm",
                  "sha256": sha256(data)}
    return contexts, data, [inventory, source, derivative], mutation


def replay(case):
    contexts, data, artifacts, mutation = inputs(case)
    job, source = contexts["job"], artifacts[1]
    report = preflight(**contexts, drawing_bytes=data, source_revision=source["revision"])
    folder = f"docs/evaluation/laser-runs/2026-09-17-{case}"
    state = {"job_id": job["job_id"], "revision": job["revision"], "units": job["units"],
             "process_family": "laser_cutting", "source_artifact_hashes": [a["sha256"] for a in artifacts[:2]],
             "material": copy.deepcopy(contexts["material"]), "machine_profile": copy.deepcopy(contexts["machine"]),
             "controller_profile": None,
             "setup": {"context_kind": "laser_evaluation_input", "evaluation_only": True,
                       "submitted_job": copy.deepcopy(job), "submitted_process": copy.deepcopy(contexts["process"]),
                       "source_revision": source["revision"]},
             "workholding": None, "work_coordinate_system": None, "tool_library": None,
             "cam_system": None, "postprocessor": None, "post_version": None,
             "generated_manufacturing_output": artifacts[-1], "simulation_status": "not_run",
             "jurisdiction": None,
             "ip_status": {"ownership_status": "repository_authored_synthetic", "licence_status": "CC0-1.0 fixture",
                           "confidentiality": "public_test_data", "redistribution_authorized": True},
             "export_review_status": "not_reviewed", "approval_status": "not_requested",
             "verification_results": [{"check_id": "laser_partial_file_and_context", "status": "inconclusive",
                                       "summary": "Partial geometry/context evidence only; design intent, path/process applicability, beam and emission review, site context and qualified approval are unresolved.",
                                       "evidence": [f"{folder}/observed.json"]}]}
    request = {"process_family": "laser_cutting", "artifact_class": "two_d_cutting",
               "consequence_level": "execution_adjacent", "machine_known": job["machine_id"] == contexts["machine"]["machine_id"],
               "material_known": job["material_id"] == contexts["material"]["material_id"]}
    route_result = route_job(request, state)
    route_result.pop("job_state")
    return {"case": case, "mutation": mutation, "contexts": contexts, "artifacts": artifacts,
            "source_revision": source["revision"], "drawing_bytes": len(data), "raw_preflight": report,
            "state": state, "request": request, "route_result": route_result,
            "scope": "Fixed synthetic evidence replay, not agent reasoning or approval; byte preflight and generic routing are distinct"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=(*CASES, "all"))
    args = parser.parse_args()
    print(json.dumps([replay(case) for case in CASES] if args.case == "all" else replay(args.case), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
