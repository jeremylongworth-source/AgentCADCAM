# Seven-skill CNC review: incorrect-tool-number

Decision: **blocked; REVIEW_REQUIRED**. Actual Codex output under the [controlled request](../README.md), using this case's [observed inputs and reports](observed.json). The [baseline review](../2026-09-17-positive/review.md) supplies the shared source/context assessment; all its unresolved requirements remain. This is not independent practitioner approval.

The controlled mutation changes T1 M6 to T2 M6, but the supplied library still assigns fixture-tool-1 only to number 1. No T2 mapping is supplied.

## 1. machine-capability-match

The same three-axis target is declared, but the tool actually selected by T2 is not established. Machine interface, spindle suitability and reach comparisons for the supplied T1 cannot be transferred to an unknown number.

## 2. cnc-setup-planner

Setup/model records refer to fixture-tool-1 and unverified initial/offset evidence. Without controlled numbering, its mapping and access assumptions cannot be applied to T2. Fixture, stock and datum evidence remains unresolved.

## 3. tooling-plan-review

Supplied row: fixture-tool-1 / T1, endmill diameter 6, fixture-holder, reach 20, fixture-only. NC row: T2 M6, no matching library entry. The scenario is labeled incorrect-tool-number, but available evidence proves only a mismatch—not that T2 must be the same physical tool.

## 4. toolpath-strategy-planner

No tool-specific contouring, entry or hole-making strategy can be accepted under unresolved numbering. Request the actual CAM operation/tool allocation and authoritative process inputs; do not invent parameters or substitute tools.

## 5. postprocessor-readiness-review

Matching post labels do not reconcile output numbering with the selected tool library. Require exact CAM/library/post version and representative tool-change output evidence; the unverified lifecycle remains blocking despite the synthetic validation flag.

## 6. nc-static-safety-review

Raw findings reject tool reconciliation, report no known selected tool at the change, and report unresolved motion prerequisites, adding MISSING_CONTEXT. The complete T2 bytes/hash are retained, not repaired. Explicit-model and composed stages remain blocked by baseline context.

## 7. simulation-readiness-review

Simulation with T1 alone cannot verify an artifact selecting T2 without an established mapping. Resolve numbering/tool assembly and all shared setup/model/post gaps, then repeat exact-artifact collision/material-removal and qualified human reviews.

## Handoff and reviewer action

Have the tooling/CAM reviewer establish the intended numbering across library, setup sheet and posted artifact; do not assume T2 aliases T1 or automatically repair the program. The [state](state.json) and [handoff](handoff.json) retain original unverified profiles, job B, linked CAD A, submitted units, actual artifact hash, unresolved assumptions and no approval. The handoff combines specific static findings with shared context/source/simulation/human blockers; composed routing alone does not identify every program mutation because context prerequisites stop it earlier.

These findings concern supplied synthetic file/context evidence and the repository's review contract, not new OEM, material or process claims. No machine, interpreter or simulator was run, no input was repaired, and no manufacturing parameters were generated. Review outcome remains non-executable; gate 04 and independent evaluation remain open.
