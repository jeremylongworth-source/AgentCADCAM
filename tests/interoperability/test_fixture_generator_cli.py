"""Test export orchestration without requiring the optional native CAD runtime."""

from __future__ import annotations

import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from scripts import generate_cad_fixture_step as generator


class FixtureGeneratorCLITests(unittest.TestCase):
    def test_cli_exports_both_formats_and_normalizes_step_timestamp(self):
        exports = []
        def export(part, path, kind, **options):
            exports.append((part, kind, options))
            Path(path).write_text("Synthetic export 2026-09-12T12:34:56  \n", encoding="utf-8")
        exporters = SimpleNamespace(export=export, ExportTypes=SimpleNamespace(STEP="STEP", STL="STL"))
        fake_cadquery = SimpleNamespace(exporters=exporters)
        part = object()
        # Output guard requires paths inside the repository; this context removes only its own temp directory.
        with tempfile.TemporaryDirectory(prefix="generator-test-", dir=generator.ROOT) as directory:
            step = Path(directory) / "step/model.step"
            stl = Path(directory) / "mesh/model.stl"
            with patch.dict(sys.modules, {"cadquery": fake_cadquery}), \
                 patch.object(generator, "build_bracket", return_value=part), \
                 patch.object(sys, "argv", ["generate", str(step), "--stl-output", str(stl)]), \
                 redirect_stdout(StringIO()):
                self.assertEqual(generator.main(), 0)
            self.assertEqual(step.read_text(encoding="utf-8"), "Synthetic export 1970-01-01T00:00:00\n")
            self.assertTrue(stl.is_file())
        self.assertEqual([item[1] for item in exports], ["STEP", "STL"])
        self.assertTrue(all(item[0] is part for item in exports))
        self.assertEqual(exports[1][2], {"tolerance": 0.01, "angularTolerance": 0.1})

    def test_cli_rejects_output_escape_before_loading_cadquery(self):
        builder = Mock()
        with patch.object(generator, "build_bracket", builder), \
             patch.dict(sys.modules, {"cadquery": None}), \
             patch.object(sys, "argv", ["generate", str(generator.ROOT.parent / "outside.step")]), \
             patch("sys.stderr", StringIO()), self.assertRaises(SystemExit) as caught:
            generator.main()
        self.assertEqual(caught.exception.code, 2)
        builder.assert_not_called()


if __name__ == "__main__":
    unittest.main()
