# Laser job review — DXF coordinates and radii doubled

Date: 2026-09-17. Skill: `laser-job-preflight`. Decision: blocked, `REVIEW_REQUIRED`; no manufacturing approval or execution permission.

## Artifact and provenance

The [observations](observed.json) preserve the exact submitted job, machine, material and process context, the source inventory hash, selected original drawing hash and derivative hash. The revision-A source inventory is repository-authored synthetic test authority only: it is not authenticated product intent, drawing approval, actual material ownership or permission to manufacture a real job. Source files remain unchanged; `replay:laser/scale-mismatch/input.dxf` identifies deterministic in-memory test bytes, not a permanent output file. This case changes drawing bytes and records a new test derivative hash while preserving optimistic geometry/scale labels.

## Geometry, units and scale

All selected fixture coordinates and circle radii are doubled while $INSUNITS remains mm. Actual extents are 120 × 80 mm and bounds are (10,10)..(130,90); the two holes are radius 6. This fits the declared working area but conflicts with the expected 60 × 40 design dimensions.

Measurements are exact within the supported planar reader subset, not a complete DXF/SVG conformance, rendering or manufacturing-equivalence verdict. Unknown semantics remain blocked. Neither a unit declaration nor the synthetic expected dimensions establish true design dimensions.

## Path intent and placement

The submitted job declares `cut` and `zero_origin_working_area`. These declarations do not establish per-contour intent, cut order, multiplicity, nesting, calibrated axes/orientation, workholding or kerf compensation. Layer/group labels are not authorization to cut, score or mark. Compare each intended path and the exact final offline output to controlled design requirements; no path is repaired, deleted, relabeled or repositioned by this review.

## Machine, material and process

The verified scale label remains unchanged and is insufficient. Machine-envelope fit does not prove design equivalence.

The machine and material lifecycle records remain unverified, with no reviewer or review evidence. The machine's 40W name and 300 × 200 mm area are fixture declarations, not OEM evidence. Actual material grade, thickness and applicable process validation are absent. Process `settings_status=verified` accompanies `settings={}`; it cannot establish usable power, speed, frequency, kerf or focus. No parameters are proposed. Obtain applicable primary machine/material/process documents and qualified review.

## Beam risk

Blocking evidence gap, independent of geometry and emissions: no applicable machine/site beam-safety review, guarding/interlock documentation or authorized operator context is supplied. The review neither evaluates a real installation nor grants permission to energize a beam. Require qualified machine/site review of applicable primary evidence; activation, guard bypass and safety-system changes remain prohibited under the repository execution boundary.

## Process-emission and ventilation risk

Separate blocking evidence gap: generic fixture labels do not establish the composition of actual stock, process emissions or suitable site ventilation. Require applicable material/process primary evidence and qualified site/operator assessment. A resolved beam-control question cannot clear this emission/ventilation question, and a known ventilation flag cannot clear unsafe-material uncertainty. This packet makes no claim that plywood or any actual material is safe to laser-process.

## Blockers and reviewer action

The physical drawing has doubled scale despite unchanged mm units and verified scale metadata.

Require design-owner confirmation of the intended geometry and a controlled corrected drawing or reviewed design revision. Do not automatically halve coordinates, change the expected dimensions, or equate available machine area with design acceptance.

The handoff additionally preserves all unresolved baseline evidence gaps above. Raw preflight blockers: HUMAN_APPROVAL_REQUIRED, MISSING_CONTEXT. Generic router blockers: HUMAN_APPROVAL_REQUIRED, MISSING_CONTEXT, SOURCE_VERIFICATION_REQUIRED. The [handoff](handoff.json) retains their union and [bounded state](state.json); verification stays inconclusive, offline output review is required, and approval is not requested. Raw utility success or schema validity cannot clear any reviewer finding.

## Evidence and limits

This is a retained same-agent, known-case review of synthetic inputs using the skill contract, not a blinded comparison, independent practitioner verdict or a real-input pilot. The deterministic replay checks file/context observations and record integrity; it does not recreate or grade this reasoning. No actual process settings, controller output, machine simulation, physical laser operation or qualified human approval was produced. Reader scope is documented in [laser file evidence](../../../architecture/laser-file-evidence.md); state binding is described in [retained laser review binding](../../../architecture/laser-retained-review-binding.md).
