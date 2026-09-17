# Integrated additive preflight — 2026-09-17

REVIEW_REQUIRED. Block the manufacturing handoff. Apply `additive-job-preflight`
to the actual positive STL fixture with unchanged printer, material and job
declarations under the [protocol](../protocol.md).

## Artifact, geometry and scale

The inventory preserves revision-A native SCAD authority and a derived STL
whose actual hash is `9447459b1eeb56d1cf1810dbbdd2f1598d349646a96b7183c682c600992e460e`.
The selected `replay:additive/positive/input.stl` locator identifies the supplied
in-memory derivative; it is not a saved printer output. The mesh is a
reconstruction, not evidence that all SCAD design intent survived.

The raw byte check found 2052 binary facets, dimensions 60 x 40 x 30, one shell,
positive signed volume, and zero supported boundary/nonmanifold/winding,
duplicate, degenerate and normal-conflict findings. Self-intersections, full
design equivalence and tolerance acceptance were not checked. Millimetres and
revision come from external fixture declarations, not STL authority. Unlike a
3MF package, this STL supplies no package units/build placement or project
configuration; none is inferred. See the scoped [format policy](../../../formats/format-registry.md).

## Printer, material and slicer

Declared dimensions fit the synthetic printer's 200 x 200 x 200 envelope;
that is an axis-aligned comparison, not usable-bed/support clearance. The
printer accepts fixture-pla by declaration, and the material lists
fixture-pla-profile. Both lifecycles are unverified. The job has no selected
slicer-profile ID, slicer identity/version or settings object. Its
`slicer_profile_status: verified` label cannot provide those facts.

Preserve `slicer_profile: null`; request applicable printer/material evidence
and a reviewed selected profile. Do not invent temperatures, layer heights,
cooling, speed or material parameters to satisfy the input schema.

## Orientation and support

The source has a base, upright back and holes on two faces. The submitted
orientation/support `reviewed` labels contain no actual decisions. A reviewer
must compare candidate orientations against functional faces, hole geometry,
support access/removal and final placement. No orientation or support strategy
is selected here: feature intent, dimensional acceptance and applicable process
evidence are missing. No slicer or build preview was run in this evaluation.

## Environment and human review

`environment_status: known` appears in job and material records, but their
sources explicitly support only synthetic declarations. They do not document
the actual material grade, site ventilation, thermal controls, handling or
operator review. Obtain the applicable manufacturer/site evidence; do not infer
safety from the PLA label or name a numerical exposure/thermal limit.

Required reviewer actions are design-to-mesh comparison and acceptance criteria,
printer/material qualification, selected slicer/version/settings, orientation,
support, usable-bed placement and site review. Then inspect the exact sliced
output and establish the applicable verification/simulation disposition. No
final output exists now; simulation status remains unknown, not waived.

## Integrated result and limits

The raw utility reports partial geometry and missing human approval. The
integrated router additionally rejects incomplete readiness context and missing
scoped evidence. Nested additive input is intentionally invalid (missing profile
selection/settings); integrated raw preflight is not rerun. The raw byte result
is retained separately in [observed.json](observed.json), not mislabeled as a
completed integrated or sliced-build check.

Seven review roles preserve the gaps with current-input bindings. The consumer
retains the state-bound handoff, unresolved assumptions and simulation/review
blockers. No human approval, print parameters or machine action was generated.
These are known-case same-agent findings; replay does not independently assess
the quality of the reasoning or establish practitioner usefulness.
