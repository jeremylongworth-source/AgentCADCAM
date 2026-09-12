from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class FormatRegistryTests(unittest.TestCase):
    def test_registry_covers_initial_exchange_formats(self):
        registry = (ROOT / "docs/formats/format-registry.md").read_text(encoding="utf-8")
        for format_name in ("STEP AP242", "IGES", "DXF", "SVG", "STL", "3MF", "NC/G-code", "STEP-NC"):
            with self.subTest(format_name=format_name):
                self.assertIn(format_name, registry)

    def test_registry_distinguishes_parseability_from_approval(self):
        registry = (ROOT / "docs/formats/format-registry.md").read_text(encoding="utf-8")
        self.assertIn("Parseability is not semantic fidelity", registry)
        self.assertIn("not manufacturing approval", registry)


if __name__ == "__main__":
    unittest.main()
