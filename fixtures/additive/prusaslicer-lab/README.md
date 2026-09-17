# PrusaSlicer geometry reference lab

Status: `REVIEW_REQUIRED`; synthetic/open geometry, never a printable job.

The opt-in probe reconstructs seven fixed cases from existing repository sources.
It does not download third-party models or accept arbitrary input paths/settings.
Input identities are fixed in `constraints/prusaslicer-win64.json`.

| Case | Source and controlled change |
| --- | --- |
| `bracket-stl` | Existing CAD bracket STL, revision A, 60/40/30 mm |
| `bracket-open-stl` | Remove its last facet and decrement the binary facet count; preserve all other bytes |
| `tetra-3mf` | Unit tetrahedron from the repository test builder, Core-default millimeter |
| `tetra-inch-3mf` | Same tetrahedron, explicitly declare inch |
| `tetra-translated-3mf` | Same tetrahedron, build translation X=200 |
| `tetra-open-3mf` | Remove the face opposite the origin |
| `tetra-required-extension-3mf` | Same tetrahedron, declare synthetic unsupported required extension |

The bracket is the repository's [CC0 synthetic fixture](../../cad/bracket/fixture.yaml)
with [authoritative source](../../cad/bracket/source/bracket.scad); STL is a
derivative, not the design master. Tetrahedron coordinates and packaging are
repository-authored in `tests/safety/test_three_mf_review.py`, under the repository
MIT license. These are openly available test models, not real customer data or
practitioner-pilot submissions. No Prusa sample-model license is implied.

The subsequent [explicit tetrahedron source](tetrahedron-source.json) records
the same coordinates/faces as a CC0 synthetic geometry definition for retained
additive handoffs. A portable regression checks that it reconstructs the earlier
test mesh exactly; historical native observations and their input hashes are
not rewritten. This source still does not define functional product requirements.

The lab reuses existing synthetic FDM contexts solely to compare software
blockers. For tetrahedra it sets declared dimensions to 1/1/1 and selects the
actual package unit. Hash renewal occurs only when constructing these fixed test
cases. No real profile, environment, support plan or approval is established.

The native action is `--info` plus geometry export to temporary STL, and one
bracket export to temporary 3MF. No G-code or slicing action occurs. Imported
units, transformed placements, open edges and unsupported-extension handling are
observations, not physical equivalence or safety verdicts. Original fixture bytes
are compared after every invocation and remain unchanged.

See [runtime and experiment notes](../../../docs/development/prusaslicer-windows.md)
and [retained observations](../../../docs/evaluation/additive-independent/prusaslicer-2.9.6-windows.json).
