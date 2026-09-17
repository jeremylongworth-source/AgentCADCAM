# Laser byte and evidence integration — 2026-09-17

Status: implemented Phase 6 increment; REVIEW_REQUIRED. This is not acceptance
of the complete integration gate or permission to manufacture.

## Problem and decision

Before this change, `route_job` could recognize an execution-adjacent laser
approval from matching state/profile records and generic passed verification
without inspecting the drawing or process context. The Phase 5 utility and
retained reviews exposed file failures separately, but the generic router did
not consume them.

`route_job(..., laser_drawing=actual_bytes)` now invokes
`router.laser_evidence.check_laser_artifact` for every execution-adjacent or
live-execution laser state. Missing bytes are a blocker, not an opt-out. Supplied
bytes or any declared manufacturing output raise the consequence floor, even
when the caller supplies an informational label. Laser bytes or a `two_d_cutting`
output cannot be reclassified into another state family to skip the gate.
Every result still forbids execution. Live requests remain `BLOCK_EXECUTION`.

Context-only advisory/planning requests with no output and no supplied drawing
can route without an invented drawing. The router is a structured API, not a
natural-language intent detector. Intake must classify actual output and intent.

## Persisted inputs and identity

Store an explicit `setup.laser_preflight` object containing:

- `job`: the complete laser preflight job declaration.
- `process`: selected profile ID, machine/material IDs, settings status,
  nonempty settings and structured source metadata.
- `source_artifact`: a handoff-schema artifact descriptor identifying the
  authoritative source, revision, units and SHA-256 identity.

[laser-preflight.schema.json](../../contexts/schemas/laser-preflight.schema.json)
defines the input shape required by the readiness gate. The root state still
allows draft setup objects to be persisted; missing/incomplete laser inputs
cannot satisfy this gate. No root field or fingerprint version is added:
version 2 already binds all setup content, including process settings and sources.

The submitted job ID, revision and units must match the bounded state. The source
descriptor must be authoritative, have matching revision/units, and have its hash
in `source_artifact_hashes`. These checks preserve declared identity; they do not
authenticate source bytes, design equivalence, ownership or authority. Source
design review is a separate required evidence role.

`generated_manufacturing_output` must be a schema-valid derived `two_d_cutting`
descriptor with current revision/units. Supplied drawing bytes must match that
descriptor and the inner job's drawing hash. The existing bounded DXF/SVG
preflight reruns against those bytes and the same machine/material/process
context. Binding failures do not suppress available fresh preflight findings.
Malformed input-contract structure can prevent preflight; this remains blocked.

Only explicit byte arguments are consumed. The gate reads no artifact paths,
fetches no sources, executes no settings and never repairs or updates a hash.
The existing byte limit applies before computing a complete-file identity.

## Independent evidence roles

Every supplied verification record must satisfy the handoff verification shape,
have `kind: verification`, nonempty evidence locators, a unique check ID and a
version-1 `context_binding` matching `verification_context_fingerprint(state)`.
The following check IDs must each have current passed evidence:

| Check ID | Review responsibility |
| --- | --- |
| `laser_design` | Controlled design, source authority, revision and physical dimensions. |
| `laser_paths` | Per-path intent, multiplicity/order, placement/axes and applicable kerf interpretation. |
| `laser_process` | Applicable machine/material/profile/settings and authoritative parameter/unit context. |
| `laser_beam` | Applicable machine/site beam-risk review and responsible human controls. |
| `laser_emissions` | Independent actual material/process emissions and site ventilation review. |
| `laser_output` | Exact offline intended output/path verification against the current design and context. |

These are required review-record roles, not automated safety judgments. Resolving
beam review cannot substitute for emissions review; neither can be averaged into
a score. Empty fixture settings plus a verified flag cannot satisfy the input
contract. Nonempty settings and source metadata alone also cannot establish
applicability: the separate bound process-review record remains required. This
portable layer does not validate vendor-specific parameter names, units or ranges.

The verification fingerprint excludes verification outcomes to avoid circular
binding. The approval fingerprint includes those records. Changing a process,
source, file, machine, material or setup therefore requires current verification
and a separate new scoped approval. Re-signing approval alone cannot renew stale
verification. No runtime function creates either evidence or approval.

## Approval result and migration

Fresh file/context/evidence failures invalidate a provisionally matching approved
record copy and add `HUMAN_APPROVAL_REQUIRED`; the original fingerprint and input
records remain unchanged. Invalid state/schema or wrong-scope records are not
recognized as effective approval. The inner job's raw approval flag is ignored;
preflight receives the router's scoped record decision instead.

Results include `laser_review` when the laser gate runs, alongside overall
blockers, copied state/approval and the context fingerprint. Consumers must use
the overall result, not a nested utility result in isolation. Even a no-blocker
test control returns `review_required: true` and `execution_allowed: false`.
Record consistency is not reviewer authentication or manufacturing permission.

The sixteen Phase 5 packets used `setup.context_kind=laser_evaluation_input`, not
this explicit input contract. They remain immutable and blocked. Their replay
test permits exactly the new missing-contract/byte/evidence diagnostics; it
still checks every original input, raw observation, state hash and blocker.
Do not migrate packets by promoting flags, inventing settings or rewriting old
verdicts. A real migration requires new applicable context, evidence and review.

## Verification and remaining work

`tests/routing/test_laser_artifact_gate.py` exercises both formats, every retained
negative with freshly bound test-only records, missing/wrong bytes, descriptor
and source conflicts, empty settings, every evidence role, failed/duplicate/stale
records, invalidation, raw-flag refusal, consequence/family bypass and all live
actions. Positive controls use an explicitly non-operational test marker, not
laser parameters or practitioner approval. Existing CNC/profile/replay tests
cover regressions. Executed results are recorded in the
[evaluation follow-up](../evaluation/laser-cut-evaluation.md).

Phase 6 still requires additive file-aware composition, the CAD handoff evidence
path, four-family integrated handoff evaluation and a complete gate audit.
Evidence authenticity, source/governance coverage and qualified real-input
validation remain later gates, not guarantees supplied by this schema.
