"""Deterministic, non-executing workflow router."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROUTE_FILE = Path(__file__).with_name("routes.yaml")
LIVE_ACTIONS = {
    "jog",
    "upload_program",
    "change_offsets",
    "activate_spindle",
    "activate_laser",
    "start_cycle",
    "control_machine",
}
PROCESS_REQUIRED_CONTEXT = {
    "cnc_milling": {"machine_known": "MACHINE_CONTEXT_REQUIRED", "controller_known": "MACHINE_CONTEXT_REQUIRED", "material_known": "MISSING_CONTEXT"},
    "additive": {"machine_known": "MACHINE_CONTEXT_REQUIRED", "material_known": "MISSING_CONTEXT"},
    "laser_cutting": {"machine_known": "MACHINE_CONTEXT_REQUIRED", "material_known": "MISSING_CONTEXT"},
}


def load_routes(path: Path = ROUTE_FILE) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data["routes"]


def route(request: dict[str, Any], routes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    routes = routes or load_routes()
    family = request.get("process_family", "unknown")
    consequence = request.get("consequence_level")
    artifact_class = request.get("artifact_class", "unknown")
    approval_state = request.get("approval_state", "not_requested")
    blockers: list[str] = []
    findings: list[str] = []
    selected = next((item for item in routes if item.get("process_family") == family), None)
    if selected is None:
        selected = next(item for item in routes if item.get("process_family") == "unknown")
        blockers.append("MISSING_CONTEXT")
        findings.append("process family is unknown")
    elif family == "unknown":
        blockers.append("MISSING_CONTEXT")
        findings.append("process family is unknown")
    elif artifact_class not in selected.get("artifact_classes", []) and artifact_class != "unknown":
        blockers.append("MISSING_CONTEXT")
        findings.append("artifact class is not valid for the selected process family")
    if consequence not in {"informational", "design_advisory", "manufacturing_planning", "execution_adjacent", "live_execution"}:
        consequence = selected.get("default_consequence", "informational")
        blockers.append("MISSING_CONTEXT")
        findings.append("consequence level is missing or invalid")

    for field, blocker in PROCESS_REQUIRED_CONTEXT.get(family, {}).items():
        if request.get(field) is not True:
            blockers.append(blocker)
            findings.append(f"{field} is not confirmed")
    if request.get("jurisdiction_required") is True and request.get("jurisdiction_known") is not True:
        blockers.append("REGULATORY_REVIEW_REQUIRED")
        findings.append("jurisdictional review context is not known")
    if consequence in {"execution_adjacent", "live_execution"} and approval_state != "approved":
        blockers.append("HUMAN_APPROVAL_REQUIRED")
        findings.append("human approval is not recorded")
    if consequence == "live_execution" or request.get("requested_action") in LIVE_ACTIONS:
        blockers.append("BLOCK_EXECUTION")
        findings.append("live physical execution is outside the project boundary")

    checks = {
        "cad_handoff": ["provenance", "interoperability", "manufacturability", "drawing_pmi"],
        "cnc_milling": ["machine_match", "setup", "tooling", "postprocessor", "nc_static", "simulation", "human_approval"],
        "additive": ["provenance", "mesh_integrity", "printer_material_match", "slicer_readiness", "human_approval"],
        "laser_cutting": ["geometry", "machine_material_match", "process_profile", "ventilation", "human_approval"],
        "unknown": ["intake_and_scope"],
    }
    blockers = sorted(set(blockers))
    return {
        "route_id": selected.get("id"),
        "process_family": selected.get("process_family"),
        "skillset": selected.get("skillset"),
        "consequence_level": consequence,
        "approval_state": approval_state,
        "required_checks": checks[selected.get("process_family", "unknown")],
        "blockers": blockers,
        "findings": findings,
        "review_required": True,
        "execution_allowed": False,
    }


if __name__ == "__main__":
    import json
    import sys

    request = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    print(json.dumps(route(request), indent=2, sort_keys=True))
