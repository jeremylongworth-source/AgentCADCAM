"""Offline declaration checks, not legal classification or permission to disclose."""

from typing import Any


IP_FIELDS = {
    "ownership_status": ("owned", "licensed", "third_party"),
    "licence_status": ("permitted",),
    "confidentiality": ("public", "internal", "confidential", "restricted"),
}


def check_governance(state: dict[str, Any], consequence: str, action: Any) -> tuple[set[str], list[str]]:
    """Check bounded declarations without resolving locators or echoing private values.

    Draft persistence stays permissive. Planning/handoff readiness requires all
    declared governance fields; a supplied unresolved declaration blocks even a
    lower-consequence review. False redistribution permission is valid for local
    review, never permission to publish. This API performs no external transfer.
    """
    required = consequence in ("manufacturing_planning", "execution_adjacent", "live_execution")
    required |= isinstance(action, str) and action.strip().lower() == "prepare_handoff"
    blockers: set[str] = set()
    findings: list[str] = []

    def fail(blocker, field):
        blockers.add(blocker)
        findings.append(f"{field}: authorization context is missing, unresolved, or conflicting")

    ip = state.get("ip_status")
    if not isinstance(ip, dict):
        if required or ip is not None:
            fail("SOURCE_VERIFICATION_REQUIRED", "ip_status")
        ip = {}
    for field, accepted in IP_FIELDS.items():
        if (required or field in ip) and ip.get(field) not in accepted:
            fail("SOURCE_VERIFICATION_REQUIRED", f"ip_status/{field}")
    if required or "third_party_restrictions" in ip:
        # No machine-readable restriction clearance exists yet. Never interpret
        # prose (including embedded instructions) as permission to waive it.
        if ip.get("third_party_restrictions") != []:
            fail("SOURCE_VERIFICATION_REQUIRED", "ip_status/third_party_restrictions")
    if required or "redistribution_authorized" in ip:
        if not isinstance(ip.get("redistribution_authorized"), bool):
            fail("SOURCE_VERIFICATION_REQUIRED", "ip_status/redistribution_authorized")

    export = state.get("export_review_status")
    if (required or export is not None) and export not in ("not_required", "reviewed"):
        fail("REGULATORY_REVIEW_REQUIRED", "export_review_status")

    # The root state cannot silently override contradictory source/job metadata.
    # Only the supported envelopes are inspected, not arbitrary free-form memory.
    setup = state.get("setup")
    if isinstance(setup, dict):
        declarations = []
        cad = setup.get("cad_handoff")
        if isinstance(cad, dict) and isinstance(cad.get("metadata"), dict):
            metadata = cad["metadata"]
            declarations.append(("setup/cad_handoff/metadata", metadata, metadata))
        for envelope in ("additive_preflight", "laser_preflight"):
            value = setup.get(envelope)
            if isinstance(value, dict) and isinstance(value.get("job"), dict):
                job = value["job"]
                declarations.append((f"setup/{envelope}/job", job.get("ip_status"), job))
        job = setup.get("submitted_job")
        if isinstance(job, dict):
            declarations.append(("setup/submitted_job", job.get("ip_status"), job))
        for path, nested_ip, metadata in declarations:
            if nested_ip is not None and not isinstance(nested_ip, dict):
                fail("SOURCE_VERIFICATION_REQUIRED", f"{path}/ip_status")
            elif isinstance(nested_ip, dict):
                for field in (*IP_FIELDS, "third_party_restrictions", "redistribution_authorized"):
                    if field in nested_ip and (type(nested_ip[field]) is not type(ip.get(field)) or nested_ip[field] != ip.get(field)):
                        fail("SOURCE_VERIFICATION_REQUIRED", f"{path}/{field}")
            if "export_review_status" in metadata and metadata["export_review_status"] != export:
                fail("REGULATORY_REVIEW_REQUIRED", f"{path}/export_review_status")
    if blockers:
        blockers.add("HUMAN_APPROVAL_REQUIRED")
    return blockers, findings
