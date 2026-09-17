# Seven-skill CNC review: machine-limit-conflict

Decision: **blocked; REVIEW_REQUIRED**. Actual Codex output under the [controlled request](../README.md), using this case's [observed inputs and reports](observed.json). The [baseline review](../2026-09-17-positive/review.md) supplies the shared source/context assessment; all its unresolved requirements remain. This is not independent practitioner approval.

The altered line commands X100 Y0 where baseline commanded X60 Y0. X100 exceeds the raw fixture X bound of 60; physical transformed travel remains unverified.

## 1. machine-capability-match

The supplied synthetic machine X bound is 0–60 while the altered raw literal is X100. This is a declared fixture conflict with MACHINE_CONTEXT_REQUIRED, not proof of an observed machine overtravel. Actual frame/offset, usable envelope and capability evidence remain unresolved.

## 2. cnc-setup-planner

G54 and the declared zero-translation model remain present but unverified. The setup reviewer must establish real frame mapping, initial pose and fixture clearance; zero translation cannot be promoted merely to classify a physical target. Stock/part coverage remains incomplete.

## 3. tooling-plan-review

T1 still matches the fixture library entry, but the changed excursion cannot be assessed for holder/fixture clearance with missing geometry. Reach 20 and fixture-holder labels do not make the altered segment acceptable; availability/source gaps persist.

## 4. toolpath-strategy-planner

The changed contour extent differs from both the baseline rectangle and the nominal source base width declaration. There is no controlled feature/allowance/entry justification for that segment. Request intended CAM geometry rather than clipping the path or inventing a strategy.

## 5. postprocessor-readiness-review

Target/post headers still match, but correct labels do not validate motion. The post's synthetic validation field cannot override the extent finding; require actual controlled output and representative validation after resolving design/setup intent.

## 6. nc-static-safety-review

The raw checker reports line 18 X100 exceeds declared fixture coordinate bound and adds MACHINE_CONTEXT_REQUIRED. The reviewed-model checker records no targets because its review prerequisite is missing. Retain that distinction: this run did not prove a transformed machine-space limit breach.

## 7. simulation-readiness-review

Require reviewed coordinate/model evidence plus complete path, fixture/tool collision and stock-removal checks for corrected bytes. Do not count the partial literal bound finding as completed simulation or a safety assessment. Human manufacturing review and simulation remain required.

## Handoff and reviewer action

Have the CAM/setup reviewer resolve the suspicious extent against controlled design intent, reviewed coordinates and actual machine limits; do not enlarge limits or assume a compensating offset to make it pass. The [state](state.json) and [handoff](handoff.json) retain original unverified profiles, job B, linked CAD A, submitted units, actual artifact hash, unresolved assumptions and no approval. The handoff combines specific static findings with shared context/source/simulation/human blockers; composed routing alone does not identify every program mutation because context prerequisites stop it earlier.

These findings concern supplied synthetic file/context evidence and the repository's review contract, not new OEM, material or process claims. No machine, interpreter or simulator was run, no input was repaired, and no manufacturing parameters were generated. Review outcome remains non-executable; gate 04 and independent evaluation remain open.
