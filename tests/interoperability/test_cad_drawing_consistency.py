"""Inspect drawing declarations themselves, independently of byte bindings."""

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.cad_handoff_checks import review_fixture
from scripts.validate_cad_fixture_design import validate


ROOT = Path(__file__).resolve().parents[2]


class CadDrawingConsistencyTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="cad-drawing-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name) / "bracket"
        shutil.copytree(ROOT / "fixtures/cad/bracket", self.root)
        self.svg = self.root / "source/bracket.svg"

    def change(self, before, after, path=None):
        target = path or self.svg
        text = target.read_text(encoding="utf-8")
        self.assertIn(before, text)
        target.write_text(text.replace(before, after), encoding="utf-8")

    def test_conflicting_visible_dimension_blocks_even_with_original_description(self):
        self.change("BASE: 60 x 40 x 6", "BASE: 61 x 40 x 6")
        self.assertTrue(validate(self.root))

    def test_conflicting_additional_annotation_is_not_masked_by_correct_one(self):
        self.change("</svg>", '<text x="10" y="45" font-size="3">REV A | UNITS: mm | BASE: 61 x 40 x 6</text></svg>')
        self.assertTrue(validate(self.root))

    def test_comment_cannot_supply_missing_visible_revision(self):
        self.change("REV A | UNITS: mm", "REV B | UNITS: mm")
        self.change("</svg>", "<!-- REV A --></svg>")
        self.assertTrue(validate(self.root))

    def test_comment_cannot_supply_source_parameter(self):
        source = self.root / "source/bracket.scad"
        self.change("plate_width = 60;", "// plate_width = 60;\nplate_width = 61;", source)
        self.assertTrue(validate(self.root))

    def test_duplicate_source_assignment_is_unresolved(self):
        self.change("plate_width = 60;", "plate_width = 60;\nplate_width = 61;", self.root / "source/bracket.scad")
        self.assertTrue(validate(self.root))

    def test_same_line_duplicates_strings_and_expressions_cannot_supply_source_parameters(self):
        source = self.root / "source/bracket.scad"
        original = source.read_bytes()
        for replacement in ('plate_width = 60; plate_width = 61;',
                            'echo("plate_width = 60;");',
                            'plate_width = 30 * 2;', 'plate_width = 1e999;'):
            with self.subTest(replacement=replacement):
                self.change("plate_width = 60;", replacement, source)
                self.assertTrue(validate(self.root))
                source.write_bytes(original)

    def test_projected_geometry_conflicts_with_declared_dimensions(self):
        for before, after in (('width="60"', 'width="61"'), ('r="3"', 'r="4"'), ('cx="22"', 'cx="23"')):
            with self.subTest(after=after):
                original = self.svg.read_bytes()
                self.change(before, after)
                self.assertTrue(validate(self.root))
                self.svg.write_bytes(original)

    def test_unsupported_rendering_and_malformed_xml_fail_closed(self):
        for before, after in (
            ('<svg xmlns=', '<svg transform="scale(2)" xmlns='),
            ('<text x="10" y="7"', '<text style="display:none" x="10" y="7"'),
            ('<svg xmlns=', '<svg onload="ignored()" xmlns='),
            ('</svg>', '<path d="M 0 0" /></svg>'),
            ('</svg>', '<text>WIDTH: 61</text></svg>'),
            ('<svg xmlns=', '<!DOCTYPE svg [<!ENTITY extra "REV A">]><svg xmlns='),
            ('<svg xmlns=', '<?xml-stylesheet href="external.css"?><svg xmlns='),
            ('</svg>', ''),
        ):
            with self.subTest(after=after):
                original = self.svg.read_bytes()
                self.change(before, after)
                self.assertTrue(validate(self.root))
                self.svg.write_bytes(original)

    def test_wrong_viewport_or_missing_mm_scale_blocks(self):
        for before, after in (('width="80mm"', 'width="80"'), ('viewBox="0 0 80 55"', 'viewBox="0 0 160 110"')):
            with self.subTest(after=after):
                original = self.svg.read_bytes()
                self.change(before, after)
                self.assertTrue(validate(self.root))
                self.svg.write_bytes(original)

    def test_structurally_equivalent_declarations_pass_without_substring_dependence(self):
        self.change("BASE: 60 x 40 x 6", "BASE: <tspan>60.0</tspan> x 40.0 x 6.0")
        metadata = self.root / "metadata/revision.json"
        metadata.write_text(json.dumps(json.loads(metadata.read_text(encoding="utf-8")), separators=(",", ":")), encoding="utf-8")
        self.assertEqual(validate(self.root), [])

    def test_xml_declaration_and_untransformed_group_preserve_valid_fixture(self):
        self.change('<svg xmlns=', '<?xml version="1.0"?><svg xmlns=')
        self.change('<rect ', '<g><rect ')
        self.change('</svg>', '</g></svg>')
        self.assertEqual(validate(self.root), [])

    def test_missing_and_nonnumeric_projected_geometry_blocks(self):
        for before, after in (('r="3"', 'r="nan"'), ('r="3"', ''), ('width="60"', 'width="6_0"'),
                              ('font-size="3"', 'font-size="0"'),
                              ('font-size="3"', 'font-size="NaN"')):
            with self.subTest(after=after):
                original = self.svg.read_bytes()
                self.change(before, after)
                self.assertTrue(validate(self.root))
                self.svg.write_bytes(original)

    def test_source_revision_and_units_declaration_must_be_unique_and_explicit(self):
        source = self.root / "source/bracket.scad"
        original = source.read_bytes()
        declaration = "// Units: millimetres. Revision: A."
        for replacement in ("", "// Units: inches. Revision: A.",
                            declaration + "\n// Units: inches. Revision: B."):
            with self.subTest(replacement=replacement):
                self.change(declaration, replacement, source)
                self.assertTrue(validate(self.root))
                source.write_bytes(original)

    def test_conflicting_drawing_still_blocks_after_matching_hash_is_declared(self):
        self.change("BASE: 60 x 40 x 6", "BASE: 61 x 40 x 6")
        path = self.root / "metadata/derivation.json"
        binding = json.loads(path.read_text(encoding="utf-8"))
        for entry in binding["derivatives"]:
            if entry["artifact"]["path"] == "source/bracket.svg":
                entry["artifact"]["sha256"] = hashlib.sha256(self.svg.read_bytes()).hexdigest()
        # Deliberately forge a self-consistent declaration in the test copy only.
        path.write_text(json.dumps(binding), encoding="utf-8")
        result = review_fixture(self.root)
        self.assertEqual(result["file_checks"][-1]["status"], "passed")
        self.assertEqual(result["file_checks"][0]["status"], "failed")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("MISSING_CONTEXT", result["blockers"])
        self.assertFalse(result["execution_allowed"])


if __name__ == "__main__":
    unittest.main()
