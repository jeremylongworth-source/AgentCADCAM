"""Validate the repository contracts required by the foundation gate.

This script intentionally uses only Python's standard library plus PyYAML when
available for YAML syntax. It validates structural contracts; full JSON Schema
instance validation is a later test-layer responsibility.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "contexts" / "schemas"
REQUIRED_SCHEMAS = {
    "job.schema.json",
    "machine.schema.json",
    "controller.schema.json",
    "material.schema.json",
    "tool.schema.json",
    "post.schema.json",
    "setup.schema.json",
    "approval.schema.json",
    "handoff.schema.json",
}
REQUIRED_FILES = {
    "README.md",
    "ROADMAP.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "CHANGELOG.md",
    "LICENSE",
    "docs/architecture/domain-contract.md",
    "docs/architecture/master-taxonomy-v1.md",
    "docs/architecture/consequence-model.md",
    "docs/architecture/execution-boundary.md",
    "docs/architecture/personas-and-job-maps.md",
    "docs/architecture/specialization-model.md",
    "docs/standards/skill-authoring-standard.md",
    "docs/standards/research-and-evidence-standard.md",
    "docs/standards/interoperability-standard.md",
    "docs/standards/safety-governance-standard.md",
    "docs/standards/testing-standard.md",
    "docs/standards/evaluation-standard.md",
    "docs/standards/context-profile-standard.md",
    "router/router-contract.md",
    "router/router.py",
    "router/routes.yaml",
    "state/state.schema.json",
    "state/state.example.json",
    "state/state.py",
    "docs/architecture/router-state-integration.md",
    "state/invalidation-rules.yaml",
    "fixtures/manifest.yaml",
    "docs/sources/source-registry.yaml",
    "docs/sources/source-freshness-process.md",
    "docs/architecture/approval-model.md",
    "docs/architecture/regulatory-review-model.md",
    "docs/architecture/ip-and-provenance-model.md",
    "docs/standards/prohibited-capability-contract.md",
    "docs/standards/fixture-licensing-standard.md",
    "docs/architecture/threat-model.md",
    "docs/evaluation/adversarial-hardening.md",
    "tests/foundation/test_foundation.py",
    "tests/routing/test_router_contract.py",
    "scripts/cad_handoff_checks.py",
    "scripts/validate_cad_fixture_step.py",
    "scripts/validate_cad_fixture_mesh.py",
    "scripts/validate_cad_fixture_design.py",
    "scripts/nc_static_checks.py",
    "scripts/validate_laser_fixture_geometry.py",
    "scripts/validate_foundation.py",
}


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def load_yaml(path: Path, errors: list[str]):
    try:
        import yaml  # type: ignore
    except ImportError:
        fail("PyYAML is required to validate YAML files", errors)
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exact parser errors vary
        fail(f"invalid YAML: {path}: {exc}", errors)
        return None


def validate_schemas(errors: list[str]) -> None:
    actual = {p.name for p in SCHEMA_DIR.glob("*.schema.json")}
    for missing in sorted(REQUIRED_SCHEMAS - actual):
        fail(f"missing required schema: {missing}", errors)
    for path in sorted(SCHEMA_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"invalid JSON schema: {path}: {exc}", errors)
            continue
        if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            fail(f"schema must declare Draft 2020-12: {path}", errors)
        if data.get("type") != "object":
            fail(f"schema root must be an object: {path}", errors)
    state_path = ROOT / "state" / "state.schema.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        fail(f"invalid state schema: {state_path}: {exc}", errors)
    else:
        if state.get("$schema") != "https://json-schema.org/draft/2020-12/schema" or state.get("type") != "object":
            fail(f"state schema must declare Draft 2020-12 object: {state_path}", errors)


def validate_manifests(errors: list[str]) -> None:
    known_skills = {
        "cadcam-intake-and-scope",
        "design-file-provenance-review",
        "file-format-interoperability-plan",
        "cad-manufacturability-review",
        "drawing-pmi-handoff-review",
        "machine-capability-match",
        "cnc-setup-planner",
        "tooling-plan-review",
        "toolpath-strategy-planner",
        "postprocessor-readiness-review",
        "nc-static-safety-review",
        "simulation-readiness-review",
        "additive-job-preflight",
        "laser-job-preflight",
    }
    for path in sorted((ROOT / "skillsets").glob("*.yaml")):
        data = load_yaml(path, errors)
        if not isinstance(data, dict):
            fail(f"skillset manifest must be a mapping: {path}", errors)
            continue
        for key in ("name", "version", "status", "skills"):
            if key not in data:
                fail(f"skillset manifest missing {key}: {path}", errors)
        for skill in data.get("skills", []) or []:
            if skill not in known_skills:
                fail(f"unknown skill {skill!r} in {path}", errors)
    routes = load_yaml(ROOT / "router" / "routes.yaml", errors)
    if not isinstance(routes, dict) or not isinstance(routes.get("routes"), list):
        fail("router/routes.yaml must contain a routes list", errors)
    else:
        families = {item.get("process_family") for item in routes["routes"] if isinstance(item, dict)}
        expected = {"cad_handoff", "cnc_milling", "additive", "laser_cutting", "unknown"}
        if families != expected:
            fail(f"router routes must cover exactly {sorted(expected)}; found {sorted(families)}", errors)
        for route in routes["routes"]:
            skillset = route.get("skillset") if isinstance(route, dict) else None
            if skillset and not (ROOT / "skillsets" / f"{skillset}.yaml").is_file():
                fail(f"router route references missing skillset: {skillset}", errors)
            if isinstance(route, dict) and route.get("id") == "unknown" and skillset is not None:
                fail("unknown router route must not select a skillset", errors)
    fixtures = load_yaml(ROOT / "fixtures" / "manifest.yaml", errors)
    if not isinstance(fixtures, dict) or not isinstance(fixtures.get("fixtures"), list):
        fail("fixtures/manifest.yaml must contain a fixtures list", errors)
    else:
        for entry in fixtures["fixtures"]:
            if not isinstance(entry, dict) or not entry.get("id") or not entry.get("path"):
                fail("fixture manifest entries require id and path", errors)
                continue
            if not (ROOT / "fixtures" / entry["path"]).is_file():
                fail(f"fixture manifest path does not exist: {entry['path']}", errors)
            else:
                fixture = load_yaml(ROOT / "fixtures" / entry["path"], errors)
                if isinstance(fixture, dict):
                    if not fixture.get("license"):
                        fail(f"fixture missing license declaration: {entry['path']}", errors)
                    fixture_root = (ROOT / "fixtures" / entry["path"]).parent
                    declared_artifacts = fixture.get("artifacts", []) or []
                    artifact_values = list(declared_artifacts.values()) if isinstance(declared_artifacts, dict) else declared_artifacts
                    for artifact in artifact_values:
                        artifact_path = artifact if isinstance(declared_artifacts, dict) else artifact.get("path") if isinstance(artifact, dict) else None
                        if artifact_path and not (fixture_root / artifact_path).is_file():
                            fail(f"fixture artifact path does not exist: {entry['path']} -> {artifact_path}", errors)
                    program_path = fixture.get("program")
                    if program_path and not (fixture_root / program_path).is_file():
                        fail(f"fixture program path does not exist: {entry['path']} -> {program_path}", errors)
                    mesh_path = fixture.get("mesh")
                    if mesh_path and not (fixture_root / mesh_path).is_file():
                        fail(f"fixture mesh path does not exist: {entry['path']} -> {mesh_path}", errors)
                    for context_name, context_path in (fixture.get("contexts") or {}).items():
                        if not (fixture_root / context_path).is_file():
                            fail(f"fixture {context_name} context path does not exist: {entry['path']} -> {context_path}", errors)
    sources = load_yaml(ROOT / "docs" / "sources" / "source-registry.yaml", errors)
    if not isinstance(sources, dict) or not isinstance(sources.get("sources"), list):
        fail("source registry must contain a sources list", errors)
    elif sources.get("sources"):
        required = {"title", "publisher", "locator", "accessed_at", "claims"}
        for index, source in enumerate(sources["sources"]):
            if not isinstance(source, dict) or not required.issubset(source):
                fail(f"source entry {index} is missing required metadata", errors)


def validate_skill_metadata(errors: list[str]) -> None:
    """Validate future SKILL.md frontmatter without requiring skills yet."""
    frontmatter = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        match = frontmatter.match(path.read_text(encoding="utf-8"))
        if not match:
            fail(f"skill metadata frontmatter missing: {path}", errors)
            continue
        data = load_yaml_text(match.group(1), path, errors)
        if not isinstance(data, dict):
            continue
        for key in ("name", "description"):
            if not data.get(key):
                fail(f"skill metadata missing {key}: {path}", errors)
        folder_name = path.parent.name
        if data.get("name") != folder_name:
            fail(f"skill name does not match folder: {path}", errors)


def load_yaml_text(content: str, path: Path, errors: list[str]):
    try:
        import yaml  # type: ignore
        return yaml.safe_load(content)
    except Exception as exc:  # pragma: no cover - parser/version dependent
        fail(f"invalid YAML frontmatter: {path}: {exc}", errors)
        return None


def validate_markdown_references(errors: list[str]) -> None:
    """Check relative Markdown links so docs do not point at missing files."""
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for target in pattern.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target_path = (path.parent / target.split("#", 1)[0]).resolve()
            if not target_path.is_file():
                fail(f"broken Markdown reference: {path}: {target}", errors)


def validate_safety_invariants(errors: list[str]) -> None:
    boundary = (ROOT / "docs/architecture/execution-boundary.md").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    required_terms = ["BLOCK_EXECUTION", "REVIEW_REQUIRED", "not self-authorizing", "interlock"]
    for term in required_terms:
        if term.lower() not in (boundary + security).lower():
            fail(f"safety contract missing required term: {term}", errors)
    prohibited = (ROOT / "docs/standards/prohibited-capability-contract.md").read_text(encoding="utf-8")
    for term in ("BLOCK_EXECUTION", "cycle start", "interlock", "postprocessor deployment"):
        if term.lower() not in prohibited.lower():
            fail(f"prohibited-capability contract missing required term: {term}", errors)
    for scan_dir in (ROOT / "scripts", ROOT / "skills"):
        for path in scan_dir.rglob("*.py"):
            if path.resolve() == Path(__file__).resolve():
                continue
            text = path.read_text(encoding="utf-8").lower()
            for token in ("serial.serial", "start_cycle", "spindle_on", "beam_on", "jog_axis", "disable_interlock"):
                if token in text:
                    fail(f"possible live-control implementation token {token!r}: {path}", errors)


def validate_invalidation_rules(errors: list[str]) -> None:
    rules = load_yaml(ROOT / "state" / "invalidation-rules.yaml", errors)
    if not isinstance(rules, dict) or not isinstance(rules.get("approval_invalidation"), list):
        fail("state/invalidation-rules.yaml must contain approval_invalidation", errors)
        return
    for index, rule in enumerate(rules["approval_invalidation"]):
        if not isinstance(rule, dict) or not rule.get("field") or not isinstance(rule.get("invalidates"), list):
            fail(f"invalid approval invalidation rule at index {index}", errors)


def main() -> int:
    errors: list[str] = []
    for relative in sorted(REQUIRED_FILES):
        if not (ROOT / relative).is_file():
            fail(f"missing required repository file: {relative}", errors)
    validate_schemas(errors)
    validate_manifests(errors)
    validate_skill_metadata(errors)
    validate_markdown_references(errors)
    validate_safety_invariants(errors)
    validate_invalidation_rules(errors)
    if errors:
        print("FOUNDATION VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("FOUNDATION VALIDATION PASSED")
    print(f"- repository files checked: {len(REQUIRED_FILES)}")
    print(f"- schemas checked: {len(list(SCHEMA_DIR.glob('*.json')))}")
    print(f"- skillset manifests checked: {len(list((ROOT / 'skillsets').glob('*.yaml')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
