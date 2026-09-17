"""File-derived planar geometry and declared-context laser review; never lases."""

from __future__ import annotations

import copy
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

if __package__:
    from .laser_svg_review import inspect_svg, MAX_BYTES
    from .laser_dxf_review import inspect_dxf
else:
    from laser_svg_review import inspect_svg, MAX_BYTES
    from laser_dxf_review import inspect_dxf


def _mapping(value):
    return value if isinstance(value, dict) else {}


def _unit(value):
    return {"mm": Fraction(1), "cm": Fraction(10), "in": Fraction(127, 5), "inch": Fraction(127, 5)}.get(value) if isinstance(value, str) else None


def _positive(value):
    if type(value) not in (int, float) or isinstance(value, float) and not math.isfinite(value) or value <= 0:
        return None
    return Fraction(str(value))


def preflight(job: dict[str, Any], machine: dict[str, Any], material: dict[str, Any], process: dict[str, Any],
              *, drawing_bytes: bytes | None = None, source_revision: str | None = None) -> dict[str, Any]:
    findings: list[str] = []
    blockers: list[str] = []
    if not all(isinstance(value, dict) for value in (job, machine, material, process)):
        blockers.append("MISSING_CONTEXT")
        findings.append("job, machine, material and process contexts must be objects")
    job, machine, material, process = (_mapping(value) for value in (job, machine, material, process))
    if not isinstance(source_revision, str) or not source_revision.strip() or job.get("revision") != source_revision:
        blockers.append("MISSING_CONTEXT")
        findings.append("source revision is missing or conflicts with job revision")
    drawing_format = job.get("format")
    file_review = None
    if drawing_format not in ("DXF", "SVG"):
        blockers.append("MISSING_CONTEXT")
        findings.append("2D cutting format is unknown")
    else:
        file_review = inspect_dxf(drawing_bytes) if drawing_format == "DXF" else inspect_svg(drawing_bytes)
        blockers.extend(file_review["blockers"])
        findings.extend(file_review["findings"])
        declared_hash = job.get("drawing_sha256")
        if not isinstance(declared_hash, str) or len(declared_hash) != 64 or declared_hash != file_review["sha256"]:
            blockers.append("SOURCE_VERIFICATION_REQUIRED")
            findings.append("drawing bytes do not match an explicit job drawing_sha256 identity")
    unit = _unit(job.get("units"))
    if unit is None:
        blockers.append("MISSING_CONTEXT")
        findings.append("drawing units are missing or unsupported")
    else:
        findings.append("job drawing units are explicit; physical design intent remains unverified")
        if file_review:
            declared_units = [file_review["declared_unit"]] if drawing_format == "DXF" else [
                _mapping(file_review["viewport"]).get("declared_width_unit"),
                _mapping(file_review["viewport"]).get("declared_height_unit")]
            if any(_unit(value) != unit for value in declared_units):
                blockers.append("MISSING_CONTEXT")
                findings.append("file unit declaration conflicts with job drawing units")
    if job.get("path_intent") != "cut":
        blockers.append("MISSING_CONTEXT")
        findings.append("explicit cut-path intent is required; score/mark semantics are not inferred")
    placement_known = job.get("placement_frame") == "zero_origin_working_area"
    if not placement_known:
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append("drawing-to-working-area placement frame is not explicitly declared")
    dimensions = _mapping(file_review.get("dimensions_mm")) if file_review else {}
    bounds = _mapping(file_review.get("bounds_mm")) if file_review else {}
    expected = _mapping(job.get("model_dimensions"))
    working_area = _mapping(_mapping(machine.get("capabilities")).get("working_area"))
    machine_unit = _unit(_mapping(_mapping(machine.get("lifecycle")).get("units")).get("length"))
    if machine_unit is None:
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append("machine working-area unit is missing or unsupported")
    for i, axis in enumerate("xy"):
        measured = Fraction(dimensions[axis]) if axis in dimensions else None
        declared, limit = _positive(expected.get(axis)), _positive(working_area.get(axis))
        if measured is None or measured <= 0 or declared is None or limit is None:
            blockers.append("MISSING_CONTEXT")
            findings.append(f"{axis}: measured, expected or working-area dimension is missing or invalid")
            continue
        if unit is not None and measured != declared*unit:
            blockers.append("MISSING_CONTEXT")
            findings.append(f"{axis}: file-derived physical dimension conflicts with expected design dimension")
        if machine_unit is not None and measured > limit*machine_unit:
            blockers.append("MACHINE_CONTEXT_REQUIRED")
            findings.append(f"drawing exceeds declared machine working area on {axis}")
        if placement_known and machine_unit is not None and bounds:
            if Fraction(bounds["min"][i]) < 0 or Fraction(bounds["max"][i]) > limit*machine_unit:
                blockers.append("MACHINE_CONTEXT_REQUIRED")
                findings.append(f"drawing placement exceeds declared zero-origin working area on {axis}")
    if job.get("scale_status") != "verified":
        blockers.append("MISSING_CONTEXT")
        findings.append("drawing scale is not verified")
    for field, label in (("geometry_status", "geometry"), ("open_contours", "open contours"), ("duplicate_geometry", "duplicate geometry")):
        invalid = job.get(field) != "valid" if field == "geometry_status" else job.get(field) is not False
        if invalid:
            blockers.append("MISSING_CONTEXT")
            findings.append(f"{label} is not valid")
    if job.get("unsupported_entities") != []:
        blockers.append("MISSING_CONTEXT")
        findings.append("unsupported entities are present")
    else:
        findings.append("metadata reports no unsupported entities; file-derived findings remain authoritative for this check")

    if not isinstance(job.get("machine_id"), str) or not job["machine_id"].strip() or machine.get("machine_id") != job.get("machine_id"):
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append("machine profile does not match job")
    if not isinstance(job.get("material_id"), str) or not job["material_id"].strip() or material.get("material_id") != job.get("material_id"):
        blockers.append("MISSING_CONTEXT")
        findings.append("material identity is unknown or does not match job")
    compatible_machines = _mapping(material.get("compatibility")).get("machines")
    if not isinstance(compatible_machines, list) or not machine.get("machine_id") or machine.get("machine_id") not in compatible_machines:
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append("machine/material compatibility is not established")
    compatible_processes = _mapping(material.get("compatibility")).get("process_profiles")
    if not isinstance(compatible_processes, list) or not process.get("process_profile_id") or process.get("process_profile_id") not in compatible_processes:
        blockers.append("MISSING_CONTEXT")
        findings.append("material/process profile compatibility is not established")
    if (not isinstance(job.get("process_profile_id"), str) or not job["process_profile_id"].strip()
            or process.get("process_profile_id") != job.get("process_profile_id")
            or process.get("machine_id") != job.get("machine_id") or process.get("material_id") != job.get("material_id")):
        blockers.append("MISSING_CONTEXT")
        findings.append("process profile identity or machine/material target chain conflicts with job")
    if process.get("settings_status") != "verified":
        blockers.append("SOURCE_VERIFICATION_REQUIRED")
        findings.append("laser process settings are not verified")
    else:
        findings.append("process settings have a verified declaration; actual applicability remains unverified")
    if job.get("process_profile_status") != "verified":
        blockers.append("SOURCE_VERIFICATION_REQUIRED")
        findings.append("job process profile review is unresolved")

    environment = _mapping(material.get("environmental_requirements"))
    if job.get("unsafe_material_status") != "not_indicated" or environment.get("unsafe_material_status") != "not_indicated":
        blockers.append("MISSING_CONTEXT")
        findings.append("material safety status is unresolved or unsafe")
    if job.get("ventilation_status") != "known" or environment.get("ventilation_status") != "known":
        blockers.append("MISSING_CONTEXT")
        findings.append("ventilation and fume context is unresolved")
    else:
        findings.append("ventilation has known-status declarations; applicable site evidence still requires review")
    findings.append("beam activation is outside project boundary and requires human control")
    findings.append("process-emission risk remains subject to operator review")
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
        "validation_scope": "byte identity, partial planar geometry, declared physical scale/placement and context consistency; not source equivalence, kerf, process applicability, evidence authenticity or approval",
    }


def load_contexts(root: Path) -> dict[str, dict[str, Any]]:
    return {name: json.loads((root / f"{name}.json").read_text(encoding="utf-8")) for name in ("job", "machine", "material", "process")}


def apply_mutation(contexts: dict[str, dict[str, Any]], mutation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result = copy.deepcopy(contexts)
    for key, value in (mutation.get("job_overrides") or {}).items():
        result["job"][key] = value
    for key, value in (mutation.get("material_overrides") or {}).items():
        result["material"][key] = value
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", type=Path, nargs="?", default=Path("fixtures/laser/cut-bracket/contexts/job.json"))
    parser.add_argument("--drawing", type=Path)
    parser.add_argument("--source-revision")
    args = parser.parse_args()
    try:
        contexts = {name: json.loads((args.job.parent / f"{name}.json").read_text(encoding="utf-8"))
                    for name in ("machine", "material", "process")}
        contexts["job"] = json.loads(args.job.read_text(encoding="utf-8"))
        drawing = None
        if args.drawing:
            with args.drawing.open("rb") as stream:
                drawing = stream.read(MAX_BYTES+1)
        result = preflight(**contexts, drawing_bytes=drawing, source_revision=args.source_revision)
    except (OSError, ValueError):
        result = {"status": "blocked", "blockers": ["MISSING_CONTEXT"], "findings": ["input file could not be read or parsed"],
                  "review_required": True, "execution_allowed": False}
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(1 if result["blockers"] else 0)
