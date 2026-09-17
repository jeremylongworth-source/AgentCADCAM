"""Bound CAD bytes and review roles; explicit fixture adapter, no CAD execution."""

import hashlib

from scripts.validate_cad_fixture_design import validate_inputs
from scripts.validate_cad_fixture_step import validate_text
from scripts.validate_cad_fixture_mesh import validate_bytes
from scripts.validate_schema_instances import validator_for
from state.state import verification_context_fingerprint


PROFILE = "cad-bracket-basic-v2"
KINDS = {"source/bracket.scad": "native_cad_source", "source/bracket.step": "neutral_solid_exchange",
         "source/bracket.stl": "mesh_derivative", "source/bracket.svg": "drawing_reference"}
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 32 * 1024 * 1024
REQUIRED_CHECKS = ("cad_provenance", "cad_interoperability", "cad_manufacturability", "cad_drawing_pmi", "cad_handoff")


def check_cad_artifacts(state, artifacts, *, catalog, fingerprint):
    # Snapshot the mapping once; immutable byte values then serve both identity
    # and geometry checks without reopening files or consulting changed entries.
    artifacts = dict(artifacts) if isinstance(artifacts, dict) else artifacts
    result = {"status": "blocked", "context_fingerprint": fingerprint, "sha256": {},
              "blockers": [], "findings": [], "file_checks": [],
              "geometry_equivalence_verified": False}

    def block(message, outcome="MISSING_CONTEXT"):
        result["blockers"].append(outcome)
        result["findings"].append(message)

    inputs = (state.get("setup") or {}).get("cad_handoff")
    valid_inputs = validator_for("cad-handoff-input.schema.json", catalog).is_valid(inputs)
    if not valid_inputs:
        block("CAD setup.cad_handoff requires structured metadata, derivation and sourced manufacturing context")
    valid_bytes = isinstance(artifacts, dict) and set(artifacts) == set(KINDS)
    if valid_bytes:
        valid_bytes = all(type(data) is bytes and data for data in artifacts.values())
    if not valid_bytes:
        block("CAD review requires the exact source/STEP/STL/drawing byte inventory; paths and passing labels are insufficient")
    elif any(len(data) > MAX_FILE_BYTES for data in artifacts.values()) or sum(map(len, artifacts.values())) > MAX_TOTAL_BYTES:
        valid_bytes = False
        block("CAD artifact bytes exceed review limits", "SOURCE_VERIFICATION_REQUIRED")
    else:
        result["sha256"] = {path: hashlib.sha256(artifacts[path]).hexdigest() for path in sorted(artifacts)}

    if valid_inputs:
        metadata, binding = inputs["metadata"], inputs["derivation"]
        if inputs["review_profile"] != PROFILE:
            block("CAD review profile is unsupported; general CAD interpretation requires a separate adapter", "SOURCE_VERIFICATION_REQUIRED")
        if any(not state.get(key) or metadata[key] != state[key] for key in ("job_id", "revision", "units")):
            block("CAD metadata identity, revision or units conflict with bounded state")
        if metadata["pmi_status"] == "unknown":
            block("CAD PMI availability is unresolved")
        elif inputs["review_profile"] == PROFILE and metadata["pmi_status"] != "not_present":
            block("CAD fixture profile has no embedded manufacturing PMI; the supplied claim conflicts")
        context = inputs["manufacturing_context"]
        if state.get("material") is not None and state["material"].get("material_id") != context["material_id"]:
            block("CAD selected material conflicts with supplied profile")
        if state.get("material") is not None and state["material"].get("process_family") != context["process_family"]:
            block("CAD selected process conflicts with supplied material profile")
        if state.get("machine_profile") is not None and state["machine_profile"].get("process_family") != context["process_family"]:
            block("CAD selected process conflicts with supplied machine profile")
        source = binding["source"]
        descriptors = [source] + [entry["artifact"] for entry in binding["derivatives"]]
        if sorted(state["source_artifact_hashes"]) != sorted(a["sha256"] for a in descriptors):
            block("CAD state hash inventory must exactly match reviewed source and derivatives", "SOURCE_VERIFICATION_REQUIRED")
        if source["path"] != "source/bracket.scad" or source["kind"] != "native_cad_source" or metadata["authoritative_artifact"] != source["path"]:
            block("CAD authoritative design must be the declared source, not a mesh or exchange derivative", "SOURCE_VERIFICATION_REQUIRED")
        if (len(descriptors) != len(KINDS) or {a["path"] for a in descriptors} != set(KINDS)
                or len({a["artifact_id"] for a in descriptors}) != len(descriptors)):
            block("CAD derivation must identify each supported artifact exactly once", "SOURCE_VERIFICATION_REQUIRED")
        for descriptor in descriptors:
            if descriptor["kind"] != KINDS.get(descriptor["path"]):
                block("CAD artifact role conflicts with the selected review profile", "SOURCE_VERIFICATION_REQUIRED")
            if descriptor["revision"] != state["revision"] or descriptor["units"] != state.get("units"):
                block("CAD artifact revision or units conflict with bounded state")
            if descriptor["sha256"] not in state["source_artifact_hashes"]:
                block("CAD artifact hash is not bound to current state", "SOURCE_VERIFICATION_REQUIRED")
            if valid_bytes and result["sha256"].get(descriptor["path"]) != descriptor["sha256"].lower():
                block("CAD bytes differ from the declared derivation identity; review before rebinding", "SOURCE_VERIFICATION_REQUIRED")
        for entry in binding["derivatives"]:
            expected_relationship = "reference_drawing" if entry["artifact"]["path"] == "source/bracket.svg" else "reconstruction"
            if entry["relationship"] != expected_relationship:
                block("CAD fixture derivation relationship conflicts with its recorded reconstruction/reference scope", "SOURCE_VERIFICATION_REQUIRED")
        output = state.get("generated_manufacturing_output")
        if output is not None and output not in descriptors:
            block("CAD selected output is not an exact member of the reviewed artifact inventory")

        # The profile is explicitly fixture-specific. Never apply its geometry
        # expectations to an unrelated part or execute its OpenSCAD source.
        if valid_bytes and inputs["review_profile"] == PROFILE:
            checks = (
                ("source_drawing_revision", lambda: validate_inputs(artifacts["source/bracket.scad"].decode("utf-8"),
                                                                   artifacts["source/bracket.svg"].decode("utf-8"), metadata)),
                ("step_envelope", lambda: validate_text(artifacts["source/bracket.step"].decode("utf-8"))),
                ("stl_envelope", lambda: validate_bytes(artifacts["source/bracket.stl"])),
            )
            for name, check in checks:
                try:
                    errors = check()
                except (UnicodeError, ValueError, OverflowError):
                    errors = ["file data could not be parsed within the selected review profile"]
                result["file_checks"].append({"check": name, "status": "failed" if errors else "passed", "findings": errors})
                if errors:
                    block(f"CAD {name}: fresh file-derived checks failed")

    schema_id = catalog[0]["handoff.schema.json"]["$id"]
    evidence_validator = validator_for("handoff.schema.json", catalog).evolve(schema={"allOf": [
        {"$ref": schema_id + "#/$defs/verification_check"},
        {"required": ["kind", "context_binding"], "properties": {"kind": {"const": "verification"}, "evidence": {"minItems": 1}}}
    ]})
    expected = verification_context_fingerprint(state)
    seen, passed = set(), set()
    for index, record in enumerate(state.get("verification_results", [])):
        label = f"CAD verification record {index}"
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
