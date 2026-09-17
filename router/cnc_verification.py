"""Check declared CNC verification scope; never fetch or authenticate evidence."""

from scripts.validate_schema_instances import validator_for
from state.state import verification_context_fingerprint


def check_cnc_verification(state, catalog):
    """Require current passed simulation and verification, with no ignored records.

    Draft/legacy records remain persistable. They cannot satisfy this readiness
    gate just by carrying a passed label or receiving a new approval fingerprint.
    """
    schema_id = catalog[0]["handoff.schema.json"]["$id"]
    validator = validator_for("handoff.schema.json", catalog).evolve(
        schema={"$ref": schema_id + "#/$defs/cnc_verification_check"})
    expected = verification_context_fingerprint(state)
    blockers, findings, kinds, check_ids = set(), [], set(), set()
    for index, record in enumerate(state.get("verification_results", [])):
        label = f"CNC verification record {index}"
        if not validator.is_valid(record):
            blockers.add("MISSING_CONTEXT")
            findings.append(f"{label}: structured evidence and versioned context binding are required")
            continue
        if record["check_id"] in check_ids:
            blockers.add("MISSING_CONTEXT")
            findings.append(f"{label}: duplicate check identity")
        check_ids.add(record["check_id"])
        if record["context_binding"]["fingerprint"] != expected:
            blockers.update(("MISSING_CONTEXT", "SOURCE_VERIFICATION_REQUIRED"))
            findings.append(f"{label}: evidence binding does not match current verification inputs")
            if record["kind"] == "simulation":
                blockers.add("SIMULATION_REQUIRED")
            continue
        if record["status"] != "passed":
            blockers.add("MISSING_CONTEXT")
            findings.append(f"{label}: verification is unresolved or failed")
            if record["kind"] == "simulation":
                blockers.add("SIMULATION_REQUIRED")
            continue
        kinds.add(record["kind"])
    if "simulation" not in kinds:
        blockers.add("SIMULATION_REQUIRED")
        findings.append("CNC simulation requires a current passed context-bound evidence record")
    if "verification" not in kinds:
        blockers.add("MISSING_CONTEXT")
        findings.append("CNC verification requires a current passed context-bound evidence record")
    return blockers, findings
