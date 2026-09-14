"""The shared source record must carry reviewable scope and claims."""

import copy
import json
import unittest
from pathlib import Path

from scripts.validate_schema_instances import load_catalog, validator_for


ROOT = Path(__file__).resolve().parents[2]


class SourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        handoff = validator_for("handoff.schema.json", cls.catalog)
        cls.validator = handoff.evolve(schema=handoff.schema["$defs"]["source"])

    def setUp(self):
        self.source = {
            "title": "Synthetic test evidence", "publisher": "Test authors",
            "locator": "fixture:test", "published_at": None,
            "accessed_at": "2026-09-13", "scope": "Offline synthetic tests only",
            "claims": ["The test fixture declares a synthetic machine identity."],
        }

    def test_complete_source_allows_explicit_unknown_publication(self):
        self.assertTrue(self.validator.is_valid(self.source))
        self.source["published_at"] = "Revision A, 2026-09-12"
        self.assertTrue(self.validator.is_valid(self.source))

    def test_required_evidence_fields_cannot_be_omitted(self):
        for field in self.source:
            with self.subTest(field=field):
                value = dict(self.source)
                del value[field]
                self.assertFalse(self.validator.is_valid(value))

    def test_required_text_rejects_blank_null_and_wrong_types(self):
        for field in ("title", "publisher", "locator", "scope"):
            for value in ("", " \t\n", None, [], 1):
                with self.subTest(field=field, value=value):
                    self.assertFalse(self.validator.is_valid(dict(self.source, **{field: value})))

    def test_claims_are_nonempty_unique_text_statements(self):
        for claims in (None, [], "a claim", [None], [1], [""], [" \t"], ["same", "same"]):
            with self.subTest(claims=claims):
                self.assertFalse(self.validator.is_valid(dict(self.source, claims=claims)))

    def test_access_date_requires_real_iso_calendar_date(self):
        for value in ("not-a-date", "2026-02-30", "2026-9-13", "2026-09-13T12:00:00Z", " ", None):
            with self.subTest(value=value):
                self.assertFalse(self.validator.is_valid(dict(self.source, accessed_at=value)))

    def test_publication_is_null_or_nonblank_text(self):
        for value in ("", " ", 1, [], {}):
            with self.subTest(value=value):
                self.assertFalse(self.validator.is_valid(dict(self.source, published_at=value)))

    def test_each_profile_uses_the_same_strict_source_contract(self):
        for name in ("machine", "controller", "material", "tool", "post"):
            profile = json.loads((ROOT / f"fixtures/cnc/mill-bracket/contexts/{name}.json").read_text(encoding="utf-8"))
            profile["source"] = copy.deepcopy(self.source)
            validator = validator_for(f"{name}.schema.json", self.catalog)
            with self.subTest(profile=name):
                self.assertTrue(validator.is_valid(profile))
                del profile["source"]["scope"]
                self.assertFalse(validator.is_valid(profile))

    def test_source_schema_does_not_authenticate_claims(self):
        # Metadata validity is intentionally not a source truth or safety score.
        self.source["claims"] = ["Unverified reviewer-supplied statement"]
        self.assertTrue(self.validator.is_valid(self.source))


if __name__ == "__main__":
    unittest.main()
