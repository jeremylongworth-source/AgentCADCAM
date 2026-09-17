# Conflicting drawing revision

Actual Codex-assisted synthetic review on 2026-09-17 using the five repository skills at baseline `fbc1916`. Apply the [shared request, protocol and limits](../negative-cases-protocol.md). This is not an independent practitioner verdict. Exact supplied inventory, declarations, hashes, source/drawing text and tool findings are retained in [observed.json](observed.json).

## 1. cadcam-intake-and-scope

Goal: assess manufacturing handoff of the submitted multi-file bundle. Family cad_handoff, consequence manufacturing_planning, next skillset cadcam-design-handoff. Known: source A and explicit mm; conflicting: drawing B. Missing: authoritative revision resolution and manufacturing requirements. Reviewer question: which definition actually governs this job?

## 2. design-file-provenance-review

The inventory and exact hashes are in observed.json. Preserve OpenSCAD as the declared source and STEP/STL/SVG as derivatives; do not silently relabel the B drawing as A. Geometry envelopes pass, but drawing-revision and byte-binding checks fail. Severity blocker; provenance must be resolved before any manufacturing-facing progression.

## 3. file-format-interoperability-plan

Keep the original source and both revision claims. Do not regenerate or select an exchange file solely because it opens. The fixture STEP remains a geometry reconstruction, not a demonstrated PMI-preserving export; STL is not complete intent. Once revision authority is resolved, compare geometry, units, critical features and required drawing/PMI in the selected receiver.

## 4. cad-manufacturability-review

Function, interfaces, tolerances, material/process, finish and inspection criteria remain unspecified, as in the baseline review. All are unresolved for manufacturing planning. Geometry/access feasibility cannot be certified across conflicting revisions. No setup, grade, fit, or parameter is invented; detailed CNC/FDM work is deferred.

## 5. drawing-pmi-handoff-review

Consistency: source/metadata A versus drawing B is a blocker even though nominal base text agrees. PMI remains declared absent and no adequate tolerance/datum alternative is supplied. Ask for the governing drawing and engineering/inspection review. Final handoff: blocked, MISSING_CONTEXT, SOURCE_VERIFICATION_REQUIRED, HUMAN_APPROVAL_REQUIRED; REVIEW_REQUIRED and no execution.

## Required correction and handoff

Ask the design authority which revision applies; preserve both claims, obtain the controlled matching source/drawing set, and repeat comparison before updating the binding or handoff.

[State](state.json) and [handoff](handoff.json) preserve the current identities and blocked review. Artifact paths beginning `replay:` are explicit logical locators resolved only by the fixed replay helper, not claims that temporary files remain on disk. The synthetic IP/export declarations apply only to this evaluation. See the [format policy](../../../formats/format-registry.md) and [baseline manufacturing-intent review](../2026-09-17-manufacturing-intent/review.md) for shared interpretation and missing-context limits. No native probe or process simulation was run on this mutation. REVIEW_REQUIRED before tooling, ordering, production, or regulated use.
