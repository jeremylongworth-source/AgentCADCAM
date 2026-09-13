"""Offline format-policy/source-reference checks, not source or job certification."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
FORMATS = {
    "Native CAD", "STEP AP242", "IGES", "DXF", "SVG", "STL", "3MF",
    "NC/G-code", "STEP-NC",
}
FIELDS = {
    "Intended purpose", "Semantics preserved", "Semantics lost or ambiguous",
    "Unit handling", "Revision implications", "Suitable workflow",
    "Unsuitable workflow", "Required validation", "Sources",
}
SOURCE_TEXT_FIELDS = {
    "id", "title", "publisher", "locator", "accessed_at", "authority",
    "review_status", "scope", "sections",
}
AUTHORITIES = {
    "standards_body", "government_research", "primary_tool_documentation",
    "oem_documentation", "primary_research", "community",
}
REVIEW_STATES = {"reviewed", "stale", "conflicted", "verification_required"}
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject ambiguous records instead of accepting the last duplicate YAML key."""

    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in result
            except TypeError as exc:
                raise yaml.constructor.ConstructorError(None, None, "unhashable YAML key", key_node.start_mark) from exc
            if duplicate:
                raise yaml.constructor.ConstructorError(None, None, "duplicate YAML key", key_node.start_mark)
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def validate_sources(registry, *, today=None):
    """Check record shape and dates. 'reviewed' remains a recorded review assertion."""
    errors = []
    sources = {}
    today = today or date.today()
    if not isinstance(registry, dict):
        return {}, ["source registry must be a mapping"]
    if type(registry.get("version")) is not int or registry["version"] != 2:
        errors.append("source registry must declare version 2")
    if registry.get("status") != "active":
        errors.append("source registry must be active")
    records = registry.get("sources")
    if not isinstance(records, list) or not records:
        return {}, errors + ["source registry requires nonempty sources"]
    for index, source in enumerate(records):
        label = f"source {index}"
        if not isinstance(source, dict):
            errors.append(f"{label} must be a mapping")
            continue
        for field in sorted(SOURCE_TEXT_FIELDS):
            if not _text(source.get(field)):
                errors.append(f"{label} requires nonempty text: {field}")
        identifier = source.get("id")
        if _text(identifier):
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier):
                errors.append(f"{label} has invalid ID")
            if identifier in sources:
                errors.append(f"duplicate source ID: {identifier}")
            sources[identifier] = source
        for field in ("claims", "applies_to"):
            value = source.get(field)
            if not isinstance(value, list) or not value or not all(_text(item) for item in value):
                errors.append(f"{label} requires nonempty text list: {field}")
        revision = source.get("publication_or_revision")
        if "publication_or_revision" not in source or (revision is not None and not _text(revision)):
            errors.append(f"{label} requires publication_or_revision text or explicit null")
        if not isinstance(source.get("authority"), str) or source["authority"] not in AUTHORITIES:
            errors.append(f"{label} has invalid authority category")
        if not isinstance(source.get("review_status"), str) or source["review_status"] not in REVIEW_STATES:
            errors.append(f"{label} has invalid review status")
        locator = source.get("locator")
        if not isinstance(locator, str) or not re.fullmatch(r"https://[^/\s?#]+/[^\s]*", locator):
            errors.append(f"{label} requires an HTTPS page locator")
        accessed = source.get("accessed_at")
        try:
            if not isinstance(accessed, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", accessed):
                raise ValueError
            if date.fromisoformat(accessed) > today:
                raise ValueError
        except ValueError:
            errors.append(f"{label} requires a valid, non-future access date")
    return sources, errors


def validate_format_registry(content, registry, *, today=None):
    sources, errors = validate_sources(registry, today=today)
    if not isinstance(content, str):
        return errors + ["format registry must be Markdown text"]
    sections = {}
    current = None
    for line in content.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            if current in sections:
                errors.append(f"duplicate format section: {current}")
            sections[current] = {}
        elif current is not None and line.startswith("- "):
            match = re.fullmatch(r"- ([^:]+):\s*(.*)", line)
            if not match:
                errors.append(f"{current}: fields require '- Label: value' syntax")
                continue
            field, value = match.groups()
            if field in sections[current]:
                errors.append(f"{current}: duplicate field {field}")
            sections[current][field] = value.strip()
    if set(sections) != FORMATS:
        errors.append("format sections must cover exactly the nine roadmap formats")
    for name, fields in sections.items():
        if set(fields) != FIELDS:
            errors.append(f"{name}: missing or unexpected policy fields")
        for field, value in fields.items():
            if not value or value.casefold() in {"todo", "tbd", "unknown", "n/a", "pending"}:
                errors.append(f"{name}: unresolved policy field {field}")
        citations = LINK.findall(fields.get("Sources", ""))
        if not citations:
            errors.append(f"{name}: requires at least one source-ID link")
        for identifier, locator in citations:
            source = sources.get(identifier)
            if source is None:
                errors.append(f"{name}: unknown source ID {identifier}")
                continue
            if locator != source.get("locator"):
                errors.append(f"{name}: locator conflicts with source {identifier}")
            applicability = source.get("applies_to")
            if not isinstance(applicability, list) or name not in applicability:
                errors.append(f"{name}: source {identifier} does not declare this format scope")
            if source.get("review_status") != "reviewed":
                errors.append(f"{name}: source {identifier} requires verification")
            if source.get("authority") == "community":
                errors.append(f"{name}: community source cannot establish primary format evidence")
    return errors


def validate_registry_files(root=ROOT, *, today=None):
    root = Path(root)
    try:
        content = (root / "docs/formats/format-registry.md").read_text(encoding="utf-8")
        registry = yaml.load(
            (root / "docs/sources/source-registry.yaml").read_text(encoding="utf-8"),
            Loader=UniqueKeyLoader,
        )
    except (OSError, UnicodeError, yaml.YAMLError):
        return ["format/source registry is missing, unreadable, or invalid YAML"]
    return validate_format_registry(content, registry, today=today)


def main():
    errors = validate_registry_files()
    if errors:
        print("FORMAT/SOURCE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("FORMAT/SOURCE VALIDATION PASSED: 9 format policies; scoped source references checked")
    print("Offline checks do not prove source truth, freshness, or manufacturing readiness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
