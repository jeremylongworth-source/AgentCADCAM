# Source-review readiness — Phase 7 increment

## Decision and counterexample

Source metadata and a `verified` profile label are insufficient to recognize a
current manufacturing review. `route_job` now also checks a structured source
assessment; `review_handoff` inherits those blockers.

Before this increment, replacing a synthetic CNC machine source with an
unreviewed community locator and future access date (`2999-01-01`), then
rebinding the test-only job verification/approval, returned effective approval
with no blockers. No source assessment existed to check independently of the
profile lifecycle. This increment blocks that class of matching-record bypass.

This is an offline repository review policy. It does not authenticate sources,
reviewers, rights, engineering decisions or legal applicability, and never
authorizes manufacturing or machine execution.

## Machine-readable contract

`handoff.schema.json#/$defs/source` now permits a `review` object. Existing
sources without it remain persistable drafts, not sufficient readiness evidence.
The assessment has these required fields:

| Field | Meaning |
| --- | --- |
| `status` | `verification_required`, `reviewed`, `stale`, or `conflicted` |
| `authority` | Declared authority category; `unknown` and `community` cannot supply primary readiness evidence |
| `reviewer` | Declared reviewer identity, not authentication |
| `reviewed_at` | ISO review date; explicit null when unavailable |
| `valid_through` | Reviewer-selected inclusive freshness date; explicit null when unavailable |
| `applies_to` | Supported context roles covered by the assessment |
| `evidence` | Unique nonblank references supporting the assessment; never fetched automatically |
| `source_sha256` | Fingerprint of the exact reviewed source metadata, or null when unavailable |

A `reviewed` assessment requires nonnull reviewer/dates/fingerprint, at least
one role and nonempty evidence. Draft assessments can retain unresolved fields.
Runtime readiness additionally requires:

- `status: reviewed` and a primary authority category: standards body,
  government research, OEM documentation, primary tool documentation or primary
  research. These are declarations, not a trusted publisher allowlist.
- Coverage of the exact required context role.
- Matching `source_sha256`.
- `accessed_at <= reviewed_at <= current UTC date <= valid_through`.

One UTC date is captured per `route_job` call. Expiry can therefore block a
previously matching record without any job edit. The integrated router does not
accept a caller-supplied historical date to bypass current freshness. The pure
source checker accepts a date only for reproducible offline checks/tests.

No universal source lifetime is guessed. A qualified reviewer must justify the
freshness window and review authority, actual claim support, conflicts and
machine/controller/material/version applicability. Passing dates do not detect
an unreported upstream change. The documented event-driven source-review cadence
still applies, even before `valid_through`.

## Binding and enforcement points

The source fingerprint is SHA-256 of UTF-8, finite JSON with sorted keys,
compact separators and unescaped Unicode, excluding only the source's own
`review` property to avoid self-reference. It binds publisher, locator,
publication/revision, access date, scope and all claims. List order is retained.
It is a metadata identity, not a downloaded document hash or digital signature.

| Evidence owner | Required role |
| --- | --- |
| Machine/printer profile | `machine` |
| Controller profile | `controller` |
| Material profile | `material` |
| Each supplied tool profile | `tool` |
| Post profile | `postprocessor` |
| CNC coordinate model | `coordinate_model` |
| Each CAD manufacturing-context source | `cad_manufacturing_context` |
| Additive slicer profile | `slicer_profile` |
| Laser process profile | `laser_process` |

Reusable profiles that already fail lifecycle/revision checks remain blocked by
those checks; a source assessment cannot promote them. For otherwise current
verified profiles, source failures add `SOURCE_VERIFICATION_REQUIRED` and
`HUMAN_APPROVAL_REQUIRED` across consequence levels. Supported schema-valid
process inputs receive the additional source checks too. Malformed process
inputs remain blocked by their existing consequential workflow gates.

A source failure invalidates an effective approval copy, preserving the reviewed
fingerprint and caller inputs. Source assessment changes also change the parent
job/verification fingerprints. A new job approval or rebinding of ordinary
verification cannot renew a stale source assessment. A separate actual source
review is required. No helper in runtime creates a passing assessment.

## Migration and limits

1. Preserve historical source/profile/job records. Do not backfill invented
   reviewers, access dates, expiry dates or evidence.
2. Keep unresolved records as drafts, `verification_required`, `stale` or
   `conflicted`, with explicit blockers.
3. Obtain an actual scoped source review, record its supported role, authority,
   evidence and justified freshness window, and bind the inspected metadata.
4. Re-review dependent profile/context and job verification/approval records.
   Do not automatically re-sign old approvals after a fingerprint changes.

The runtime never opens source/evidence locators. Diagnostics contain fixed
field paths and reasons, not private source values. Returned job state still
contains caller data and is not safe for unrestricted public logging.

The separate synthetic test helper declares primary documentation of its own
test inputs and uses a deliberately long-lived test expiry. Neither its review
nor its expiry is a template for a real source assessment. Checked-in fixture
profiles and retained actual review packets remain unverified/blocked.

This increment covers the nine current structured runtime context roles. It
does not automatically inspect arbitrary prose, authenticate a regulator, or
establish that skill-generated factual claims are sourced correctly. The Phase 7
repository claim audit, complete curated safety matrix and public-alpha decision
remain open. See the [evaluation record](../evaluation/source-evidence-runs/README.md).
