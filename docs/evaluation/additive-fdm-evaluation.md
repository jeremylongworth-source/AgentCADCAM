# FDM Additive Evaluation Plan

## Scope

This evaluation covers actual STL byte identity/partial topology and declared-unit extents, alongside metadata-level printer/material, orientation/support, slicer, environmental and approval checks. 3MF package inspection remains incomplete and blocks explicitly. It does not slice, print, authenticate evidence or certify a material profile.

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
