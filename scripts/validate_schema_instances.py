"""Validate repository JSON Schemas and declared examples using local references."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
PROFILE_SCHEMAS = {
    "machine": "machine", "printer": "machine", "controller": "controller",
    "material": "material", "post": "post", "setup": "setup", "tool": "tool",
}


def load_catalog(root: Path = ROOT):
    paths = sorted((root / "contexts/schemas").glob("*.schema.json"))
    paths.append(root / "state/state.schema.json")
    schemas = {}
    resources = []
    ids = set()
    for path in paths:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        schema_id = schema["$id"]
        if schema_id in ids:
            raise ValueError(f"duplicate schema ID: {schema_id}")
        ids.add(schema_id)
        schemas[path.name] = schema
        resources.append((schema_id, Resource.from_contents(schema)))
    # Registry has no retrieval callback: unknown references fail without network access.
    return schemas, Registry().with_resources(resources)


def validator_for(name: str, catalog=None):
    schemas, registry = catalog if catalog is not None else load_catalog()
    return Draft202012Validator(
        schemas[name], registry=registry,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )


def instance_paths(root: Path = ROOT):
    for path in sorted((root / "contexts/examples").glob("*.example.json")):
        yield path, path.name.replace(".example.json", ".schema.json")
    yield root / "state/state.example.json", "state.schema.json"
    for path in sorted((root / "fixtures").glob("**/metadata/derivation.json")):
        yield path, "derivation.schema.json"
    for path in sorted((root / "fixtures").glob("**/contexts/*.json")):
        if path.stem in PROFILE_SCHEMAS:
            yield path, PROFILE_SCHEMAS[path.stem] + ".schema.json"


def validate_repository(root: Path = ROOT):
    catalog = load_catalog(root)
    errors = []
    count = 0
    for path, schema_name in instance_paths(root):
        count += 1
        instance = json.loads(path.read_text(encoding="utf-8"))
        for error in validator_for(schema_name, catalog).iter_errors(instance):
            location = "/".join(str(item) for item in error.absolute_path) or "<root>"
            errors.append(f"{path.relative_to(root)}:{location}: {error.message}")
    return errors, len(catalog[0]), count


def main() -> int:
    try:
        errors, schemas, instances = validate_repository()
    except Exception as exc:
        print(f"SCHEMA INSTANCE VALIDATION FAILED: {exc}")
        return 1
    if errors:
        print("SCHEMA INSTANCE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"SCHEMA INSTANCE VALIDATION PASSED: {schemas} schemas, {instances} instances")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
