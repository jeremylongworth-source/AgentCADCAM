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
| Missing PMI/datum/tolerance intent | Surface interpretation risk and require qualified review |
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

The [recorded positive report](../../fixtures/cad/bracket/expected/file-review.json) is actual CLI output for the checked-in revision-A fixture, retained as a regression expectation. It is deterministic tool evidence, not an agent skill-run evaluation, authenticated review, or a handoff-schema instance. Its three checks remain explicitly scoped and geometry equivalence remains false.

Tests copy the real fixture into isolated temporary directories and alter the SVG revision, units declaration and dimension text, OpenSCAD dimension assignment, or STEP/STL file contents. Missing/unreadable files, invalid manifest/metadata shapes, path escapes, and conflicting metadata design authority block the report. Production artifacts are neither read nor edited. `review_bundle` remains the metadata-only API; callers needing these file checks must use `review_fixture` or the CLI. The latter supports only the version-2 synthetic bracket contract and does not execute OpenSCAD.

Executed follow-up validation: nine new fixture-review tests pass; the complete portable suite passes 220 tests. Foundation validation passes (58 required files, nine context schemas, five skillsets), and schema-instance validation passes (ten definitions, thirteen instances). Native CAD checks were not rerun for this orchestration-only change.

### Remaining gate evidence

The source/drawing validator uses fixed revision-A numeric/text declarations, not a general OpenSCAD or SVG semantic parser. Extent checks alone miss stale derivatives with unchanged envelopes, and declaration checks do not detect every contradictory or hidden annotation. The follow-up below adds declared byte identity checks, not general PMI interpretation, unit conversion, arbitrary-model manufacturability review, or qualified reviewer authentication. Retained five-skill workflow outputs and the remaining semantic cases are still required before gate 03 can be accepted. Missing PMI remains an explicit interpretation risk in the prototype fixture, not proof of complete manufacturing intent.

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
| Missing PMI | Missing status field blocks; explicit `not_present` surfaces a review risk for the prototype. | Test missing required dimensional/datum/tolerance intent, not just a missing status field; retain the manufacturing-facing blocked output. |
| Conflicting dimensions | Actual source width and SVG dimension-text mutations block. | Evaluate conflicting visible dimensions even when expected text remains elsewhere; retain drawing/source interpretation evidence. |

These checks are required evidence components, not a percentage of gate completion. All positive and negative outputs must remain review-only and non-executable. Neither the tool snapshots nor green tests replace the five-skill workflow evaluation.
