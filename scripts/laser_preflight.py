"""Metadata-level, non-lasing preflight checks for the laser fixture."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


def preflight(job: dict[str, Any], machine: dict[str, Any], material: dict[str, Any], process: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    blockers: list[str] = []
    if job.get("format") not in {"DXF", "SVG"}:
        blockers.append("MISSING_CONTEXT")
        findings.append("2D cutting format is unknown")
    if job.get("units") != "mm":
        blockers.append("MISSING_CONTEXT")
        findings.append("units are missing or conflict with the fixture contract")
    else:
        findings.append("units mm are explicit")
    if job.get("scale_status") != "verified":
        blockers.append("MISSING_CONTEXT")
        findings.append("drawing scale is not verified")
    for field, label in (("geometry_status", "geometry"), ("open_contours", "open contours"), ("duplicate_geometry", "duplicate geometry")):
        invalid = job.get(field) != "valid" if field == "geometry_status" else job.get(field) is not False
        if invalid:
            blockers.append("MISSING_CONTEXT")
            findings.append(f"{label} is not valid")
    if job.get("unsupported_entities"):
        blockers.append("MISSING_CONTEXT")
        findings.append("unsupported entities are present")
    else:
        findings.append("contours are closed and supported")

    if machine.get("machine_id") != job.get("machine_id"):
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append("machine profile does not match job")
    if material.get("material_id") != job.get("material_id"):
        blockers.append("MISSING_CONTEXT")
        findings.append("material identity is unknown or does not match job")
    if machine.get("machine_id") not in (material.get("compatibility") or {}).get("machines", []):
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append("machine/material compatibility is not established")
    if process.get("process_profile_id") not in (material.get("compatibility") or {}).get("process_profiles", []):
        blockers.append("MISSING_CONTEXT")
        findings.append("material/process profile compatibility is not established")
    if process.get("settings_status") != "verified":
        blockers.append("SOURCE_VERIFICATION_REQUIRED")
        findings.append("laser process settings are not verified")
    else:
        findings.append("material compatible with verified process profile")

    if job.get("unsafe_material_status") != "not_indicated":
        blockers.append("MISSING_CONTEXT")
        findings.append("material safety status is unresolved or unsafe")
    if job.get("ventilation_status") != "known":
        blockers.append("MISSING_CONTEXT")
        findings.append("ventilation and fume context is unresolved")
    else:
        findings.append("ventilation context is known")
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
    }


def load_contexts(root: Path) -> dict[str, dict[str, Any]]:
    return {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in root.glob("*.json")}


def apply_mutation(contexts: dict[str, dict[str, Any]], mutation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result = copy.deepcopy(contexts)
    for key, value in (mutation.get("job_overrides") or {}).items():
        result["job"][key] = value
    for key, value in (mutation.get("material_overrides") or {}).items():
        result["material"][key] = value
    return result


if __name__ == "__main__":
    import sys

    job_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("fixtures/laser/cut-bracket/contexts/job.json")
    print(json.dumps(preflight(**load_contexts(job_path.parent)), indent=2, sort_keys=True))
