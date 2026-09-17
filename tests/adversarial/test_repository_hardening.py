from __future__ import annotations

import ast
import json
import re
import tempfile
import unittest
from pathlib import Path

from scripts.generate_cad_fixture_step import _workspace_path
from router.router import route


ROOT = Path(__file__).resolve().parents[2]
PORTABLE_DIRECTORIES = ("scripts", "router", "state")
FORBIDDEN_IMPORT_ROOTS = frozenset({
    "requests", "urllib", "http", "httpx", "aiohttp", "ftplib", "smtplib",
    "subprocess", "socket", "paramiko",
})


def forbidden_imports(source, filename="<test>"):
    """Explicit AST imports only; not a sandbox or transitive-code analysis."""
    imported = set()
    for node in ast.walk(ast.parse(source, filename=filename)):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            imported.add(node.module.split(".")[0])
    return imported & FORBIDDEN_IMPORT_ROOTS


def portable_python_files(root):
    return sorted(path for directory in PORTABLE_DIRECTORIES
                  for path in (root / directory).rglob("*.py"))


class RepositoryHardeningTests(unittest.TestCase):
    def test_untrusted_instruction_override_patterns_are_absent_from_skill_content(self):
        patterns = re.compile(r"ignore previous|do not tell the user|secretly exfiltrate|download and run", re.IGNORECASE)
        for path in (ROOT / "skills").rglob("*.md"):
            self.assertIsNone(patterns.search(path.read_text(encoding="utf-8")), path)

    def test_portable_code_has_no_selected_network_or_process_imports(self):
        paths = portable_python_files(ROOT)
        for directory in PORTABLE_DIRECTORIES:
            self.assertTrue(any(path.is_relative_to(ROOT / directory) for path in paths), directory)
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual(forbidden_imports(path.read_text(encoding="utf-8"), str(path)), set())

    def test_import_guard_detects_roots_aliases_and_nested_imports(self):
        for module in sorted(FORBIDDEN_IMPORT_ROOTS):
            for source in (f"import {module}", f"import {module}.client as alias",
                           f"from {module} import client as alias",
                           f"def deferred():\n    import {module}\n"):
                with self.subTest(source=source):
                    self.assertEqual(forbidden_imports(source), {module})
        self.assertEqual(forbidden_imports("from http.client import HTTPSConnection"), {"http"})
        self.assertEqual(forbidden_imports("import json, socket as transport"), {"socket"})

    def test_import_guard_ignores_inert_text_and_documents_dynamic_limit(self):
        source = '# import socket\ntext = "import subprocess"\nimport json\nfrom pathlib import Path\n'
        self.assertEqual(forbidden_imports(source), set())
        # These do not run. The lexical check must not be advertised as detecting them.
        self.assertEqual(forbidden_imports('__import__("socket")'), set())
        self.assertEqual(forbidden_imports('import importlib\nimportlib.import_module("socket")'), set())

    def test_portable_scan_includes_nested_modules_and_excludes_test_launchers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            selected = {f"{area}/nested/probe.py" for area in PORTABLE_DIRECTORIES}
            for name in selected | {"tests/native/probe.py", "scripts/notes.md"}:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("import subprocess\n", encoding="utf-8")
            paths = portable_python_files(root)
            self.assertEqual({path.relative_to(root).as_posix() for path in paths}, selected)
            for path in paths:
                self.assertEqual(forbidden_imports(path.read_text(encoding="utf-8")), {"subprocess"})

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
