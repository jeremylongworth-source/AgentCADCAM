"""Deterministic metadata checks for the synthetic CAD handoff fixture.

This is deliberately not a CAD kernel or geometry validator. It checks the
portable handoff invariants that can be evaluated from a fixture manifest.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


BLOCKING = {
    "MISSING_CONTEXT",
    "SOURCE_VERIFICATION_REQUIRED",
}


def review_bundle(bundle: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    """Return findings and blockers for a metadata-level CAD bundle review."""
    findings: list[str] = []
    blockers: list[str] = []

    authoritative = bundle.get("authoritative_artifact")
    artifacts = bundle.get("artifacts") or []
    by_path = {item.get("path"): item for item in artifacts if isinstance(item, dict)}
    if not authoritative or authoritative not in by_path:
        blockers.append("MISSING_CONTEXT")
    else:
        if by_path[authoritative].get("authority") != "authoritative":
            blockers.append("SOURCE_VERIFICATION_REQUIRED")
        if root and not (root / authoritative).is_file():
            findings.append("authoritative artifact path is not present in the checked bundle")

    for item in artifacts:
        path = item.get("path") if isinstance(item, dict) else None
        if path and root and not (root / path).is_file():
            blockers.append("MISSING_CONTEXT")
            findings.append(f"declared artifact is missing: {path}")

    revisions = {item.get("revision") for item in artifacts if item.get("revision")}
    if len(revisions) > 1:
        blockers.append("MISSING_CONTEXT")
        findings.append("artifact revisions conflict")
    elif revisions:
        findings.append(f"bundle revision is consistent: {next(iter(revisions))}")
    else:
        blockers.append("MISSING_CONTEXT")
        findings.append("artifact revision is missing")

    units = {item.get("units") for item in artifacts}
    if None in units or "" in units or not units:
        blockers.append("MISSING_CONTEXT")
        findings.append("artifact units are missing")
    elif len(units) > 1:
        blockers.append("MISSING_CONTEXT")
        findings.append("artifact units conflict")
    else:
        findings.append(f"bundle units are consistent: {next(iter(units))}")

    if authoritative and authoritative.lower().endswith((".stl", ".obj", ".3mf")):
        blockers.append("SOURCE_VERIFICATION_REQUIRED")
        findings.append("mesh/package derivative is incorrectly treated as design master")
    elif any(item.get("kind") == "mesh_derivative" for item in artifacts):
        findings.append("mesh is identified as a derived artifact")

    step_artifact = bundle.get("step_artifact") or {}
    if step_artifact.get("status") == "generated":
        if "source/bracket.step" in by_path:
            findings.append("neutral solid exchange is present; independent geometry verification is still required")
        else:
            blockers.append("MISSING_CONTEXT")
            findings.append("STEP status claims generated but the artifact is not declared")

    metadata = bundle.get("metadata") or {}
    if "pmi_status" not in metadata:
        blockers.append("MISSING_CONTEXT")
        findings.append("PMI status is missing")
    elif metadata.get("pmi_status") == "not_present":
        findings.append("PMI is not present; manufacturing interpretation requires review")

    dimensions = bundle.get("dimension_checks") or []
    conflicts = [item for item in dimensions if isinstance(item, dict) and item.get("status") == "conflict"]
    if conflicts:
        blockers.append("MISSING_CONTEXT")
        findings.append("critical dimensions conflict across artifacts")

    blockers = sorted(set(blockers))
    return {
        "status": "blocked" if blockers else "review_required",
        "blockers": blockers,
        "findings": findings,
        "review_required": True,
        "geometry_equivalence_verified": False,
    }


def load_fixture(path: Path) -> dict[str, Any]:
    import yaml  # type: ignore

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def apply_mutation(bundle: dict[str, Any], mutation: dict[str, Any]) -> dict[str, Any]:
    """Apply a declarative fixture mutation without changing the source fixture."""
    import copy

    result = copy.deepcopy(bundle)
    by_path = {item.get("path"): item for item in result.get("artifacts", []) if isinstance(item, dict)}
    for path, revision in (mutation.get("artifact_revision_overrides") or {}).items():
        if path in by_path:
            by_path[path]["revision"] = revision
    for path, units in (mutation.get("artifact_units_overrides") or {}).items():
        if path in by_path:
            by_path[path]["units"] = units
    if "authoritative_artifact" in mutation:
        result["authoritative_artifact"] = mutation["authoritative_artifact"]
    if "dimension_checks" in mutation:
        result["dimension_checks"] = mutation["dimension_checks"]
    for key in mutation.get("metadata_remove", []) or []:
        result.setdefault("metadata", {}).pop(key, None)
    return result


if __name__ == "__main__":
    import json
    import sys

    fixture_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("fixtures/cad/bracket/fixture.yaml")
    bundle = load_fixture(fixture_path)
    metadata_path = fixture_path.parent / "metadata" / "revision.json"
    if metadata_path.is_file():
        bundle["metadata"] = json.loads(metadata_path.read_text(encoding="utf-8"))
    result = review_bundle(bundle, fixture_path.parent)
    print(json.dumps(result, indent=2, sort_keys=True))
