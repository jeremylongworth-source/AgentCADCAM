"""Static, non-executing checks for the synthetic CNC NC fixture."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


HEADER_RE = re.compile(r"\(\s*([A-Z_]+):\s*([^)]*?)\s*\)")
COMMAND_RE = re.compile(r"\b([GM]\d+)\b")
TOOL_RE = re.compile(r"\bT(\d+)\s+M6\b")
COORD_RE = re.compile(r"\b([XYZ])\s*(-?(?:\d+(?:\.\d*)?|\.\d+))\b")


def _headers(program: str) -> dict[str, str]:
    return {key: value.strip() for key, value in HEADER_RE.findall(program)}


def review_program(program: str, contexts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    findings: list[str] = []
    blockers: list[str] = []
    job = contexts.get("job", {})
    machine = contexts.get("machine", {})
    controller = contexts.get("controller", {})
    post = contexts.get("post", {})
    setup = contexts.get("setup", {})
    tool = contexts.get("tool", {})
    headers = _headers(program)

    if headers.get("JOB") != job.get("job_id"):
        blockers.append("MISSING_CONTEXT")
        findings.append("program job identity does not match context")
    if headers.get("REVISION") != job.get("revision"):
        blockers.append("MISSING_CONTEXT")
        findings.append("program revision does not match job revision")
    if headers.get("MACHINE") != machine.get("machine_id"):
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append("program machine identity does not match machine context")
    if headers.get("CONTROLLER") != controller.get("controller_id"):
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append("program controller identity does not match controller context")
    if headers.get("POST") != post.get("post_id"):
        blockers.append("SOURCE_VERIFICATION_REQUIRED")
        findings.append("program post identity does not match post context")
    if headers.get("SETUP") != setup.get("setup_id"):
        blockers.append("MISSING_CONTEXT")
        findings.append("program setup identity does not match setup context")

    unit_commands = set(re.findall(r"\bG(?:20|21)\b", program))
    expected_units = job.get("units")
    expected_command = "G21" if expected_units == "mm" else "G20" if expected_units in ("in", "inch") else None
    if expected_command is None or unit_commands != {expected_command}:
        blockers.append("MISSING_CONTEXT")
        findings.append("program units are missing or conflict with job units")
    else:
        findings.append(f"program units are explicit: {expected_units}")

    expected_wcs = (controller.get("modes_and_offsets") or {}).get("wcs", [None])[0]
    if not expected_wcs or expected_wcs not in program:
        blockers.append("MISSING_CONTEXT")
        findings.append("required work coordinate system is missing")
    else:
        findings.append(f"WCS {expected_wcs} is present")

    tool_numbers = {int(value) for value in TOOL_RE.findall(program)}
    known_tool = tool.get("tool_number")
    if not tool_numbers or known_tool not in tool_numbers or len(tool_numbers) != 1:
        blockers.append("MISSING_CONTEXT")
        findings.append("tool references do not reconcile with tool context")
    else:
        findings.append(f"tool number T{known_tool} reconciled")

    supported = set(controller.get("supported_commands", []))
    commands = set(COMMAND_RE.findall(program))
    unsupported = sorted(commands - supported)
    if unsupported:
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append(f"unsupported controller commands: {', '.join(unsupported)}")

    limits = machine.get("limits") or {}
    for axis, value_text in COORD_RE.findall(program):
        value = float(value_text)
        limit = limits.get(axis.lower()) or {}
        if limit and not (float(limit.get("min", float("-inf"))) <= value <= float(limit.get("max", float("inf")))):
            blockers.append("MACHINE_CONTEXT_REQUIRED")
            findings.append(f"{axis}{value_text} exceeds machine limit")

    for command in ("M3", "M5"):
        if command in commands:
            findings.append(f"{command} present; human review required for spindle state")
    if post.get("validation_state") != "verified":
        blockers.append("SOURCE_VERIFICATION_REQUIRED")
        findings.append("postprocessor validation is not verified")
    if job.get("simulation_status") != "verified":
        blockers.append("SIMULATION_REQUIRED")
        findings.append("simulation evidence is not verified")
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
    contexts: dict[str, dict[str, Any]] = {}
    for path in root.glob("*.json"):
        contexts[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    return contexts


def apply_mutation(program: str, mutation: dict[str, Any]) -> str:
    for replacement in mutation.get("replacements", []) or []:
        program = program.replace(replacement["from"], replacement["to"], 1)
    return program


if __name__ == "__main__":
    import json as json_module
    import sys

    program_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("fixtures/cnc/mill-bracket/programs/positive.nc")
    context_path = program_path.parent.parent / "contexts"
    result = review_program(program_path.read_text(encoding="utf-8"), load_contexts(context_path))
    print(json_module.dumps(result, indent=2, sort_keys=True))
