from __future__ import annotations

import copy
import io
import re
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest.mock import patch

import yaml

from scripts import validate_foundation
from scripts.validate_format_registry import (
    FIELDS, FORMATS, SOURCE_TEXT_FIELDS,
    validate_format_registry, validate_registry_files,
)


ROOT = Path(__file__).resolve().parents[2]


class FormatRegistryTests(unittest.TestCase):
    def setUp(self):
        self.content = (ROOT / "docs/formats/format-registry.md").read_text(encoding="utf-8")
        self.sources = yaml.safe_load((ROOT / "docs/sources/source-registry.yaml").read_text(encoding="utf-8"))
        # Fixed review date keeps fixture mutations independent of the wall clock.
        self.today = date(2026, 9, 13)

    def errors(self, content=None, sources=None):
        return validate_format_registry(
            self.content if content is None else content,
            self.sources if sources is None else sources,
            today=self.today,
        )

    def test_all_policies_and_scoped_sources_validate(self):
        self.assertEqual(self.errors(), [])

    def test_each_required_field_is_checked_in_every_format(self):
        for name in sorted(FORMATS):
            before, section = self.content.split(f"## {name}\n", 1)
            body, separator, after = section.partition("\n## ")
            for field in sorted(FIELDS):
                with self.subTest(format=name, field=field):
                    mutated = re.sub(rf"^- {re.escape(field)}:.*$", "", body, flags=re.MULTILINE)
                    content = before + f"## {name}\n" + mutated + separator + after
                    self.assertTrue(any("policy fields" in error for error in self.errors(content=content)))

    def test_missing_duplicate_and_unexpected_formats_fail(self):
        for content in (
            self.content.replace("## Native CAD", "## Other"),
            self.content + "\n## STL\n",
            self.content.split("## STEP-NC")[0],
        ):
            with self.subTest(content_length=len(content)):
                self.assertTrue(self.errors(content=content))

    def test_empty_placeholder_duplicate_and_malformed_fields_fail(self):
        for replacement in (
            "- Unit handling:", "- Unit handling: TBD",
            "- Unit handling: first\n- Unit handling: duplicate",
            "- Unit handling without a colon",
        ):
            content = re.sub(r"^- Unit handling:.*$", lambda _: replacement, self.content, count=1, flags=re.MULTILINE)
            self.assertTrue(self.errors(content=content))

    def test_citations_must_match_source_id_locator_scope_and_status(self):
        for field, value, expected in (
            ("id", "renamed", "unknown source ID"),
            ("locator", "https://example.invalid/changed", "locator conflicts"),
            ("applies_to", ["STL"], "format scope"),
            ("review_status", "stale", "requires verification"),
            ("review_status", "conflicted", "requires verification"),
            ("review_status", "verification_required", "requires verification"),
            ("authority", "community", "primary format evidence"),
        ):
            with self.subTest(field=field, value=value):
                sources = copy.deepcopy(self.sources)
                sources["sources"][0][field] = value
                self.assertTrue(any(expected in error for error in self.errors(sources=sources)))

    def test_source_metadata_is_required_and_cannot_be_empty(self):
        for field in SOURCE_TEXT_FIELDS | {"claims", "applies_to", "publication_or_revision"}:
            with self.subTest(field=field):
                sources = copy.deepcopy(self.sources)
                del sources["sources"][0][field]
                self.assertTrue(self.errors(sources=sources))
        for field in SOURCE_TEXT_FIELDS | {"claims", "applies_to"}:
            with self.subTest(empty_field=field):
                sources = copy.deepcopy(self.sources)
                sources["sources"][0][field] = [] if field in {"claims", "applies_to"} else " "
                self.assertTrue(self.errors(sources=sources))

    def test_malformed_source_values_fail_without_crashing(self):
        for field in SOURCE_TEXT_FIELDS | {"claims", "applies_to", "publication_or_revision"}:
            for value in ([], {}, 1, True):
                with self.subTest(field=field, value=value):
                    sources = copy.deepcopy(self.sources)
                    sources["sources"][0][field] = value
                    self.assertTrue(self.errors(sources=sources))

    def test_source_registry_root_and_duplicate_ids_fail(self):
        duplicate = copy.deepcopy(self.sources)
        duplicate["sources"].append(copy.deepcopy(duplicate["sources"][0]))
        for sources in ([], {}, {"version": 2, "status": "active", "sources": []}, dict(self.sources, sources=[None]), duplicate):
            self.assertTrue(self.errors(sources=sources))

    def test_bad_future_and_unquoted_access_dates_fail(self):
        for value in ("2026-02-30", "2027-01-01", "20260913", date(2026, 9, 13)):
            with self.subTest(value=value):
                sources = copy.deepcopy(self.sources)
                sources["sources"][0]["accessed_at"] = value
                self.assertTrue(any("access date" in error for error in self.errors(sources=sources)))

    def test_missing_or_malformed_registry_files_report_errors(self):
        with patch.object(Path, "read_text", side_effect=FileNotFoundError):
            self.assertTrue(validate_registry_files(ROOT))
        with patch.object(Path, "read_text", side_effect=[self.content, "sources: ["]):
            self.assertTrue(validate_registry_files(ROOT))

    def test_duplicate_yaml_keys_cannot_hide_source_status(self):
        source_text = (ROOT / "docs/sources/source-registry.yaml").read_text(encoding="utf-8")
        source_text = source_text.replace("review_status: reviewed", "review_status: stale\n    review_status: reviewed", 1)
        with patch.object(Path, "read_text", side_effect=[self.content, source_text]):
            self.assertTrue(validate_registry_files(ROOT))

    def test_foundation_command_rejects_missing_source_evidence(self):
        read_text = Path.read_text

        def without_sources(path, *args, **kwargs):
            if path == ROOT / "docs/sources/source-registry.yaml":
                return "version: 2\nstatus: active\nsources: []\n"
            return read_text(path, *args, **kwargs)

        output = io.StringIO()
        with patch.object(Path, "read_text", without_sources), redirect_stdout(output):
            self.assertEqual(validate_foundation.main(), 1)
        self.assertIn("source registry requires nonempty sources", output.getvalue())

    def test_registry_covers_initial_exchange_formats(self):
        registry = (ROOT / "docs/formats/format-registry.md").read_text(encoding="utf-8")
        for format_name in ("STEP AP242", "IGES", "DXF", "SVG", "STL", "3MF", "NC/G-code", "STEP-NC"):
            with self.subTest(format_name=format_name):
                self.assertIn(format_name, registry)

    def test_registry_distinguishes_parseability_from_approval(self):
        registry = (ROOT / "docs/formats/format-registry.md").read_text(encoding="utf-8")
        self.assertIn("Parseability is not semantic fidelity", registry)
        self.assertIn("not manufacturing approval", registry)


if __name__ == "__main__":
    unittest.main()
