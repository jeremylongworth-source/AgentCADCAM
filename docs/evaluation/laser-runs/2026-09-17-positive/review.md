# Laser job review — DXF baseline

Date: 2026-09-17. Skill: `laser-job-preflight`. Decision: blocked, `REVIEW_REQUIRED`; no manufacturing approval or execution permission.

## Artifact and provenance

The [observations](observed.json) preserve the exact submitted job, machine, material and process context, the source inventory hash, selected original drawing hash and derivative hash. The revision-A source inventory is repository-authored synthetic test authority only: it is not authenticated product intent, drawing approval, actual material ownership or permission to manufacture a real job. Source files remain unchanged; `replay:laser/positive/input.dxf` identifies deterministic in-memory test bytes, not a permanent output file. This case preserves the original selected drawing bytes; any context mutation is retained explicitly.

## Geometry, units and scale

The selected revision-A DXF contains one closed four-edge rectangle and two circles. Measured bounds are (5,5)..(65,45) mm, giving 60 × 40 mm extents. No defect was detected by the supported planar checks. Layer 0 is recorded, not interpreted as an approved cut strategy.

Measurements are exact within the supported planar reader subset, not a complete DXF/SVG conformance, rendering or manufacturing-equivalence verdict. Unknown semantics remain blocked. Neither a unit declaration nor the synthetic expected dimensions establish true design dimensions.

## Path intent and placement

The submitted job declares `cut` and `zero_origin_working_area`. These declarations do not establish per-contour intent, cut order, multiplicity, nesting, calibrated axes/orientation, workholding or kerf compensation. Layer/group labels are not authorization to cut, score or mark. Compare each intended path and the exact final offline output to controlled design requirements; no path is repaired, deleted, relabeled or repositioned by this review.

## Machine, material and process

The selected fixture-laser-40w, fixture-plywood and fixture-plywood-profile identifiers agree. This is a declaration-only match: machine/material lifecycle revision 1 remains unverified and the process settings object is empty.

The machine and material lifecycle records remain unverified, with no reviewer or review evidence. The machine's 40W name and 300 × 200 mm area are fixture declarations, not OEM evidence. Actual material grade, thickness and applicable process validation are absent. Process `settings_status=verified` accompanies `settings={}`; it cannot establish usable power, speed, frequency, kerf or focus. No parameters are proposed. Obtain applicable primary machine/material/process documents and qualified review.

## Beam risk

Blocking evidence gap, independent of geometry and emissions: no applicable machine/site beam-safety review, guarding/interlock documentation or authorized operator context is supplied. The review neither evaluates a real installation nor grants permission to energize a beam. Require qualified machine/site review of applicable primary evidence; activation, guard bypass and safety-system changes remain prohibited under the repository execution boundary.

## Process-emission and ventilation risk

Separate blocking evidence gap: generic fixture labels do not establish the composition of actual stock, process emissions or suitable site ventilation. Require applicable material/process primary evidence and qualified site/operator assessment. A resolved beam-control question cannot clear this emission/ventilation question, and a known ventilation flag cannot clear unsafe-material uncertainty. This packet makes no claim that plywood or any actual material is safe to laser-process.

## Blockers and reviewer action

Matching synthetic labels and partial contour evidence do not establish product intent, material suitability, process applicability, site controls or approval.

Obtain the design acceptance criteria, actual material/grade/thickness and applicable machine/process documentation; review path intent, orientation, placement, kerf and offline output, then obtain qualified design/process/site approval for the exact files.

The handoff additionally preserves all unresolved baseline evidence gaps above. Raw preflight blockers: HUMAN_APPROVAL_REQUIRED. Generic router blockers: HUMAN_APPROVAL_REQUIRED, MISSING_CONTEXT, SOURCE_VERIFICATION_REQUIRED. The [handoff](handoff.json) retains their union and [bounded state](state.json); verification stays inconclusive, offline output review is required, and approval is not requested. Raw utility success or schema validity cannot clear any reviewer finding.

## Evidence and limits

This is a retained same-agent, known-case review of synthetic inputs using the skill contract, not a blinded comparison, independent practitioner verdict or a real-input pilot. The deterministic replay checks file/context observations and record integrity; it does not recreate or grade this reasoning. No actual process settings, controller output, machine simulation, physical laser operation or qualified human approval was produced. Reader scope is documented in [laser file evidence](../../../architecture/laser-file-evidence.md); state binding is described in [retained laser review binding](../../../architecture/laser-retained-review-binding.md).
