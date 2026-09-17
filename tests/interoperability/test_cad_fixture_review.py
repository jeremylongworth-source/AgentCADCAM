"""File mutations must reach the synthetic CAD fixture's review result."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import cad_handoff_checks


ROOT = Path(__file__).resolve().parents[2]


class CadFixtureReviewTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="cad-review-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "bracket"
        shutil.copytree(ROOT / "fixtures/cad/bracket", self.root)

    def replace(self, path, before, after):
        target = self.root / path
        text = target.read_text(encoding="utf-8")
        self.assertIn(before, text)
        target.write_text(text.replace(before, after), encoding="utf-8")

    def cli(self, module=False):
        command = [sys.executable]
        command += ["-m", "scripts.cad_handoff_checks"] if module else ["scripts/cad_handoff_checks.py"]
        return subprocess.run(command + [str(self.root / "fixture.yaml")], cwd=ROOT,
                              capture_output=True, text=True, timeout=30)

    def test_cli_blocks_drawing_revision_change_with_unchanged_manifest(self):
        self.replace("source/bracket.svg", "REV A", "REV B")
        for module in (False, True):
            with self.subTest(module=module):
                completed = self.cli(module)
                result = json.loads(completed.stdout)
                self.assertEqual(result["status"], "blocked")
                self.assertEqual(completed.returncode, 1)
                self.assertIn("MISSING_CONTEXT", result["blockers"])

    def test_positive_reports_bounded_file_checks_without_approval(self):
        completed = self.cli()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "review_required")
        self.assertEqual([check["status"] for check in result["file_checks"]], ["passed"] * 3)
        self.assertTrue(result["review_required"])
        self.assertFalse(result["execution_allowed"])
        self.assertFalse(result["geometry_equivalence_verified"])
        recorded = json.loads((ROOT / "fixtures/cad/bracket/expected/file-review.json").read_text(encoding="utf-8"))
        self.assertEqual(result, recorded)

    def test_actual_source_and_drawing_mutations_block(self):
        for path, before, after in (
            ("source/bracket.svg", "UNITS: mm", "UNITS: unknown"),
            ("source/bracket.svg", "60 mm wide", "61 mm wide"),
            ("source/bracket.scad", "plate_width = 60;", "plate_width = 61;"),
            ("source/bracket.scad", "plate_width = 60;", "plate_width = 1e+;"),
        ):
            with self.subTest(path=path, mutation=after):
                target = self.root / path
                original = target.read_bytes()
                self.replace(path, before, after)
                result = cad_handoff_checks.review_fixture(self.root)
                self.assertEqual(result["status"], "blocked")
                self.assertEqual(result["file_checks"][0]["status"], "failed")
                target.write_bytes(original)

    def test_actual_exchange_file_damage_blocks(self):
        for path, content, index in (("source/bracket.step", b"not a STEP file", 1),
                                     ("source/bracket.stl", b"solid empty\nendsolid empty\n", 2),
                                     ("source/bracket.stl", b"\xff\xfe", 2)):
            with self.subTest(path=path, content=content):
                target = self.root / path
                original = target.read_bytes()
                target.write_bytes(content)
                result = cad_handoff_checks.review_fixture(self.root)
                self.assertEqual(result["status"], "blocked")
                self.assertEqual(result["file_checks"][index]["status"], "failed")
                target.write_bytes(original)

    def test_missing_file_returns_blocked_report(self):
        (self.root / "source/bracket.svg").unlink()
        result = cad_handoff_checks.review_fixture(self.root)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("MISSING_CONTEXT", result["blockers"])

    def test_malformed_or_unsupported_manifest_returns_blocked_report(self):
        for content in ("[]", "fixture_id: unrelated", "artifacts: [", "null"):
            with self.subTest(content=content):
                (self.root / "fixture.yaml").write_text(content, encoding="utf-8")
                result = cad_handoff_checks.review_fixture(self.root)
                self.assertEqual(result["status"], "blocked")
                self.assertEqual(result["file_checks"], [])

    def test_malformed_revision_metadata_returns_blocked_report(self):
        for content in ("not JSON", "[]", '{"revision": null}'):
            with self.subTest(content=content):
                (self.root / "metadata/revision.json").write_text(content, encoding="utf-8")
                self.assertEqual(cad_handoff_checks.review_fixture(self.root)["status"], "blocked")

    def test_manifest_cannot_hide_missing_inventory_or_use_escaped_paths(self):
        import yaml

        path = self.root / "fixture.yaml"
        original = yaml.safe_load(path.read_text(encoding="utf-8"))
        for replacement in ([], [{"path": "../outside.step"}], [None]):
            with self.subTest(artifacts=replacement):
                path.write_text(yaml.safe_dump(dict(original, artifacts=replacement)), encoding="utf-8")
                self.assertEqual(cad_handoff_checks.review_fixture(self.root)["status"], "blocked")
        result = cad_handoff_checks.review_fixture(self.root, "../fixture.yaml")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("inside the supplied bundle", result["findings"][0])

    def test_metadata_design_authority_conflict_blocks(self):
        self.replace("metadata/revision.json", '"source/bracket.scad"', '"source/bracket.stl"')
        result = cad_handoff_checks.review_fixture(self.root)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("SOURCE_VERIFICATION_REQUIRED", result["blockers"])


if __name__ == "__main__":
    unittest.main()
