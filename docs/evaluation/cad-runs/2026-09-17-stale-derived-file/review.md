# Changed source with old derivatives

Actual Codex-assisted synthetic review on 2026-09-17 using the five repository skills at baseline `fbc1916`. Apply the [shared request, protocol and limits](../negative-cases-protocol.md). This is not an independent practitioner verdict. Exact supplied inventory, declarations, hashes, source/drawing text and tool findings are retained in [observed.json](observed.json).

## 1. cadcam-intake-and-scope

Goal: assess handoff after a source edit with unchanged derivatives. Family cad_handoff, consequence manufacturing_planning. Known: labels A/mm remain; conflicting: current source hole diameter versus old drawing/derivative association. Missing: change authorization, controlled revision and validated regeneration evidence. Ask which design intent is current.

## 2. design-file-provenance-review

Observed source hash changes to 545f8072ac46b266fbb467a47117d2550099dec852586bd44698fc7d4117d836; derivative hashes remain those in the baseline. The old binding no longer covers the source. Severity blocker. Preserve the old outputs for audit; do not treat them as verified exports of the new source or silently elevate a derivative over the source.

## 3. file-format-interoperability-plan

Unchanged STEP/STL envelopes do not validate the changed feature. Preserve editable source, selected exchange artifacts, export options and revision history. After an authorized decision, regenerate the relevant derivatives and independently compare hole features, topology, scale and any required semantics. No conversion or native geometry probe was run on this mutation.

## 4. cad-manufacturability-review

Function and assembly: the hole change could affect unspecified mating requirements, so no fit judgment is possible. Geometry/access and tolerances need re-review after the intended change is resolved. Material/process, finish and inspection remain unspecified. These are blockers to handoff, not a recommendation to use either diameter.

## 5. drawing-pmi-handoff-review

Consistency: source assignment is 8, drawing base-hole radii are 3, all labels still say A. Source-parameter, drawing projection and byte-binding findings block handoff despite passing envelopes. PMI/acceptance intent remains absent. Request engineering/change-control and inspection review; retain MISSING_CONTEXT, SOURCE_VERIFICATION_REQUIRED, HUMAN_APPROVAL_REQUIRED and REVIEW_REQUIRED.

## Required correction and handoff

Have the design authority resolve whether the source edit is intended, assign the controlled revision, and regenerate/review affected derivatives where appropriate. Never replace stored hashes just to suppress the mismatch.

[State](state.json) and [handoff](handoff.json) preserve the current identities and blocked review. Artifact paths beginning `replay:` are explicit logical locators resolved only by the fixed replay helper, not claims that temporary files remain on disk. The synthetic IP/export declarations apply only to this evaluation. See the [format policy](../../../formats/format-registry.md) and [baseline manufacturing-intent review](../2026-09-17-manufacturing-intent/review.md) for shared interpretation and missing-context limits. No native probe or process simulation was run on this mutation. REVIEW_REQUIRED before tooling, ordering, production, or regulated use.
