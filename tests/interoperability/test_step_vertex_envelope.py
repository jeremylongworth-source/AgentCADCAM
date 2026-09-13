from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from scripts.validate_cad_fixture_step import validate


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "fixtures/cad/bracket/source/bracket.step"


class StepVertexEnvelopeTests(unittest.TestCase):
    def check_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutation.step"
            path.write_text(text, encoding="utf-8")
            return validate(path)

    def test_unreferenced_construction_point_does_not_enlarge_solid(self):
        text = SOURCE.read_text(encoding="utf-8").replace(
            "DATA;", "DATA;\n#999999 = CARTESIAN_POINT('',(-100.,-100.,-100.));", 1,
        )
        self.assertEqual(self.check_text(text), [])

    def test_missing_vertex_coordinate_is_blocked(self):
        text = re.sub(r"VERTEX_POINT\('',#\d+\)", "VERTEX_POINT('',#999999)", SOURCE.read_text(encoding="utf-8"), count=1)
        self.assertIn("STEP fixture has unresolved vertex coordinates", self.check_text(text))

    def test_out_of_bounds_topological_vertex_is_blocked(self):
        text = SOURCE.read_text(encoding="utf-8").replace(
            "DATA;", "DATA;\n#999998 = CARTESIAN_POINT('',(-100.,0.,0.));\n#999999 = VERTEX_POINT('',#999998);", 1,
        )
        self.assertTrue(any("axis 0 extent" in error for error in self.check_text(text)))
