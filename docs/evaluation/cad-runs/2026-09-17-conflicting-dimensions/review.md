# Conflicting visible base dimension

Actual Codex-assisted synthetic review on 2026-09-17 using the five repository skills at baseline `fbc1916`. Apply the [shared request, protocol and limits](../negative-cases-protocol.md). This is not an independent practitioner verdict. Exact supplied inventory, declarations, hashes, source/drawing text and tool findings are retained in [observed.json](observed.json).

## 1. cadcam-intake-and-scope

Goal: assess handoff with conflicting dimensions inside the supplied drawing. Family cad_handoff, consequence manufacturing_planning. Known: source A/mm and nominal source width 60. Conflicting: visible drawing width 61 versus description/projection/source width 60. Missing: engineering disposition and complete manufacturing intent.

## 2. design-file-provenance-review

The source, STEP and STL hashes are unchanged; drawing hash is df0f54ab6e130958e5fe547f0e07752fd0784a13a149b317a96347599d13429c. The supplied binding does not cover the changed drawing. Preserve source/derivative roles and the contradictory statements. Severity blocker even if a new hash declaration were supplied: identity is not dimensional correctness.

## 3. file-format-interoperability-plan

Do not resolve the conflict by converting the drawing, taking the STEP envelope as overriding authority, or treating one-millimetre disagreement as an acceptable tolerance. After a controlled design decision, compare all required dimensions/units/revisions and inspect exchange losses. Preserve the editable source and original contradictory drawing for audit.

## 4. cad-manufacturability-review

Function and mating interfaces are unspecified; there is no evidence that either width meets them. Geometry/access, tolerance/process compatibility, material, finish and inspection remain unresolved. No process plan or manufacturing parameter is supplied. Obtain designer and inspection review before detailed CNC/FDM routing.

## 5. drawing-pmi-handoff-review

The consistency matrix is source/description/rectangle width 60 versus annotation width 61; depth and thickness remain 40/6, revision A, units mm. The structural drawing checker detects the conflict; expected text elsewhere cannot override it. Missing PMI/acceptance intent also persists. Final handoff remains blocked, review-required and non-executable.

## Required correction and handoff

Ask the design authority to resolve the 60/61 conflict and issue the controlled consistent source/drawing set; do not average dimensions, choose whichever representation is convenient, or infer a tolerance.

[State](state.json) and [handoff](handoff.json) preserve the current identities and blocked review. Artifact paths beginning `replay:` are explicit logical locators resolved only by the fixed replay helper, not claims that temporary files remain on disk. The synthetic IP/export declarations apply only to this evaluation. See the [format policy](../../../formats/format-registry.md) and [baseline manufacturing-intent review](../2026-09-17-manufacturing-intent/review.md) for shared interpretation and missing-context limits. No native probe or process simulation was run on this mutation. REVIEW_REQUIRED before tooling, ordering, production, or regulated use.
