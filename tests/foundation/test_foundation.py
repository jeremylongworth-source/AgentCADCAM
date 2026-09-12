"""Dependency-free smoke tests for the Phase 1 foundation contracts."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class FoundationContractTests(unittest.TestCase):
    def test_required_context_schemas_are_valid_json(self):
        schema_dir = ROOT / "contexts" / "schemas"
        expected = {
            "job.schema.json",
            "machine.schema.json",
            "controller.schema.json",
            "material.schema.json",
            "tool.schema.json",
            "post.schema.json",
            "setup.schema.json",
            "approval.schema.json",
            "handoff.schema.json",
        }
        self.assertTrue(expected.issubset({p.name for p in schema_dir.glob("*.json")}))
        for path in schema_dir.glob("*.json"):
            with self.subTest(path=path):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(data["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(data["type"], "object")

    def test_job_example_has_safe_default_approval(self):
        example = json.loads((ROOT / "contexts/examples/job.example.json").read_text(encoding="utf-8"))
        self.assertEqual(example["approval_status"], "not_requested")
        self.assertEqual(example["process_family"], "cad_handoff")

    def test_handoff_example_requires_review_and_reports_blocker(self):
        example = json.loads((ROOT / "contexts/examples/handoff.example.json").read_text(encoding="utf-8"))
        self.assertTrue(example["review_required"])
        self.assertIn("MISSING_CONTEXT", example["blockers"])

    def test_execution_boundary_contains_hard_blocks(self):
        text = (ROOT / "docs/architecture/execution-boundary.md").read_text(encoding="utf-8").lower()
        for term in ("block_execution", "review_required", "not self-authorizing", "interlocks"):
            self.assertIn(term.lower(), text)

    def test_invalidation_rules_cover_all_consequential_inputs(self):
        text = (ROOT / "state/invalidation-rules.yaml").read_text(encoding="utf-8")
        for field in ("revision", "units", "machine_profile", "controller_profile", "setup", "tool_library", "postprocessor", "material"):
            self.assertIn(f"field: {field}", text)

    def test_prohibited_capability_contract_is_explicit(self):
        text = (ROOT / "docs/standards/prohibited-capability-contract.md").read_text(encoding="utf-8").lower()
        for term in ("block_execution", "cycle start", "interlock", "spindle activation", "beam activation"):
            self.assertIn(term, text)


if __name__ == "__main__":
    unittest.main()
