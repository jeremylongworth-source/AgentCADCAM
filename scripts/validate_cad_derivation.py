"""Check a declared byte binding for the bounded synthetic bracket, read-only."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

if __package__:
    from .validate_schema_instances import validator_for
else:
    from validate_schema_instances import validator_for


BINDING_PATH = "metadata/derivation.json"
SOURCE_PATH = "source/bracket.scad"
DERIVATIVE_PATHS = {"source/bracket.step", "source/bracket.stl", "source/bracket.svg"}


def validate(root: Path, bundle: dict, metadata: dict) -> list[str]:
    """Compare record shape, inventory/context declarations, then raw file hashes.

    Paths are a fixed fixture allowlist, never arbitrary paths taken from JSON.
    This does not write a new binding or establish the truth of its declaration.
    """
    root = root.resolve()
    paths = {BINDING_PATH, SOURCE_PATH} | DERIVATIVE_PATHS
    if any(not (root / path).resolve().is_relative_to(root) for path in paths):
        return ["binding or artifact path escapes the supplied fixture"]
    try:
        binding = json.loads((root / BINDING_PATH).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return ["derivation binding is missing, unreadable, or invalid JSON"]
    failures = list(validator_for("derivation.schema.json").iter_errors(binding))
    if failures:
        return ["derivation binding does not conform to its schema"]
    source = binding["source"]
    derivatives = [entry["artifact"] for entry in binding["derivatives"]]
    if source["path"] != SOURCE_PATH or {item["path"] for item in derivatives} != DERIVATIVE_PATHS or len(derivatives) != 3:
        return ["derivation binding must cover the authoritative source and each of the three fixture derivatives once"]
    artifacts = [source] + derivatives
    if len({item["artifact_id"] for item in artifacts}) != len(artifacts):
        return ["derivation artifact identifiers must be unique"]
    errors = []
    if source["path"] != bundle.get("authoritative_artifact") or source["path"] != metadata.get("authoritative_artifact"):
        errors.append("derivation source conflicts with manifest or revision metadata authority")
    inventory = {item["path"]: item for item in bundle["artifacts"]}
    for item in artifacts:
        path = item["path"]
        declared = inventory.get(path, {})
        for field in ("kind", "authority", "revision", "units"):
            if item[field] != declared.get(field):
                errors.append(f"{path}: binding {field} conflicts with manifest")
        for field in ("revision", "units"):
            if item[field] != metadata.get(field):
                errors.append(f"{path}: binding {field} conflicts with revision metadata")
        try:
            digest = hashlib.sha256((root / path).read_bytes()).hexdigest()
        except OSError:
            errors.append(f"{path}: bound artifact is missing or unreadable")
            continue
        if digest != item["sha256"].lower():
            errors.append(f"{path}: bytes differ from the declared derivation binding; resolve freshness and review before rebinding")
    return errors
