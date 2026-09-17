"""Planar DXF byte mutations, exact geometry and explicit unsupported semantics."""

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import tempfile
import shutil
import unittest
from unittest.mock import patch

from scripts import laser_dxf_review as dxf
from scripts.laser_svg_review import inspect_svg
from scripts.validate_laser_fixture_geometry import validate


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures/laser/cut-bracket"


def tags(values):
    return "".join(f"{code}\n{value}\n" for code, value in values).encode("ascii")


def document(entities, unit=4, layer_extra=(), header_extra=()):
    return tags([(0, "SECTION"), (2, "HEADER"), (9, "$ACADVER"), (1, "AC1024"),
                 (9, "$INSUNITS"), (70, unit), *header_extra, (0, "ENDSEC"),
                 (0, "SECTION"), (2, "TABLES"), (0, "TABLE"), (2, "LAYER"),
                 (0, "LAYER"), (2, "0"), *layer_extra, (0, "ENDTAB"), (0, "ENDSEC"),
                 (0, "SECTION"), (2, "ENTITIES"), *entities, (0, "ENDSEC"), (0, "EOF")])


def polygon(points=((1, 1), (11, 1), (11, 11), (1, 11)), closed=1, extra=()):
    return [(0, "LWPOLYLINE"), (8, "0"), (90, len(points)), (70, closed), *extra,
            *(tag for x, y in points for tag in ((10, x), (20, y)))]


def circle(x=5, y=5, r=1, extra=()):
    return [(0, "CIRCLE"), (8, "0"), (10, x), (20, y), (40, r), *extra]


def fixture_mutation(data, change):
    head, tail = data.split(b"  2\nENTITIES\n", 1)
    entities, rest = tail.split(b"  0\nENDSEC", 1)
    return head+b"  2\nENTITIES\n"+change(entities)+b"  0\nENDSEC"+rest


class LaserDxfReviewTests(unittest.TestCase):
    def check(self, data, blocker=None):
        result = dxf.inspect_dxf(data)
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

    def test_actual_dxf_matches_svg_contours_in_physical_units(self):
        data = (FIXTURE / "source/bracket.dxf").read_bytes()
        result = self.check(data)
        self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())
        other = inspect_svg((FIXTURE / "source/bracket.svg").read_bytes())
        for key in ("contours_mm", "bounds_mm", "dimensions_mm", "geometry"):
            self.assertEqual(result[key], other[key])
        self.assertEqual(result["declared_unit"], "mm")
        self.assertEqual(result["layers"], ["0"])

    def test_explicit_units_and_decimal_coordinates_are_exact(self):
        result = self.check(document(polygon(), unit=1))
        self.assertEqual(result["dimensions_mm"], {"x": "254", "y": "254"})
        self.assertEqual(result["unit_scale_mm"], "127/5")
        result = self.check(document(polygon(), unit=5))
        self.assertEqual(result["dimensions_mm"]["x"], "100")
        result = self.check(document(polygon(((1, 1), ("11.000000000000000001", 1), (11, 11), (1, 11)))))
        self.assertGreater(Fraction(result["dimensions_mm"]["x"]), 10)

    def test_open_duplicate_and_intersecting_contours_are_byte_derived(self):
        self.assertEqual(self.check(document(polygon(closed=0)), "MISSING_CONTEXT")["geometry"]["open_contours"], 1)
        self.assertEqual(self.check(document(polygon()+polygon()), "MISSING_CONTEXT")["geometry"]["duplicate_segments"], 4)
        self.assertEqual(self.check(document(circle()+circle()), "MISSING_CONTEXT")["geometry"]["duplicate_circles"], 1)
        self.assertGreater(self.check(document(polygon()+circle(11, 5, 2)), "MISSING_CONTEXT")["geometry"]["intersections_or_touches"], 0)

    def test_exact_line_chains_close_without_tolerance_or_invented_edges(self):
        edges = [((1, 1), (11, 1)), ((11, 11), (1, 11)), ((11, 1), (11, 11)), ((1, 11), (1, 1))]
        lines = [tag for a, b in edges for tag in [(0, "LINE"), (8, "0"), (10, a[0]), (20, a[1]), (11, b[0]), (21, b[1])]]
        self.assertEqual(self.check(document(lines))["geometry"]["open_contours"], 0)
        self.check(document(lines[:-6]), "MISSING_CONTEXT")
        fork = [(0, "LINE"), (8, "0"), (10, 1), (20, 1), (11, 5), (21, 5)]
        self.check(document(lines+fork), "MISSING_CONTEXT")
        self.check(document(lines+lines[:6]), "MISSING_CONTEXT")

    def test_bulges_widths_extrusion_and_nonplanar_coordinates_block(self):
        for extra in (((38, 1),), ((43, 2),), ((210, 1),), ((230, -1),), ((39, 1),)):
            self.check(document(polygon(extra=extra)), "SOURCE_VERIFICATION_REQUIRED")
        for code in (40, 41, 42):
            self.check(document(polygon()+[(code, "0.5")]), "SOURCE_VERIFICATION_REQUIRED")
        self.check(document(circle(extra=((30, 1),))), "SOURCE_VERIFICATION_REQUIRED")
        self.check(document(polygon(closed=128)), "SOURCE_VERIFICATION_REQUIRED")

    def test_unsupported_entities_and_custom_subclasses_are_not_ignored(self):
        for kind in ("ARC", "SPLINE", "ELLIPSE", "INSERT", "IMAGE", "TEXT", "HATCH", "POLYLINE"):
            self.check(document(polygon()+[(0, kind), (8, "0")]), "SOURCE_VERIFICATION_REQUIRED")
        self.check(document(circle(extra=((100, "AcDbEntity"), (100, "AcDbEllipse")))), "SOURCE_VERIFICATION_REQUIRED")
        self.check(document(circle(extra=((1001, "untrusted-app"),))), "SOURCE_VERIFICATION_REQUIRED")

    def test_hidden_frozen_external_or_paper_space_paths_block(self):
        for extra in (((60, 1),), ((67, 1),), ((410, "Layout1"),), ((6, "DASHED"),), ((62, -1),), ((440, 0),)):
            self.check(document(circle(extra=extra)), "SOURCE_VERIFICATION_REQUIRED")
        for extra in (((70, 1),), ((70, 16),), ((62, -7),), ((290, 0),), ((6, "DASHED"),), ((440, 0),)):
            self.check(document(circle(), layer_extra=extra), "SOURCE_VERIFICATION_REQUIRED")

    def test_malformed_tags_counts_references_and_units_fail_closed(self):
        for data in (b"", None, b"not DXF", document(polygon())[:-6], document(polygon())+b"0\nEOF\n",
                     document(polygon()).replace(b"90\n4\n", b"90\n5\n"),
                     document(polygon()).replace(b"8\n0\n", b"8\nabsent\n"),
                     document(circle(extra=((40, 2),))), document(circle(r=-1)),
                     document(circle(r="NaN")), document(polygon()).replace(b"$INSUNITS", b"$OTHER")):
            self.check(data, "MISSING_CONTEXT")
        for unit in (0, 999):
            self.check(document(circle(), unit=unit), "SOURCE_VERIFICATION_REQUIRED")

    def test_limits_and_extreme_exponents_are_structured_refusals(self):
        data = document(polygon())
        with patch.object(dxf, "MAX_BYTES", 10):
            self.assertIsNone(self.check(data, "SOURCE_VERIFICATION_REQUIRED")["sha256"])
        with patch.object(dxf, "MAX_TAGS", 3):
            self.check(data, "SOURCE_VERIFICATION_REQUIRED")
        with patch.object(dxf, "MAX_SEGMENTS", 3):
            self.check(data, "SOURCE_VERIFICATION_REQUIRED")
        self.check(document(circle(r="1e999999999999999999999")), "SOURCE_VERIFICATION_REQUIRED")

    def test_real_fixture_mutations_fail_fixture_validation(self):
        data = (FIXTURE / "source/bracket.dxf").read_bytes()
        changes = (lambda b: b.replace(b" 70\n1\n", b" 70\n0\n"),
                   lambda b: b.replace(b"17.0\n", b"18.0\n"),
                   lambda b: b.replace(b"3.0\n", b"4.0\n"),
                   lambda b: b+tags(circle(17, 25, 3)),
                   lambda b: b+tags([(0, "ARC"), (8, "0")]))
        with tempfile.TemporaryDirectory(prefix="laser-dxf-") as directory:
            root = Path(directory)
            shutil.copytree(FIXTURE / "source", root / "source")
            self.assertEqual(validate(root), [])
            for change in changes:
                (root / "source/bracket.dxf").write_bytes(fixture_mutation(data, change))
                self.assertTrue(validate(root))


if __name__ == "__main__":
    unittest.main()
