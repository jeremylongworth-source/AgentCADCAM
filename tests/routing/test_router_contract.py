from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RouterContractTests(unittest.TestCase):
    def test_contract_mentions_all_initial_process_families(self):
        contract = (ROOT / "router/router-contract.md").read_text(encoding="utf-8")
        for family in ("cad_handoff", "cnc_milling", "additive", "laser_cutting", "unknown"):
            self.assertIn(family, contract)

    def test_live_execution_is_hard_blocked(self):
        contract = (ROOT / "router/router-contract.md").read_text(encoding="utf-8")
        self.assertIn("BLOCK_EXECUTION", contract)
        self.assertIn("Live-control intent", contract)


if __name__ == "__main__":
    unittest.main()
