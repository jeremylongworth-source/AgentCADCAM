"""Portable retained-evidence checks; importing this never launches native tools."""

import json
import math
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tests.evaluation.replay_cnc_reviews import CASES, ROOT
from tests.native import check_camotics_runtime as probe


class CamoticsEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((ROOT / "docs/evaluation/cnc-independent/camotics-1.2.0-windows.json").read_text(encoding="utf-8"))
        cls.cases = {run["case"]: run for run in cls.report["cases"]}

    def test_all_cases_match_retained_input_and_original_blocked_context(self):
        self.assertEqual(set(self.cases), set(CASES))
        self.assertEqual(len(self.report["cases"]), len(CASES))
        for case, result in self.cases.items():
            original = json.loads((ROOT / f"docs/evaluation/cnc-runs/2026-09-17-{case}/observed.json").read_text(encoding="utf-8"))
            self.assertEqual(result["nc_sha256"], probe.sha256(original["program"].encode("utf-8")))
            self.assertEqual(result["router_blockers"], original["route_result"]["blockers"])
            self.assertEqual(result["job_simulation_status"], "not_run")
            self.assertEqual(result["job_approval_status"], "not_requested")
            self.assertTrue(result["router_blockers"])
        self.assertFalse(self.report["execution_allowed"])
        self.assertFalse(self.report["job_approval_promoted"])
        self.assertTrue(self.report["review_required"])

    def test_runtime_project_and_actual_version_outputs_are_preserved(self):
        self.assertEqual(self.report["runtime"], json.loads(probe.PIN.read_text(encoding="utf-8")))
        self.assertEqual(self.report["project_sha256"], probe.sha256(probe.PROJECT.read_bytes()))
        self.assertEqual(self.report["project"], json.loads(probe.PROJECT.read_bytes()))
        self.assertFalse(self.report["project"]["workpiece"]["automatic"])
        self.assertEqual(set(self.report["project"]["tools"]), {"1"})
        for name, version in (("gcodetool", "1.2"), ("camsim", "0.0")):
            run = self.report["versions"][name]
            self.assertEqual(run["exit_code"], 0)
            self.assertEqual((run["stdout"] + run["stderr"]).strip(), version)

    def test_native_completion_is_not_negative_case_acceptance(self):
        for result in self.cases.values():
            self.assertEqual(result["interpreter"]["exit_code"], 0)
            self.assertEqual(result["simulator"]["exit_code"], 0)
            self.assertIsNone(result["surface_error"])
            mesh = result["surface"]
            self.assertGreater(mesh["triangles"], 0)
            self.assertEqual(mesh["bytes"], 84 + 50 * mesh["triangles"])
            self.assertGreater(mesh["absolute_signed_volume"], 0)
            self.assertIn("HUMAN_APPROVAL_REQUIRED", result["router_blockers"])
            self.assertIn("SIMULATION_REQUIRED", result["router_blockers"])

    def test_identity_comments_and_missing_wcs_are_not_native_rejections(self):
        baseline = self.cases["positive"]
        for case in ("wrong-post", "wrong-controller", "revision-mismatch", "missing-wcs"):
            self.assertEqual(self.cases[case]["interpreter"]["stdout"], baseline["interpreter"]["stdout"])
            self.assertEqual(self.cases[case]["surface"]["triangle_data_sha256"], baseline["surface"]["triangle_data_sha256"])
            self.assertNotEqual(self.cases[case]["nc_sha256"], baseline["nc_sha256"])

    def test_missing_tools_are_auto_created_not_verified(self):
        baseline = self.cases["positive"]["surface"]["triangle_data_sha256"]
        for case, number in (("unknown-tool", 9), ("incorrect-tool-number", 2)):
            result = self.cases[case]
            self.assertIn(f"Auto-creating missing tool {number}", result["simulator"]["stderr"])
            self.assertIn(f"M6 T{number}", result["interpreter"]["stdout"])
            self.assertNotEqual(result["surface"]["triangle_data_sha256"], baseline)
            self.assertIn("MISSING_CONTEXT", result["router_blockers"])

    def test_unit_conversion_and_limit_excursion_survive_native_processing(self):
        units = self.cases["wrong-units"]["interpreter"]["stdout"]
        for token in ("X1524", "Y1016", "Z635", "F2540", "F5080"):
            self.assertIn(token, units)
        self.assertIn("X100", self.cases["machine-limit-conflict"]["interpreter"]["stdout"])
        self.assertNotEqual(self.cases["wrong-units"]["surface"]["triangle_data_sha256"],
                            self.cases["positive"]["surface"]["triangle_data_sha256"])

    def test_exported_triangle_count_is_not_replaced_by_console_reduction_count(self):
        baseline = self.cases["positive"]
        self.assertIn("Triangles: 146 Reduction:", baseline["simulator"]["stderr"])
        self.assertEqual(baseline["surface"]["triangles"], 9432)


class CamoticsProbeUtilityTests(unittest.TestCase):
    @staticmethod
    def tetrahedron():
        a, b, c, d = (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)
        return b"test".ljust(80, b" ") + struct.pack("<I", 4) + b"".join(
            struct.pack("<12fH", 0, 0, 0, *p, *q, *r, 0) for p, q, r in ((a, c, b), (a, b, d), (a, d, c), (b, c, d)))

    def test_binary_mesh_measurements_and_payload_identity(self):
        data = self.tetrahedron()
        result = probe.mesh_summary(data)
        self.assertEqual(result["triangles"], 4)
        self.assertEqual(result["bounds"], {"min": [0, 0, 0], "max": [1, 1, 1]})
        self.assertAlmostEqual(result["absolute_signed_volume"], 1 / 6)
        other = probe.mesh_summary(b"new header".ljust(80, b" ") + data[80:])
        self.assertNotEqual(result["sha256"], other["sha256"])
        self.assertEqual(result["triangle_data_sha256"], other["triangle_data_sha256"])

    def test_empty_truncated_and_nonfinite_meshes_are_rejected(self):
        data = self.tetrahedron()
        nonfinite = bytearray(data)
        struct.pack_into("<f", nonfinite, 96, math.inf)
        for invalid in (b"", data[:83], data[:-1], data + b"x", b" " * 80 + struct.pack("<I", 0), nonfinite):
            with self.subTest(length=len(invalid)):
                with self.assertRaises(ValueError):
                    probe.mesh_summary(invalid)

    def test_missing_or_changed_pinned_runtime_blocks_before_any_launch(self):
        with tempfile.TemporaryDirectory(prefix="camotics-pin-test-") as temporary:
            root = Path(temporary)
            pin = root / "pin.json"
            pin.write_text(json.dumps({"files": {"gcodetool.exe": probe.sha256(b"fixture")}}), encoding="utf-8")
            with patch.object(probe, "PIN", pin), patch.object(probe.subprocess, "run") as launch:
                with self.assertRaisesRegex(ValueError, "missing or changed"):
                    probe.verify_runtime(root)
                (root / "gcodetool.exe").write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError, "missing or changed"):
                    probe.verify_runtime(root)
                (root / "gcodetool.exe").write_bytes(b"fixture")
                self.assertEqual(probe.verify_runtime(root)["files"]["gcodetool.exe"], probe.sha256(b"fixture"))
                launch.assert_not_called()

    def test_process_errors_and_timeout_are_not_converted_to_success(self):
        failed = subprocess.CompletedProcess([], 3, b"partial\r\n", b"failed\r\n")
        with patch.object(probe.subprocess, "run", return_value=failed) as launch:
            result = probe.invoke(Path("gcodetool.exe"), ["--metric"], Path("isolated"), b"test")
            self.assertEqual(result["exit_code"], 3)
            self.assertEqual(result["stderr"], "failed\n")
            self.assertEqual(launch.call_args.kwargs["timeout"], 45)
            self.assertNotIn("shell", launch.call_args.kwargs)
        with patch.object(probe.subprocess, "run", side_effect=subprocess.TimeoutExpired("fixed-tool", 45)):
            with self.assertRaises(subprocess.TimeoutExpired):
                probe.invoke(Path("gcodetool.exe"), [], Path("isolated"))


if __name__ == "__main__":
    unittest.main()
