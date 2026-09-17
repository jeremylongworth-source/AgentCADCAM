# Seven-skill CNC review: revision-mismatch

Decision: **blocked; REVIEW_REQUIRED**. Actual Codex output under the [controlled request](../README.md), using this case's [observed inputs and reports](observed.json). The [baseline review](../2026-09-17-positive/review.md) supplies the shared source/context assessment; all its unresolved requirements remain. This is not independent practitioner approval.

The NC header claims revision C while the selected CNC job and submitted artifact descriptor remain revision B; linked CAD revision A is a separate source identity.

## 1. machine-capability-match

The same machine profile is supplied, but the requirements associated with an unexplained revision C are unknown. Do not assume revision B capability comparisons apply to an untraced output revision; actual applicability and OEM evidence remain unverified.

## 2. cnc-setup-planner

Stock, orientation, G54 and setup-1 still come from the revision-B job context. No change-impact or setup applicability evidence links them to C. Datum, fixture, initial-position and stock/feature gaps remain unresolved.

## 3. tooling-plan-review

T1 matches numerically, but there is no controlled change record establishing that the revision-C artifact uses the intended revision-B tooling plan. Keep tool provenance, geometry/availability and numbering review open.

## 4. toolpath-strategy-planner

Source CAD A remains unchanged, and the rectangle still does not establish full feature coverage. An unexplained output revision cannot supply a new strategy or acceptance requirement; require controlled design/CAM lineage and intent.

## 5. postprocessor-readiness-review

Machine/controller/post names match, but post version 1.0 and synthetic validation do not trace generation of an output labeled C. Require actual CAM version, source/job revision and posted-output evidence, not just matching target labels.

## 6. nc-static-safety-review

Raw findings explicitly report program revision does not match job revision, adding MISSING_CONTEXT. Handoff preserves job B and CAD A while observations retain header C; it does not silently change either identity. Hash/fingerprint identity does not resolve the semantic mismatch.

## 7. simulation-readiness-review

No simulation exists, and any later result must bind the corrected exact NC and intended design/job/setup revision chain. A revision-B result cannot simply be relabeled C. Qualified design/CAM and manufacturing review remains required.

## Handoff and reviewer action

Ask the design/CAM authority which job/output revision is intended, trace the generation chain, reconcile controlled inputs and regenerate/review as needed; preserve the conflict instead of relabeling to pass. The [state](state.json) and [handoff](handoff.json) retain original unverified profiles, job B, linked CAD A, submitted units, actual artifact hash, unresolved assumptions and no approval. The handoff combines specific static findings with shared context/source/simulation/human blockers; composed routing alone does not identify every program mutation because context prerequisites stop it earlier.

These findings concern supplied synthetic file/context evidence and the repository's review contract, not new OEM, material or process claims. No machine, interpreter or simulator was run, no input was repaired, and no manufacturing parameters were generated. Review outcome remains non-executable; gate 04 and independent evaluation remain open.
