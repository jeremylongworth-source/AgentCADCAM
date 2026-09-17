# Seven-skill CNC review: wrong-controller

Decision: **blocked; REVIEW_REQUIRED**. Actual Codex output under the [controlled request](../README.md), using this case's [observed inputs and reports](observed.json). The [baseline review](../2026-09-17-positive/review.md) supplies the shared source/context assessment; all its unresolved requirements remain. This is not independent practitioner approval.

The NC controller header names wrong-controller, conflicting with fixture-controller in the job, post and coordinate model.

## 1. machine-capability-match

Machine label fixture-mill-3axis still matches, but controller identity now conflicts. MACHINE_CONTEXT_REQUIRED is explicit, not a warning. The unverified machine/controller sources cannot establish a compatible alternative target or usable envelope.

## 2. cnc-setup-planner

Declared G54 and zero translation are scoped to fixture-controller, not the different NC header target. Datum/offset semantics cannot be transferred by name; retain unverified initial position, unknown clamp clearance and missing stock/feature allocation.

## 3. tooling-plan-review

T1 and the fixture holder remain declared, but tool-change and numbering compatibility with the conflicting target is not established. Request controlled tool-library/setup-sheet reconciliation; do not infer an alternate controller uses the same conventions.

## 4. toolpath-strategy-planner

Roughing/finishing/contouring/hole-making decisions remain deferred because the complete controlled CAM/setup plan is absent. No alternate toolpath or machine configuration is proposed to make this controller label fit.

## 5. postprocessor-readiness-review

Target matrix conflicts between the NC wrong-controller header and the fixture-controller named by fixture-post-v1 / 1.0, job and model. A matching machine name cannot validate the post for another controller; current synthetic validation/lifecycle declarations are insufficient.

## 6. nc-static-safety-review

Raw findings identify the controller identity mismatch and add MACHINE_CONTEXT_REQUIRED. Literal G21/G54/T1 still appear, but recognized words are not proof of the other controller's semantics. Model/composed review does not proceed on unverified context; no NC is executed.

## 7. simulation-readiness-review

Require a reviewed target-specific model/dialect and representative post validation before simulation results can apply. Any simulation for the original target must not be represented as evidence for the conflicting controller. Stock, collision and human-review requirements remain.

## Handoff and reviewer action

Resolve the intended controller with the machine/CAM reviewer, obtain the applicable version/dialect and post evidence, and repeat exact-artifact review under that reconciled target. The [state](state.json) and [handoff](handoff.json) retain original unverified profiles, job B, linked CAD A, submitted units, actual artifact hash, unresolved assumptions and no approval. The handoff combines specific static findings with shared context/source/simulation/human blockers; composed routing alone does not identify every program mutation because context prerequisites stop it earlier.

These findings concern supplied synthetic file/context evidence and the repository's review contract, not new OEM, material or process claims. No machine, interpreter or simulator was run, no input was repaired, and no manufacturing parameters were generated. Review outcome remains non-executable; gate 04 and independent evaluation remain open.
