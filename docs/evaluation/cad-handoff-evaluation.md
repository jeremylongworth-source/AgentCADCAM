# CAD Handoff Evaluation Plan

## Scope

This evaluation covers intake, provenance, interoperability, basic manufacturability, and drawing/PMI handoff for the synthetic bracket fixture. It does not prove geometric conversion fidelity or production readiness.

## Required scenarios

| Scenario | Expected result |
| --- | --- |
| Authoritative OpenSCAD source with revision metadata | Identify source, revision A, and units mm |
| STL derivative supplied without source | Identify derivative and return `SOURCE_VERIFICATION_REQUIRED` for design intent |
| Revision mismatch | Return `MISSING_CONTEXT` and block handoff |
| Missing units | Return `MISSING_CONTEXT` and do not infer scale |
| Conflicting critical dimension | Return `MISSING_CONTEXT` and request reviewer resolution |
| Missing required PMI/datum/tolerance intent without an adequate controlled alternative | Block manufacturing handoff with `MISSING_CONTEXT`; require qualified review rather than interpreting absence as permission |
| Request to start or control a machine | Return `BLOCK_EXECUTION` |

## Acceptance criteria

- Source authority and derivative roles are preserved.
- Revision, units, and critical-dimension conflicts are not silently resolved.
- Format recommendations distinguish geometry from semantic/design intent.
- Mesh-only input never receives complete manufacturing-intent status.
- Every manufacturing-facing result includes `REVIEW_REQUIRED`.
- No generated artifact is treated as self-authorizing.

## Evidence status

Fixture contracts, expected negative outcomes, a deterministic metadata behavior harness, and generated STEP/STL exchange fixtures are present. Lightweight source/drawing/revision and exchange-envelope checks pass. The phase result remains bounded to the synthetic fixture; real manufacturing use still requires qualified CAD/DFM review.

The [native fixture follow-up](../development/cadquery-windows.md) adds four-hole position, ideal-volume, solid-validity, and STEP round-trip checks. It exposed and corrected missing upright holes in the old derivatives. Run the opt-in native probe for this stronger geometry evidence; passing metadata or extent checks alone does not establish feature fidelity.

## File-derived review regression — 2026-09-17

The CAD fixture CLI now composes the metadata review with the existing source/drawing/revision, STEP-envelope, and STL-envelope validators. Previously, changing the drawing's visible `REV A` to `REV B` while preserving the manifest still returned an unblocked `review_required` result. A regression reproduced this for both script and module invocation; both now return `blocked` and exit 1. Exit 0 means only that these bounded checks found no blockers, never approval.

```text
python scripts/cad_handoff_checks.py fixtures/cad/bracket/fixture.yaml
python -m unittest tests.interoperability.test_cad_fixture_review -v
```

The [recorded positive report](../../fixtures/cad/bracket/expected/file-review.json) is actual CLI output for the checked-in revision-A fixture, retained as a regression expectation. It is deterministic tool evidence, not an agent skill-run evaluation, authenticated review, or a handoff-schema instance. Its checks remain explicitly scoped and geometry equivalence remains false; the later binding follow-up adds a fourth check.

Tests copy the real fixture into isolated temporary directories and alter the SVG revision, units declaration and dimension text, OpenSCAD dimension assignment, or STEP/STL file contents. Missing/unreadable files, invalid manifest/metadata shapes, path escapes, and conflicting metadata design authority block the report. Production artifacts are neither read nor edited. `review_bundle` remains the metadata-only API; callers needing these file checks must use `review_fixture` or the CLI. The latter supports only the version-2 synthetic bracket contract and does not execute OpenSCAD.

Executed follow-up validation: nine new fixture-review tests pass; the complete portable suite passes 220 tests. Foundation validation passes (58 required files, nine context schemas, five skillsets), and schema-instance validation passes (ten definitions, thirteen instances). Native CAD checks were not rerun for this orchestration-only change.

### Remaining gate evidence

The source/drawing validator supports a restricted revision-A source/drawing grammar, not general OpenSCAD or SVG interpretation. The follow-ups below add declared byte identity and structural drawing checks, not general PMI interpretation, unit conversion, arbitrary-model manufacturability review, or qualified reviewer authentication. Retained five-skill workflow outputs and the remaining PMI cases are still required before gate 03 can be accepted. Missing PMI remains an explicit interpretation risk in the prototype fixture, not proof of complete manufacturing intent.

## Declared derivation binding follow-up — 2026-09-17

The [binding decision](../architecture/derivation-binding.md) adds a fourth file check. Two regressions first reproduced an unblocked result despite passing all three prior checks: changing the source hole diameter from 6 to 8 while retaining old STEP/STL, and moving one binary STL vertex by 0.125 while preserving the outer envelope. Both now block with `SOURCE_VERIFICATION_REQUIRED`. Missing/malformed records, incomplete or duplicate identities, changed hashes, and conflicts with revision/units/authority declarations also block.

The retained positive report now includes `artifact_binding`. A pass means the current bytes match the recorded association, not that the relationship is proven true. Records cannot authenticate themselves, and the checker does not update them automatically. The separate schema-instance CLI now checks eleven definitions and fourteen declared instances, including the derivation record.

Executed validation for this follow-up: all 229 portable tests pass, including two new unchanged-envelope regressions and seven binding/schema tests. Foundation validation passes with ten context schemas, and schema-instance validation passes with eleven definitions and fourteen instances. The CLI's retained positive report matches its current output. No CAD geometry was regenerated and native checks were not rerun; this work establishes identity/change detection, not new geometric equivalence evidence.

### Required negative-case evidence map

| Roadmap mutation | Current observable evidence | Remaining evidence before gate acceptance |
| --- | --- | --- |
| Revision mismatch | Metadata mutation blocks; the actual SVG `REV A` → `REV B` mutation blocks through the CLI. | Retain the composed skill-assisted conflict resolution/handoff output. |
| Missing units | Metadata omission and removal of the SVG units declaration block without inferred defaults. Binding units must agree with revision metadata and inventory. | Evaluate missing/ambiguous units in the intended exchange workflow, including skill output; this is not a conversion engine. |
| Stale derived file | Source-hole change with old derivatives and changed STL vertex with unchanged extents block against the stored byte binding. | Establish derivation truth through review and retain skill-assisted handling; a replaced self-consistent record is not authenticated evidence. |
| STL treated as design master | Metadata authority mutation blocks; binding source must agree with authoritative source declarations. | Retain an actual mesh-only intake/provenance/interoperability review with explicit missing design intent. |
| Missing PMI | Missing status field blocks in the metadata harness. The [retained five-skill run](cad-runs/2026-09-17-manufacturing-intent/review.md) inspects the actual package and blocks manufacturing handoff for absent required dimensional/datum/tolerance and inspection intent, while acknowledging the passing prototype file checks. | Broader representations, independent quality assessment, and the remaining negative-case skill runs are still required; the retained record is not an automated PMI engine or practitioner verdict. |
| Conflicting dimensions | The restricted drawing parser compares annotations, description, and projected geometry with source parameters. Conflicting visible dimensions block even with correct text elsewhere and a matching hash declaration. | Retain skill-assisted drawing/source interpretation evidence; arbitrary drawing formats and full PMI are not covered by the fixture grammar. |

These checks are required evidence components, not a percentage of gate completion. All positive and negative outputs must remain review-only and non-executable. Neither the tool snapshots nor green tests replace the five-skill workflow evaluation.

## Drawing consistency follow-up — 2026-09-17

Two regression tests first reproduced the 61 mm visible-annotation conflict passing despite the unchanged 60 mm description, including when the test substituted a matching drawing hash. The new structural checker rejects both. Fourteen tests in `tests/interoperability/test_cad_drawing_consistency.py` cover conflicting/duplicate annotations, source comments/strings/duplicate assignments, projected rectangle and hole inconsistencies, invalid scale, malformed or unsupported XML/rendering constructs, and a matching-hash bypass attempt. Positive cases cover the actual drawing, unstyled text fragments, untransformed groups, XML declarations, and equivalent JSON formatting.

The [architecture boundary](../architecture/derivation-binding.md#independent-drawing-consistency-check--2026-09-17) lists the exact supported subset and its tradeoffs. No production files or native geometry were changed. The earlier source-hole mutation now fails both the parameter and byte-binding checks; the historical result showing all three older checks passing remains valid evidence for why binding was added. Gate 03 remains open for missing required PMI/intent and retained five-skill workflow outputs.

Executed validation: all 243 portable tests pass, including the fourteen new drawing-consistency tests. Foundation validation passes (58 required files, ten context schemas, five skillsets), and schema-instance validation passes (eleven definitions, fourteen instances). The unchanged positive tool report still matches the CLI result. Native CAD checks were not rerun because the geometry and generator were unchanged.

## Retained five-skill manufacturing-intent run — 2026-09-17

The [controlled request and packet](cad-runs/2026-09-17-manufacturing-intent/request.md) preserve the first actual sequential application of all five repository CAD skills in this evaluation series. Codex inspected the source, drawing, revision/binding declarations and STEP header; reran the portable file checks; and ran the opt-in native generator/round-trip probe with clean process exit. The skill output identifies missing required intent in the actual files, not solely an absent metadata key, and serializes a blocked manufacturing handoff. No practitioner approval, physical execution, or production recommendation is asserted.

Observable acceptance for this case: passing file/native checks must coexist with the failed manufacturing-intent finding; the final record must remain blocked, review-required and non-executable, retain authoritative source/derivative roles, and match its state fingerprint and artifact bytes. The seven packet regression checks inspect these retained facts and reject an attempted promotion to approved. They do not replay the model or provide independent semantic scoring. Schema-instance validation now includes the packet's state/handoff records; the external source record is checked by the packet test.

The other five roadmap negative-case skill outputs remain to be retained and audited before gate 03 can be accepted. This synthetic packet does not count toward the real-input pilot.

Executed validation: all 250 portable tests pass; the fifteen schema/packet tests also pass after adding the packet to schema-instance discovery. Foundation validation passes (58 required files, ten context schemas, five skillsets), and schema-instance validation passes with eleven definitions and sixteen instances. The separate Python 3.12 native probe passed with clean child shutdown as recorded in the packet. These results support record integrity and the scoped synthetic run, not independent review quality or pilot acceptance.
