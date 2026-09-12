"""Metadata-level, non-printing preflight checks for the FDM fixture."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


def preflight(job: dict[str, Any], printer: dict[str, Any], material: dict[str, Any], source_revision: str = "A") -> dict[str, Any]:
    findings: list[str] = []
    blockers: list[str] = []
    if job.get("revision") != source_revision:
        blockers.append("MISSING_CONTEXT")
        findings.append("job revision does not match source revision")
    if job.get("mesh_format") not in {"STL", "3MF"}:
        blockers.append("MISSING_CONTEXT")
        findings.append("mesh/package format is unknown")
    if job.get("mesh_status") != "valid":
        blockers.append("MISSING_CONTEXT")
        findings.append("mesh integrity is not valid")
    if job.get("mesh_units") not in {"mm", "in", "inch"}:
        blockers.append("MISSING_CONTEXT")
        findings.append("mesh units are missing")
    else:
        findings.append(f"{job['mesh_format']} is treated as a print derivative")

    if printer.get("machine_id") != job.get("printer_id"):
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append("printer profile does not match job")
    if material.get("material_id") != job.get("material_id"):
        blockers.append("MISSING_CONTEXT")
        findings.append("material profile does not match job")
    supported_materials = (printer.get("capabilities") or {}).get("materials", [])
    if job.get("material_id") not in supported_materials:
        blockers.append("MISSING_CONTEXT")
        findings.append("printer/material compatibility is not established")
    compatible_printers = (material.get("compatibility") or {}).get("printers", [])
    if printer.get("machine_id") not in compatible_printers:
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append("material/printer compatibility is not established")

    dimensions = job.get("model_dimensions") or {}
    build = (printer.get("capabilities") or {}).get("build_volume") or {}
    for axis in ("x", "y", "z"):
        if axis not in dimensions or axis not in build:
            blockers.append("MACHINE_CONTEXT_REQUIRED")
            findings.append("model or build-volume dimension is missing")
            continue
        if float(dimensions[axis]) > float(build[axis]):
            blockers.append("MACHINE_CONTEXT_REQUIRED")
            findings.append(f"model exceeds printer build volume on {axis}")
    if not any(item == "MACHINE_CONTEXT_REQUIRED" for item in blockers):
        findings.append("printer build volume is compatible")

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
    }


def load_contexts(root: Path) -> dict[str, dict[str, Any]]:
    return {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in root.glob("*.json")}


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
    import sys

    job_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("fixtures/additive/fdm-bracket/contexts/job.json")
    result = preflight(**load_contexts(job_path.parent))
    print(json.dumps(result, indent=2, sort_keys=True))
