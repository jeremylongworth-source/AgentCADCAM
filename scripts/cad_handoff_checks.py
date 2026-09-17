"""Deterministic metadata and bounded file checks for the synthetic CAD fixture.

The metadata API is not a geometry validator. The fixture entry point also runs
the existing revision-A bracket content/envelope checks, not a general CAD parser.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

if __package__:
    from .validate_cad_fixture_design import validate as validate_design
    from .validate_cad_fixture_step import validate as validate_step
    from .validate_cad_fixture_mesh import validate as validate_mesh
    from .validate_cad_derivation import validate as validate_binding
else:
    from validate_cad_fixture_design import validate as validate_design
    from validate_cad_fixture_step import validate as validate_step
    from validate_cad_fixture_mesh import validate as validate_mesh
    from validate_cad_derivation import validate as validate_binding


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
        "execution_allowed": False,
        "geometry_equivalence_verified": False,
    }


def review_fixture(root: Path, manifest_name: str = "fixture.yaml") -> dict[str, Any]:
    """Read and check the revision-A synthetic bracket; never execute CAD source.

    This report is evidence for review, not a serialized handoff or approval.
    Passing extent/declaration checks does not prove feature or PMI fidelity.
    """
    import yaml  # type: ignore

    result = {
        "status": "blocked", "blockers": ["MISSING_CONTEXT"], "findings": [],
        "review_required": True, "execution_allowed": False,
        "geometry_equivalence_verified": False, "file_checks": [],
        "validation_scope": "synthetic revision-A bracket declarations, exchange envelopes, and declared byte binding only",
    }
    root = root.resolve()
    required_paths = {
        "source/bracket.scad", "source/bracket.svg", "source/bracket.step",
        "source/bracket.stl", "metadata/revision.json",
    }
    # Do not follow a fixture's declared paths to unrelated files or symlink targets.
    if any(not (root / path).resolve().is_relative_to(root) for path in required_paths | {manifest_name}):
        result["findings"].append("fixture paths must remain inside the supplied bundle")
        return result
    try:
        bundle = load_fixture(root / manifest_name)
        metadata = json.loads((root / "metadata/revision.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, yaml.YAMLError):
        result["findings"].append("fixture manifest or revision metadata could not be read or parsed")
        return result
    if not isinstance(bundle, dict) or bundle.get("fixture_id") != "cad-bracket-basic" or bundle.get("version") != 2:
        result["findings"].append("file checks support only the version-2 cad-bracket-basic fixture")
        return result
    artifacts = bundle.get("artifacts")
    if (
        not isinstance(metadata, dict) or not isinstance(artifacts, list)
        or len(artifacts) != len(required_paths)
        or any(not isinstance(item, dict) or not isinstance(item.get("path"), str)
               or any(not isinstance(item.get(field), (str, type(None))) for field in ("revision", "units"))
               for item in artifacts)
        or {item["path"] for item in artifacts} != required_paths
        or not isinstance(bundle.get("authoritative_artifact"), str)
        or not isinstance(bundle.get("step_artifact"), dict)
        or not isinstance(bundle.get("dimension_checks", []), list)
    ):
        result["findings"].append("fixture inventory or metadata does not match the bounded bracket contract")
        return result
    bundle["metadata"] = metadata
    result.update(review_bundle(bundle, root))
    if metadata.get("authoritative_artifact") != bundle["authoritative_artifact"]:
        result["blockers"].append("SOURCE_VERIFICATION_REQUIRED")
        result["findings"].append("revision metadata and manifest disagree on design authority")
    for name, paths, validator, target in (
        ("source_drawing_revision", ["source/bracket.scad", "source/bracket.svg", "metadata/revision.json"], validate_design, root),
        ("step_envelope", ["source/bracket.step"], validate_step, root / "source/bracket.step"),
        ("stl_envelope", ["source/bracket.stl"], validate_mesh, root / "source/bracket.stl"),
    ):
        try:
            errors = validator(target)
        except (OSError, UnicodeError, ValueError, OverflowError):
            errors = ["file data could not be read or parsed"]
        result["file_checks"].append({"check": name, "paths": paths,
                                      "status": "failed" if errors else "passed", "findings": errors})
        if errors:
            result["blockers"].append("MISSING_CONTEXT")
            result["findings"].append(f"{name}: file-derived checks failed; inspect file_checks findings")
    binding_errors = validate_binding(root, bundle, metadata)
    result["file_checks"].append({
        "check": "artifact_binding", "paths": ["metadata/derivation.json", "source/bracket.scad", "source/bracket.step", "source/bracket.stl", "source/bracket.svg"],
        "status": "failed" if binding_errors else "passed", "findings": binding_errors,
    })
    if binding_errors:
        result["blockers"].append("SOURCE_VERIFICATION_REQUIRED")
        result["findings"].append("artifact_binding: declared source/derivative association needs review; inspect file_checks findings")
    result["blockers"] = sorted(set(result["blockers"]))
    result["status"] = "blocked" if result["blockers"] else "review_required"
    return result


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
    import sys

    fixture_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("fixtures/cad/bracket/fixture.yaml")
    result = review_fixture(fixture_path.parent, fixture_path.name)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(1 if result["status"] == "blocked" else 0)
