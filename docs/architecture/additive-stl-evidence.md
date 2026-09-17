# Additive STL evidence and declared-unit extents — 2026-09-17

## Implemented decision

For callers of `scripts.additive_preflight.preflight` and maintainers of Phase 4.
REVIEW_REQUIRED. The previous utility accepted `mesh_status: valid` without mesh
bytes and compared unconverted metadata dimensions. The current implementation
requires actual STL bytes, a matching declared SHA-256, an explicit source
revision and explicit mesh/printer units. This is partial file evidence, not
Phase 4 acceptance or manufacturing approval.

The [inspector](../../scripts/stl_mesh_review.py) is a pure byte consumer. It
does not open paths, import native mesh tools, repair/weld geometry, infer units,
fetch data, slice, create process parameters or connect to a printer. The
preflight composes its findings with the existing metadata checks without
altering caller context. Existing CAD envelope checks and their retained
historical outputs remain unchanged.

## Parsed and measured evidence

Binary input requires an exact 84-byte envelope plus the declared number of
50-byte facets, little-endian numeric fields, finite vertices/normals and zero
attribute fields. An exact binary envelope takes precedence over a header
beginning with `solid`. Other data must parse as a complete ASCII solid with
matching names and ordered facet/normal/loop/three-vertex/end markers. Loose
vertex extraction, extra garbage, unsupported syntax and nonfinite values do
not supply geometry. The byte layouts are cross-checked with the upstream
[ADMesh v0.98.5 header](https://github.com/admesh/admesh/blob/v0.98.5/src/stl.h)
and [reader](https://github.com/admesh/admesh/blob/v0.98.5/src/stlinit.c), accessed
2026-09-17. This is a new local implementation, not imported ADMesh code or a
claim of equivalent repair behavior.

The inspector records exact input SHA-256, encoding, facet count, axis bounds
and dimensions, including rational `dimensions_exact` strings used by preflight
so a rounded display extent cannot hide an exceedance. It detects repeated/zero-area triangles, duplicate faces,
boundary/overused edges, inconsistent shared-edge winding, non-cyclic vertex
fans, opposed stored normals and nonpositive signed volume. Exact coordinate
identity defines adjacency; rational arithmetic is used for cross products and
signed-volume decisions after decoding coordinates. No tolerance or repair is
silently applied. Zero stored normals are allowed; geometry drives topology,
not an assertion that all supplied normals are normalized or correct.

Software review limits are 16 MiB and 100,000 facets, not printer limits. CLI
reads stop at the byte limit plus one; over-limit input returns no digest so a
prefix cannot masquerade as whole-file identity. Multiple shells return
`SOURCE_VERIFICATION_REQUIRED` because containment, cavities and inter-shell
intersection semantics are not implemented. Detected mesh defects return
`MISSING_CONTEXT`. Successful partial inspection is named
`checked_partial_geometry`, never `valid`, `printable` or `approved`.

Self-intersections, coplanar overlaps without repeated faces, wall thickness,
dimensional/source equivalence and physical suitability are not established.
STL can contain problematic geometry and does not itself supply units or a
slicer project, as the [Prusa format explanation](https://blog.prusa3d.com/3mf-file-format-and-why-its-great_30986/)
describes (published 2019-11-01, accessed 2026-09-17). Only those format/metadata
claims are used; this is not an endorsement of automatic repair, uploaded-file
services or every statement in that article.

## Units, dimensions and provenance

STL units must be externally declared as `mm`, `in` or `inch` in the job;
printer build dimensions use `printer.lifecycle.units.length`. Unknown units,
strings masquerading as numbers, booleans, nonfinite or nonpositive dimensions
block comparison. File-derived extents must match the declared model dimensions
numerically; no manufacturing tolerance is invented to resolve a mismatch.
This may conservatively block exporter rounding differences pending review.

Fit compares measured extents and build dimensions after conversion to a common
length unit, using a rational factor of 127/5 millimetres per inch. That factor
is exact under the [NIST length-unit definition](https://www.nist.gov/pml/owm/si-units-length),
accessed 2026-09-17. Equal numeric boundaries are accepted, exceedances block.
The claim is only an axis-aligned dimension comparison, not validated placement,
orientation, usable bed shape, supports, brim, clearance or a sliced build.

`job.mesh_sha256` binds the exact submitted bytes; a header-only byte change
requires a renewed declared identity. Geometry is still checked after a hash
mismatch, so identity and file defects remain separately visible. Source revision
must be supplied explicitly rather than defaulting to A. Neither that declaration
nor the hash authenticates the source-to-mesh derivation or permission to print.

## Migration and usage

Pass `mesh_bytes=...` and `source_revision=...` to `preflight`. Provide a reviewed
lowercase `mesh_sha256` in job context; do not update a real job's hash simply to
silence a changed-input blocker. API calls with old metadata alone now block.
The fixture moved to version 2 and records the unchanged CAD STL's hash; its
printer/material lifecycles remain unverified synthetic declarations.

```text
python scripts/additive_preflight.py --mesh fixtures/cad/bracket/source/bracket.stl --source-revision A
python -m unittest tests.safety.test_stl_mesh_review tests.safety.test_additive_preflight -v
```

The CLI accepts a job path and reads the adjacent printer/material JSON plus
the explicitly supplied mesh path. It does not follow a mesh path embedded in
untrusted metadata. It prints JSON and exits 1 for any blockers, including the
fixture's missing human approval. A zero exit means only no detected blockers
in this limited utility; output remains review-required and non-executable.

The subsequent [3MF evidence contract](additive-3mf-evidence.md) adds a bounded
Core package/resource/unit/build inspection path; unsupported constructs still
require explicit further review rather than borrowing STL evidence.
Profile evidence truth, actual slicer configuration,
environment, placement and approval authentication remain qualified review and
composed-workflow obligations; this helper still evaluates declarations for them.

## Acceptance evidence and remaining gate work

The [retained observations](../../fixtures/additive/fdm-bracket/expected/stl-observations.json)
record the actual 2,052-facet bracket and the same mesh with its final facet
removed and count adjusted. Bounds remain 60 by 40 by 30, but the altered mesh
has three boundary edges and three nonmanifold vertices. Tests keep its metadata
label valid and renew only its test hash, so topology supplies the refusal.

Additional positive/negative tests cover ASCII/binary parsing, `solid` binary
headers, winding, degenerate/duplicate faces, edge and vertex defects, separate
shells, malformed/truncated/nonfinite input, resource guards, exact identity,
unit-aware boundary/exceedance, spoofed dimensions and CLI refusal. The tests
do not grade the skill's full reasoning or replace independent geometry review.
Validation results are in the [evaluation follow-up](../evaluation/additive-fdm-evaluation.md).

Rejected alternatives were continuing to trust labels/dimensions or using the
CAD fixture's envelope-only reader as proof of topology. A general mesh repair
dependency is not needed for these bounded observations, and repair would alter
the evidence under review. No supplied model is repaired. Phase 4 remains open
for further package/geometry limits, PrusaSlicer/open-model evidence,
retained skill-assisted handoffs and its complete gate audit. Revisit this
contract for new formats, geometry support, tolerance rules or false-ready cases.
