# Seven-skill CNC review: wrong-units

Decision: **blocked; REVIEW_REQUIRED**. Actual Codex output under the [controlled request](../README.md), using this case's [observed inputs and reports](observed.json). The [baseline review](../2026-09-17-positive/review.md) supplies the shared source/context assessment; all its unresolved requirements remain. This is not independent practitioner approval.

G20 conflicts with the mm job, NC header, machine/controller and setup/model declarations. Units cannot be silently converted or resolved by a comment.

## 1. machine-capability-match

Machine evidence still declares only mm support and is unverified. The altered G20 is absent from the supplied controller command list, adding MACHINE_CONTEXT_REQUIRED. Numeric travel/feed comparisons cannot establish a compatible physical job under conflicting unit declarations.

## 2. cnc-setup-planner

Stock remains declared 60 × 40 × 6 mm and G54/zero-translation context is unchanged. The mm model cannot resolve the program's altered units. Datum establishment, clamp clearance and stock/part coverage remain unknown; no scaling or re-fixturing is inferred.

## 3. tooling-plan-review

The supplied T1/fixture-tool-1 numbering still matches, but its nominal diameter/reach are mm declarations with unverified provenance and fixture-only availability. Do not rescale the library to accommodate the NC; require tooling and unit reconciliation.

## 4. toolpath-strategy-planner

The rectangle is still not a complete L-bracket operation plan. Conflicting units invalidate any proposed interpretation of extents, feed and engagement; roughing, finishing and hole-making choices remain deferred pending controlled geometry, stock, material and CAM inputs.

## 5. postprocessor-readiness-review

Post/machine/controller header identities still match, but the G20/mm contradiction makes the output unsuitable for the declared contract. The synthetic validation flag and unverified post lifecycle do not resolve it. Request exact-version, unit-specific post validation.

## 6. nc-static-safety-review

Actual text has G20 where baseline had G21 while its UNITS comment still says mm. Raw findings report program-unit conflict, unsupported G20 and missing required motion prerequisites. MISSING_CONTEXT and MACHINE_CONTEXT_REQUIRED are added to baseline static blockers. Model arithmetic is not run; no conversion, upload or execution occurs.

## 7. simulation-readiness-review

Existing not_run simulation cannot be reused as evidence, and a future result under assumed units would not satisfy this package. Establish one reviewed unit contract across stock, tool, machine, NC and model before compatibility, collision and material-removal checks. Human review remains required.

## Handoff and reviewer action

Resolve intended units with the CAM/setup authority, produce a correctly targeted controlled artifact and repeat context, static and simulation reviews; do not edit only the unit label. The [state](state.json) and [handoff](handoff.json) retain original unverified profiles, job B, linked CAD A, submitted units, actual artifact hash, unresolved assumptions and no approval. The handoff combines specific static findings with shared context/source/simulation/human blockers; composed routing alone does not identify every program mutation because context prerequisites stop it earlier.

These findings concern supplied synthetic file/context evidence and the repository's review contract, not new OEM, material or process claims. No machine, interpreter or simulator was run, no input was repaired, and no manufacturing parameters were generated. Review outcome remains non-executable; gate 04 and independent evaluation remain open.
