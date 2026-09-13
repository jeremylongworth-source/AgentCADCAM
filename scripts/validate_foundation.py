"""Validate the repository contracts required by the foundation gate.

This script uses Python's standard library plus PyYAML. It validates structural
contracts and format/source cross-references; full JSON Schema
instance validation is a later test-layer responsibility.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import yaml

if __package__:
    from .validate_format_registry import UniqueKeyLoader, validate_registry_files
else:
    from validate_format_registry import UniqueKeyLoader, validate_registry_files


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
    "router/job_router.py",
    "router/routes.yaml",
    "state/state.schema.json",
    "state/state.example.json",
    "state/state.py",
    "docs/architecture/router-state-integration.md",
    "state/invalidation-rules.yaml",
    "docs/development/fingerprint-v2-migration.md",
    "fixtures/manifest.yaml",
    "docs/sources/source-registry.yaml",
    "docs/formats/format-registry.md",
    "scripts/validate_format_registry.py",
    "docs/sources/source-freshness-process.md",
    "docs/architecture/approval-model.md",
    "docs/architecture/regulatory-review-model.md",
    "docs/architecture/ip-and-provenance-model.md",
    "docs/standards/prohibited-capability-contract.md",
    "docs/standards/fixture-licensing-standard.md",
    "docs/architecture/threat-model.md",
    "docs/evaluation/adversarial-hardening.md",
    "docs/evaluation/pilot-protocol.md",
    "scripts/validate_pilot_packet.py",
    "scripts/evaluate_pilot_gate.py",
    "scripts/validate_schema_instances.py",
    "requirements-test.txt",
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
        return yaml.load(read_text(path, errors), Loader=UniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError):
        fail(f"missing, unreadable, or invalid YAML: {path}", errors)
        return None


def read_text(path: Path, errors: list[str]) -> str:
    try:
        if not path.resolve().is_relative_to(ROOT.resolve()):
            fail(f"repository file resolves outside workspace: {path.name}", errors)
            return ""
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError, RuntimeError):
        fail(f"missing or unreadable repository text file: {path}", errors)
        return ""


def repository_files(suffixes, errors):
    """Walk repository content without traversing environments or external links."""
    excluded = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".pytest_cache", ".mypy_cache"}
    root = ROOT.resolve()
    for directory, names, files in os.walk(ROOT, followlinks=False):
        base = Path(directory)
        names[:] = sorted(name for name in names if name not in excluded and not (base / name).is_symlink() and (base / name).resolve().is_relative_to(root))
        for name in sorted(files):
            path = base / name
            if path.suffix.lower() not in suffixes:
                continue
            if not path.resolve().is_relative_to(root):
                fail(f"repository reference resolves outside workspace: {path.name}", errors)
                continue
            yield path


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("non-finite JSON constant")


def validate_structured_files(errors):
    """Check syntax throughout repository-owned YAML/JSON, including mutations."""
    for path in repository_files({".json", ".yaml", ".yml"}, errors):
        if path.suffix.lower() == ".json":
            try:
                json.loads(read_text(path, errors), object_pairs_hook=_json_object, parse_constant=_reject_constant)
            except (ValueError, RecursionError):
                fail(f"invalid or ambiguous JSON: {path}", errors)
        else:
            load_yaml(path, errors)


def validate_schemas(errors: list[str]) -> None:
    actual = {p.name for p in SCHEMA_DIR.glob("*.schema.json")}
    for missing in sorted(REQUIRED_SCHEMAS - actual):
        fail(f"missing required schema: {missing}", errors)
    for path in sorted(SCHEMA_DIR.glob("*.json")):
        try:
            data = json.loads(read_text(path, errors))
        except (OSError, UnicodeError, ValueError):
            fail(f"invalid JSON schema: {path}", errors)
            continue
        if not isinstance(data, dict):
            fail(f"schema document must be a mapping: {path}", errors)
            continue
        if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            fail(f"schema must declare Draft 2020-12: {path}", errors)
        if data.get("type") != "object":
            fail(f"schema root must be an object: {path}", errors)
    state_path = ROOT / "state" / "state.schema.json"
    try:
        state = json.loads(read_text(state_path, errors))
    except (OSError, UnicodeError, ValueError):
        fail(f"invalid state schema: {state_path}", errors)
    else:
        if not isinstance(state, dict) or state.get("$schema") != "https://json-schema.org/draft/2020-12/schema" or state.get("type") != "object":
            fail(f"state schema must declare Draft 2020-12 object: {state_path}", errors)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _slug(value):
    return isinstance(value, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value) is not None


def _text_list(value):
    return isinstance(value, list) and bool(value) and all(_text(item) for item in value)


def _file_reference(base, value, boundary, errors, label):
    """Resolve portable paths only within the designated repository subtree."""
    if not _text(value) or "\\" in value or ":" in value or value.startswith("/"):
        fail(f"{label}: requires a portable relative file path", errors)
        return None
    try:
        allowed = boundary.resolve()
        target = (base / value).resolve()
        if not allowed.is_relative_to(ROOT.resolve()) or not target.is_relative_to(allowed):
            fail(f"{label}: path escapes the allowed repository subtree", errors)
            return None
        if not target.is_file():
            fail(f"{label}: referenced file is missing", errors)
            return None
    except (OSError, ValueError, RuntimeError):
        fail(f"{label}: cannot resolve file reference", errors)
        return None
    return target


def _manifest_header(data, label, errors):
    if not isinstance(data, dict):
        fail(f"{label}: manifest must be a mapping", errors)
        return False
    version = data.get("version")
    if not ((type(version) is int and version > 0) or (_text(version) and re.fullmatch(r"\d+\.\d+\.\d+", version))):
        fail(f"{label}: version must be a positive integer or semantic version", errors)
    return True


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
        if not _manifest_header(data, path.name, errors):
            continue
        if data.get("name") != path.stem or not _slug(data.get("name")):
            fail(f"{path.name}: skillset name must match filename", errors)
        if not _text(data.get("status")):
            fail(f"{path.name}: skillset status is missing", errors)
        skills = data.get("skills")
        if not _text_list(skills):
            fail(f"{path.name}: skills must be a nonempty list of names", errors)
            continue
        if len(set(skills)) != len(skills):
            fail(f"{path.name}: duplicate skills", errors)
        for skill in skills:
            if not _slug(skill) or skill not in known_skills:
                fail(f"{path.name}: unknown skill reference", errors)
                continue
            _file_reference(ROOT / "skills", f"{skill}/SKILL.md", ROOT / "skills", errors, path.name)
    routes = load_yaml(ROOT / "router" / "routes.yaml", errors)
    families = set()
    if not _manifest_header(routes, "router/routes.yaml", errors) or not isinstance(routes.get("routes"), list) or not routes["routes"]:
        fail("router/routes.yaml must contain a nonempty routes list", errors)
    else:
        ids = set()
        for route in routes["routes"]:
            if not isinstance(route, dict):
                fail("router route must be a mapping", errors)
                continue
            identifier, family = route.get("id"), route.get("process_family")
            if not _slug(identifier) or identifier in ids:
                fail("router route ID is missing, invalid, or duplicated", errors)
            else:
                ids.add(identifier)
            if not _text(family) or family in families:
                fail("router route family is missing, invalid, or duplicated", errors)
            else:
                families.add(family)
            classes = route.get("artifact_classes")
            if not _text_list(classes) or len(set(classes)) != len(classes):
                fail("router artifact_classes must be a nonempty unique list", errors)
            consequence = route.get("default_consequence")
            if not isinstance(consequence, str) or consequence not in {"informational", "design_advisory", "manufacturing_planning", "execution_adjacent", "live_execution"}:
                fail("router default consequence is invalid", errors)
            skillset = route.get("skillset")
            if family == "unknown":
                if "skillset" not in route or skillset is not None:
                    fail("unknown router route must explicitly select no skillset", errors)
            elif not _slug(skillset):
                fail("router skillset reference must be a manifest name", errors)
            else:
                _file_reference(ROOT / "skillsets", f"{skillset}.yaml", ROOT / "skillsets", errors, "router skillset")
    expected = {"cad_handoff", "cnc_milling", "additive", "laser_cutting", "unknown"}
    if families != expected:
        fail("router routes must cover exactly the four initial families and unknown", errors)
    fixtures = load_yaml(ROOT / "fixtures" / "manifest.yaml", errors)
    if not _manifest_header(fixtures, "fixtures/manifest.yaml", errors) or not isinstance(fixtures.get("fixtures"), list) or not fixtures["fixtures"]:
        fail("fixtures/manifest.yaml must contain a nonempty fixtures list", errors)
    else:
        ids, paths = set(), set()
        for entry in fixtures["fixtures"]:
            if not isinstance(entry, dict) or not _slug(entry.get("id")):
                fail("fixture manifest entries require a valid ID", errors)
                continue
            identifier = entry["id"]
            if identifier in ids:
                fail("fixture index contains duplicate IDs", errors)
            ids.add(identifier)
            if not _text(entry.get("family")) or entry["family"] not in expected - {"unknown"}:
                fail(f"{identifier}: invalid fixture family", errors)
            if not _text(entry.get("status")):
                fail(f"{identifier}: missing fixture status", errors)
            path = _file_reference(ROOT / "fixtures", entry.get("path"), ROOT / "fixtures", errors, identifier)
            if path is None:
                continue
            if path in paths:
                fail("fixture index contains duplicate descriptor paths", errors)
            paths.add(path)
            fixture = load_yaml(path, errors)
            if not _manifest_header(fixture, identifier, errors):
                continue
            if fixture.get("fixture_id") != identifier:
                fail(f"{identifier}: index and descriptor IDs conflict", errors)
            for field in ("license", "status", "description"):
                if not _text(fixture.get(field)):
                    fail(f"{identifier}: fixture requires {field}", errors)
            if not any(key in fixture for key in ("artifacts", "program", "mesh")):
                fail(f"{identifier}: fixture has no declared artifacts", errors)
            for field in ("source_job", "authoritative_artifact", "program", "mesh"):
                if field in fixture:
                    _file_reference(path.parent, fixture[field], ROOT / "fixtures", errors, f"{identifier}/{field}")
            if "artifacts" in fixture:
                artifacts = fixture["artifacts"]
                if isinstance(artifacts, dict) and artifacts:
                    for key, value in artifacts.items():
                        if not _text(key):
                            fail(f"{identifier}: artifact names must be text", errors)
                        _file_reference(path.parent, value, ROOT / "fixtures", errors, f"{identifier}/artifact")
                elif isinstance(artifacts, list) and artifacts:
                    for artifact in artifacts:
                        if not isinstance(artifact, dict):
                            fail(f"{identifier}: artifact entry must be a mapping", errors)
                            continue
                        _file_reference(path.parent, artifact.get("path"), ROOT / "fixtures", errors, f"{identifier}/artifact")
                        for field in ("kind", "authority", "revision", "units"):
                            if not _text(artifact.get(field)):
                                fail(f"{identifier}: artifact requires {field}", errors)
                else:
                    fail(f"{identifier}: artifacts must be a nonempty mapping or list", errors)
            if "contexts" in fixture:
                contexts = fixture["contexts"]
                if not isinstance(contexts, dict) or not contexts:
                    fail(f"{identifier}: contexts must be a nonempty mapping", errors)
                else:
                    for key, value in contexts.items():
                        if not _text(key):
                            fail(f"{identifier}: context names must be text", errors)
                        _file_reference(path.parent, value, ROOT / "fixtures", errors, f"{identifier}/context")
            generation = fixture.get("step_artifact")
            if generation is not None:
                if not isinstance(generation, dict):
                    fail(f"{identifier}: step_artifact must be a mapping", errors)
                else:
                    for field in ("generator", "tested_windows_constraints"):
                        if field in generation:
                            _file_reference(ROOT, generation[field], ROOT, errors, f"{identifier}/{field}")


def validate_skill_metadata(errors: list[str]) -> None:
    """Validate future SKILL.md frontmatter without requiring skills yet."""
    frontmatter = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        match = frontmatter.match(read_text(path, errors))
        if not match:
            fail(f"skill metadata frontmatter missing: {path}", errors)
            continue
        data = load_yaml_text(match.group(1), path, errors)
        if not isinstance(data, dict):
            fail(f"skill metadata must be a mapping: {path}", errors)
            continue
        for key in ("name", "description"):
            if not _text(data.get(key)):
                fail(f"skill metadata missing {key}: {path}", errors)
        folder_name = path.parent.name
        if data.get("name") != folder_name:
            fail(f"skill name does not match folder: {path}", errors)


def load_yaml_text(content: str, path: Path, errors: list[str]):
    try:
        return yaml.load(content, Loader=UniqueKeyLoader)
    except yaml.YAMLError:
        fail(f"invalid or ambiguous YAML frontmatter: {path}", errors)
        return None


def validate_markdown_references(errors: list[str]) -> None:
    """Check relative Markdown links so docs do not point at missing files."""
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in repository_files({".md"}, errors):
        text = read_text(path, errors)
        for target in pattern.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            _file_reference(path.parent, target.split("#", 1)[0], ROOT, errors, f"broken Markdown reference in {path}")


def validate_safety_invariants(errors: list[str]) -> None:
    boundary = read_text(ROOT / "docs/architecture/execution-boundary.md", errors)
    security = read_text(ROOT / "SECURITY.md", errors)
    required_terms = ["BLOCK_EXECUTION", "REVIEW_REQUIRED", "not self-authorizing", "interlock"]
    for term in required_terms:
        if term.lower() not in (boundary + security).lower():
            fail(f"safety contract missing required term: {term}", errors)
    prohibited = read_text(ROOT / "docs/standards/prohibited-capability-contract.md", errors)
    for term in ("BLOCK_EXECUTION", "cycle start", "interlock", "postprocessor deployment"):
        if term.lower() not in prohibited.lower():
            fail(f"prohibited-capability contract missing required term: {term}", errors)
    for scan_dir in (ROOT / "scripts", ROOT / "skills"):
        for path in scan_dir.rglob("*.py"):
            if path.resolve() == Path(__file__).resolve():
                continue
            text = read_text(path, errors).lower()
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
    validate_structured_files(errors)
    validate_schemas(errors)
    validate_manifests(errors)
    errors.extend(validate_registry_files(ROOT))
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
