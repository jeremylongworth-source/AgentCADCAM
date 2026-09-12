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

`router/router.py` and `state/state.py` are dependency-light utilities using the repository YAML/JSON contracts. Tests cover deterministic routing, all initial families, live-execution blocking, fingerprint changes, and approval invalidation.

## Risks and open questions

- Route normalization and state persistence are currently local utilities, not a hosted service or API.
- A future integration must define concurrency, audit retention, authentication, and approval identity separately.
- Machine connectors remain explicitly prohibited by the execution boundary.
