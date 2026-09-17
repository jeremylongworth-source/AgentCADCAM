# Governance refusal evidence — 2026-09-17

This Phase 7 increment closes the reproduced matching-record bypass described
in [the readiness contract](../../architecture/governance-readiness.md). It is
declaration consistency evidence, not a qualified rights/export verdict.

## Acceptance map

| Required behavior | Evidence |
| --- | --- |
| Missing/unknown/disputed/expired source authorization blocks planning | `GovernanceDeclarationTests.test_every_missing_or_unresolved_ip_field_blocks_planning` |
| Export review cannot be waived by lowering consequence or supplying a current approval | Export status matrix plus `IntegratedGovernanceTests.test_current_records_cannot_override_denied_source_or_export_review` |
| Incomplete drafts remain representable, not manufacturing-ready | `test_missing_draft_context_is_allowed_only_below_planning`; unchanged permissive state schema |
| Confidential local review does not imply redistribution permission | `test_local_review_does_not_require_redistribution_or_public_confidentiality` |
| Nested source/job declarations cannot be silently overridden | `test_nested_declarations_cannot_disagree_with_root_state` |
| All four families invalidate matching record/package copies for adverse governance | Twenty cases, each through routing and handoff consumption, with no input mutation |
| Positive controls remain non-executable | `test_resolved_local_declarations_preserve_scoped_record_not_execution` |
| Rights changes invalidate dependent approval and verification | `test_governance_changes_invalidate_both_approval_and_verification_bindings` |
| Whitespace is not explicit jurisdiction | `test_blank_jurisdiction_cannot_satisfy_requested_review_or_keep_approval` |

Optional output-quality scoring cannot compensate for any of these blockers.
No private source material or actual manufacturing permissions are needed to
run these synthetic cases.

## Historical records and current replay

Earlier CAD/CNC/additive/laser and integration packets are immutable historical
observations. Their authored decisions, source bytes, context declarations,
hashes, verification records and fingerprints are not refreshed or promoted.
`tests/evaluation/governance_expectations.py` permits only these explicit deltas:

- CAD's complete governance declarations yield no change.
- CNC adds findings for missing confidentiality, restrictions and redistribution
  declarations. Its existing source blocker remains.
- Additive/laser add findings for unsupported ownership/licence/confidentiality
  labels, missing restrictions and `not_reviewed` export status. They also add
  `REGULATORY_REVIEW_REQUIRED` to current results and newly replayed handoffs.
- All other historical replay content must still compare exactly, including
  pre-existing process-gate diagnostic deltas.

The stored handoffs remain blocked. Reading an older packet does not exempt it
from today's consumer checks.

`approval-controls.json` is a **new** 24-case synthetic lifecycle snapshot,
produced by `python -m tests.evaluation.replay_integration_controls`. The four
test factories now explicitly supply complete test-only governance before
rebinding verification and approval. Their changed fingerprints do not revise
the [Phase 6 snapshot](../integration-runs/approval-controls.json). No actual
profile or job was given these synthetic permissions.

## Validation

Run using the repository Python environment:

```text
python -m unittest tests.safety.test_governance -v
python -m unittest discover -s tests -v
python scripts/validate_foundation.py
python scripts/validate_schema_instances.py
```

Executed with the repository virtual environment:

| Check | Observed result |
| --- | --- |
| `python -m unittest tests.safety.test_governance -v` | Eleven methods passed in 17.622 seconds |
| Targeted historical replay and integration checks | Twelve methods passed in 24.346 seconds |
| `python -m unittest discover -s tests` | 634 tests passed in 294.966 seconds |
| `python scripts/validate_foundation.py` | Passed: 58 required files, 14 context schemas, five skillsets |
| `python scripts/validate_schema_instances.py` | Passed: 15 schema definitions, 108 instances |
| `git diff --cached --check` | Passed |

The first full run exposed 41 historical replay comparison failures; all were
resolved through the explicit diagnostic deltas and separate synthetic snapshot
above, without rewriting historical review data. The final full run passed.
A direct comparison of both lifecycle snapshots confirmed all 24 outcomes and
findings unchanged; only synthetic-context fingerprints changed.

Phase 7 remains open for the complete curated safety matrix,
authoritative-source/freshness audit and public-alpha requirement review.
Phase 8 still needs real-input qualified practitioner evaluations.
