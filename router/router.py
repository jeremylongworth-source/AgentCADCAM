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
    "bypass_guard",
    "disable_interlock",
    "disable_safety_system",
}
CONSEQUENCES = ("informational", "design_advisory", "manufacturing_planning", "execution_adjacent", "live_execution")
APPROVAL_STATES = ("not_requested", "pending", "approved", "invalidated", "rejected")
REVIEW_ACTIONS = {"explain", "review", "plan", "verify", "prepare_handoff"}
PROCESS_REQUIRED_CONTEXT = {
    "cnc_milling": {"machine_known": "MACHINE_CONTEXT_REQUIRED", "controller_known": "MACHINE_CONTEXT_REQUIRED", "material_known": "MISSING_CONTEXT"},
    "additive": {"machine_known": "MACHINE_CONTEXT_REQUIRED", "material_known": "MISSING_CONTEXT"},
    "laser_cutting": {"machine_known": "MACHINE_CONTEXT_REQUIRED", "material_known": "MISSING_CONTEXT"},
}


def load_routes(path: Path = ROUTE_FILE) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data["routes"]


def route(request: dict[str, Any], routes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    routes = load_routes() if routes is None else routes
    blockers: list[str] = []
    findings: list[str] = []
    if not isinstance(request, dict):
        request = {}
        blockers.append("MISSING_CONTEXT")
        findings.append("request must be an object")
    def text_field(name, default):
        value = request.get(name, default)
        if value is None and default is None:
            return None
        if not isinstance(value, str):
            blockers.append("MISSING_CONTEXT")
            findings.append(f"{name} must be a string")
            return default
        return value.strip().lower()
    family = text_field("process_family", "unknown")
    consequence = text_field("consequence_level", None)
    artifact_class = text_field("artifact_class", "unknown")
    approval_state = text_field("approval_state", "not_requested")
    action = text_field("requested_action", None)
    if approval_state not in APPROVAL_STATES:
        approval_state = "not_requested"
        blockers.append("MISSING_CONTEXT")
        findings.append("approval state is invalid")
    if action is not None and action not in LIVE_ACTIONS | REVIEW_ACTIONS:
        blockers.append("MISSING_CONTEXT")
        findings.append("requested action is unknown")
    for field in ("machine_known", "controller_known", "material_known", "jurisdiction_known", "jurisdiction_required", "generated_manufacturing_artifact"):
        if field in request and not isinstance(request[field], bool):
            blockers.append("MISSING_CONTEXT")
            findings.append(f"{field} must be boolean")
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
    if consequence not in CONSEQUENCES:
        consequence = selected.get("default_consequence", "informational")
        blockers.append("MISSING_CONTEXT")
        findings.append("consequence level is missing or invalid")
    minimum = "informational"
    if artifact_class in ("nc_program", "toolpath") or request.get("generated_manufacturing_artifact") is True:
        minimum = "execution_adjacent"
    if action in LIVE_ACTIONS:
        minimum = "live_execution"
    if CONSEQUENCES.index(consequence) < CONSEQUENCES.index(minimum):
        consequence = minimum
        findings.append("consequence raised to match the artifact or requested action")

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
    if consequence == "live_execution":
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
