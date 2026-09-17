# Phase 2 CAD handoff gate review — 2026-09-17

## Decision and audience

For maintainers deciding whether to proceed to Phase 3: the inspected evidence supports `CADCAM_03_DESIGN_HANDOFF_READY` for repository development against the initial CAD fixture family specified in [ROADMAP.md](../../ROADMAP.md#phase-2---core-cad-and-digital-handoff-skills). This is not public-alpha readiness, practitioner acceptance, or approval to manufacture. All six retained manufacturing handoffs are blocked; detecting those failures is the required outcome, not a failed development gate.

This review supersedes the earlier blanket synthetic gate claim with an explicit requirement map. The five added case packets use skill baseline `fbc1916`; the earlier manufacturing-intent packet records its own baseline. The evaluator and implementer are the same Codex agent. No independent model replay, blinded assessment or qualified human verdict is claimed.

## Required deliverables

| Roadmap deliverable | Inspected evidence and result |
| --- | --- |
| Intake: brief, inventory, workflow, missing context, consequence | Section 1 of the [baseline review](../evaluation/cad-runs/2026-09-17-manufacturing-intent/review.md) and each [negative review](../evaluation/cad-runs/negative-cases-protocol.md); identities retained in handoffs/observations. Manufacturing planning is distinguished from execution; unresolved process choice is not guessed. |
| Provenance: authority, revisions, derivatives, ownership/licensing, conflicts, traceability | Section 2 of the six reviews; source/derivative roles, exact hashes, synthetic IP limits, revision conflicts and unverified derivation truth are explicit. Mesh-only submitted authority becomes unknown, not an accepted design master. |
| Interoperability: format choice, semantic losses, transformation risks, verification | Section 3 of the baseline review distinguishes editable source, AP214 geometry exchange, STL mesh and reference drawing; the five follow-ups preserve those limits and specify corrections before conversion. Required receiver/process information remains a blocker where absent. |
| Manufacturability: feasibility, access, complexity, tolerance/process alignment, missing context | Section 4 of the baseline review groups function, geometry/access, tolerance, assembly, material/process, finish and inspection findings. Follow-ups explain the effect of each defect. Unknown feasibility is escalated, not replaced with invented parameters or an affirmative production verdict. |
| Drawing/PMI: consistency, availability, datums/tolerances, revisions, interpretation | Section 5 of all six reviews compares supplied definitions and records missing intent. The nominal base projection is not mistaken for complete upright-feature or inspection coverage; an adequate controlled alternative to embedded PMI is allowed but absent here. |
| Five-skill composition | [Manifest](../../skillsets/cadcam-design-handoff.yaml) lists the five named skills in roadmap order; six retained outputs apply that order. |
| Reproducible part and five artifact types | [Fixture](../../fixtures/cad/bracket/fixture.yaml) identifies editable OpenSCAD, STEP, STL, SVG drawing and revision metadata. The unchanged positive file report and the earlier native generator/round-trip probe support their stated, bounded checks. Reconstruction is not claimed to be direct OpenSCAD export. |
| All six negative mutations | [Packet index](../evaluation/cad-runs/README.md): revision mismatch, missing units, stale derivative, mesh-as-master, missing manufacturing PMI/intent, and conflicting dimensions. Five fixed replays compare actual observations with archived results; the sixth inspects missing intent in the actual nominal package. |

## Exit criteria and safety checks

| Required criterion | Observable acceptance and evidence | Finding |
| --- | --- | --- |
| CAD bundle operational | Given the fixture, the ordered bundle produces a brief, provenance/interoperability/DFM/drawing review and a state-bound, schema-valid handoff. All six packets retain these outputs; the unchanged file control remains review-required. | Met for the initial corpus; not an autonomous general-purpose CAD engine. |
| Source hierarchy respected | Given native and derivative inputs, identities/roles survive review. Given only STL claiming authority, the reviewer refuses promotion and requests the governing definition. Packet identity tests inspect both outcomes. | Met. Byte binding is not authenticated export history. |
| Revision mismatches detected | Given a B drawing with A source/metadata, actual drawing and inventory checks fail, and the handoff preserves A/B rather than relabeling either. | Met by the revision packet and replay regression. |
| Format semantics correctly distinguished | Given readable STEP/STL and nominal SVG, the reviews do not infer feature history, complete PMI, scale authority or manufacturing approval. The baseline explains AP214 versus a PMI deliverable; missing-unit and mesh-only cases refuse inference. | Met in inspected outputs; independent quality evaluation remains Phase 8 work. |
| Negative fixtures correctly blocked | Given each named mutation, the final handoff has blockers, unresolved findings, no approval ID, review required and execution prohibited. Tests reproduce five input/checker pairs, validate all six state/handoff pairs and reject approval promotion. | Met for all six named cases, not a universal safety-recall claim. |
| No silent mesh-equals-intent assumption | Given mesh-only input, review requests missing authoritative definition, tolerance/datum, interface, material/process and inspection intent. Passing the mesh envelope does not remove blockers. | Met by the mesh-only and manufacturing-intent packets. |

No criterion permits machine control. Qualified engineering/inspection review remains necessary for actual manufacturing decisions. Synthetic public/IP/export declarations cannot authorize use or disclosure of external files. Missing consequential evidence is blocking rather than a score deduction.

## Validation and limits

The focused seven-test negative-packet suite passes. Schema-instance validation passes for 11 definitions and 26 instances; foundation validation passes for 58 required files, 10 context schemas and five skillsets. Full-suite evidence is recorded in the accompanying [evaluation follow-up](../evaluation/cad-handoff-evaluation.md#six-case-retention-and-gate-review--2026-09-17).

The native probe result belongs to the earlier baseline packet; it was not rerun on these mutations. The four file checks are restricted declarations/projections, exchange envelopes and declared byte association. They do not prove general topology, conversion equivalence, arbitrary PMI interpretation, process feasibility or supplied evidence authenticity. The model-authored reviews, not those checkers alone, establish the retained missing-intent decisions. Record-integrity tests do not independently grade reasoning.

Independent practitioner usefulness, baseline comparison, reviewer edit burden, real inputs and human pilot verdicts are required later, not satisfied here. Broader geometry/package and process checks remain in Phases 3–7. These are retained roadmap obligations, not removed requirements or optional substitutes.

Reopen this gate if the governing CAD skill contracts or source hierarchy change, supported format/fixture scope expands, evidence identities drift, or a consequential false-ready counterexample appears. Preserve old packets and perform a new applicable review rather than rewriting historical evidence to fit new bytes. Next: Phase 3 CNC artifact checks and retained workflow evidence.
