"""Synthetic source assessments; never copy these declarations into real jobs."""

from router.source_evidence import source_fingerprint


def declare_test_source_review(source, role):
    source["review"] = {
        "status": "reviewed", "authority": "primary_tool_documentation",
        "reviewer": "synthetic-test-reviewer", "reviewed_at": "2026-09-17",
        # Long-lived, non-operational control, not a real freshness recommendation.
        "valid_through": "2099-12-31", "applies_to": [role],
        "evidence": ["test-only:source-declaration-consistency-not-external-verification"],
        "source_sha256": source_fingerprint(source),
    }
    return source
