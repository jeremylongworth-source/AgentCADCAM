# Additive byte and evidence integration — 2026-09-17

Status: implemented Phase 6 increment; REVIEW_REQUIRED. This does not accept
the complete integration gate or authorize manufacturing.

## Decision and inputs

`route_job(..., additive_mesh=actual_bytes)` invokes the additive gate for every
execution-adjacent or live-execution additive state. Missing bytes block; the
caller cannot opt out. Supplied bytes or a declared manufacturing output raise
the consequence floor. Additive bytes or a selected `mesh_derivative` or
`print_package` manufacturing output cannot move to another family to skip review.
Context-only planning without bytes or generated output can still proceed.

Persist `setup.additive_preflight` under the
[additive input schema](../../contexts/schemas/additive-preflight.schema.json):

- `job`: complete submitted preflight declarations, including `slicer_profile_id`.
- `slicer_profile`: profile ID/revision, slicer ID/version, printer/material IDs,
  nonempty settings and structured source metadata.
- `source_artifact`: authoritative source descriptor, revision, units and hash.

The root state permits incomplete draft setup objects. The execution-adjacent
gate validates this nested contract; storing an object does not make it ready.
No state field or fingerprint version changes. Version 2 already binds setup,
including selected settings, versions and sources.

Job identity/revision/units must match state. Source revision/units must match,
and the declared source hash must occur in `source_artifact_hashes`. These checks
do not read source bytes or authenticate authority, derivation or design intent.

`generated_manufacturing_output` must be a schema-valid derived artifact with
current revision/units: `mesh_derivative` for STL or `print_package` for 3MF.
Actual bytes must match both its hash and the submitted job's `mesh_sha256`.
Fresh preflight inspects bounded STL/3MF geometry and declared context, retaining
embedded/default 3MF units and supported transformed-build placement checks.
Available file findings are not suppressed by descriptor or source conflicts;
invalid input-contract structure prevents preflight and remains blocked.

The selected slicer profile must match the job, printer and material; material
compatibility must explicitly include that profile, and both job and material
environmental context must be known. Applicable profile lifecycle checks remain
independent. Nonempty settings are required data, not validated print parameters.
Vendor-specific settings, parameter units/ranges and applicability require review.

## Required review roles

Every verification record must satisfy the handoff verification shape, have
`kind: verification`, nonempty evidence locators, a unique check ID and a current
version-1 verification-context binding. Each role below requires a passed record.

| Check ID | Required review responsibility |
| --- | --- |
| `additive_design` | Source authority, revision, design intent and acceptance criteria. |
| `additive_geometry` | Applicable model/package validity beyond the partial byte checks. |
| `additive_orientation` | Intended build orientation, placement and usable-bed constraints. |
| `additive_supports` | Applicable support plan, clearances and removal considerations. |
| `additive_slicer` | Selected slicer/version/settings and printer/material applicability. |
| `additive_environment` | Actual material/process/site environmental and operator context. |
| `additive_output` | Exact intended offline output and applicable sliced-build verification. |

These are independent evidence obligations, not automatic engineering judgments.
The output record is a declaration about supplied evidence: this gate does not
slice, parse printer G-code or verify a real sliced build. Evidence authenticity
and adequacy remain qualified human responsibilities. Missing one role cannot
be offset by another passing role or a new approval.

Verification fingerprints bind inputs but exclude verification outcomes to avoid
circularity. Approval fingerprints also bind the outcome records. Changed source,
bytes, profile, settings, revision or setup requires current evidence and a new
scoped review; re-signing only approval cannot renew stale verification.

## Results, migration and limits

The gate adds `additive_review` to routing results. Consumers must use overall
blockers, not just the nested raw utility report. Fresh failures invalidate a
provisionally recognized approval copy and require human review. Original inputs
and reviewed fingerprints are preserved. Raw job/request/state approval flags
cannot authorize; preflight receives the router's scoped record decision.
Every result remains review-required and non-executable, including positive
test controls. Prohibited live actions always retain `BLOCK_EXECUTION`.

The gate reads explicit bytes only: no artifact-path access, source fetching,
settings execution, repair, slicing or printer connection. Existing byte/package
limits remain enforced. The numeric reader now rejects lexical exponents outside
its bounded range before Decimal conversion; extreme vertex/transform exponents
return structured source-review blockers instead of an uncaught exception.

The twelve historical Phase 4 packets retain their original evaluation wrappers,
observations, states, reviews and blocked handoffs. Replay now returns additional
missing-contract/byte/evidence diagnostics. An exact regression permits only
those additions, not arbitrary observation or identity drift. Migration requires
new applicable inputs and review, not invented settings or promoted old flags.

## Evidence and remaining work

`tests/routing/test_additive_artifact_gate.py` covers both formats, every retained
negative with fresh test-only records, missing/changed bytes, source/descriptor
conflicts, profile/settings/version/compatibility checks, all seven roles,
failed/duplicate/stale records, invalidation and classification/live-action
bypasses. Controls use a non-operational settings marker, not print parameters
or practitioner approval. A separate reader regression covers extreme positive
and negative exponents in vertices and transforms. Executed results are recorded
in the [evaluation follow-up](../evaluation/additive-fdm-evaluation.md).

Phase 6 still requires CAD handoff evidence integration, four-family retained
workflow/approval evaluation and the complete integration gate audit. General
geometry/package validation, source truth and qualified real-input validation
are not established by these test-only records.
