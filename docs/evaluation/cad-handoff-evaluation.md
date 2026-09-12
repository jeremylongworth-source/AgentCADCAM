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

Fixture contracts, expected negative outcomes, a deterministic metadata behavior harness, and generated STEP/STL exchange fixtures are present. Lightweight envelope and extent checks pass; a geometry-kernel or independent CAD validation review is still required before `CADCAM_03_DESIGN_HANDOFF_READY` can be claimed.
