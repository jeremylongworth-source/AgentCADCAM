# Seven-skill CNC review: wrong-post

Decision: **blocked; REVIEW_REQUIRED**. Actual Codex output under the [controlled request](../README.md), using this case's [observed inputs and reports](observed.json). The [baseline review](../2026-09-17-positive/review.md) supplies the shared source/context assessment; all its unresolved requirements remain. This is not independent practitioner approval.

The NC names wrong-post-v9 while the supplied post profile identifies fixture-post-v1 version 1.0. Program origin and applicability are unresolved.

## 1. machine-capability-match

The NC's machine/controller labels still match the unverified synthetic profiles, but the post mismatch prevents treating that identity chain as a machine-capability match. Envelope, access, stock and real OEM evidence remain unresolved.

## 2. cnc-setup-planner

Stock/orientation/G54 declarations are unchanged and unverified. Do not assume another post uses identical coordinate, tool-change or retract conventions; the setup reviewer must reconcile actual output against the controlled datum and fixture definition.

## 3. tooling-plan-review

T1 still matches the sole fixture tool label. That does not establish that the wrong-post output used the intended library/holder or numbering convention. Keep fixture-only availability, unknown clearance and unverified tool evidence as blockers.

## 4. toolpath-strategy-planner

No complete feature-to-operation or stock-removal plan is supplied. The altered header does not identify any alternate valid strategy. Request the controlled CAM job and generation record before reviewing roughing/finishing/hole-making, without inventing parameters.

## 5. postprocessor-readiness-review

Identity matrix has one explicit contradiction: NC POST wrong-post-v9 versus profile fixture-post-v1 / 1.0, for fixture-cam, fixture-controller and fixture-mill-3axis. SOURCE_VERIFICATION_REQUIRED is blocking. No actual post implementation/test evidence is supplied; do not deploy or rename a post to reconcile labels.

## 6. nc-static-safety-review

Raw text inspection reports program post identity does not match post context. Exact altered bytes have their own retained hash; matching units/WCS/T1 do not remove the mismatch. Explicit-model and composed stages remain blocked by unverified baseline context; approval is not_requested.

## 7. simulation-readiness-review

Require representative post/controller validation and collision/material-removal verification for the corrected, identified output with matching setup/tool/model identities. There is no simulation evidence to transfer, and a result from fixture-post-v1 cannot validate an unidentified alternate post. Human review is mandatory.

## Handoff and reviewer action

Have the CAM/post reviewer establish the actual generator and version, reconcile its target and validation evidence, then regenerate or withdraw the artifact under change control and repeat verification. The [state](state.json) and [handoff](handoff.json) retain original unverified profiles, job B, linked CAD A, submitted units, actual artifact hash, unresolved assumptions and no approval. The handoff combines specific static findings with shared context/source/simulation/human blockers; composed routing alone does not identify every program mutation because context prerequisites stop it earlier.

These findings concern supplied synthetic file/context evidence and the repository's review contract, not new OEM, material or process claims. No machine, interpreter or simulator was run, no input was repaired, and no manufacturing parameters were generated. Review outcome remains non-executable; gate 04 and independent evaluation remain open.
