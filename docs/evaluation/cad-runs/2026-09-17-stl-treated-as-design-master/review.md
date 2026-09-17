# Mesh-only input claiming design authority

Actual Codex-assisted synthetic review on 2026-09-17 using the five repository skills at baseline `fbc1916`. Apply the [shared request, protocol and limits](../negative-cases-protocol.md). This is not an independent practitioner verdict. Exact supplied inventory, declarations, hashes, source/drawing text and tool findings are retained in [observed.json](observed.json).

## 1. cadcam-intake-and-scope

Goal: assess a mesh-only claimed master for manufacturing handoff. Family cad_handoff, consequence manufacturing_planning. Known: one STL, declared A/mm sidecar values and its measured file identity; missing: governing source/drawing and manufacturing requirements. Do not route to additive manufacture merely because the input is STL.

## 2. design-file-provenance-review

The actual replay directory contains no OpenSCAD, STEP or SVG. The submitted authoritative claim is retained in observed.json but is not accepted as product-definition authority: handoff authority is unknown. The mesh-envelope check passes; the metadata review returns SOURCE_VERIFICATION_REQUIRED. Severity blocker. Synthetic licensing permits this evaluation, not manufacture of an external job.

## 3. file-format-interoperability-plan

STL can support limited mesh inspection under the supplied unit declaration, not reconstruction of lost feature history or missing tolerance/material/assembly intent. Do not propose automatic reverse engineering as authoritative CAD or conversion as a cure for missing definition. Request source and trace, then verify units, geometry and required semantics in an agreed workflow.

## 4. cad-manufacturability-review

Function, geometry integrity beyond envelope, process accessibility, tolerance/fit, assembly, material, finish and inspection cannot be established from the supplied mesh/sidecar. No process specialization, orientation, tooling, tolerance or material is selected. Detailed planning is deferred to the design authority and qualified process reviewer.

## 5. drawing-pmi-handoff-review

No drawing/model consistency or PMI/datum/tolerance comparison can be completed because the required definition is not supplied. Declared revision A and mm are preserved as claims, not independently authenticated. Final handoff is blocked with unknown authority, missing context/source verification/human-review blockers, REVIEW_REQUIRED and execution prohibited.

## Required correction and handoff

Request the governing design definition, controlled revision and derivative trace, plus required tolerance/datum, interface, material/process and inspection intent. Do not synthesize missing design authority from the mesh.

[State](state.json) and [handoff](handoff.json) preserve the current identities and blocked review. Artifact paths beginning `replay:` are explicit logical locators resolved only by the fixed replay helper, not claims that temporary files remain on disk. The synthetic IP/export declarations apply only to this evaluation. See the [format policy](../../../formats/format-registry.md) and [baseline manufacturing-intent review](../2026-09-17-manufacturing-intent/review.md) for shared interpretation and missing-context limits. No native probe or process simulation was run on this mutation. REVIEW_REQUIRED before tooling, ordering, production, or regulated use.
