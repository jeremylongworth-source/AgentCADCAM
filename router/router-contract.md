# Router Contract

The router deterministically maps a request and bounded job context to a workflow family, consequence level, required skills, and blocking outcomes. It does not execute machines or approve manufacturing.

## Inputs

```yaml
process_family: cad_handoff | cnc_milling | additive | laser_cutting | unknown
artifact_class: design | drawing | mesh | toolpath | nc_program | two_d_cutting | handoff | unknown
machine_known: true | false
controller_known: true | false
material_known: true | false
jurisdiction_known: true | false
consequence_level: informational | design_advisory | manufacturing_planning | execution_adjacent | live_execution
approval_state: not_requested | pending | approved | invalidated | rejected
```

Missing or invalid `consequence_level` is not treated as informational. The router uses the route’s declared default consequence and returns `MISSING_CONTEXT` so the request cannot be silently down-classified.

## Contract rules

- Live-control intent always returns `BLOCK_EXECUTION`.
- Unknown process family returns `MISSING_CONTEXT`.
- Execution-adjacent CNC routes require machine, controller, setup, tooling, post, simulation, verification, and human approval checks as applicable.
- Missing or conflicting context produces explicit blockers.
- Approval is scoped to a revision and context fingerprint and is invalidated by consequential changes.
- Routing is deterministic: identical normalized inputs produce identical results.
