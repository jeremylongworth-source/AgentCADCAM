# Serialized handoff and current-state binding — 2026-09-17

Status: implemented Phase 6 increment; REVIEW_REQUIRED. This closes a declared
package-consistency gap, not the complete integration gate or physical approval.

## Problem and decision

The handoff schema validates shape and status declarations. `route_job` evaluates
state, scoped approval and process bytes, but does not consume a handoff package.
A consumer must not assume that a schema-valid package with a copied fingerprint
and approval ID contains the artifacts or review conclusions covered by that record.

Use `router.handoff_review.review_handoff(handoff, current_state, approval, ...)`
for the serialized manufacturing-handoff check. It accepts the same explicit
`nc_program`, `laser_drawing`, `additive_mesh` or `cad_artifacts` byte arguments,
optional `previous_state`, and an exact `required_scope` token. It reruns bounded
routing with manufacturing-handoff intent and at least execution-adjacent
consequence. This is not a generic validator for low-consequence advisory notes.
Missing bytes cannot be bypassed with an informational package label.

## Binding review details before approval

Persist an explicit `setup.handoff_review` object containing:

- `handoff_id`: controlled package identity.
- `artifacts`: complete source/output descriptors.
- `assumptions`: review conclusions, statuses and evidence.
- `simulation`: requirement, status, rationale, checks and evidence.
- `human_review`: action, scope tokens and responsible reviewer role.

[handoff-review.schema.json](../../contexts/schemas/handoff-review.schema.json)
reuses the existing handoff field contracts. The CNC setup schema adds this one
typed optional field; it still rejects unrelated properties. Other families
retain their explicit process setup plus this review object. Incomplete drafts
can remain in bounded state, but cannot pass this consumer's readiness checks.

Bind these details before current-context verification and scoped approval.
Version-1 verification fingerprints and version-2 approval fingerprints already
cover all setup content. No version change or automatic migration is needed.
Verification outcomes stay in `state.verification_results`; package identity,
revision, units and process stay in their existing state fields. Fingerprints,
approval IDs, package statuses and blocker lists are not nested into the review
object, avoiding circular hashes. The consumer never copies a supplied package
into state, generates review records, refreshes hashes or re-signs approval.

## Checks and outcomes

The consumer validates the package schema, runs the selected process gate and
compares package job/revision/units/family, fingerprint and consequence with the
current result. Every current routing blocker must appear in the package; all
declared blockers are retained in the decision even when routing does not derive
them independently.

Each review-detail field must exactly match its state-bound counterpart.
Verification must exactly match current state records, and simulation status
must agree with state. Unknown/required/failed simulation and unresolved/rejected
assumptions produce explicit blockers, not an averaged quality deduction.
For non-CNC processes, a sourced and reviewed `not_required` disposition remains
representable; the checker cannot decide its engineering adequacy. CNC routing
still requires its independently bound simulation evidence.

Artifact IDs and locators must be unique. Hash coverage must equal the current
source/output inventory, with a declared authoritative source bound to state.
The exact generated-output descriptor and the CAD/additive/laser source or
derivative descriptors bound by their process inputs must be preserved.
Unknown authority, conflicting units/revisions, and promotion of known mesh,
print-package or manufacturing-code derivatives to design authority block.
Hashes and descriptive roles remain declarations unless a process gate inspects
the actual bytes; this layer does not fetch additional source files or evidence.

An approved package also needs the supplied current record's exact approval ID
and coverage of every declared handoff review scope. A matching record never
promotes a draft automatically. Package failures invalidate a provisionally
recognized approval copy while preserving its reviewed fingerprint and original
inputs. Pending/rejected records are not rewritten as approved or invalidated.

Results contain current `context_fingerprint`, effective `approval_state`, a
copied `approval_record`, routing classification/blockers, findings and validation
errors. Schema-valid packages get a reviewed `handoff` copy. Failed approved
packages become `invalidated`; other failures become `blocked`; live requests
always remain blocked. Original package fingerprints and approval references are
not rewritten. Malformed packages return no validated package copy. Validation
diagnostics report rules/locations, not private submitted values.

The top-level decision is only `blocked` or `review_required`. All outcomes have
`review_required: true` and `execution_allowed: false`. A recognized synthetic
record is not authority to manufacture; reviewer authentication, evidence truth,
access authorization and physical operating decisions remain outside this API.

## Verification, migration and remaining work

`tests/routing/test_handoff_review.py` covers all four consistent controls,
schema-valid identity/content substitutions, missing snapshots, exact evidence
binding, stale approvals, changed bytes, omitted blockers, simulation/assumption
failures, inventory/source/output conflicts, approval ID/scope failures, draft
non-promotion, live refusals and malformed inputs. Controls use explicitly
non-operational test declarations, including the CNC control's dummy source
identity; they are not real qualified approvals or proof of CAD derivation.

The four historical baseline packages are also checked using their actual
fixture bytes and no approval. Their old snapshots and missing context remain
blocked. Original artifacts, conclusions, fingerprints and packet files are
preserved; additional current findings are returned separately. New applicable
review is required for migration, not flag promotion or reconstruction of an old
approval. Executed results are recorded in the
[evaluation follow-up](../evaluation/router-state-evaluation.md).

This consumer supplies an integration primitive, not retained four-family
skill-assisted workflow acceptance. That evaluation and the complete Phase 6
gate audit remain open. Public-alpha hardening and qualified real-input pilot
evidence are separate requirements.
