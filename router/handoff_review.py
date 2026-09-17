"""Cross-check a serialized handoff against current routing; never issue approval."""

import copy

from router.job_router import route_job
from scripts.validate_schema_instances import load_catalog, validator_for


REVIEW_FIELDS = ("handoff_id", "artifacts", "assumptions", "simulation", "human_review")


def review_handoff(handoff, current_state, approval=None, *, previous_state=None,
                   required_scope="manufacturing_handoff", nc_program=None,
                   laser_drawing=None, additive_mesh=None, cad_artifacts=None):
    """Return a review-only decision and copy; never fetch evidence or re-sign data."""
    catalog = load_catalog()
    errors = []
    for failure in validator_for("handoff.schema.json", catalog).iter_errors(handoff):
        path = "/".join(str(item) for item in failure.absolute_path) or "<root>"
        errors.append(f"handoff/{path}: {failure.validator} validation failed")
    valid_handoff = not errors
    supplied = handoff if isinstance(handoff, dict) else {}
    request = {"process_family": supplied.get("process_family"), "artifact_class": "handoff",
               "consequence_level": supplied.get("consequence_level"), "requested_action": "prepare_handoff",
               "generated_manufacturing_artifact": True, "machine_known": True,
               "controller_known": True, "material_known": True, "jurisdiction_known": True}
    route = route_job(request, current_state, approval, previous_state=previous_state,
                      required_scope=required_scope, nc_program=nc_program, laser_drawing=laser_drawing,
                      additive_mesh=additive_mesh, cad_artifacts=cad_artifacts)
    blockers, findings = set(route["blockers"]), list(route["findings"])

    def block(message, outcome="MISSING_CONTEXT"):
        blockers.add(outcome)
        findings.append(message)

    if errors:
        block("handoff schema is invalid; no validated package copy is returned")
    if valid_handoff:
        blockers.update(handoff["blockers"])
    state = route["job_state"]
    if valid_handoff and state is not None:
        for field in ("job_id", "revision", "units", "process_family"):
            if handoff[field] != state.get(field):
                block(f"handoff {field} conflicts with current state")
        if handoff["context_fingerprint"] != route["context_fingerprint"]:
            block("handoff fingerprint does not match current state; preserve the reviewed identity", "SOURCE_VERIFICATION_REQUIRED")
        if handoff["consequence_level"] != route["consequence_level"]:
            block("handoff consequence conflicts with current routing classification")
        if not set(route["blockers"]).issubset(handoff["blockers"]):
            block("handoff omits current routing blockers")
        snapshot = (state.get("setup") or {}).get("handoff_review")
        if not validator_for("handoff-review.schema.json", catalog).is_valid(snapshot):
            block("setup.handoff_review must bind the package review details before approval")
        else:
            for field in REVIEW_FIELDS:
                if handoff[field] != snapshot[field]:
                    block(f"handoff {field} differs from the state-bound review details", "SOURCE_VERIFICATION_REQUIRED")
        if handoff["verification"] != state.get("verification_results", []):
            block("handoff verification differs from current state evidence", "SOURCE_VERIFICATION_REQUIRED")
        if handoff["simulation"]["status"] != state.get("simulation_status"):
            block("handoff simulation status conflicts with current state", "SIMULATION_REQUIRED")
        if handoff["simulation"]["status"] not in ("verified", "not_required"):
            block("handoff simulation requirement is unresolved", "SIMULATION_REQUIRED")
        if any(item["status"] != "resolved" for item in handoff["assumptions"]):
            block("handoff has unresolved or rejected assumptions")
        if required_scope not in handoff["human_review"]["scope"]:
            block("handoff human review does not cover the requested scope", "HUMAN_APPROVAL_REQUIRED")

        artifacts = handoff["artifacts"]
        if (len({a["artifact_id"] for a in artifacts}) != len(artifacts)
                or len({a["path"] for a in artifacts}) != len(artifacts)):
            block("handoff artifact identifiers and locators must be unique")
        expected_hashes = set(state["source_artifact_hashes"])
        output = state.get("generated_manufacturing_output")
        artifact_schema = {"$ref": catalog[0]["handoff.schema.json"]["$id"] + "#/$defs/artifact"}
        if output is not None:
            if not validator_for("handoff.schema.json", catalog).evolve(schema=artifact_schema).is_valid(output):
                block("current manufacturing output descriptor is invalid")
            else:
                expected_hashes.add(output["sha256"])
                if output not in artifacts:
                    block("handoff does not preserve the exact current output descriptor", "SOURCE_VERIFICATION_REQUIRED")
        if {a["sha256"] for a in artifacts} != expected_hashes:
            block("handoff artifact hashes do not cover exactly the current source/output inventory", "SOURCE_VERIFICATION_REQUIRED")
        if not any(a["authority"] == "authoritative" and a["sha256"] in state["source_artifact_hashes"] for a in artifacts):
            block("handoff lacks a declared authoritative source bound to current state", "SOURCE_VERIFICATION_REQUIRED")
        for artifact in artifacts:
            if artifact["authority"] == "unknown":
                block("handoff artifact authority remains unknown", "SOURCE_VERIFICATION_REQUIRED")
            if artifact["authority"] == "authoritative" and (
                    artifact["kind"] in ("mesh_derivative", "print_package", "nc_program", "two_d_cutting")
                    or artifact["path"].lower().endswith((".stl", ".obj", ".3mf", ".nc", ".gcode"))):
                block("handoff manufacturing derivative cannot become an authoritative design source", "SOURCE_VERIFICATION_REQUIRED")
            if artifact["revision"] != state["revision"] or artifact.get("units") != state.get("units"):
                block("handoff artifact revision or units conflict with current state")
        setup = state.get("setup") or {}
        required_artifacts = []
        cad = setup.get("cad_handoff")
        if state["process_family"] == "cad_handoff" and validator_for("cad-handoff-input.schema.json", catalog).is_valid(cad):
            required_artifacts = [cad["derivation"]["source"]] + [a["artifact"] for a in cad["derivation"]["derivatives"]]
        for family, key, schema in (("additive", "additive_preflight", "additive-preflight.schema.json"),
                                    ("laser_cutting", "laser_preflight", "laser-preflight.schema.json")):
            inputs = setup.get(key)
            if state["process_family"] == family and validator_for(schema, catalog).is_valid(inputs):
                required_artifacts = [inputs["source_artifact"]]
        if any(artifact not in artifacts for artifact in required_artifacts):
            block("handoff changes or omits a process-bound source/derivative descriptor", "SOURCE_VERIFICATION_REQUIRED")

    record = copy.deepcopy(route["approval_record"])
    effective_status = route["approval_state"]
    if valid_handoff:
        if handoff["approval_id"] is not None and (record is None or handoff["approval_id"] != record["approval_id"]):
            block("handoff approval reference does not resolve to the supplied record", "HUMAN_APPROVAL_REQUIRED")
        if handoff["status"] == "approved":
            if effective_status != "approved":
                block("handoff approval is not current and scoped", "HUMAN_APPROVAL_REQUIRED")
            elif not set(handoff["human_review"]["scope"]).issubset(record["scope"]):
                block("approval record does not cover every declared handoff review scope", "HUMAN_APPROVAL_REQUIRED")
    if blockers:
        blockers.add("HUMAN_APPROVAL_REQUIRED")
        if effective_status == "approved":
            effective_status = "invalidated"
            record["status"] = "invalidated"
            record["invalidation_reason"] = "handoff conflicts with current context, evidence or required review"
    elif not valid_handoff or handoff["status"] != "approved":
        # A current review record never promotes a draft package automatically.
        effective_status = "not_requested"
    reviewed = copy.deepcopy(handoff) if valid_handoff else None
    if reviewed is not None and blockers:
        reviewed["blockers"] = sorted(blockers)
        reviewed["status"] = "invalidated" if handoff["status"] == "approved" and route["consequence_level"] != "live_execution" else "blocked"
    return {"status": "blocked" if blockers else "review_required", "blockers": sorted(blockers),
            "findings": findings, "validation_errors": errors + route["validation_errors"],
            "context_fingerprint": route["context_fingerprint"], "approval_state": effective_status,
            "approval_record": record, "handoff": reviewed,
            "routing": {key: route[key] for key in ("process_family", "skillset", "consequence_level", "blockers")},
            "review_required": True, "execution_allowed": False}
