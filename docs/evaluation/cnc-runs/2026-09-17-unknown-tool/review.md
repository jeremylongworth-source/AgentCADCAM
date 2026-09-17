# Seven-skill CNC review: unknown-tool

Decision: **blocked; REVIEW_REQUIRED**. Actual Codex output under the [controlled request](../README.md), using this case's [observed inputs and reports](observed.json). The [baseline review](../2026-09-17-positive/review.md) supplies the shared source/context assessment; all its unresolved requirements remain. This is not independent practitioner approval.

T9 M6 references a tool absent from the supplied one-tool library, which contains only T1 / fixture-tool-1.

## 1. machine-capability-match

Target labels and declared bounds are unchanged, but an unknown tool prevents checking interface, reach, spindle applicability or clearance requirements. Unverified machine/material profiles remain insufficient for a capability conclusion.

## 2. cnc-setup-planner

Tool-dependent access and coordinate mapping cannot be established for T9. The stored translation is scoped to fixture-tool-1, not an unidentified replacement; retain datum, clamp and initial-position gaps rather than reusing that mapping.

## 3. tooling-plan-review

Tooling table now has supplied T1 (nominal diameter 6, two-flute endmill, fixture-holder, reach 20, fixture-only) versus requested T9 with no entry, geometry, holder, reach, availability or source. This is a blocking identity gap, not a missing optional description.

## 4. toolpath-strategy-planner

No cutter-dependent entry, engagement, finishing or hole-making recommendation is supportable for the unidentified T9. Request controlled feature/tool allocation and sources without copying T1's synthetic feeds or geometry.

## 5. postprocessor-readiness-review

Post labels remain consistent, but there is no evidence that the CAM library, tool selection and posted number agree. The unverified post lifecycle cannot validate the unknown reference. Require representative tool-selection output review.

## 6. nc-static-safety-review

Raw findings reject the tool reference and report a tool change lacking a known selected tool plus unresolved motion prerequisites. MISSING_CONTEXT is explicit. All altered bytes and identity are retained; no tool replacement is made or executed.

## 7. simulation-readiness-review

No tool/holder model for T9 exists, so collision/material-removal results using T1 would not verify this artifact. Resolve actual tooling, setup and post evidence, then repeat matching simulation and human handoff review.

## Handoff and reviewer action

Obtain the intended controlled tool assembly/library and reconcile NC, CAM and setup-sheet numbering with the tooling reviewer; do not invent T9 geometry or automatically substitute T1. The [state](state.json) and [handoff](handoff.json) retain original unverified profiles, job B, linked CAD A, submitted units, actual artifact hash, unresolved assumptions and no approval. The handoff combines specific static findings with shared context/source/simulation/human blockers; composed routing alone does not identify every program mutation because context prerequisites stop it earlier.

These findings concern supplied synthetic file/context evidence and the repository's review contract, not new OEM, material or process claims. No machine, interpreter or simulator was run, no input was repaired, and no manufacturing parameters were generated. Review outcome remains non-executable; gate 04 and independent evaluation remain open.
