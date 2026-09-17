"""Explicit diagnostic deltas for immutable pre-governance review packets.

This is a test oracle, not a call into the policy implementation. Identities,
inputs, authored decisions, raw reports and previous findings must not drift.
"""


def add_governance_diagnostics(result, family):
    if family == "cad":
        return
    fields = ["confidentiality", "third_party_restrictions", "redistribution_authorized"] if family == "cnc" else [
        "ownership_status", "licence_status", "confidentiality", "third_party_restrictions",
    ]
    additions = [f"ip_status/{field}: authorization context is missing, unresolved, or conflicting" for field in fields]
    if family in ("additive", "laser"):
        additions.append("export_review_status: authorization context is missing, unresolved, or conflicting")
        result["blockers"] = sorted(set(result["blockers"]) | {"REGULATORY_REVIEW_REQUIRED"})
    position = result["findings"].index("human approval is not recorded") + 1
    result["findings"][position:position] = additions


def add_integrated_governance_diagnostics(packet, family):
    observed = packet["observed"]
    add_governance_diagnostics(observed["route_result"], family)
    consumer = observed["handoff_result"]
    add_governance_diagnostics(consumer, family)
    if family in ("additive", "laser"):
        for result in (packet["handoff"], consumer["handoff"], consumer["routing"]):
            result["blockers"] = sorted(set(result["blockers"]) | {"REGULATORY_REVIEW_REQUIRED"})
