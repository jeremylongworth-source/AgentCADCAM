"""Replay fixed additive input evidence, not agent reasoning or physical approval."""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct

import yaml

from router.job_router import route_job
from scripts.additive_preflight import apply_mutation, load_contexts, preflight
from state.state import context_fingerprint
from tests.safety.test_three_mf_review import model, package, ZIP_STORED


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures/additive/fdm-bracket"
CAD = ROOT / "fixtures/cad/bracket"
TETRA = ROOT / "fixtures/additive/prusaslicer-lab/tetrahedron-source.json"
CASES = ("positive", "non-manifold-geometry", "unsupported-material", "missing-material-profile",
         "incompatible-printer-profile", "revision-mismatch", "unsupported-build-volume", "missing-environment",
         "3mf-positive", "3mf-unit-conflict", "3mf-build-placement", "3mf-required-extension")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def tetrahedron_mesh(source):
    vertices = ''.join('<vertex ' + ' '.join(f'{axis}="{value}"' for axis, value in zip("xyz", point)) + '/>'
                       for point in source["vertices"])
    triangles = ''.join('<triangle ' + ' '.join(f'v{i}="{value}"' for i, value in enumerate(face, 1)) + '/>'
                        for face in source["triangles"])
    return f'<mesh><vertices>{vertices}</vertices><triangles>{triangles}</triangles></mesh>'


def inputs(case):
    if case not in CASES:
        raise ValueError("unknown fixed additive case")
    contexts = load_contexts(FIXTURE / "contexts")
    source_path = TETRA if case.startswith("3mf-") else CAD / "source/bracket.scad"
    source_bytes = source_path.read_bytes()
    mutation = None
    if case.startswith("3mf-"):
        source = json.loads(source_bytes)
        xml = model(mesh=tetrahedron_mesh(source))
        contexts["job"].update(job_id="additive-unit-tetrahedron", mesh_format="3MF", model_dimensions=dict(x=1, y=1, z=1))
        if case == "3mf-unit-conflict":
            xml = model(mesh=tetrahedron_mesh(source), attributes='unit="inch"')
            mutation = {"kind": "package_xml", "change": "embedded unit inch; submitted job/source mm unchanged"}
        elif case == "3mf-build-placement":
            xml = model(mesh=tetrahedron_mesh(source), build='<item objectid="1" transform="1 0 0 0 1 0 0 0 1 200 0 0"/>')
            mutation = {"kind": "package_xml", "change": "translate build by 200 model units on X"}
        elif case == "3mf-required-extension":
            xml = model(mesh=tetrahedron_mesh(source), attributes='xmlns:p="urn:agentcadcam:unsupported" requiredextensions="p"')
            mutation = {"kind": "package_xml", "change": "declare synthetic unsupported required extension"}
        mesh = package(xml, compression=ZIP_STORED)
        source_revision = source["revision"]
    else:
        mesh = (CAD / "source/bracket.stl").read_bytes()
        source_revision = json.loads((CAD / "metadata/revision.json").read_text(encoding="utf-8"))["revision"]
        if case == "non-manifold-geometry":
            count = struct.unpack_from("<I", mesh, 80)[0]
            mesh = mesh[:80] + struct.pack("<I", count - 1) + mesh[84:-50]
            mutation = {"kind": "stl_bytes", "change": "remove last binary facet and decrement count; mesh_status remains valid"}
        elif case != "positive":
            mutation = yaml.safe_load((FIXTURE / f"mutations/{case}.yaml").read_text(encoding="utf-8"))
            contexts = apply_mutation(contexts, mutation)
    # Bind the deliberately selected test derivative; never overwrite fixture files.
    contexts["job"]["mesh_sha256"] = sha256(mesh)
    source_artifact = {"artifact_id": source_path.name, "path": source_path.relative_to(ROOT).as_posix(),
                       "kind": "synthetic_geometry_definition" if case.startswith("3mf-") else "native_cad_source",
                       "authority": "authoritative", "revision": source_revision, "units": "mm", "sha256": sha256(source_bytes)}
    derivative = {"artifact_id": f"additive-{case}", "path": f"replay:additive/{case}/input.{contexts['job']['mesh_format'].lower()}",
                  "kind": "print_package" if case.startswith("3mf-") else "mesh_derivative", "authority": "derived",
                  "revision": source_revision, "units": "inch" if case == "3mf-unit-conflict" else "mm", "sha256": sha256(mesh)}
    return contexts, mesh, source_artifact, derivative, mutation


def replay(case):
    contexts, mesh, source, derivative, mutation = inputs(case)
    job = contexts["job"]
    report = preflight(**contexts, mesh_bytes=mesh, source_revision=source["revision"])
    folder = f"docs/evaluation/additive-runs/2026-09-17-{case}"
    state = {"job_id": job["job_id"], "revision": job["revision"], "units": job["mesh_units"],
             "source_artifact_hashes": [source["sha256"]], "process_family": "additive",
             "material": copy.deepcopy(contexts["material"]), "machine_profile": copy.deepcopy(contexts["printer"]),
             "controller_profile": None,
             "setup": {"context_kind": "additive_evaluation_input", "evaluation_only": True,
                       "submitted_job": copy.deepcopy(job), "source_revision": source["revision"]},
             "workholding": None, "work_coordinate_system": None, "tool_library": None, "cam_system": None,
             "postprocessor": None, "post_version": None, "generated_manufacturing_output": derivative,
             "simulation_status": "not_run", "jurisdiction": None,
             "ip_status": {"ownership_status": "repository_authored_synthetic", "licence_status": "CC0-1.0 fixture",
                           "confidentiality": "public_test_data", "redistribution_authorized": True},
             "export_review_status": "not_reviewed", "approval_status": "not_requested",
             "verification_results": [{"check_id": "additive_partial_geometry_and_context", "status": "inconclusive",
                                       "summary": "File-derived partial evidence only; profile, intent, slicer, orientation/support, environment and qualified review are unresolved.",
                                       "evidence": [f"{folder}/observed.json"]}]}
    request = {"process_family": "additive", "artifact_class": "mesh", "consequence_level": "execution_adjacent",
               "machine_known": job["printer_id"] == contexts["printer"]["machine_id"],
               "material_known": job["material_id"] == contexts["material"]["material_id"]}
    route_result = route_job(request, state)
    route_result.pop("job_state")
    return {"case": case, "mutation": mutation, "contexts": contexts, "source_revision": source["revision"],
            "artifacts": [source, derivative], "mesh_bytes": len(mesh), "raw_preflight": report,
            "state": state, "context_fingerprint": context_fingerprint(state), "request": request,
            "route_result": route_result,
            "scope": "Fixed synthetic evidence replay; additive byte findings and generic routing remain distinct; not an approval API"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=(*CASES, "all"))
    args = parser.parse_args()
    results = [replay(case) for case in CASES] if args.case == "all" else [replay(args.case)]
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
