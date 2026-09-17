# Router and State Evaluation Plan

## Acceptance criteria

- Each initial workflow family routes deterministically to its declared skillset.
- Missing or invalid process/consequence context produces an explicit blocker.
- CNC, additive, and laser routes require process-applicable machine/material context; CNC additionally requires controller context before execution-adjacent review.
- Live-execution intent always returns `BLOCK_EXECUTION`, even if approval is marked approved.
- State fingerprints change when any consequential field changes.
- Approved records become `invalidated` when consequential context changes; pending/rejected records are not rewritten.
- No route or state operation can set `execution_allowed` to true.

## Evidence

The router and state unit/integration tests cover all four initial families, missing context, live-execution blocking, all invalidating fields, and approval lifecycle behavior. This is a local deterministic utility layer, not a hosted authorization or machine-control service.

## Serialized handoff consumer — 2026-09-17

The [handoff/state binding contract](../architecture/handoff-state-binding.md)
adds a read-only consumer beyond schema validation and job routing. Its explicit
`setup.handoff_review` snapshot binds artifacts, assumptions, simulation and
human-review details before current-context evidence and approval. Fresh process
checks, package identity/classification, exact evidence and approval scope/ID
are compared without renewing records or changing historical packet files.

Seventeen consumer methods exercise consistent controls for CAD, CNC, additive
and laser; schema-valid substitutions; missing snapshots; stale evidence and
approvals; changed bytes; omitted blockers; source/output coverage; unresolved
simulation/assumptions; derivative-authority refusal; draft non-promotion; live
refusals; malformed inputs; and all four historical baseline packages. The
controls use test-only declared reviews, not practitioner verdicts. The CNC
control's dummy source identity is not proof of real CAD-to-NC derivation.

The initial sixteen-method consumer run passed in 38.557 seconds. After adding
the four historical packet checks, 46 combined consumer and schema tests passed
in 41.245 seconds. All four archived packages remained blocked and retained their
original artifacts, assumptions, evidence, simulation, review instructions and
fingerprints. Current checks add findings rather than rewriting old conclusions.

A subsequent inspection reproduced loss of a valid package's declared regulatory
blocker when current state was malformed. Declared blockers are now preserved
before attempting state comparisons. The focused malformed-input method passed
in 1.833 seconds, including preservation of that blocker in the returned copy.

The final full portable suite passed all 608 tests in 210.643 seconds after the
blocker-preservation fix. Foundation validation passed (58 required files,
fourteen context schemas, five skillsets), schema-instance validation passed
(fifteen definitions, 100 instances), and whitespace checks passed. No native
tool or machine was invoked; these are scoped software/record assertions.

This increment verifies package/record consistency and conservative refusal, not
source truth, evidence authenticity or engineering adequacy. It does not create
new skill-assisted workflow verdicts or accept gate 07. Retained four-family
integrated review evidence and the full Phase 6 audit remain required, followed
by public-alpha hardening and qualified real-input pilot validation.

## Four-family evaluation and gate audit — 2026-09-17

The later [integrated evaluation milestone](integration-runs/README.md) retained
four actual skill-assisted reviews and 24 separate synthetic approval-lifecycle
observations. Nine replay/integrity methods and the then-current 617-test suite
passed. Missing fixture context and blocked manufacturing handoffs were preserved.

The [full Phase 6 audit](../development/integration-gate-review.md) subsequently
checked every deliverable and exit criterion. It added six gate-matrix methods:
all twenty roadmap state fields, key-order determinism, exact family selection,
all consequence levels, 250 explicit live-action/classification combinations,
twenty integrated byte/consequence controls, and 72 stale-record checks covering
all nine required changes across four families with/without previous state.

The focused matrix passed in 33.741 seconds. The full suite passed 623 tests in
261.981 seconds. Foundation validation passed (58 required files, 14 context
schemas, five skillsets); schema-instance validation passed (15 definitions,
108 instances). No runtime correction, source fixture, skill or actual approval
change was required. The router test entry point maps the roadmap directory to
the canonical repository-wide routing tests.

Gate 07 is accepted for repository development against the initial corpus.
This is not source authentication, qualified engineering review, public-alpha
acceptance or practitioner validation. Phase 7 hardening is next.
