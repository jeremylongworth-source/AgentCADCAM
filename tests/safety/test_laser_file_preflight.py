"""Byte-aware laser utility, distinct from authenticated/composed approval."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.laser_preflight import load_contexts, preflight
from tests.safety.test_laser_dxf_review import FIXTURE, fixture_mutation, tags, circle


class LaserFilePreflightTests(unittest.TestCase):
    def control(self, format="DXF"):
        contexts = load_contexts(FIXTURE / "contexts")
        data = (FIXTURE / f"source/bracket.{format.lower()}").read_bytes()
        contexts["job"].update(format=format, drawing_sha256=hashlib.sha256(data).hexdigest(), approval_status="approved")
        return contexts, data

    def check(self, contexts, data, blocker=None, revision="A"):
        before = copy.deepcopy(contexts)
        result = preflight(**contexts, drawing_bytes=data, source_revision=revision)
        self.assertEqual(contexts, before)
        self.assertTrue(result["review_required"])
        self.assertFalse(result["execution_allowed"])
        self.assertNotIn("HUMAN_APPROVAL_REQUIRED", result["blockers"])
        if blocker:
            self.assertIn(blocker, result["blockers"], result)
            self.assertEqual(result["status"], "blocked")
        else:
            self.assertEqual(result["blockers"], [], result)
            self.assertEqual(result["status"], "review_required")
        json.dumps(result, allow_nan=False)
        return result

    def test_both_formats_have_review_only_controls_with_exact_identity(self):
        for format in ("DXF", "SVG"):
            contexts, data = self.control(format)
            result = self.check(contexts, data)
            self.assertEqual(result["file_review"]["sha256"], contexts["job"]["drawing_sha256"])
            self.assertEqual(result["file_review"]["dimensions_mm"], {"x": "60", "y": "40"})
            self.assertEqual(contexts["process"]["settings"], {})
            self.assertEqual(contexts["material"]["properties"], {})

    def test_actual_dxf_geometry_failures_survive_valid_labels_and_new_test_hash(self):
        for change, blocker, finding in (
            (lambda b: b.replace(b" 70\n1\n", b" 70\n0\n"), "MISSING_CONTEXT", "open_contours"),
            (lambda b: b+tags(circle(17, 25, 3)), "MISSING_CONTEXT", "duplicate_circles"),
            (lambda b: b+tags([(0, "ARC"), (8, "0")]), "SOURCE_VERIFICATION_REQUIRED", "unsupported entity"),
            (lambda b: b.replace(b"65.0\n", b"125.0\n"), "MISSING_CONTEXT", "physical dimension conflicts"),
        ):
            contexts, data = self.control()
            data = fixture_mutation(data, change)
            contexts["job"]["drawing_sha256"] = hashlib.sha256(data).hexdigest()
            result = self.check(contexts, data, blocker)
            self.assertTrue(any(finding in item for item in result["findings"]))
            self.assertEqual(contexts["job"]["geometry_status"], "valid")
            self.assertFalse(any("drawing_sha256 identity" in item for item in result["findings"]))

    def test_actual_svg_geometry_scale_and_units_are_not_status_labels(self):
        for before, after, blocker, finding in (
            (b"</g>", b'<polyline points="1,1 2,2 3,2"/></g>', "MISSING_CONTEXT", "open_contours"),
            (b"</g>", b'<circle cx="17" cy="25" r="3"/></g>', "MISSING_CONTEXT", "duplicate_circles"),
            (b"</g>", b'<path d="M1 1C2 2 3 3 4 4Z"/></g>', "SOURCE_VERIFICATION_REQUIRED", "unsupported path"),
            (b"70 50", b"140 100", "MISSING_CONTEXT", "physical dimension conflicts"),
            (b"70mm", b"70in", "MISSING_CONTEXT", "unit declaration conflicts"),
        ):
            contexts, data = self.control("SVG")
            data = data.replace(before, after)
            contexts["job"]["drawing_sha256"] = hashlib.sha256(data).hexdigest()
            result = self.check(contexts, data, blocker)
            self.assertTrue(any(finding in item for item in result["findings"]))

    def test_dxf_unit_change_is_detected_even_if_extents_are_declared_to_match(self):
        contexts, data = self.control()
        changed = data.replace(b"$INSUNITS\n 70\n4\n", b"$INSUNITS\n 70\n1\n")
        self.assertNotEqual(changed, data)
        contexts["job"]["drawing_sha256"] = hashlib.sha256(changed).hexdigest()
        contexts["job"]["model_dimensions"] = {"x": 1524, "y": 1016}
        result = self.check(contexts, changed, "MISSING_CONTEXT")
        self.assertIn("file unit declaration conflicts with job drawing units", result["findings"])
        self.assertEqual(result["file_review"]["declared_unit"], "inch")

    def test_source_revision_identity_and_missing_bytes_fail_independently(self):
        for format in ("DXF", "SVG"):
            contexts, data = self.control(format)
            self.check(contexts, None, "MISSING_CONTEXT")
            for revision in (None, "", "B"):
                self.check(contexts, data, "MISSING_CONTEXT", revision)
            contexts["job"]["drawing_sha256"] = "0"*64
            self.assertEqual(self.check(contexts, data, "SOURCE_VERIFICATION_REQUIRED")["blockers"], ["SOURCE_VERIFICATION_REQUIRED"])

    def test_exact_machine_units_envelope_boundary_and_position(self):
        contexts, data = self.control()
        contexts["machine"]["capabilities"]["working_area"] = {"x": 65, "y": 45}
        self.check(contexts, data)
        contexts["machine"]["capabilities"]["working_area"]["x"] = 64.99999999999999
        self.check(contexts, data, "MACHINE_CONTEXT_REQUIRED")
        contexts["machine"]["lifecycle"]["units"]["length"] = "inch"
        contexts["machine"]["capabilities"]["working_area"] = {"x": 3, "y": 2}
        self.check(contexts, data)
        contexts["machine"]["capabilities"]["working_area"]["x"] = 2
        self.check(contexts, data, "MACHINE_CONTEXT_REQUIRED")
        contexts, data = self.control("SVG")
        data = data.replace(b'width="70mm"', b'width="700mm"').replace(b'70 50', b'700 50').replace(b'id="cut"', b'id="cut" transform="translate(300)"')
        contexts["job"]["drawing_sha256"] = hashlib.sha256(data).hexdigest()
        result = self.check(contexts, data, "MACHINE_CONTEXT_REQUIRED")
        self.assertEqual(result["file_review"]["dimensions_mm"]["x"], "60")
        self.assertTrue(any("placement exceeds" in item for item in result["findings"]))

    def test_context_chain_material_and_environment_fail_without_invention(self):
        changes = (("process", "machine_id", "other", "MISSING_CONTEXT"),
                   ("process", "material_id", "other", "MISSING_CONTEXT"),
                   ("job", "process_profile_id", None, "MISSING_CONTEXT"),
                   ("job", "material_id", "unknown", "MISSING_CONTEXT"),
                   ("job", "unsafe_material_status", "unsafe", "MISSING_CONTEXT"),
                   ("job", "ventilation_status", "unknown", "MISSING_CONTEXT"),
                   ("job", "path_intent", None, "MISSING_CONTEXT"),
                   ("job", "placement_frame", None, "MACHINE_CONTEXT_REQUIRED"),
                   ("process", "settings_status", "unknown", "SOURCE_VERIFICATION_REQUIRED"))
        for owner, key, value, blocker in changes:
            with self.subTest(field=f"{owner}.{key}"):
                contexts, data = self.control()
                contexts[owner][key] = value
                self.check(contexts, data, blocker)
                self.assertEqual(contexts["process"]["settings"], {})
        contexts, data = self.control()
        contexts["material"]["compatibility"]["machines"] = ["other"]
        self.check(contexts, data, "MACHINE_CONTEXT_REQUIRED")
        for key, value in (("unsafe_material_status", "unknown"), ("ventilation_status", "unknown")):
            contexts, data = self.control()
            contexts["material"]["environmental_requirements"][key] = value
            self.check(contexts, data, "MISSING_CONTEXT")

    def test_malformed_nested_context_and_numeric_fields_fail_closed(self):
        for owner in ("machine", "material", "process"):
            for value in (None, [], "unknown"):
                contexts, data = self.control()
                contexts[owner] = value
                self.check(contexts, data, "MISSING_CONTEXT" if owner != "machine" else "MACHINE_CONTEXT_REQUIRED")
        for value in (None, "60", True, -1, float("nan"), float("inf")):
            contexts, data = self.control()
            contexts["job"]["model_dimensions"]["x"] = value
            # NaN equality does not matter here: compare before/after JSON-safe output.
            result = preflight(**contexts, drawing_bytes=data, source_revision="A")
            self.assertIn("MISSING_CONTEXT", result["blockers"])
            json.dumps(result, allow_nan=False)
        contexts, data = self.control()
        contexts["job"]["format"] = {}
        self.check(contexts, data, "MISSING_CONTEXT")

    def test_cli_uses_requested_job_and_explicit_drawing_and_returns_blocked_exit(self):
        contexts, data = self.control()
        contexts["job"]["approval_status"] = "not_requested"
        with tempfile.TemporaryDirectory(prefix="laser-cli-") as directory:
            root = Path(directory)
            for name, context in contexts.items():
                (root / f"{name}.json").write_text(json.dumps(context), encoding="utf-8")
            # A non-default job path must not silently select adjacent job.json.
            alternate = copy.deepcopy(contexts["job"])
            alternate["revision"] = "B"
            (root / "requested.json").write_text(json.dumps(alternate), encoding="utf-8")
            (root / "job.json").unlink()  # Only the explicitly requested job exists.
            (root / "drawing.dxf").write_bytes(data)
            for module in (False, True):
                command = [sys.executable, "-m", "scripts.laser_preflight"] if module else [sys.executable, "scripts/laser_preflight.py"]
                output = subprocess.run(command + [str(root / "requested.json"), "--drawing", str(root / "drawing.dxf"), "--source-revision", "A"],
                                        cwd=FIXTURE.parents[2], capture_output=True, text=True, timeout=30)
                self.assertEqual(output.returncode, 1, output.stderr)
                result = json.loads(output.stdout)
                self.assertIn("source revision is missing or conflicts with job revision", result["findings"])
                self.assertFalse(result["execution_allowed"])


if __name__ == "__main__":
    unittest.main()
