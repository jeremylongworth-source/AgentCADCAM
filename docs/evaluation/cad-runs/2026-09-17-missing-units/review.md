# Missing mesh unit contract

Actual Codex-assisted synthetic review on 2026-09-17 using the five repository skills at baseline `fbc1916`. Apply the [shared request, protocol and limits](../negative-cases-protocol.md). This is not an independent practitioner verdict. Exact supplied inventory, declarations, hashes, source/drawing text and tool findings are retained in [observed.json](observed.json).

## 1. cadcam-intake-and-scope

Goal: assess the bundle with an unassigned mesh unit. Family cad_handoff, consequence manufacturing_planning. Known: revision-A source/drawing mm declarations. Missing: mesh/export and bundle unit contract. Preserve overall units as null and the mesh's units as null; route to source verification, not automatic conversion.

## 2. design-file-provenance-review

All four geometry file hashes are unchanged. The submitted inventory, metadata and binding have been inspected in observed.json; the mesh unit is absent, not an invented inch/mm conflict. Source roles remain source versus derivatives. Severity blocker: matching hashes do not make the incomplete unit declaration valid. Ask for the export evidence.

## 3. file-format-interoperability-plan

Do not assign mesh scale from STL extension, a slicer default, matching raw coordinate bounds, or the unit of a different artifact. Require the controlled export unit and a source/mesh dimension comparison. Preserve native source and the original mesh; do not scale or convert during this review. The existing STEP is not proof of mesh-unit inheritance or semantic completeness.

## 4. cad-manufacturability-review

Function, interfaces, tolerances, material/process, finish and inspection remain unresolved. Unit uncertainty additionally prevents dimensional feasibility or fit claims for the mesh. No physical build envelope, printer, machine, material or manufacturing parameter is assumed. Defer process-specific planning until scale and requirements are established.

## 5. drawing-pmi-handoff-review

Consistency: revision labels agree, source/drawing units are mm, mesh/bundle units are unknown. The metadata and binding checks fail while the numeric envelopes pass; that is not a physical-scale pass. No adequate PMI/tolerance/datum intent is supplied. Final handoff: blocked with unresolved units, context/source/human-review blockers and execution prohibited.

## Required correction and handoff

Obtain the mesh export's controlled unit/scale declaration and verify a known dimension against the authoritative source before repairing metadata or binding; do not guess mm from the shape or adjacent files.

[State](state.json) and [handoff](handoff.json) preserve the current identities and blocked review. Artifact paths beginning `replay:` are explicit logical locators resolved only by the fixed replay helper, not claims that temporary files remain on disk. The synthetic IP/export declarations apply only to this evaluation. See the [format policy](../../../formats/format-registry.md) and [baseline manufacturing-intent review](../2026-09-17-manufacturing-intent/review.md) for shared interpretation and missing-context limits. No native probe or process simulation was run on this mutation. REVIEW_REQUIRED before tooling, ordering, production, or regulated use.
