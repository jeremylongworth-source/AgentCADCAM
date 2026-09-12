# Router and State Evaluation Plan

## Acceptance criteria

- Each initial workflow family routes deterministically to its declared skillset.
- Missing or invalid process/consequence context produces an explicit blocker.
- CNC, additive, and laser routes require their machine/material/controller context before execution-adjacent review.
- Live-execution intent always returns `BLOCK_EXECUTION`, even if approval is marked approved.
- State fingerprints change when any consequential field changes.
- Approved records become `invalidated` when consequential context changes; pending/rejected records are not rewritten.
- No route or state operation can set `execution_allowed` to true.

## Evidence

The router and state unit/integration tests cover all four initial families, missing context, live-execution blocking, all invalidating fields, and approval lifecycle behavior. This is a local deterministic utility layer, not a hosted authorization or machine-control service.
