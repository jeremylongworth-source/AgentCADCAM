"""Offline source-review declarations; never fetch a locator or certify its truth."""

import hashlib
import json
from datetime import date, datetime, timezone

from scripts.validate_schema_instances import validator_for


PRIMARY_AUTHORITIES = {
    "standards_body", "government_research", "oem_documentation",
    "primary_tool_documentation", "primary_research",
}


def source_fingerprint(source):
    """Bind all source metadata except its own review, with finite canonical JSON."""
    payload = {key: value for key, value in source.items() if key != "review"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def check_source_review(source, role, *, catalog, today=None):
    """Return fixed diagnostics. `today` is for deterministic offline date tests.

    Runtime callers use the current UTC date; valid_through is inclusive. The
    reviewer chooses and justifies that date, not a guessed universal lifetime.
    Source assessment does not prove authenticity, applicability or claim truth.
    """
    today = today if today is not None else datetime.now(timezone.utc).date()
    schema_id = catalog[0]["handoff.schema.json"]["$id"]
    validator = validator_for("handoff.schema.json", catalog).evolve(schema={"$ref": schema_id + "#/$defs/source"})
    if not validator.is_valid(source) or not isinstance(source.get("review"), dict):
        return ["structured source review is missing or invalid"]
    review = source["review"]
    findings = []
    if review["status"] != "reviewed":
        findings.append("source review is unresolved, stale or conflicted")
    if review["authority"] not in PRIMARY_AUTHORITIES:
        findings.append("source authority is not primary evidence")
    if role not in review["applies_to"]:
        findings.append("source review does not cover the required context role")
    if review["source_sha256"] != source_fingerprint(source):
        findings.append("source metadata differs from the reviewed source fingerprint")
    accessed = date.fromisoformat(source["accessed_at"])
    reviewed = date.fromisoformat(review["reviewed_at"]) if review["reviewed_at"] is not None else None
    expiry = date.fromisoformat(review["valid_through"]) if review["valid_through"] is not None else None
    if reviewed is None or expiry is None or not accessed <= reviewed <= today <= expiry:
        findings.append("source access/review dates are future, out of order or expired")
    return findings


def check_setup_source_reviews(state, *, catalog, today=None):
    """Check supported, schema-valid process inputs; malformed inputs block elsewhere."""
    setup = state.get("setup") or {}
    candidates = []
    model = setup.get("coordinate_model")
    schema_id = catalog[0]["setup.schema.json"]["$id"]
    validator = validator_for("setup.schema.json", catalog).evolve(schema={"$ref": schema_id + "#/$defs/coordinate_model"})
    if validator.is_valid(model) and model["lifecycle"]["verification"]["status"] == "verified":
        candidates.append(("setup/coordinate_model/source", model["source"], "coordinate_model"))
    for key, role, owner in (("additive_preflight", "slicer_profile", "slicer_profile"),
                             ("laser_preflight", "laser_process", "process")):
        inputs = setup.get(key)
        if validator_for(key.replace("_", "-") + ".schema.json", catalog).is_valid(inputs):
            candidates.append((f"setup/{key}/{owner}/source", inputs[owner]["source"], role))
    cad = setup.get("cad_handoff")
    if validator_for("cad-handoff-input.schema.json", catalog).is_valid(cad):
        candidates.extend((f"setup/cad_handoff/manufacturing_context/sources/{index}", source, "cad_manufacturing_context")
                          for index, source in enumerate(cad["manufacturing_context"]["sources"]))
    return [f"{path}: {finding}" for path, source, role in candidates
            for finding in check_source_review(source, role, catalog=catalog, today=today)]
