"""Bind inert NC bytes to declared state before a fresh static review."""

from __future__ import annotations

import hashlib

from scripts.nc_static_checks import review_program
from scripts.validate_schema_instances import validator_for


def check_nc_artifact(state, program, *, catalog, fingerprint, approval_status, context_ready):
    """No filesystem lookup, program execution, persistence or approval creation."""
    result = {"status": "not_run", "sha256": None, "context_fingerprint": fingerprint,
              "blockers": [], "findings": [], "report": None}

    def block(message, outcome="MISSING_CONTEXT"):
        result["blockers"].append(outcome)
        result["findings"].append(message)

    descriptor = state.get("generated_manufacturing_output")
    handoff_id = catalog[0]["handoff.schema.json"]["$id"]
    validator = validator_for("handoff.schema.json", catalog).evolve(schema={"$ref": handoff_id + "#/$defs/artifact"})
    descriptor_ok = validator.is_valid(descriptor)
    if not descriptor_ok:
        block("NC artifact descriptor is missing or violates the handoff artifact schema")
    elif (descriptor["kind"] != "nc_program" or descriptor["authority"] != "derived"
          or descriptor["revision"] != state["revision"]
          or not descriptor.get("units") or descriptor["units"] != state.get("units")):
        block("NC artifact kind, authority, revision or units conflict with the bounded job")
    if not isinstance(program, bytes) or not program:
        block("actual nonempty NC bytes are required; a path, text label or passing declaration is insufficient")
    else:
        result["sha256"] = hashlib.sha256(program).hexdigest()
        if descriptor_ok and result["sha256"] != descriptor["sha256"].lower():
            block("actual NC bytes do not match the state-bound SHA-256 identity", "SOURCE_VERIFICATION_REQUIRED")
    if result["blockers"]:
        result["status"] = "blocked"
        result["blockers"] = sorted(set(result["blockers"]))
        return result
    if not context_ready:
        block("NC static review was not run because required context is unresolved")
        return result
    tools = state["tool_library"]["tools"]
    if len(tools) != 1:
        block("the current static reviewer requires exactly one tool; multi-tool programs need additional review semantics",
              "SOURCE_VERIFICATION_REQUIRED")
        return result
    try:
        text = program.decode("utf-8", errors="strict")
    except UnicodeError:
        block("NC bytes are not valid UTF-8; no lossy decoding was attempted", "SOURCE_VERIFICATION_REQUIRED")
        return result
    contexts = {
        "job": {key: state.get(key) for key in ("job_id", "revision", "units", "simulation_status")},
        "machine": state["machine_profile"], "controller": state["controller_profile"],
        "setup": state["setup"], "tool": tools[0], "post": state["postprocessor"],
    }
    # Use the router's scoped record decision, never the state's raw approval flag.
    contexts["job"]["approval_status"] = approval_status
    report = review_program(text, contexts, selected_wcs=state["work_coordinate_system"]["code"])
    result.update(status=report["status"], report=report, blockers=report["blockers"], findings=report["findings"])
    return result
