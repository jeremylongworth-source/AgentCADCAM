from __future__ import annotations

import unittest
from pathlib import Path

from scripts.validate_pilot_packet import validate


ROOT = Path(__file__).resolve().parents[2]


class PilotPacketTests(unittest.TestCase):
    def test_template_has_required_structure(self):
        root = ROOT / "docs/evaluation/pilot-packet-template"
        self.assertEqual(validate(root), [])

    def test_template_uses_roadmap_final_verdict_directory(self):
        root = ROOT / "docs/evaluation/pilot-packet-template"
        self.assertTrue((root / "final-verdict").is_dir())
        self.assertTrue((root / "final-verdict/final-verdict.yaml").is_file())
        self.assertFalse((root / "final-verdict.yaml").exists())

    def test_protocol_does_not_claim_pilot_gate(self):
        protocol = (ROOT / "docs/evaluation/pilot-protocol.md").read_text(encoding="utf-8")
        self.assertIn("CADCAM_09_PILOT_VALIDATED", protocol)
        self.assertIn("cannot satisfy the gate alone", protocol)


if __name__ == "__main__":
    unittest.main()
