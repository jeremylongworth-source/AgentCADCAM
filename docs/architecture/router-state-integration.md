# Router and State Integration

## Scope

Phase 6 integrates the four workflow families without turning the repository into a machine controller. The router selects a skillset and consequence level; bounded state preserves the context fingerprint required to interpret an approval.

## Data flow

```text
request + explicit context -> normalize -> route -> required checks/blockers
                                      |
                                      v
                              bounded job state -> fingerprint -> approval invalidation
```

## Router responsibilities

- Select one declared process family and skillset.
- Classify consequence.
- Require process-specific context before execution-adjacent review.
- Return explicit blockers and never authorize execution.

## State responsibilities

- Preserve job/revision/source identity and consequential context.
- Compute a deterministic fingerprint over invalidating fields.
- Invalidate approved records when any consequential field changes.
- Avoid free-form persistent agent memory as a source of truth.

## Validation notes

The [2026-09-17 requirement audit](../development/integration-gate-review.md)
accepts Phase 6 for repository development against the initial corpus. It maps
all required inputs/state fields and six exit criteria to inspected evidence,
including retained integrated reviews and four-family invalidation controls.
This is not public-alpha acceptance or manufacturing approval.

`router/router.py` and `state/state.py` are dependency-light utilities using the repository YAML/JSON contracts. Tests cover deterministic routing, all initial families, live-execution blocking, fingerprint changes, and approval invalidation.

`router/job_router.py` adds the bounded integration path using the local JSON Schema validator. It checks records before routing and returns effective approval, copied state, blockers, and audit diagnostics. See the [router contract](../../router/router-contract.md) for inputs and status semantics, and the [fingerprint migration](../development/fingerprint-v2-migration.md) for existing approvals.

`router/handoff_review.py` adds the [serialized package consumer](handoff-state-binding.md):
handoff review details are bound in setup before evidence and approval, then
checked against the supplied package and fresh process routing. Schema-valid
content substitutions, stale records and omitted blockers are explicit failures.
The consumer persists nothing and does not authenticate evidence or reviewers.

## Risks and open questions

- Route normalization and state persistence are currently local utilities, not a hosted service or API.
- A future integration must define concurrency, audit retention, authentication, and approval identity separately.
- Machine connectors remain explicitly prohibited by the execution boundary.
