# FDM Additive Evaluation Plan

## Scope

This evaluation covers actual STL/3MF byte identity and partial topology, supported Core package/resources/build transforms, unit-aware extents and declared rectangular placement, alongside metadata-level printer/material, orientation/support, slicer, environmental and approval checks. Unsupported 3MF semantics block explicitly. It does not slice, print, authenticate evidence or certify a material profile.

## Acceptance matrix

| Case | Expected result |
| --- | --- |
| Byte-bound STL with no detected partial-topology defects, matching dimensions/units and the fixture's declared profiles | Block on `HUMAN_APPROVAL_REQUIRED`; no printable/physical-readiness claim |
| Non-manifold geometry | `MISSING_CONTEXT` |
| Unsupported or missing material profile | `MISSING_CONTEXT` |
| Incompatible printer profile | `MACHINE_CONTEXT_REQUIRED` |
| Revision mismatch | `MISSING_CONTEXT` |
| Model exceeds build volume | `MACHINE_CONTEXT_REQUIRED` |
| Missing environmental context | `MISSING_CONTEXT` |

## Hard gates

- STL and 3MF remain print derivatives, not complete design masters.
- Material parameters are never invented.
- Unknown printer, material, slicer, or environmental context cannot receive manufacturing-ready status.
- Preflight never starts a printer and never sets `execution_allowed` to true.

## Evidence status

The synthetic FDM fixture and all seven declared negative mutations are exercised by the test suite. Real printer/material/slicer compatibility and operator safety remain qualified-review responsibilities.

## Actual STL observations and preflight integration — 2026-09-17

Baseline `81ae19d` used labels and metadata dimensions without reading the mesh.
The [new evidence contract](../architecture/additive-stl-evidence.md) now requires
actual bytes, a job-declared SHA-256 and source revision. It inspects bounded
binary/ASCII facet structure, finite values, degenerate/duplicate faces, boundary
and overused edges, winding, vertex fans, opposed normals and signed-volume sign.
Multiple shells require further review; self-intersections are explicitly not
checked. Nothing is repaired or declared printable.

The actual CAD bracket has 2,052 facets, one connected shell, no detected topology
defects and 60 by 40 by 30 extents. Removing its final facet and decrementing the
binary count preserves those extents but produces three boundary edges and three
nonmanifold vertices. Both observations and exact hashes are retained in
`fixtures/additive/fdm-bracket/expected/stl-observations.json` and replayed in
tests. Keeping `mesh_status: valid` and updating only the test hash cannot hide
the defect. The original CAD bytes and synthetic profile review states remain
unchanged; the additive fixture is now version 2.

Measured extents, not metadata dimensions, drive the build-size comparison with
explicit mesh/printer length units. Fractional arithmetic preserves both the
inch conversion and decoded coordinate differences; a test catches an exceedance
of 2^-60 that rounds to 1.0 in a display extent. Missing/invalid units, nonfinite,
boolean and nonpositive dimensions block. This is not a placement, orientation,
support-clearance or usable-bed validation, and it does not establish a sliced
build. A 3MF label cannot borrow the STL result.

The 29 focused tests passed in 4.693 seconds, covering those observations,
constructed geometry defects, malformed input, identity changes, unit boundaries,
context immutability and both CLI invocation forms. The actual baseline CLI
returned blocked with `HUMAN_APPROVAL_REQUIRED` and exit 1, as intended. No slicer,
printer, network uploader or native geometry repair process was invoked.

Executed repository validation: all 416 portable tests passed in 101.280 seconds.
Foundation validation passed (58 required files, ten context schemas, five
skillsets), schema-instance validation passed (eleven definitions, 44 instances),
and `git diff --check` passed. No Phase 4 gate is awarded by this test count.

Phase 4 remains open. Required next evidence includes 3MF package/resource/build
semantics, the specified PrusaSlicer/open-model experiment, remaining geometry
and placement boundaries, retained full skill-assisted handoffs and the complete
gate audit. Green partial checks do not waive any of those requirements.

## Actual 3MF package observations — 2026-09-17

Baseline `94498d0` rejected every 3MF as unsupported. The subsequent
[bounded Core inspection](../architecture/additive-3mf-evidence.md) now reads
actual ZIP/XML, content types and relationships, object meshes, component/build
references, units and transforms. It reuses the STL partial-topology kernel
without float conversion. Embedded/default units govern physical comparisons;
external job units must agree. Transformed build bounds, not only dimensions,
are compared with the declared rectangular zero-origin envelope.

The [retained package observations](../../fixtures/additive/fdm-bracket/expected/3mf-observations.json)
are reproduced from repository-authored tetrahedron XML in a fixed stored ZIP.
They are not PrusaSlicer exports or independently verified manufacturing inputs.
Each case explicitly binds its fresh test hash so identity mismatch does not
mask the intended geometry/context failure:

| Actual package case | Preflight blockers |
| --- | --- |
| Positive default-millimeter package | `HUMAN_APPROVAL_REQUIRED` |
| Removed tetrahedron face, metadata still valid | `MISSING_CONTEXT`, `HUMAN_APPROVAL_REQUIRED` |
| Unit-size object translated to X=200 in the 200-unit envelope | `MACHINE_CONTEXT_REQUIRED`, `HUMAN_APPROVAL_REQUIRED` |
| Embedded inch unit conflicts with the job's mm declaration | `MISSING_CONTEXT`, `HUMAN_APPROVAL_REQUIRED` |

Additional tests cover all six Core units, non-default model paths, exact decimal
precision, transform order, reflection, repeated/unreferenced resources,
overlapping envelopes, stale settings hashes, invalid IDs/indices, geometry
defects, unsupported extensions/materials, opaque auxiliary parts, unsafe paths,
duplicate parts, external relationships, CRC failure, DTD/entity input, archive
encryption/compression/link entries, resource limits and both CLI forms.
The CLI positive package still exits 1 for required human approval. No settings
were executed; no archive was extracted or input repaired.

Executed validation: 58 focused additive tests passed in 5.081 seconds; all
445 portable tests passed in 109.455 seconds. Foundation validation passed
(58 required files, ten context schemas, five skillsets), schema-instance
validation passed (eleven definitions, 44 instances), and whitespace checks
passed. A separate deterministic 400-case corrupted-package probe returned
non-executable reports without unhandled exceptions; this is a bounded probe,
not exhaustive fuzzing or a security certification. The retained-package replay
also passed after explicitly fixing ZIP platform fields for portable identities.

Unknown semantics are not silently accepted: vendor settings, material/property
assignments, non-model object types, extra model parts, required/recommended
extensions and other unsupported constructs need separate review. The checker
does not claim full OPC/XSD conformance, positive-fill Boolean evaluation,
self-intersection detection or usable-bed/support clearance. Synthetic profile
statuses and historical STL/CNC observations remain unchanged.

Gate 05 remains open for the specified independent PrusaSlicer/open-model
experiment, retained full skill-assisted handoffs, remaining geometry/package
boundaries and the complete acceptance audit. Nothing in this evidence grants
manufacturing approval or closes the real-input practitioner pilot.

## Independent PrusaSlicer geometry evidence — 2026-09-17

The [pinned Windows experiment](../development/prusaslicer-windows.md) ran actual
PrusaSlicer 2.9.6 against the open CC0 bracket and repository-authored tetrahedron
packages. The [retained report](additive-independent/prusaslicer-2.9.6-windows.json)
contains seven geometry cases, a version/help result and a bracket 3MF export.
All nine child invocations exited 0; all supplied input bytes remained unchanged.
The native runtime is optional, ignored locally and not redistributed.

Independent observations agree with the bracket's 2,052 facets, dimensions and
the three open edges introduced by removing a face. PrusaSlicer exported both
open meshes without closing them. Inch geometry was converted to the expected
display scale, with measurable float32 precision loss in binary STL. The
translated build retained X=200..201 in the exported STL even though CLI info
reported centered local coordinates. The original package remains blocked by
the declared build envelope.

Two additional observations prevent overclaiming reference-tool acceptance:
the synthetic required-extension package exported without a diagnostic, while
our original-package review remained blocked; and the native bracket 3MF export
contained a missing-thumbnail relationship and auxiliary XML/config parts without
content-type declarations. Its actual package envelope is retained and our
package checker rejects it. No vendor exception or automatic repair was added.

The 15 portable evidence/probe tests passed in 0.570 seconds. They replay current
input identities/reviews and inspect retained native observations without
requiring the runtime. They also check dependency drift, environment isolation,
fixed actions, timeout/error preservation and malformed/missing exports. These
tests do not authenticate upstream binaries or rerun PrusaSlicer in portable CI.

The full portable suite passed all 460 tests in 104.240 seconds. Foundation
validation passed (58 required files, ten context schemas, five skillsets),
schema-instance validation passed (eleven definitions, 44 instances), and
whitespace checks passed. No production profile or historical approval record
was changed by these checks.

This supplies initial independent PrusaSlicer/open-model geometry reference
evidence, not slicing or a manufacturing-ready build. No G-code, material process
parameters, printer connection or production verification was generated. Phase 4
still requires retained full skill-assisted handoffs, review of the remaining
geometry/package limits and its full exit-gate audit. Real-input pilot evidence
is unchanged and absent.

## Retained full additive skill reviews — 2026-09-17

The [twelve packets](additive-runs/README.md) retain Codex's actual application of
the additive-job-preflight contract to the STL baseline, every required roadmap
negative, and four additional 3MF cases. The known-case rubric was fixed before
retaining conclusions; these are same-agent controlled evaluations, not blinded
tests, independent human verdicts or a no-skill baseline comparison.

Each packet includes complete parsed inputs, source/derivative hashes, controlled
mutation, raw preflight and separate routing diagnostics, bounded state, an
agent-authored review and a schema-valid blocked handoff. The actual open-STL
case removes one facet while leaving mesh_status valid and binding its new test
hash; the three boundary edges/vertex defects remain visible. Other cases retain
material/printer conflicts, job B versus source A, measured envelope exceedance,
unknown environment, embedded inch versus mm, transformed out-of-envelope build
placement and unsupported required-extension handling.

The full skill reviews add evidence-quality findings that the declaration-based
utility cannot establish: actual printer/material applicability, complete slicer
profile/version, source intent and acceptance criteria, orientation/support
rationale, usable-bed and unsupported geometry checks, and job/site environmental
review. The fixture's known/reviewed/verified labels remain unchanged inputs,
not proof. Every handoff requires qualified follow-up and applicable sliced-build
verification; no temperatures, cooling, speeds or support parameters are invented.

Fourteen focused packet tests passed in 3.440 seconds. They check exact replay,
state/handoff schemas and fingerprints, file identities, individual negative
findings, unmodified profiles, status-only promotion refusal, and invalidation
when submitted additive context changes. The repository schema-instance command
now includes all 24 additive state/handoff records. Heading checks confirm
contract sections exist; they are not automated reasoning-quality scores.

The full portable suite passed all 474 tests in 105.547 seconds. Foundation
validation passed (58 required files, ten context schemas, five skillsets),
schema-instance validation passed (eleven definitions, 68 instances), and
whitespace checks passed. These checks establish the inspected assertions,
not independent practitioner validation or manufacturing approval.

See the [evaluation-state decision](../architecture/additive-retained-evidence.md)
for why submitted additive context is bound under an evaluation-only setup
wrapper. This is not a new production approval API or completed Phase 6 composed
integration. Phase 4 remains open pending its requirement-by-requirement gate
audit; public-alpha and real-input practitioner requirements are not waived.
