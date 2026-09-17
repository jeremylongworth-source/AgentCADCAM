"""Fresh additive file/context and scoped evidence checks; never slice or print."""

import copy
import hashlib

from scripts.additive_preflight import preflight
from scripts.stl_mesh_review import MAX_BYTES
from scripts.validate_schema_instances import validator_for
from state.state import verification_context_fingerprint


REQUIRED_CHECKS = ("additive_design", "additive_geometry", "additive_orientation", "additive_supports",
                   "additive_slicer", "additive_environment", "additive_output")


def check_additive_artifact(state, mesh, *, catalog, fingerprint, approval_status):
    result = {"status": "blocked", "sha256": None, "context_fingerprint": fingerprint,
              "blockers": [], "findings": [], "report": None}

    def block(message, outcome="MISSING_CONTEXT"):
        result["blockers"].append(outcome)
        result["findings"].append(message)

    inputs = (state.get("setup") or {}).get("additive_preflight")
    valid_inputs = validator_for("additive-preflight.schema.json", catalog).is_valid(inputs)
    if not valid_inputs:
        block("additive setup.additive_preflight requires structured job, versioned slicer settings/source and source artifact")
    descriptor = state.get("generated_manufacturing_output")
    schema_id = catalog[0]["handoff.schema.json"]["$id"]
    artifact_validator = validator_for("handoff.schema.json", catalog).evolve(schema={"$ref": schema_id + "#/$defs/artifact"})
    descriptor_ok = artifact_validator.is_valid(descriptor)
    if not descriptor_ok:
        block("additive artifact descriptor is missing or violates the handoff artifact schema")
    elif (descriptor["kind"] not in ("mesh_derivative", "print_package") or descriptor["authority"] != "derived"
          or descriptor["revision"] != state["revision"] or not descriptor.get("units")
          or descriptor["units"] != state.get("units")):
        block("additive artifact kind, authority, revision or units conflict with bounded state")
    if type(mesh) is not bytes or not mesh:
        block("actual nonempty additive mesh/package bytes are required; paths and passing labels are insufficient")
    elif len(mesh) > MAX_BYTES:
        block("additive artifact exceeds byte review limit", "SOURCE_VERIFICATION_REQUIRED")
    else:
        result["sha256"] = hashlib.sha256(mesh).hexdigest()
        if descriptor_ok and result["sha256"] != descriptor["sha256"].lower():
            block("actual additive bytes do not match the state-bound SHA-256 identity", "SOURCE_VERIFICATION_REQUIRED")
    if valid_inputs:
        job, source, slicer = inputs["job"], inputs["source_artifact"], inputs["slicer_profile"]
        if (any(job.get(key) != state.get(key) or not state.get(key) for key in ("job_id", "revision"))
                or not state.get("units") or job.get("mesh_units") != state.get("units")):
            block("additive submitted job identity, revision or units conflict with bounded state")
        expected_kind = "mesh_derivative" if job.get("mesh_format") == "STL" else "print_package" if job.get("mesh_format") == "3MF" else None
        if descriptor_ok and descriptor["kind"] != expected_kind:
            block("additive descriptor kind conflicts with the selected STL/3MF format")
        if (source["authority"] != "authoritative" or source["revision"] != state["revision"]
                or source.get("units") != state.get("units") or source["sha256"] not in state["source_artifact_hashes"]):
            block("additive authoritative source identity, revision or units are not bound to current state", "SOURCE_VERIFICATION_REQUIRED")
        if (slicer["profile_id"] != job.get("slicer_profile_id") or slicer["printer_id"] != job.get("printer_id")
                or slicer["material_id"] != job.get("material_id")):
            block("additive slicer profile selection or printer/material target chain conflicts with job")
        material = state.get("material") if isinstance(state.get("material"), dict) else {}
        compatibility = material.get("compatibility") if isinstance(material.get("compatibility"), dict) else {}
        profiles = compatibility.get("slicer_profiles")
        if not isinstance(profiles, list) or slicer["profile_id"] not in profiles:
            block("additive material/slicer profile compatibility is not established")
        environment = material.get("environmental_requirements")
        if not isinstance(environment, dict) or environment.get("environment_status") != "known":
            block("additive material environmental context is unresolved")
        job = copy.deepcopy(job)
        job["approval_status"] = approval_status
        report = preflight(job, state.get("machine_profile"), state.get("material"),
                           source_revision=source["revision"], mesh_bytes=mesh)
        result["report"] = report
        result["blockers"].extend(report["blockers"])
        result["findings"].extend(report["findings"])

    expected = verification_context_fingerprint(state)
    evidence_validator = validator_for("handoff.schema.json", catalog).evolve(schema={"allOf": [
        {"$ref": schema_id + "#/$defs/verification_check"},
        {"required": ["kind", "context_binding"], "properties": {"kind": {"const": "verification"}, "evidence": {"minItems": 1}}}
    ]})
    seen, passed = set(), set()
    for index, record in enumerate(state.get("verification_results", [])):
        label = f"additive verification record {index}"
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
