# Seven-skill CNC review: missing-wcs

Decision: **blocked; REVIEW_REQUIRED**. Actual Codex output under the [controlled request](../README.md), using this case's [observed inputs and reports](observed.json). The [baseline review](../2026-09-17-positive/review.md) supplies the shared source/context assessment; all its unresolved requirements remain. This is not independent practitioner approval.

G54 was removed from the program even though setup/model context selects G54. Supplied configuration cannot establish the program's active WCS.

## 1. machine-capability-match

Machine/controller header identity remains consistent, but neither unverified profiles nor numeric machine limits establish where this program's coordinates lie. Machine applicability remains unresolved until the selected coordinate system is established.

## 2. cnc-setup-planner

The setup says WCS defined, not verified, and its G54 model is unverified. The altered G90 G17 block no longer selects that WCS. Request explicit datum location/axes, offset evidence, initial position and qualified verification method; no inherited state is assumed.

## 3. tooling-plan-review

T1 still agrees with the single fixture library entry. Unknown position/offset context prevents assessing feature access or holder clearance even if tool labels match. Availability and supplier/reach evidence remain unresolved.

## 4. toolpath-strategy-planner

The rectangle cannot be placed meaningfully in the reviewed setup without WCS evidence. Do not infer entry/exit clearance, stock engagement or a valid feature strategy from its numbers; complete design/stock and CAM decisions remain required.

## 5. postprocessor-readiness-review

The post labels match but the supplied output lacks the WCS prerequisite required by this bounded contract. Its synthetic verified flag does not validate startup state. Obtain controlled post/setup output evidence; do not silently insert a command in this review.

## 6. nc-static-safety-review

Raw findings say required WCS is missing and each axis move precedes required prerequisites, adding MISSING_CONTEXT. G90/G17 cannot substitute for G54. Explicit-model review returns not_run for absent model review; it does not establish coordinates from the context label.

## 7. simulation-readiness-review

Require simulation and verification initialized from the actual reviewed coordinate state, not a simulator default that happens to match G54. No current simulation exists. Retain collision, stock-removal, target/post and qualified human-review requirements.

## Handoff and reviewer action

Have the setup/CAM reviewer reconcile the intended datum and explicit WCS selection against the actual target and regenerate a controlled program before re-review; never assume an inherited active offset. The [state](state.json) and [handoff](handoff.json) retain original unverified profiles, job B, linked CAD A, submitted units, actual artifact hash, unresolved assumptions and no approval. The handoff combines specific static findings with shared context/source/simulation/human blockers; composed routing alone does not identify every program mutation because context prerequisites stop it earlier.

These findings concern supplied synthetic file/context evidence and the repository's review contract, not new OEM, material or process claims. No machine, interpreter or simulator was run, no input was repaired, and no manufacturing parameters were generated. Review outcome remains non-executable; gate 04 and independent evaluation remain open.
