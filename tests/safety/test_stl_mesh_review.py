"""Deterministic byte mutations, not pre-labeled mesh-validity assertions."""

import copy
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.additive_preflight import load_contexts, preflight
from scripts.stl_mesh_review import inspect_stl


ROOT = Path(__file__).resolve().parents[2]


def tetrahedron(scale=1):
    a, b, c, d = (0, 0, 0), (scale, 0, 0), (0, scale, 0), (0, 0, scale)
    return [(a, c, b), (a, b, d), (a, d, c), (b, c, d)]


def binary(triangles, header=b"synthetic topology test", normal=(0, 0, 0)):
    return header.ljust(80, b" ") + struct.pack("<I", len(triangles)) + b"".join(
        struct.pack("<12fH", *normal, *a, *b, *c, 0) for a, b, c in triangles)


def ascii_stl(triangles):
    facets = ["facet normal 0 0 0\nouter loop\n" + "\n".join(
        "vertex " + " ".join(str(value) for value in point) for point in triangle) + "\nendloop\nendfacet"
        for triangle in triangles]
    return ("solid test\n" + "\n".join(facets) + "\nendsolid test\n").encode()


class StlMeshReviewTests(unittest.TestCase):
    def assert_defect(self, data, key):
        result = inspect_stl(data)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("MISSING_CONTEXT", result["blockers"])
        self.assertGreater(result["topology"][key], 0)
        self.assertFalse(result["execution_allowed"])
        self.assertTrue(result["review_required"])
        json.dumps(result, allow_nan=False)

    def test_closed_ascii_and_binary_controls_preserve_identity(self):
        for data in (binary(tetrahedron()), ascii_stl(tetrahedron())):
            result = inspect_stl(data)
            self.assertEqual(result["status"], "checked_partial_geometry")
            self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(result["triangles"], 4)
            self.assertEqual(result["dimensions"], dict(x=1, y=1, z=1))
            self.assertIn("self-intersections not checked", result["limitations"])

    def test_binary_solid_header_is_not_misclassified_as_ascii(self):
        result = inspect_stl(binary(tetrahedron(), header=b"solid binary header"))
        self.assertEqual(result["encoding"], "binary")
        self.assertEqual(result["blockers"], [])

    def test_removed_face_exposes_open_boundary(self):
        self.assert_defect(binary(tetrahedron()[:-1]), "boundary_edges")

    def test_duplicate_face_and_overused_edges_are_detected(self):
        data = binary(tetrahedron() + [tetrahedron()[0]])
        self.assert_defect(data, "duplicate_faces")
        self.assert_defect(data, "nonmanifold_edges")

    def test_reversed_face_exposes_winding_conflict(self):
        triangles = tetrahedron()
        triangles[0] = tuple(reversed(triangles[0]))
        self.assert_defect(binary(triangles), "winding_conflicts")

    def test_zero_area_distinct_vertices_and_repeated_vertices_are_detected(self):
        for triangle in (((0, 0, 0), (1, 0, 0), (2, 0, 0)), ((0, 0, 0),) * 3):
            self.assert_defect(binary(tetrahedron() + [triangle]), "degenerate_faces")

    def test_touching_tetrahedra_require_vertex_fan_check_not_only_edge_counts(self):
        second = [tuple(tuple(-value for value in point) for point in reversed(triangle)) for triangle in tetrahedron()]
        data = binary(tetrahedron() + second)
        self.assert_defect(data, "nonmanifold_vertices")
        self.assertEqual(inspect_stl(data)["topology"]["nonmanifold_edges"], 0)

    def test_disconnected_shells_require_further_review(self):
        second = [tuple(tuple(value + 3 for value in point) for point in triangle) for triangle in tetrahedron()]
        result = inspect_stl(binary(tetrahedron() + second))
        self.assertEqual(result["topology"]["shells"], 2)
        self.assertIn("SOURCE_VERIFICATION_REQUIRED", result["blockers"])

    def test_reversed_closed_surface_is_not_a_positive_volume(self):
        result = inspect_stl(binary([tuple(reversed(triangle)) for triangle in tetrahedron()]))
        self.assertFalse(result["topology"]["signed_volume_positive"])
        self.assertIn("MISSING_CONTEXT", result["blockers"])

    def test_stored_normal_opposed_to_geometric_winding_blocks(self):
        self.assert_defect(binary(tetrahedron(), normal=(0, 0, 1)), "normal_conflicts")

    def test_parser_rejects_truncation_trailing_data_and_wrong_count(self):
        data = binary(tetrahedron())
        wrong_count = data[:80] + struct.pack("<I", 999) + data[84:]
        for invalid in (data[:-1], data + b"extra", wrong_count, b"", b"solid x\nendsolid x\n", b"\xff"):
            with self.subTest(length=len(invalid)):
                self.assertIn("MISSING_CONTEXT", inspect_stl(invalid)["blockers"])

    def test_ascii_vertices_without_valid_facet_grammar_are_not_accepted(self):
        data = ascii_stl(tetrahedron())
        for invalid in (data.replace(b"outer loop", b"unknown"), data.replace(b"endfacet", b""),
                        data.replace(b"endsolid test", b"endsolid wrong"), data + b"vertex 1 1 1",
                        data.replace(b"vertex 0", b"vertex NaN", 1)):
            self.assertEqual(inspect_stl(invalid)["status"], "blocked")

    def test_nonfinite_coordinates_and_normals_never_leak_into_json(self):
        for offset in (84, 96):
            for value in (math.nan, math.inf, -math.inf):
                data = bytearray(binary(tetrahedron()))
                struct.pack_into("<f", data, offset, value)
                result = inspect_stl(bytes(data))
                self.assertIn("MISSING_CONTEXT", result["blockers"])
                self.assertIsNone(result["bounds"])
                json.dumps(result, allow_nan=False)

    def test_attribute_extensions_and_resource_limits_require_review(self):
        data = bytearray(binary(tetrahedron()))
        struct.pack_into("<H", data, 132, 1)
        self.assertEqual(inspect_stl(bytes(data))["status"], "blocked")
        with patch("scripts.stl_mesh_review.MAX_BYTES", 10):
            result = inspect_stl(bytes(data))
            self.assertIn("SOURCE_VERIFICATION_REQUIRED", result["blockers"])
            self.assertIsNone(result["sha256"])
        with patch("scripts.stl_mesh_review.MAX_TRIANGLES", 3):
            for data in (binary(tetrahedron()), ascii_stl(tetrahedron())):
                self.assertEqual(inspect_stl(data)["status"], "blocked")

    def test_tiny_nonzero_geometry_is_not_rounded_to_degenerate(self):
        result = inspect_stl(ascii_stl(tetrahedron(1e-200)))
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["topology"]["degenerate_faces"], 0)


class AdditiveFilePreflightTests(unittest.TestCase):
    def setUp(self):
        self.contexts = load_contexts(ROOT / "fixtures/additive/fdm-bracket/contexts")
        self.mesh = (ROOT / "fixtures/cad/bracket/source/bracket.stl").read_bytes()

    def review(self, mesh=None, reidentify=False):
        data = self.mesh if mesh is None else mesh
        if reidentify:
            self.contexts["job"]["mesh_sha256"] = hashlib.sha256(data).hexdigest()
        return preflight(**self.contexts, mesh_bytes=data, source_revision="A")

    def test_real_fixture_has_observed_topology_and_unit_aware_dimensions(self):
        before = copy.deepcopy(self.contexts)
        result = self.review()
        self.assertEqual(result["blockers"], ["HUMAN_APPROVAL_REQUIRED"])
        self.assertEqual(result["file_review"]["triangles"], 2052)
        self.assertEqual(result["file_review"]["dimensions"], dict(x=60, y=40, z=30))
        self.assertEqual(self.contexts, before)

    def test_retained_actual_mesh_observations_replay_without_repair(self):
        report = json.loads((ROOT / "fixtures/additive/fdm-bracket/expected/stl-observations.json").read_text(encoding="utf-8"))
        count = struct.unpack_from("<I", self.mesh, 80)[0]
        changed = self.mesh[:80] + struct.pack("<I", count - 1) + self.mesh[84:-50]
        for case, data in (("positive", self.mesh), ("missing-last-facet", changed)):
            with self.subTest(case=case):
                expected = dict(report["cases"][case])
                expected.pop("mutation")
                result = inspect_stl(data)
                self.assertEqual({key: result[key] for key in expected}, expected)
                self.assertFalse(result["execution_allowed"])
                self.assertTrue(result["review_required"])
        self.assertEqual(self.mesh, (ROOT / "fixtures/cad/bracket/source/bracket.stl").read_bytes())

    def test_actual_removed_facet_blocks_even_with_updated_hash_and_valid_label(self):
        count = struct.unpack_from("<I", self.mesh, 80)[0]
        changed = self.mesh[:80] + struct.pack("<I", count - 1) + self.mesh[84:-50]
        result = self.review(changed, reidentify=True)
        self.assertEqual(self.contexts["job"]["mesh_status"], "valid")
        self.assertIn("MISSING_CONTEXT", result["blockers"])
        self.assertGreater(result["file_review"]["topology"]["boundary_edges"], 0)

    def test_changed_bytes_cannot_reuse_original_identity(self):
        result = self.review(b"new header".ljust(80, b" ") + self.mesh[80:])
        self.assertIn("SOURCE_VERIFICATION_REQUIRED", result["blockers"])
        self.assertEqual(result["file_review"]["status"], "checked_partial_geometry")

    def test_actual_extents_cannot_be_hidden_by_metadata(self):
        self.contexts["job"]["model_dimensions"] = dict(x=1, y=1, z=1)
        self.contexts["printer"]["capabilities"]["build_volume"] = dict(x=10, y=10, z=10)
        result = self.review()
        self.assertIn("MISSING_CONTEXT", result["blockers"])
        self.assertIn("MACHINE_CONTEXT_REQUIRED", result["blockers"])

    def test_extent_subtraction_cannot_round_away_a_real_exceedance(self):
        triangles = [tuple((-2**-60 if point[0] == 0 else point[0], point[1], point[2])
                           for point in triangle) for triangle in tetrahedron()]
        self.contexts["job"]["model_dimensions"] = dict(x=1, y=1, z=1)
        self.contexts["printer"]["capabilities"]["build_volume"] = dict(x=1, y=1, z=1)
        result = self.review(binary(triangles), reidentify=True)
        self.assertEqual(result["file_review"]["dimensions"]["x"], 1.0)
        self.assertNotEqual(result["file_review"]["dimensions_exact"]["x"], "1")
        self.assertIn("MACHINE_CONTEXT_REQUIRED", result["blockers"])

    def test_inches_are_not_compared_as_millimetres(self):
        self.contexts["job"]["mesh_units"] = "in"
        self.assertIn("MACHINE_CONTEXT_REQUIRED", self.review()["blockers"])

    def test_printer_inches_are_converted_and_exact_boundary_is_accepted(self):
        mesh = binary(tetrahedron(2.5))
        self.contexts["job"].update(mesh_units="inch", model_dimensions=dict(x=2.5, y=2.5, z=2.5))
        self.contexts["printer"]["capabilities"]["build_volume"] = dict(x=63.5, y=63.5, z=63.5)
        self.assertEqual(self.review(mesh, reidentify=True)["blockers"], ["HUMAN_APPROVAL_REQUIRED"])
        self.contexts["printer"]["capabilities"]["build_volume"]["x"] = 63.499999
        self.assertIn("MACHINE_CONTEXT_REQUIRED", self.review(mesh)["blockers"])
        self.contexts["printer"]["lifecycle"]["units"]["length"] = "inch"
        self.contexts["printer"]["capabilities"]["build_volume"] = dict(x=2.5, y=2.5, z=2.5)
        self.assertEqual(self.review(mesh)["blockers"], ["HUMAN_APPROVAL_REQUIRED"])

    def test_absent_bytes_revision_units_and_invalid_numeric_context_block(self):
        self.assertIn("MISSING_CONTEXT", preflight(**self.contexts)["blockers"])
        self.assertIn("MISSING_CONTEXT", preflight(**self.contexts, mesh_bytes=self.mesh)["blockers"])
        original = copy.deepcopy(self.contexts)
        for field, value in (("mesh_units", None), ("model_dimensions", None), ("mesh_format", [])):
            self.contexts = copy.deepcopy(original)
            self.contexts["job"][field] = value
            self.assertTrue(self.review()["blockers"])
        for value in (None, True, 0, -1, "200", math.nan, math.inf):
            self.contexts = copy.deepcopy(original)
            self.contexts["printer"]["capabilities"]["build_volume"]["x"] = value
            result = self.review()
            self.assertIn("MACHINE_CONTEXT_REQUIRED", result["blockers"])
            json.dumps(result, allow_nan=False)
        self.contexts = copy.deepcopy(original)
        self.contexts["printer"]["lifecycle"]["units"] = {}
        self.assertIn("MACHINE_CONTEXT_REQUIRED", self.review()["blockers"])

    def test_3mf_is_not_accepted_as_an_stl_or_a_metadata_label(self):
        self.contexts["job"]["mesh_format"] = "3MF"
        result = self.review()
        self.assertIn("MISSING_CONTEXT", result["blockers"])
        self.assertEqual(result["file_review"]["status"], "blocked")
        self.assertIsNone(result["file_review"]["dimensions_exact"])

    def test_malformed_top_level_and_nested_contexts_fail_closed(self):
        for field in ("job", "printer", "material"):
            contexts = dict(self.contexts, **{field: None})
            result = preflight(**contexts, mesh_bytes=self.mesh, source_revision="A")
            self.assertIn("MISSING_CONTEXT", result["blockers"])
        for field in ("capabilities", "lifecycle"):
            self.contexts["printer"][field] = []
            self.assertIn("MACHINE_CONTEXT_REQUIRED", self.review()["blockers"])

    def test_cli_reads_explicit_mesh_and_returns_blocked_exit_for_damaged_file(self):
        with tempfile.TemporaryDirectory(prefix="additive-file-test-") as temporary:
            path = Path(temporary) / "damaged.stl"
            path.write_bytes(self.mesh[:-50])
            for entry in (["scripts/additive_preflight.py"], ["-m", "scripts.additive_preflight"]):
                run = subprocess.run([sys.executable, *entry, "--mesh", str(path), "--source-revision", "A"],
                                     cwd=ROOT, capture_output=True, text=True, timeout=30)
                self.assertEqual(run.returncode, 1, run.stderr)
                result = json.loads(run.stdout)
                self.assertIn("MISSING_CONTEXT", result["blockers"])
                self.assertFalse(result["execution_allowed"])


if __name__ == "__main__":
    unittest.main()
