"""Portable evidence/probe regressions; these never require or launch PrusaSlicer."""

from fractions import Fraction
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from tests.native import check_prusaslicer_runtime as probe
from scripts.three_mf_review import RELS, TYPES


class PrusaSlicerEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((probe.ROOT / "docs/evaluation/additive-independent/prusaslicer-2.9.6-windows.json").read_text(encoding="utf-8"))
        cls.cases = {case["case"]: case for case in cls.report["cases"]}

    def test_retained_inputs_replay_current_blocked_review_without_native_runtime(self):
        self.assertEqual(set(self.cases), set(probe.CASES))
        self.assertEqual(len(self.report["cases"]), len(probe.CASES))
        for case, data in probe.fixture_cases().items():
            result = self.cases[case]
            self.assertEqual(result["input_sha256"], probe.sha256(data))
            self.assertEqual(result["original_review"], probe.input_review(case, data))
            self.assertEqual(result["original_review"]["job_approval_status"], "not_requested")
            self.assertIn("HUMAN_APPROVAL_REQUIRED", result["original_review"]["blockers"])
            self.assertTrue(result["input_preserved"])
        self.assertFalse(self.report["execution_allowed"])
        self.assertFalse(self.report["job_approval_promoted"])
        self.assertTrue(self.report["review_required"])

    def test_retained_runtime_and_input_pin_match(self):
        pin = json.loads(probe.PIN.read_text(encoding="utf-8"))
        self.assertEqual(self.report["runtime"], pin)
        self.assertEqual({name: probe.sha256(data) for name, data in probe.fixture_cases().items()}, pin["input_sha256"])
        self.assertEqual(pin["runtime_identity"]["file_count"], 1119)
        self.assertIn("prusa-slicer-console.exe", pin["runtime_identity"]["binaries"])
        self.assertIn("PrusaSlicer-2.9.6", self.report["help"]["stdout"])
        self.assertEqual(self.report["help"]["exit_code"], 0)

    def test_geometry_exports_have_observed_success_but_no_approval(self):
        for case in self.cases.values():
            self.assertEqual(case["process"]["exit_code"], 0)
            self.assertFalse(case["process"]["diagnostics_truncated"])
            exported = case["stl_export"]
            self.assertTrue(exported["present"])
            self.assertTrue(exported["complete"])
            self.assertEqual(exported["bytes"], 84 + 50 * exported["review"]["triangles"])
            self.assertFalse(exported["review"]["execution_allowed"])
            self.assertTrue(exported["review"]["review_required"])
            self.assertNotEqual(exported["review"]["sha256"], case["input_sha256"])

    def test_open_meshes_are_reported_not_silently_repaired_or_approved(self):
        for name, triangles in (("bracket-open-stl", 2051), ("tetra-open-3mf", 3)):
            case = self.cases[name]
            self.assertIn("manifold = no\nopen_edges = 3", case["process"]["stdout"])
            self.assertIn("MISSING_CONTEXT", case["original_review"]["blockers"])
            mesh = case["stl_export"]["review"]
            self.assertEqual(mesh["triangles"], triangles)
            self.assertEqual(mesh["topology"]["boundary_edges"], 3)
            self.assertEqual(mesh["topology"]["nonmanifold_vertices"], 3)
            self.assertIn("MISSING_CONTEXT", mesh["blockers"])

    def test_bracket_extents_and_facet_count_agree_with_independent_info(self):
        case = self.cases["bracket-stl"]
        self.assertIn("number_of_facets = 2052\nmanifold = yes", case["process"]["stdout"])
        for axis, size in zip("xyz", (60, 40, 30)):
            self.assertIn(f"size_{axis} = {size:.6f}", case["process"]["stdout"])
            self.assertEqual(case["stl_export"]["review"]["dimensions_exact"][axis], str(size))

    def test_inch_conversion_preserves_observed_float32_precision_loss(self):
        case = self.cases["tetra-inch-3mf"]
        self.assertEqual(case["original_review"]["file_review"]["unit_scale_mm"], "127/5")
        self.assertIn("size_x = 25.400000", case["process"]["stdout"])
        exported = Fraction(case["stl_export"]["review"]["dimensions_exact"]["x"])
        self.assertEqual(exported, Fraction(struct.unpack('<f', struct.pack('<f', 25.4))[0]))
        self.assertNotEqual(exported, Fraction(127, 5))

    def test_centered_info_bounds_do_not_erase_translated_build_placement(self):
        case = self.cases["tetra-translated-3mf"]
        self.assertIn("min_x = -0.500000", case["process"]["stdout"])
        self.assertIn("max_x = 0.500000", case["process"]["stdout"])
        self.assertEqual(case["stl_export"]["review"]["bounds"]["min"], [200, 0, 0])
        self.assertEqual(case["stl_export"]["review"]["bounds"]["max"], [201, 1, 1])
        self.assertIn("MACHINE_CONTEXT_REQUIRED", case["original_review"]["blockers"])

    def test_native_acceptance_does_not_override_unsupported_required_extension(self):
        case = self.cases["tetra-required-extension-3mf"]
        self.assertIn("SOURCE_VERIFICATION_REQUIRED", case["original_review"]["blockers"])
        self.assertEqual(case["stl_export"]["review"]["sha256"],
                         self.cases["tetra-3mf"]["stl_export"]["review"]["sha256"])
        self.assertEqual(case["process"]["stderr"], "")

    def test_native_3mf_envelope_gap_is_retained_not_waived(self):
        case = self.cases["bracket-stl"]
        self.assertEqual(case["package_process"]["exit_code"], 0)
        exported = case["package_export"]
        self.assertTrue(exported["present"])
        self.assertIn("MISSING_CONTEXT", exported["review"]["blockers"])
        parts = {part["name"] for part in exported["parts"]}
        rels = ET.fromstring(exported["package_xml"]["_rels/.rels"])
        targets = {node.get("Target").lstrip("/") for node in rels.findall(f"{{{RELS}}}Relationship")}
        self.assertIn("Metadata/thumbnail.png", targets - parts)
        types = ET.fromstring(exported["package_xml"]["[Content_Types].xml"])
        defaults = {node.get("Extension") for node in types.findall(f"{{{TYPES}}}Default")}
        self.assertNotIn("config", defaults)
        self.assertNotIn("xml", defaults)
        self.assertIn("Metadata/Slic3r_PE_model.config", parts)
        self.assertIn("Metadata/Prusa_Slicer_wipe_tower_information.xml", parts)

    def test_recorded_commands_are_only_isolated_geometry_actions(self):
        processes = [self.report["help"], self.cases["bracket-stl"]["package_process"]]
        processes += [case["process"] for case in self.cases.values()]
        for process in processes:
            args = process["arguments"]
            self.assertIn("--datadir", args)
            self.assertIn("disable", args)
            for prohibited in ("--slice", "--export-gcode", "--load", "--single-instance", "--post-process", "--delete-after-load"):
                self.assertNotIn(prohibited, args)
        raw = json.dumps(self.report)
        self.assertNotIn("C:\\\\Users", raw)
        self.assertNotIn("D:\\\\AgentCADCAM", raw)


class PrusaSlicerProbeUtilityTests(unittest.TestCase):
    def test_runtime_tree_identity_detects_resources_additions_and_changes(self):
        with tempfile.TemporaryDirectory(prefix="prusa-pin-test-") as temporary:
            root = Path(temporary)
            runtime = root / "runtime"
            runtime.mkdir()
            (runtime / "tool.exe").write_bytes(b"test binary")
            (runtime / "profile.ini").write_bytes(b"inert profile")
            pin = root / "pin.json"
            identity = probe.runtime_identity(runtime)
            pin.write_text(json.dumps({"runtime_identity": identity}), encoding="utf-8")
            with patch.object(probe, "PIN", pin), patch.object(probe.subprocess, "run") as launch:
                self.assertEqual(probe.verify_runtime(runtime)["runtime_identity"], identity)
                (runtime / "profile.ini").write_bytes(b"changed")
                with self.assertRaises(ValueError):
                    probe.verify_runtime(runtime)
                (runtime / "profile.ini").write_bytes(b"inert profile")
                (runtime / "extra.txt").write_bytes(b"extra")
                with self.assertRaises(ValueError):
                    probe.verify_runtime(runtime)
                with self.assertRaises(ValueError):
                    probe.verify_runtime(root / "absent")
                launch.assert_not_called()

    def test_parent_environment_credentials_and_profiles_are_not_inherited(self):
        with patch.dict(os.environ, {"SECRET_TOKEN": "do-not-inherit", "APPDATA": "personal-profile"}):
            env = probe.isolated_environment(Path("private"), Path("runtime"))
        self.assertNotIn("SECRET_TOKEN", env)
        self.assertEqual(env["APPDATA"], str(Path("private/roaming")))
        self.assertEqual(env["USERPROFILE"], str(Path("private/profile")))
        self.assertNotIn("personal-profile", env.values())

    def test_action_and_filename_allowlist_prevents_arbitrary_commands(self):
        with patch.object(probe.subprocess, "run") as launch:
            for action in ("slice", "export-gcode", "load", "--help", "upload"):
                with self.assertRaises(ValueError):
                    probe.invoke(Path("runtime"), action, Path("unused"), "input.stl")
            for filename in ("../input.stl", "--slice", "private.3mf", None):
                with self.assertRaises(ValueError):
                    probe.invoke(Path("runtime"), "stl", Path("unused"), filename)
            launch.assert_not_called()

    def test_process_failures_and_timeout_are_preserved_without_shell(self):
        with tempfile.TemporaryDirectory(prefix="prusa-process-test-") as temporary:
            root = Path(temporary)
            failed = subprocess.CompletedProcess([], 3, b"partial\r\n", str(root).encode() + b" failed\r\n")
            with patch.object(probe.subprocess, "run", return_value=failed) as launch:
                result = probe.invoke(Path("runtime"), "stl", root, "input.stl")
                self.assertEqual(result["exit_code"], 3)
                self.assertEqual(result["stderr"], "<temporary> failed\n")
                self.assertEqual(launch.call_args.kwargs["timeout"], 45)
                self.assertNotIn("shell", launch.call_args.kwargs)
                self.assertEqual(launch.call_args.kwargs["env"]["APPDATA"], str(root / "roaming"))
            with patch.object(probe.subprocess, "run", side_effect=subprocess.TimeoutExpired("fixed-tool", 45)):
                with self.assertRaises(subprocess.TimeoutExpired):
                    probe.invoke(Path("runtime"), "help", root)

    def test_missing_damaged_and_oversized_exports_are_not_successful_geometry(self):
        with tempfile.TemporaryDirectory(prefix="prusa-export-test-") as temporary:
            path = Path(temporary) / "output.3mf"
            self.assertFalse(probe.read_export(path, probe.inspect_3mf)["present"])
            path.write_bytes(b"malformed package")
            report = probe.read_export(path, probe.inspect_3mf)
            self.assertTrue(report["review"]["blockers"])
            self.assertIn("package_envelope_error", report)
            with patch.object(probe, "MAX_OUTPUT", 4), patch("scripts.three_mf_review.MAX_BYTES", 4):
                result = probe.read_export(path, probe.inspect_3mf)
                self.assertFalse(result["complete"])
                self.assertIsNone(result["review"]["sha256"])


if __name__ == "__main__":
    unittest.main()
