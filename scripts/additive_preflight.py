"""File-derived STL/3MF and declared-context FDM preflight; never prints or repairs."""

from __future__ import annotations

import copy
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

if __package__:
    from .stl_mesh_review import inspect_stl, MAX_BYTES
    from .three_mf_review import inspect_3mf, UNITS
else:
    from stl_mesh_review import inspect_stl, MAX_BYTES
    from three_mf_review import inspect_3mf, UNITS


def _mapping(value):
    return value if isinstance(value, dict) else {}


def _positive(value):
    if (type(value) not in (int, float)
            or isinstance(value, float) and not math.isfinite(value) or value <= 0):
        return None
    return Fraction(str(value))


def _unit(value):
    if not isinstance(value, str):
        return None
    return {"mm": Fraction(1), "in": Fraction(127, 5), **UNITS}.get(value)


def preflight(job: dict[str, Any], printer: dict[str, Any], material: dict[str, Any], source_revision: str | None = None,
              *, mesh_bytes: bytes | None = None) -> dict[str, Any]:
    findings: list[str] = []
    blockers: list[str] = []
    malformed = not all(isinstance(value, dict) for value in (job, printer, material))
    job, printer, material = (_mapping(value) for value in (job, printer, material))
    if malformed:
        blockers.append("MISSING_CONTEXT")
        findings.append("job, printer and material contexts must be objects")
    if not isinstance(source_revision, str) or not source_revision.strip() or job.get("revision") != source_revision:
        blockers.append("MISSING_CONTEXT")
        findings.append("source revision is missing or conflicts with job revision")
    mesh_format = job.get("mesh_format")
    file_review = None
    if mesh_format in ("STL", "3MF"):
        file_review = inspect_stl(mesh_bytes) if mesh_format == "STL" else inspect_3mf(mesh_bytes)
        blockers.extend(file_review["blockers"])
        findings.extend(file_review["findings"])
        declared_hash = job.get("mesh_sha256")
        if (not isinstance(declared_hash, str) or len(declared_hash) != 64
                or declared_hash != file_review["sha256"]):
            blockers.append("SOURCE_VERIFICATION_REQUIRED")
            findings.append(f"{mesh_format} bytes do not match an explicit job mesh_sha256 identity")
    else:
        blockers.append("MISSING_CONTEXT")
        findings.append("mesh/package format is unknown")
    if job.get("mesh_status") != "valid":
        blockers.append("MISSING_CONTEXT")
        findings.append("mesh integrity is not valid")
    mesh_unit = _unit(job.get("mesh_units"))
    if mesh_unit is None:
        blockers.append("MISSING_CONTEXT")
        findings.append("mesh units are missing")
    else:
        findings.append("mesh/package remains a print derivative, not authoritative design intent")
    if mesh_format == "3MF" and file_review["unit_scale_mm"] is not None:
        embedded_unit = Fraction(file_review["unit_scale_mm"])
        if mesh_unit != embedded_unit:
            blockers.append("MISSING_CONTEXT")
            findings.append("3MF embedded/default unit conflicts with declared job mesh units")
        # Embedded Core semantics govern the geometry even when job metadata lies.
        mesh_unit = embedded_unit

    if printer.get("machine_id") != job.get("printer_id"):
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append("printer profile does not match job")
    if material.get("material_id") != job.get("material_id"):
        blockers.append("MISSING_CONTEXT")
        findings.append("material profile does not match job")
    capabilities = _mapping(printer.get("capabilities"))
    supported_materials = capabilities.get("materials")
    if not isinstance(supported_materials, list) or not job.get("material_id") or job.get("material_id") not in supported_materials:
        blockers.append("MISSING_CONTEXT")
        findings.append("printer/material compatibility is not established")
    compatible_printers = _mapping(material.get("compatibility")).get("printers")
    if not isinstance(compatible_printers, list) or not printer.get("machine_id") or printer.get("machine_id") not in compatible_printers:
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append("material/printer compatibility is not established")

    declared_dimensions = _mapping(job.get("model_dimensions"))
    dimensions = _mapping(file_review.get("dimensions_exact")) if file_review else {}
    build = _mapping(capabilities.get("build_volume"))
    printer_unit = _unit(_mapping(_mapping(printer.get("lifecycle")).get("units")).get("length"))
    envelope_ok = True
    if printer_unit is None:
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append("printer build-volume length unit is missing or unsupported")
        envelope_ok = False
    for axis in ("x", "y", "z"):
        # Exact rational strings come only from our byte inspector, not metadata.
        measured = Fraction(dimensions[axis]) if axis in dimensions else None
        if measured is not None and measured <= 0:
            measured = None
        declared, limit = (_positive(mapping.get(axis)) for mapping in (declared_dimensions, build))
        if measured is None or declared is None or limit is None:
            blockers.append("MACHINE_CONTEXT_REQUIRED")
            findings.append(f"{axis}: measured, declared or build-volume dimension is missing, nonfinite or nonpositive")
            envelope_ok = False
            continue
        if measured != declared:
            blockers.append("MISSING_CONTEXT")
            findings.append(f"{axis}: file-derived dimension conflicts with declared model dimension")
            envelope_ok = False
        if mesh_unit is None or printer_unit is None:
            envelope_ok = False
            continue
        if measured * mesh_unit > limit * printer_unit:
            blockers.append("MACHINE_CONTEXT_REQUIRED")
            findings.append(f"model exceeds printer build volume on {axis} after explicit unit conversion")
            envelope_ok = False
        if mesh_format == "3MF" and file_review["bounds_exact"] is not None:
            axis_index = "xyz".index(axis)
            low = Fraction(file_review["bounds_exact"]["min"][axis_index]) * mesh_unit
            high = Fraction(file_review["bounds_exact"]["max"][axis_index]) * mesh_unit
            if low < 0 or high > limit * printer_unit:
                blockers.append("MACHINE_CONTEXT_REQUIRED")
                findings.append(f"3MF transformed build placement exceeds the declared zero-origin envelope on {axis}")
                envelope_ok = False
    if envelope_ok:
        findings.append("file-derived axis-aligned extents fit declared build dimensions; placement, supports and usable bed shape remain unverified")

    for field, label in (("slicer_profile_status", "slicer profile"), ("orientation_status", "orientation"), ("support_status", "support plan")):
        if job.get(field) != "verified" and job.get(field) != "reviewed":
            blockers.append("MISSING_CONTEXT")
            findings.append(f"{label} is not ready")
    if job.get("environment_status") != "known":
        blockers.append("MISSING_CONTEXT")
        findings.append("environmental context is unresolved")
    if job.get("approval_status") != "approved":
        blockers.append("HUMAN_APPROVAL_REQUIRED")
        findings.append("human approval is not recorded")

    blockers = sorted(set(blockers))
    return {
        "status": "blocked" if blockers else "review_required",
        "blockers": blockers,
        "findings": findings,
        "review_required": True,
        "execution_allowed": False,
        "file_review": file_review,
        "validation_scope": "STL/3MF byte identity, partial topology, unit-aware extents, supported Core build placement and metadata compatibility; not slicing, usable-bed clearance, self-intersection, evidence authenticity or print approval",
    }


def load_contexts(root: Path) -> dict[str, dict[str, Any]]:
    return {name: json.loads((root / f"{name}.json").read_text(encoding="utf-8")) for name in ("job", "printer", "material")}


def apply_mutation(contexts: dict[str, dict[str, Any]], mutation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result = copy.deepcopy(contexts)
    for key, value in (mutation.get("job_overrides") or {}).items():
        result["job"][key] = value
    for key, value in (mutation.get("printer_overrides") or {}).items():
        if key == "build_volume":
            result["printer"].setdefault("capabilities", {})["build_volume"] = value
        else:
            result["printer"][key] = value
    for key, value in (mutation.get("material_overrides") or {}).items():
        result["material"][key] = value
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", type=Path, nargs="?", default=Path("fixtures/additive/fdm-bracket/contexts/job.json"))
    parser.add_argument("--mesh", type=Path)
    parser.add_argument("--source-revision")
    args = parser.parse_args()
    try:
        contexts = {name: json.loads((args.job.parent / f"{name}.json").read_text(encoding="utf-8"))
                    for name in ("printer", "material")}
        contexts["job"] = json.loads(args.job.read_text(encoding="utf-8"))
        mesh = None
        if args.mesh is not None:
            with args.mesh.open("rb") as stream:
                mesh = stream.read(MAX_BYTES + 1)
        result = preflight(**contexts, mesh_bytes=mesh, source_revision=args.source_revision)
    except (OSError, ValueError):
        result = {"status": "blocked", "blockers": ["MISSING_CONTEXT"], "findings": ["input file could not be read or parsed"],
                  "review_required": True, "execution_allowed": False}
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(1 if result["blockers"] else 0)
