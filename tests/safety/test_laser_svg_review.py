"""Actual SVG mutations; no renderer, network, repair, settings or laser action."""

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import laser_svg_review as svg
from scripts.validate_laser_fixture_geometry import validate


ROOT = Path(__file__).resolve().parents[2]


def drawing(body, attributes='width="100mm" height="100mm" viewBox="0 0 100 100"'):
    return (f'<svg xmlns="{svg.SVG}" {attributes}><g fill="none" stroke="black">{body}</g></svg>').encode()


class LaserSvgReviewTests(unittest.TestCase):
    def inspect(self, data, blocker=None):
        result = svg.inspect_svg(data)
        self.assertTrue(result["review_required"])
        self.assertFalse(result["execution_allowed"])
        json.dumps(result, allow_nan=False)
        if blocker:
            self.assertIn(blocker, result["blockers"], result)
            self.assertEqual(result["status"], "blocked")
        else:
            self.assertEqual(result["blockers"], [], result)
            self.assertEqual(result["status"], "checked_partial_geometry")
        return result

    def test_actual_fixture_preserves_identity_physical_bounds_and_contours(self):
        data = (ROOT / "fixtures/laser/cut-bracket/source/bracket.svg").read_bytes()
        result = self.inspect(data)
        self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(result["dimensions_mm"], {"x": "60", "y": "40"})
        self.assertEqual(result["bounds_mm"], {"min": ["5", "5"], "max": ["65", "45"]})
        self.assertEqual(result["geometry"], {"contours": 3, "segments": 4, "circles": 2,
            "open_contours": 0, "degenerate_contours_or_edges": 0, "duplicate_segments": 0,
            "duplicate_circles": 0, "intersections_or_touches": 0})

    def test_changed_viewbox_or_physical_units_change_measured_scale(self):
        body = '<rect x="1" y="1" width="10" height="10"/>'
        double = self.inspect(drawing(body, 'width="100mm" height="100mm" viewBox="0 0 50 50"'))
        inch = self.inspect(drawing(body, 'width="100in" height="100in" viewBox="0 0 100 100"'))
        self.assertEqual(double["dimensions_mm"], {"x": "20", "y": "20"})
        self.assertEqual(inch["dimensions_mm"], {"x": "254", "y": "254"})
        self.assertEqual(inch["viewport"]["declared_width_unit"], "in")

    def test_meet_letterboxing_and_nonzero_viewbox_origin_are_applied(self):
        body = '<rect x="10" y="20" width="10" height="10"/>'
        result = self.inspect(drawing(body, 'width="100mm" height="50mm" viewBox="10 20 50 50"'))
        self.assertEqual(result["bounds_mm"], {"min": ["25", "0"], "max": ["35", "10"]})
        result = self.inspect(drawing(body, 'width="100mm" height="50mm" viewBox="10 20 50 50" preserveAspectRatio="xMaxYMin"'))
        self.assertEqual(result["bounds_mm"]["min"], ["50", "0"])

    def test_nested_transform_order_rotation_and_reflection(self):
        result = self.inspect(drawing('<g transform="translate(20 10) scale(2)"><rect x="1" y="2" width="3" height="4"/></g>'))
        self.assertEqual(result["bounds_mm"], {"min": ["22", "14"], "max": ["28", "22"]})
        result = self.inspect(drawing('<rect x="20" y="20" width="3" height="4" transform="rotate(90 20 20)"/>'))
        self.assertEqual(result["bounds_mm"], {"min": ["16", "20"], "max": ["20", "23"]})
        result = self.inspect(drawing('<g transform="translate(50 0)"><circle cx="10" cy="10" r="3" transform="scale(-1 1)"/></g>'))
        self.assertEqual(result["bounds_mm"], {"min": ["37", "7"], "max": ["43", "13"]})

    def test_absolute_relative_and_repeated_linear_path_commands(self):
        for path in ('M10 10 L20 10 20 20 10 20Z', 'm10 10 h10v10h-10z', 'M10,10H20V20H10Z', 'M10 10 20 10 20 20 10 20z'):
            with self.subTest(path=path):
                result = self.inspect(drawing(f'<path d="{path}"/>'))
                self.assertEqual(result["dimensions_mm"], {"x": "10", "y": "10"})

    def test_actual_open_lines_paths_and_polylines_block(self):
        for body in ('<line x1="1" y1="1" x2="10" y2="10"/>', '<polyline points="1,1 10,1 10,10"/>', '<path d="M1 1L10 1 10 10"/>'):
            result = self.inspect(drawing(body), "MISSING_CONTEXT")
            self.assertEqual(result["geometry"]["open_contours"], 1)

    def test_explicit_return_to_start_is_measured_as_closed_without_input_repair(self):
        data = drawing('<polyline points="1,1 10,1 10,10 1,1"/>')
        result = self.inspect(data)
        self.assertTrue(result["contours_mm"][0]["closed"])
        self.assertEqual(len(result["contours_mm"][0]["points"]), 3)
        self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())

    def test_duplicate_geometry_ignores_path_start_direction_and_element_kind(self):
        result = self.inspect(drawing('<rect x="10" y="10" width="10" height="10"/><path d="M20 20L20 10 10 10 10 20z"/>'), "MISSING_CONTEXT")
        self.assertEqual(result["geometry"]["duplicate_segments"], 4)
        result = self.inspect(drawing('<circle cx="20" cy="20" r="3"/><circle cx="10" cy="10" r="1.5" transform="scale(2)"/>'), "MISSING_CONTEXT")
        self.assertEqual(result["geometry"]["duplicate_circles"], 1)

    def test_crossings_touches_and_partial_collinear_overlap_block(self):
        for body in (
            '<polygon points="10,10 20,20 10,20 20,10"/>',
            '<rect x="10" y="10" width="10" height="10"/><rect x="20" y="20" width="10" height="10"/>',
            '<polygon points="10,10 20,10 15,10 15,20 10,20"/>',
            '<circle cx="20" cy="20" r="5"/><circle cx="30" cy="20" r="5"/>',
            '<rect x="10" y="10" width="10" height="10"/><circle cx="20" cy="15" r="3"/>',
        ):
            with self.subTest(body=body):
                result = self.inspect(drawing(body), "MISSING_CONTEXT")
                self.assertGreater(result["geometry"]["intersections_or_touches"], 0)

    def test_containment_is_not_mistaken_for_contour_intersection(self):
        result = self.inspect(drawing('<circle cx="20" cy="20" r="10"/><circle cx="20" cy="20" r="3"/>'))
        self.assertEqual(result["geometry"]["intersections_or_touches"], 0)
        self.inspect(drawing('<rect x="1" y="1" width="40" height="40"/><polygon points="10,10 20,10 20,20 10,20"/>'))

    def test_tiny_exact_differences_survive_measurement(self):
        result = self.inspect(drawing('<rect x="1" y="1" width="10.000000000000000001" height="10"/>'))
        self.assertGreater(Fraction(result["dimensions_mm"]["x"]), 10)
        self.assertNotEqual(result["dimensions_mm"]["x"], "10")

    def test_unsupported_semantics_cannot_be_ignored(self):
        for body in ('<ellipse cx="20" cy="20" rx="3" ry="4"/>', '<path d="M1 1C2 2 3 3 4 4Z"/>',
                     '<rect width="10" height="10" rx="2"/>', '<use href="https://example.invalid/remote.svg"/>',
                     '<script>raise_approval()</script>', '<image href="private.png"/>',
                     '<rect width="10" height="10" style="display:none"/>',
                     '<rect width="10" height="10" stroke="transparent"/>',
                     '<circle cx="20" cy="20" r="3" transform="scale(2 1)"/>',
                     '<rect width="10" height="10" transform="rotate(45)"/>'):
            with self.subTest(body=body):
                self.inspect(drawing(body), "SOURCE_VERIFICATION_REQUIRED")

    def test_missing_ambiguous_viewport_and_clipping_require_review(self):
        for attrs in ('width="100" height="100" viewBox="0 0 100 100"',
                      'width="100px" height="100px" viewBox="0 0 100 100"',
                      'width="100mm" height="100mm" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice"'):
            self.inspect(drawing('<rect width="10" height="10"/>', attrs), "SOURCE_VERIFICATION_REQUIRED")
        self.inspect(drawing('<rect x="95" y="1" width="10" height="10"/>'), "SOURCE_VERIFICATION_REQUIRED")

    def test_malformed_degenerate_and_nonfinite_geometry_block(self):
        for body in ('<rect width="0" height="1"/>', '<circle r="-1"/>', '<rect width="NaN" height="1"/>',
                     '<path d="M1 1L"/>', '<path d="L1 1 2 2"/>', '<polygon points="1 1 2 2 3 3"/>',
                     '<rect width="1" height="1" transform="matrix(0 0 0 1 0 0)"/>'):
            self.inspect(drawing(body), "MISSING_CONTEXT")
        for data in (None, b"", b"not XML", b'<svg xmlns="wrong"/>'):
            self.inspect(data, "MISSING_CONTEXT")

    def test_declarations_and_processing_instructions_do_not_execute_or_resolve(self):
        valid = drawing('<rect width="10" height="10"/>')
        self.inspect(b'<?xml version="1.0" encoding="UTF-8"?>'+valid)
        for prefix in (b'<!DOCTYPE svg [<!ENTITY x SYSTEM "file:///private">]>',
                       b'<?xml-stylesheet href="https://example.invalid/style.css"?>',
                       b'<?xml version="1.0" encoding="UTF-16"?>'):
            self.inspect(prefix+valid, "SOURCE_VERIFICATION_REQUIRED")

    def test_resource_limits_do_not_return_partial_success(self):
        data = drawing('<rect width="10" height="10"/>')
        with patch.object(svg, "MAX_BYTES", 10):
            self.assertIsNone(self.inspect(data, "SOURCE_VERIFICATION_REQUIRED")["sha256"])
        for field, value in (("MAX_NODES", 2), ("MAX_SEGMENTS", 3)):
            with patch.object(svg, field, value):
                self.inspect(data, "SOURCE_VERIFICATION_REQUIRED")
        self.inspect(drawing('<g>'*33+'<rect width="1" height="1"/>'+'</g>'*33), "SOURCE_VERIFICATION_REQUIRED")
        self.inspect(drawing('<rect width="1e100" height="1"/>'), "SOURCE_VERIFICATION_REQUIRED")

    def test_malformed_separators_cannot_be_silently_normalized(self):
        for body in ('<polygon points="1,1,,10,1,10,10"/>', '<path d="M,1 1L10 1 10 10Z"/>',
                     '<path d="M1 1L10 1 10 10Z,"/>', '<path d="M1 1L10,,1 10 10Z"/>',
                     '<rect width="1" height="1" transform=",translate(1)"/>'):
            self.inspect(drawing(body), "MISSING_CONTEXT")

    def test_exponents_beyond_decimal_implementation_range_block_without_exception(self):
        for numeric in ("1e999999999999999999999999999", "1e-999999999999999999999999999"):
            for body in (f'<rect width="{numeric}" height="1"/>',
                         f'<rect width="1" height="1" transform="scale({numeric})"/>',
                         f'<circle cx="20" cy="20" r="3" stroke-width="{numeric}"/>'):
                self.inspect(drawing(body), "SOURCE_VERIFICATION_REQUIRED")
            self.inspect(drawing('<rect width="1" height="1"/>',
                                f'width="{numeric}mm" height="100mm" viewBox="0 0 100 100"'),
                         "SOURCE_VERIFICATION_REQUIRED")

    def test_fixture_validator_reads_altered_geometry_not_status_labels(self):
        source = ROOT / "fixtures/laser/cut-bracket"
        original = (source / "source/bracket.svg").read_text(encoding="utf-8")
        mutations = (
            original.replace('width="60"', 'width="61"'),
            original.replace('cx="17"', 'cx="18"'),
            original.replace('r="3"', 'r="4"'),
            original.replace('70 50', '140 100'),
            original.replace('70mm', '70in'),
            original.replace('</g>', '<circle cx="17" cy="25" r="3"/></g>'),
            original.replace('</g>', '<polyline points="1,1 2,2 3,2"/></g>'),
            original.replace('</g>', '<path d="M1 1C2 2 3 3 4 4Z"/></g>'),
        )
        with tempfile.TemporaryDirectory(prefix="laser-svg-") as directory:
            root = Path(directory)
            shutil.copytree(source / "source", root / "source")
            self.assertEqual(validate(root), [])
            for mutated in mutations:
                with self.subTest(mutation=mutated):
                    (root / "source/bracket.svg").write_text(mutated, encoding="utf-8")
                    self.assertTrue(validate(root))
            (root / "source/bracket.svg").write_bytes(b"\xff\xfe invalid SVG")
            self.assertTrue(validate(root))


if __name__ == "__main__":
    unittest.main()
