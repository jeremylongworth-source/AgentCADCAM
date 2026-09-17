# Source assessment controls — 2026-09-17

This is Phase 7 evidence for the [source-review readiness contract](../../architecture/source-review-readiness.md),
not a source-authentication, engineering, regulatory or practitioner verdict.

## Acceptance and evidence

| Requirement | Executable evidence in `tests/safety/test_source_evidence.py` |
| --- | --- |
| Missing assessment remains a draft, not readiness evidence | `test_absent_assessment_is_persistable_but_not_ready` |
| Required review fields and dates fail closed | `test_missing_assessment_fields_and_bad_dates_fail_closed` |
| Future access/review, reversed dates and expired records block | `test_future_access_review_and_reversed_chronology_block`; `test_current_source_and_inclusive_expiry_boundary_pass_only_consistency` |
| Unknown/community authority, stale/conflicted status and wrong context role block | `test_community_unknown_unresolved_conflicted_stale_and_wrong_scope_block` |
| Changed source metadata cannot retain its old assessment | `test_source_metadata_changes_require_a_new_source_review_not_just_job_approval` |
| No fetching or disclosure through diagnostics | `test_diagnostics_do_not_echo_source_contents_or_fetch_evidence` |
| Every supported evidence owner needs its own assessment | Nine isolated cases in `test_all_context_roles_require_their_own_source_review` |
| Current job approval cannot waive source failures | Seven adverse assessments across four families in `test_current_approval_cannot_waive_adverse_source_assessment_across_families` |
| Separate source renewal is required | `test_new_job_record_does_not_renew_changed_source_claims` |

The four-family controls use current synthetic profile, process, verification
and approval records so stale job identity cannot be the only reason they fail.
They assert unchanged inputs, retained reviewed fingerprints, invalidated
approval/handoff copies and non-execution. Positive controls test only record
consistency; they supply no actual manufacturing approval.

## Historical integrity

Existing source metadata remains valid for draft persistence. No fixture source
is relabelled as practitioner-verified, and earlier authored reviews are not
rewritten. Unverified historical profiles already block; invalid/incomplete
process inputs retain their previous blockers. The current historical replay
tests must continue to match exactly with their previously documented diagnostic
deltas; no new source-review findings are backfilled into those packets.

`approval-controls.json` records the new 24-case synthetic lifecycle run from
`python -m tests.evaluation.replay_integration_controls`. Test-only factories now
supply source assessments before binding job verification/approval. The earlier
[governance snapshot](../governance-runs/approval-controls.json) remains unchanged.
The new source assessments intentionally change synthetic context fingerprints;
the lifecycle outcomes must remain unchanged.

## Validation

Executed with the repository virtual environment:

| Check | Observed result |
| --- | --- |
| `python -m unittest tests.safety.test_source_evidence -v` | Ten methods passed in 14.548 seconds |
| Source-schema, profile-lifecycle and job-router group | 43 methods passed in 28.934 seconds |
| `python -m unittest discover -s tests` | 644 tests passed in 304.323 seconds |
| `python scripts/validate_foundation.py` | Passed: 58 required files, 14 context schemas, five skillsets |
| `python scripts/validate_schema_instances.py` | Passed: 15 schema definitions, 108 instances |
| `git diff --check` | Passed |

Comparing the old/new 24-case control snapshots after excluding their five
fingerprint fields confirmed identical lifecycle outcomes, findings, errors and
non-execution flags. No historical observation was refreshed in place.

A separate integrated clock probe used the unchanged synthetic CNC handoff,
then patched only `router.job_router.datetime.now` to `2100-01-01T00:00:00Z`.
Its effective approval changed from `approved` to `invalidated` after the
test-only source expiry, with equal job fingerprints, preserved reviewed
fingerprint and `execution_allowed: false`. This was an in-memory test-clock
override, not a system clock change or actual waiting period.

The source tests use fixed dates for boundary checks. Runtime freshness uses the
current UTC date, not a stored optimistic `reviewed` label. Test-only long-lived
expiry dates are not manufacturing recommendations.
