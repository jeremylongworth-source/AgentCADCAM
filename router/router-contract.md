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
requested_action: explain | review | plan | verify | prepare_handoff | <prohibited live action>
generated_manufacturing_artifact: true | false
jurisdiction_required: true | false
```

Missing or invalid `consequence_level` is not treated as informational. The router uses the route’s declared default consequence and returns `MISSING_CONTEXT` so the request cannot be silently down-classified.

Recognized live actions, including machine starts and safety-system disabling, force `live_execution` regardless of the supplied label. NC programs, toolpaths, and explicitly generated manufacturing artifacts have an `execution_adjacent` floor. Informational explanations without such an artifact can remain informational. Scalar strings are trimmed and lowercased; malformed fields and unknown actions produce `MISSING_CONTEXT`. This is structured input classification, not a natural-language intent detector; the intake skill must supply the action and artifact context.

## Contract rules

- Live-control intent always returns `BLOCK_EXECUTION`.
- Unknown process family returns `MISSING_CONTEXT`.
- Execution-adjacent CNC routes require machine, controller, setup, tooling, post, simulation, verification, and human approval checks as applicable.
- Missing or conflicting context produces explicit blockers.
- Approval is scoped to a revision and context fingerprint and is invalidated by consequential changes.
- Routing is deterministic: identical normalized inputs produce identical results.

## Bounded job integration

`route(request)` is the triage utility. Its `approval_state` input is only a declaration; it does not establish a valid approval. Use `router.job_router.route_job(request, current_state, approval, previous_state=..., required_scope="manufacturing_handoff", nc_program=...)` to evaluate a persisted job and approval together. Actual NC bytes are now required for execution-adjacent CNC; see the [binding and migration contract](../docs/architecture/nc-artifact-approval-binding.md).

The integrated function:

- Validates current/previous state, approval records, and supplied machine/controller/material profiles using local schemas. A `*_known: true` flag cannot establish a missing or invalid profile.
- Validates supplied post and tool profiles even outside execution-adjacent CNC. All five reusable profile types require lifecycle metadata; unverified or revision-mismatched profile reviews block effective approval across families and consequence levels. See the [profile lifecycle contract](../docs/standards/context-profile-standard.md). This does not authenticate reviewers or infer unit conversions.
- Uses the state process family and blocks conflicts with the request or supplied profiles.
- Ignores raw approval flags. It requires a record with a matching version-2 context fingerprint, review timestamp, and exact required scope token before recognizing `approved` for this request.
- Marks stale approval copies `invalidated`, preserving the original reviewed fingerprint. A previous state is optional and supplies changed-field diagnostics. A new review of the current fingerprint remains valid even if the previous snapshot differs.
- Preserves records that apply to another scope but does not count them as approval for this scope.
- Keeps CNC simulation and verification blockers independent of approval: execution-adjacent CNC requires `simulation_status: verified`, separate passed simulation/verification records with current input-context bindings, unique check identities and nonempty evidence locators. Every supplied record is checked; a new approval alone cannot renew stale verification. See the [verification-binding contract](../docs/architecture/cnc-verification-binding.md). Laser has the scoped evidence gate below; additive and CAD currently retain generic nonempty passed verification checks pending further integration.
- Checks declared CNC setup, stock units, workholding, WCS, tool identities/geometry/availability, and postprocessor identity/validation. Required CNC context failures invalidate a provisionally recognized approval copy and require human review. See the [CNC context contract](../docs/development/cnc-context-approval.md) for accepted shapes and migration behavior.
- For execution-adjacent CNC, requires actual NC bytes matching a schema-valid state-bound artifact descriptor, reruns static checks against the same context and selected WCS, and invalidates matching approvals when fresh checks fail. Hashes and review fingerprints are not repaired automatically. Unsupported multi-tool inputs require further review support.
- For execution-adjacent laser jobs, requires `laser_drawing` bytes and schema-checked `setup.laser_preflight` inputs, binds source/job/output identity, reruns DXF/SVG preflight, and requires separate current design/path/process/beam/emissions/output evidence records. Missing, stale or failed inputs invalidate effective approval; fixture flags cannot supply process evidence. See the [laser integration and migration contract](../docs/architecture/laser-router-integration.md).
- Returns `job_state`, `approval_record`, `context_fingerprint`, `validation_errors` and `nc_review` alongside the ordinary route result. It copies inputs, persists nothing, and always returns `execution_allowed: false` and `review_required: true`.
- Adds `laser_review` when the laser gate runs. Supplied laser bytes or a declared manufacturing output enforce an execution-adjacent consequence floor; changing the state family cannot bypass the laser byte gate.

This local function checks declared context and record consistency, not reviewer authentication or truth of evidence. Physical suitability, source authority, and process-specific evidence review remain downstream responsibilities; an empty blocker list is not manufacturing readiness or permission to execute.
