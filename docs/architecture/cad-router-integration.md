# CAD byte and review integration — 2026-09-17

Status: implemented Phase 6 increment; REVIEW_REQUIRED. The complete integration
gate remains open. This is not general CAD validation or manufacturing approval.

## Decision and supported scope

`route_job(..., cad_artifacts={locator: bytes, ...})` now binds CAD handoff review
to actual supplied artifacts and separate review roles. The initial explicit
`cad-bracket-basic-v2` profile reuses the existing restricted source/drawing and
STEP/STL envelope checks. Unsupported profiles return
`SOURCE_VERIFICATION_REQUIRED`; matching hashes cannot supply geometry support.

The profile's four locator keys are `source/bracket.scad`, `source/bracket.step`,
`source/bracket.stl` and `source/bracket.svg`. These are inventory keys, not paths
the router opens. All values must be nonempty bytes, each at most 16 MiB and at
most 32 MiB in total. The router does not write temporary files, follow paths,
fetch sources, run OpenSCAD/CadQuery, regenerate geometry or execute machines.
The shared file validators expose pure text/byte functions while their existing
path/CLI interfaces remain available. Nonfinite exchange coordinates block.

The gate runs for execution-adjacent and live CAD states. Supplying CAD bytes,
selecting generated output, or requesting CAD `prepare_handoff` enforces an
execution-adjacent floor. Advisory discussion without those inputs/actions can
remain advisory; it need not invent artifacts. CAD bytes cannot move to another
process family to skip review. A reviewed mesh derivative can be a selected CAD
handoff output only with the full CAD byte inventory; this is not additive print
preparation and cannot waive the additive gate on a later additive job.

## Persisted inputs and identity

Store `setup.cad_handoff` under the
[input schema](../../contexts/schemas/cad-handoff-input.schema.json):

- `review_profile`: explicit adapter selection, currently `cad-bracket-basic-v2`.
- `metadata`: job identity, revision, units, design authority and PMI availability.
- `derivation`: the existing source/derivative binding contract.
- `manufacturing_context`: selected process/material, nonempty requirements,
  drawing/PMI basis and scoped source records.

Draft state can still hold incomplete setup objects. Gate validation requires
the nested input contract; root-schema acceptance is not readiness. All fields
are already covered by the version-2 state fingerprint, so its version does not
change. Parsed metadata is bound as state, not a separately authenticated file.

Metadata identity/revision/units must match state. The source must be the native
design, not a mesh/exchange derivative. Each expected artifact occurs once with
a unique ID, the expected role and matching revision/units. The state hash list
must exactly cover the reviewed inventory, and raw byte hashes must match the
declared descriptors. The bracket's STEP/STL relationships remain reconstruction,
not direct export; the SVG remains a reference drawing. A selected output must
exactly equal one of the bound descriptors. No hash or approval is refreshed.

The fixture has no embedded manufacturing PMI. Claiming otherwise blocks; a
declared controlled alternative needs an explicit basis and separate review.
Missing requirements, unknown PMI availability, absent sources and conflicting
supplied material/process profiles also block. CAD review need not invent a
machine profile; if one is supplied, its lifecycle and process are checked.
These schema fields represent declarations, not proof of adequate tolerances,
datums, interfaces, finish, inspection criteria or process feasibility.

## Independent evidence and approval

Every verification record requires the handoff shape, `kind: verification`,
nonempty evidence, a unique check ID and a current version-1 input-context
binding. The following roles must each have a current passed record:

| Check ID | Review responsibility |
| --- | --- |
| `cad_provenance` | Source authority, revisions, derivation, ownership/licensing and traceability. |
| `cad_interoperability` | Receiver/process suitability, preserved/lost semantics and conversion verification. |
| `cad_manufacturability` | Applicable material/process, feasibility and complete acceptance requirements. |
| `cad_drawing_pmi` | Drawing/model consistency and adequate controlled dimensional/datum/tolerance/inspection intent. |
| `cad_handoff` | Complete inventory, resolved assumptions, intended recipient/context and scoped final review. |

These are evidence obligations, not automatic engineering assessments. A passed
envelope check cannot replace any role. Input fingerprints exclude outcomes;
approval fingerprints include them. Changing requirements, sources, files or
context requires renewed evidence and scoped approval. A new approval alone
cannot renew stale records. A matching approval cannot waive fresh failures:
the router invalidates a copy while preserving original inputs and its reviewed
fingerprint. Raw status flags cannot supply a scoped approval.

`cad_review` contains fresh byte identities, file findings and evidence blockers.
Consumers must use the overall route result, not isolated nested checks. Every
result remains `review_required: true` and `execution_allowed: false`. All live
actions remain `BLOCK_EXECUTION`, including when test-only records otherwise pass.

## Migration, verification and remaining work

Existing callers preparing a CAD handoff must supply the new context, bytes and
applicable evidence. Do not promote generic passed labels or fabricate missing
manufacturing requirements. The six historical CAD packets retain their original
inputs, observations, states and blocked handoffs; their fixed fixture replays
remain unchanged. New in-memory controls are explicitly test-only declarations,
not repairs of those missing-intent verdicts or qualified human approvals.

`tests/routing/test_cad_artifact_gate.py` covers positive controls, all six named
roadmap failure categories, current hashes with independently failing drawing or
source checks, missing/malformed inventory, profiles and roles, stale evidence,
old approvals, classification/family bypass, all live actions and bounded malformed
input. Existing CLI/replay tests check compatibility. Executed results are in the
[evaluation follow-up](../evaluation/cad-handoff-evaluation.md).

The bounded checks do not interpret arbitrary CAD programs, validate general STEP
topology or full PMI, prove geometric equivalence, or authenticate sources and
reviewers. New fixture/format adapters require explicit contracts and tests.
Four-family retained workflow/approval evaluation and the full Phase 6 gate audit
remain required. Safety/source hardening and qualified real-input pilot validation
are not replaced by this integration.
