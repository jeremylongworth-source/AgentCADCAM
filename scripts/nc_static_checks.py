"""Static, non-executing checks for the synthetic CNC NC fixture."""

from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path
from typing import Any


HEADER_RE = re.compile(r"\s*([A-Z_]+):\s*(.*?)\s*")
WORD_RE = re.compile(r"([A-Z])([+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+))")
ACTIVE_COMMENT_RE = re.compile(r"\s*(?:MSG|DEBUG|PRINT|LOGOPEN|LOGAPPEND|LOGCLOSE|LOG|PROBEOPEN|PROBECLOSE)(?:\s|,|$)", re.I)
REVIEWED_COMMANDS = {"G0", "G1", "G17", "G20", "G21", "G54", "G90", "M3", "M5", "M6", "M30"}
MODAL_GROUPS = ({"G0", "G1", "G2", "G3"}, {"G17", "G18", "G19"},
                {"G20", "G21"}, {"G90", "G91"}, {"G54", "G55", "G56", "G57", "G58", "G59"},
                {"M3", "M4", "M5"})


def _literal_blocks(program: str):
    """Read inert words and prologue declarations, rejecting unevaluated syntax.

    This intentionally does not evaluate parameters, expressions or subprograms.
    See docs/architecture/nc-static-review-scope.md for the supported subset.
    """
    headers, blocks, errors = {}, [], []
    code_seen = False
    delimiters = 0
    for number, line in enumerate(program.splitlines(), 1):
        code, comments, position = [], [], 0
        while position < len(line):
            char = line[position]
            if char == ";":
                if ACTIVE_COMMENT_RE.match(line[position + 1:]):
                    errors.append(f"line {number}: active comment extension requires review")
                break
            if char == "(":
                end = line.find(")", position + 1)
                if end == -1 or "(" in line[position + 1:end]:
                    errors.append(f"line {number}: malformed or nested comment")
                    break
                comments.append(line[position + 1:end])
                prefix = "".join(code).rstrip()
                suffix = line[end + 1:].lstrip()
                if (prefix and prefix[-1].isalpha()) or (prefix and suffix
                        and prefix[-1] in "0123456789.+-" and suffix[0] in "0123456789.+-"):
                    errors.append(f"line {number}: comment splits an NC word")
                position = end + 1
                continue
            code.append(char)
            position += 1
        compact = "".join(code).replace(" ", "").replace("\t", "").upper()
        for comment in comments:
            if ACTIVE_COMMENT_RE.match(comment):
                errors.append(f"line {number}: active comment extension requires review")
            match = HEADER_RE.fullmatch(comment)
            if match:
                key, value = match.groups()
                if code_seen or compact or key in headers:
                    errors.append(f"line {number}: duplicate or non-prologue header {key}")
                else:
                    headers[key] = value.strip()
        if not compact:
            continue
        if compact == "%":
            delimiters += 1
            if delimiters > 2 or (delimiters == 1 and code_seen):
                errors.append(f"line {number}: misplaced program delimiter")
            continue
        if delimiters >= 2:
            errors.append(f"line {number}: code after closing delimiter")
        code_seen = True
        words, position = [], 0
        while position < len(compact):
            match = WORD_RE.match(compact, position)
            if not match:
                errors.append(f"line {number}: unsupported or malformed NC syntax at column {position + 1}")
                break
            letter, literal = match.groups()
            value = Decimal(literal)
            if letter not in "GMNXYZTFS":
                errors.append(f"line {number}: unsupported word {letter}")
            if letter in "GMNT" and (value < 0 or value != value.to_integral_value()):
                # Decimal G codes are retained below, never truncated to another command.
                if letter != "G" or value < 0:
                    errors.append(f"line {number}: invalid {letter} number")
            words.append((letter, value))
            position = match.end()
        blocks.append((number, words))
    if delimiters == 1:
        errors.append("missing closing program delimiter")
    return headers, blocks, errors


def _command(letter: str, value: Decimal) -> str:
    spelling = format(value, "f")
    if "." in spelling:
        spelling = spelling.rstrip("0").rstrip(".")
    return letter + spelling


def review_program(program: str, contexts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    findings: list[str] = []
    blockers: list[str] = []
    job = contexts.get("job", {})
    machine = contexts.get("machine", {})
    controller = contexts.get("controller", {})
    post = contexts.get("post", {})
    setup = contexts.get("setup", {})
    tool = contexts.get("tool", {})
    headers, blocks, parse_errors = _literal_blocks(program)
    if parse_errors:
        blockers.append("SOURCE_VERIFICATION_REQUIRED")
        findings.extend(parse_errors)
    commands = {_command(letter, value) for _, words in blocks for letter, value in words if letter in "GM"}

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

    unit_commands = commands & {"G20", "G21"}
    expected_units = job.get("units")
    expected_command = "G21" if expected_units == "mm" else "G20" if expected_units in ("in", "inch") else None
    if expected_command is None or unit_commands != {expected_command}:
        blockers.append("MISSING_CONTEXT")
        findings.append("program units are missing or conflict with job units")
    else:
        findings.append(f"program units are explicit: {expected_units}")

    wcs_options = (controller.get("modes_and_offsets") or {}).get("wcs") or []
    expected_wcs = wcs_options[0] if wcs_options else None
    if not expected_wcs or expected_wcs not in commands:
        blockers.append("MISSING_CONTEXT")
        findings.append("required work coordinate system is missing")
    else:
        findings.append(f"WCS {expected_wcs} is present")

    tool_numbers = {value for _, words in blocks for letter, value in words if letter == "T"}
    known_tool = tool.get("tool_number")
    if not tool_numbers or known_tool not in tool_numbers or len(tool_numbers) != 1:
        blockers.append("MISSING_CONTEXT")
        findings.append("tool references do not reconcile with tool context")
    else:
        findings.append(f"tool number T{known_tool} reconciled")

    supported = set(controller.get("supported_commands", []))
    unsupported = sorted(commands - supported)
    if unsupported:
        blockers.append("MACHINE_CONTEXT_REQUIRED")
        findings.append(f"unsupported controller commands: {', '.join(unsupported)}")

    outside_scope = sorted(commands - REVIEWED_COMMANDS)
    if outside_scope:
        blockers.append("SOURCE_VERIFICATION_REQUIRED")
        findings.append(f"commands outside static reviewer semantics: {', '.join(outside_scope)}")

    limits = machine.get("limits") or {}
    units_mode = absolute_mode = wcs_mode = motion_mode = selected_tool = loaded_tool = None
    ended = False
    for number, words in blocks:
        block_commands = [_command(letter, value) for letter, value in words if letter in "GM"]
        values = {letter: value for letter, value in words}
        letters = [letter for letter, _ in words if letter not in "GM"]
        if len(letters) != len(set(letters)) or len(block_commands) != len(set(block_commands)):
            blockers.append("SOURCE_VERIFICATION_REQUIRED")
            findings.append(f"line {number}: repeated NC word")
        if any(len(set(block_commands) & group) > 1 for group in MODAL_GROUPS):
            blockers.append("SOURCE_VERIFICATION_REQUIRED")
            findings.append(f"line {number}: conflicting modal commands")
        if ended and words:
            blockers.append("SOURCE_VERIFICATION_REQUIRED")
            findings.append(f"line {number}: executable words after program end")
        for command in block_commands:
            if command in {"G20", "G21"}:
                units_mode = command
            elif command in {"G90", "G91"}:
                absolute_mode = command
            elif command in {"G54", "G55", "G56", "G57", "G58", "G59"}:
                wcs_mode = command
            elif command in {"G0", "G1"}:
                motion_mode = command
        if "T" in values:
            selected_tool = values["T"]
        if "M6" in block_commands:
            loaded_tool = selected_tool
            if loaded_tool is None or loaded_tool != known_tool:
                blockers.append("MISSING_CONTEXT")
                findings.append(f"line {number}: tool change lacks a known selected tool")
        if any(axis in values for axis in "XYZ"):
            if (units_mode != expected_command or absolute_mode != "G90" or not expected_wcs
                    or wcs_mode != expected_wcs or motion_mode is None
                    or loaded_tool is None or loaded_tool != known_tool):
                blockers.append("MISSING_CONTEXT")
                findings.append(f"line {number}: motion precedes required units, G90, WCS, motion mode or tool change")
            for axis in "XYZ":
                if axis not in values:
                    continue
                value = values[axis]
                limit = limits.get(axis.lower()) or {}
                if limit and not (Decimal(str(limit.get("min", "-Infinity"))) <= value <= Decimal(str(limit.get("max", "Infinity")))):
                    blockers.append("MACHINE_CONTEXT_REQUIRED")
                    findings.append(f"line {number}: {axis}{value} exceeds declared fixture coordinate bound")
        if "M30" in block_commands:
            ended = True

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
        "validation_scope": "synthetic literal NC words, selected modal prerequisites and declared coordinate bounds; not physical travel, simulation or approval verification",
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
