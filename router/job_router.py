"""Route bounded job state with scoped, fingerprint-checked review records."""

from __future__ import annotations

import copy
from typing import Any

from router.router import route
from scripts.validate_schema_instances import load_catalog, validator_for
from state.state import changed_fields, context_fingerprint


def route_job(
    request: dict[str, Any], current_state: dict[str, Any],
    approval: dict[str, Any] | None = None, *,
    previous_state: dict[str, Any] | None = None,
    required_scope: str = "manufacturing_handoff",
) -> dict[str, Any]:
    """Return routing plus copied state/approval; never persist or authenticate a reviewer."""
    catalog = load_catalog()
    errors: list[str] = []
    findings: list[str] = []

    def validate(value, schema_name, label):
        failures = list(validator_for(schema_name, catalog).iter_errors(value))
        for failure in failures:
            path = "/".join(str(item) for item in failure.absolute_path) or "<root>"
            # Report the failing rule, not private values from a manufacturing packet.
            errors.append(f"{label}/{path}: {failure.validator} validation failed")
        return not failures

    state_ok = validate(current_state, "state.schema.json", "state")
    if previous_state is not None:
        if validate(previous_state, "state.schema.json", "previous_state"):
            try:
                context_fingerprint(previous_state)
            except (TypeError, ValueError):
                errors.append("previous_state fingerprint requires finite JSON values and string object keys")
    record = copy.deepcopy(approval)
    record_ok = approval is not None and validate(approval, "approval.schema.json", "approval")
    if not record_ok:
        record = None
    if not isinstance(required_scope, str) or not required_scope.strip():
        errors.append("required_scope must be a non-empty string")

    normalized = dict(request) if isinstance(request, dict) else {}
    if not isinstance(request, dict):
        errors.append("request must be an object")
    fingerprint = None
    if state_ok:
        state = copy.deepcopy(current_state)
        family = state["process_family"]
        requested_family = normalized.get("process_family")
        if requested_family is not None and requested_family != family:
            errors.append("request process_family conflicts with bounded state")
        normalized["process_family"] = family
        for known, field, schema in (
            ("machine_known", "machine_profile", "machine.schema.json"),
            ("controller_known", "controller_profile", "controller.schema.json"),
            ("material_known", "material", "material.schema.json"),
        ):
            profile = state.get(field)
            valid = profile is not None and validate(profile, schema, field)
            if valid and family != "cad_handoff" and "process_family" in profile and profile["process_family"] != family:
                errors.append(f"{field} process_family conflicts with bounded state")
                valid = False
            normalized[known] = valid and normalized.get(known) is True
        normalized["jurisdiction_known"] = bool(state.get("jurisdiction")) and normalized.get("jurisdiction_known") is True
        if state.get("generated_manufacturing_output") is not None:
            normalized["generated_manufacturing_artifact"] = True
        try:
            fingerprint = context_fingerprint(state)
        except (TypeError, ValueError):
            errors.append("state fingerprint requires finite JSON values and string object keys")
            state = None
            state_ok = False
    else:
        state = None

    effective_status = "not_requested"
    if record_ok and not errors:
        effective_status = record["status"]
        if effective_status == "approved":
            if record["context_fingerprint"] != fingerprint:
                record["status"] = "invalidated"
                record["invalidation_reason"] = "approval fingerprint does not match current context (version 2)"
                # Keep the reviewed fingerprint as evidence; never re-sign an old approval.
                if previous_state is not None:
                    fields = changed_fields(previous_state, current_state)
                    if fields:
                        record["changed_fields"] = fields
                effective_status = "invalidated"
                findings.append("approval is stale for the current job context")
            elif not record.get("reviewed_at"):
                effective_status = "not_requested"
                findings.append("approved record is missing its review timestamp")
            elif required_scope not in record["scope"]:
                effective_status = "not_requested"
                findings.append("approval does not cover the requested review scope")
    normalized["approval_state"] = effective_status
    result = route(normalized)
    if state_ok and result["consequence_level"] in ("execution_adjacent", "live_execution"):
        additional = set()
        if state["process_family"] == "cnc_milling" and state.get("simulation_status") != "verified":
            additional.add("SIMULATION_REQUIRED")
            findings.append("CNC simulation evidence is not verified")
        verification = state.get("verification_results", [])
        if not verification or any(item.get("status") != "passed" for item in verification):
            additional.add("MISSING_CONTEXT")
            findings.append("verification evidence is missing, unresolved, or failed")
        result["blockers"] = sorted(set(result["blockers"]) | additional)
    if errors:
        result["blockers"] = sorted(set(result["blockers"]) | {"MISSING_CONTEXT", "HUMAN_APPROVAL_REQUIRED"})
    result["findings"].extend(findings)
    if state is not None:
        state["approval_status"] = effective_status
    result.update({
        "job_state": state,
        "approval_record": record,
        "context_fingerprint": fingerprint,
        "validation_errors": errors,
    })
    return result
