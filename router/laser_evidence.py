"""Fresh laser file/context checks and scoped evidence; no fetching or equipment."""

import copy
import hashlib

from scripts.laser_preflight import preflight
from scripts.laser_svg_review import MAX_BYTES
from scripts.validate_schema_instances import validator_for
from state.state import verification_context_fingerprint


REQUIRED_CHECKS = ("laser_design", "laser_paths", "laser_process", "laser_beam", "laser_emissions", "laser_output")


def check_laser_artifact(state, drawing, *, catalog, fingerprint, approval_status):
    result = {"status": "blocked", "sha256": None, "context_fingerprint": fingerprint,
              "blockers": [], "findings": [], "report": None}

    def block(message, outcome="MISSING_CONTEXT"):
        result["blockers"].append(outcome)
        result["findings"].append(message)

    setup = state.get("setup") or {}
    inputs = setup.get("laser_preflight")
    valid_inputs = validator_for("laser-preflight.schema.json", catalog).is_valid(inputs)
    if not valid_inputs:
        block("laser setup.laser_preflight requires structured job, nonempty process settings/source and source artifact")
    descriptor = state.get("generated_manufacturing_output")
    schema_id = catalog[0]["handoff.schema.json"]["$id"]
    artifact_validator = validator_for("handoff.schema.json", catalog).evolve(schema={"$ref": schema_id + "#/$defs/artifact"})
    descriptor_ok = artifact_validator.is_valid(descriptor)
    if not descriptor_ok:
        block("laser drawing descriptor is missing or violates the handoff artifact schema")
    elif (descriptor["kind"] != "two_d_cutting" or descriptor["authority"] != "derived"
          or descriptor["revision"] != state["revision"] or not descriptor.get("units")
          or descriptor["units"] != state.get("units")):
        block("laser drawing kind, authority, revision or units conflict with bounded state")
    if type(drawing) is not bytes or not drawing:
        block("actual nonempty laser drawing bytes are required; paths and passing labels are insufficient")
    elif len(drawing) > MAX_BYTES:
        block("laser drawing exceeds byte review limit", "SOURCE_VERIFICATION_REQUIRED")
    else:
        result["sha256"] = hashlib.sha256(drawing).hexdigest()
        if descriptor_ok and result["sha256"] != descriptor["sha256"].lower():
            block("actual laser bytes do not match the state-bound SHA-256 identity", "SOURCE_VERIFICATION_REQUIRED")
    if valid_inputs:
        job, source = inputs["job"], inputs["source_artifact"]
        if any(job.get(key) != state.get(key) or not state.get(key) for key in ("job_id", "revision", "units")):
            block("laser submitted job identity, revision or units conflict with bounded state")
        hashes = state["source_artifact_hashes"]
        if (source["authority"] != "authoritative" or source["revision"] != state["revision"]
                or source.get("units") != state.get("units") or source["sha256"] not in hashes):
            block("laser authoritative source identity, revision or units are not bound to current state", "SOURCE_VERIFICATION_REQUIRED")
        # Run fresh semantics even when a descriptor or source binding is wrong.
        # Never let the submitted job's raw approval flag authorize the result.
        job = copy.deepcopy(job)
        job["approval_status"] = approval_status
        report = preflight(job, state.get("machine_profile"), state.get("material"), inputs["process"],
                           drawing_bytes=drawing, source_revision=source["revision"])
        result["report"] = report
        result["blockers"].extend(report["blockers"])
        result["findings"].extend(report["findings"])

    expected = verification_context_fingerprint(state)
    # Reuse the handoff's structured verification record, adding required binding
    # and kind here; these are laser evidence roles, not CNC simulation records.
    evidence_validator = validator_for("handoff.schema.json", catalog).evolve(schema={"allOf": [
        {"$ref": schema_id + "#/$defs/verification_check"},
        {"required": ["kind", "context_binding"], "properties": {"kind": {"const": "verification"}, "evidence": {"minItems": 1}}}
    ]})
    seen, passed = set(), set()
    for index, record in enumerate(state.get("verification_results", [])):
        label = f"laser verification record {index}"
        if not evidence_validator.is_valid(record):
            block(f"{label}: structured evidence and versioned context binding are required")
            continue
        identity = record["check_id"]
        if identity in seen:
            block(f"{label}: duplicate check identity")
        seen.add(identity)
        if record["context_binding"]["fingerprint"] != expected:
            block(f"{label}: evidence binding does not match current verification inputs", "SOURCE_VERIFICATION_REQUIRED")
        elif record["status"] != "passed":
            block(f"{label}: verification is unresolved or failed")
        else:
            passed.add(identity)
    for identity in REQUIRED_CHECKS:
        if identity not in passed:
            block(f"{identity}: a current passed context-bound evidence record is required")
    result["blockers"] = sorted(set(result["blockers"]))
    result["status"] = "blocked" if result["blockers"] else "review_required"
    return result
