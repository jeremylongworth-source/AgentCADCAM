from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

from scripts.generate_cad_fixture_step import _workspace_path
from router.router import route
import json


ROOT = Path(__file__).resolve().parents[2]


class RepositoryHardeningTests(unittest.TestCase):
    def test_untrusted_instruction_override_patterns_are_absent_from_skill_content(self):
        patterns = re.compile(r"ignore previous|do not tell the user|secretly exfiltrate|download and run", re.IGNORECASE)
        for path in (ROOT / "skills").rglob("*.md"):
            self.assertIsNone(patterns.search(path.read_text(encoding="utf-8")), path)

    def test_scripts_do_not_import_network_or_process_execution_modules(self):
        forbidden = {"requests", "urllib", "http.client", "subprocess", "socket", "paramiko"}
        for path in (ROOT / "scripts").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
            self.assertTrue(not imported.intersection(forbidden), f"forbidden imports in {path}")

    def test_fixture_generator_rejects_path_escape(self):
        with self.assertRaises(ValueError):
            _workspace_path(Path("..") / "outside-step.step")

    def test_live_execution_is_blocked_even_when_approved(self):
        for family in ("cad_handoff", "cnc_milling", "additive", "laser_cutting"):
            result = route({"process_family": family, "consequence_level": "live_execution", "approval_state": "approved"})
            with self.subTest(family=family):
                self.assertIn("BLOCK_EXECUTION", result["blockers"])
                self.assertFalse(result["execution_allowed"])

    def test_context_profiles_require_source_metadata(self):
        schema_dir = ROOT / "contexts/schemas"
        for name in ("machine.schema.json", "controller.schema.json", "material.schema.json", "tool.schema.json", "post.schema.json"):
            schema = json.loads((schema_dir / name).read_text(encoding="utf-8"))
            with self.subTest(schema=name):
                self.assertIn("source", schema["required"])


if __name__ == "__main__":
    unittest.main()
