---
name: file-format-interoperability-plan
description: Choose and review CAD/CAM exchange formats by workflow, units, revision, and semantic fidelity, documenting transformations, likely information loss, and verification requirements.
metadata:
  short-description: Plan safe CAD/CAM file exchange
---

# File Format Interoperability Plan

Use this skill when a design or manufacturing job must cross file formats or software boundaries.

## Workflow

1. Identify the authoritative source and target workflow.
2. Select a candidate format using the registry in `docs/formats/format-registry.md`.
3. Record units, scale, revision, representation type, and intended semantics.
4. Separate what the format preserves from what it commonly loses: feature history, PMI, GD&T, material, tolerances, assembly constraints, toolpath intent, or process metadata.
5. Define transformation steps and independent verification for geometry, units, topology, PMI, revision, and manufacturing meaning.

## Hard rules

- Parseability is not geometric fidelity; geometric fidelity is not semantic fidelity; semantic fidelity is not manufacturing approval.
- STL is a geometry derivative and must not be treated as a complete product definition.
- Do not recommend a format as suitable merely because a target application can open it.
- Unverified conversion, conflicting units, or lost critical semantics returns `SOURCE_VERIFICATION_REQUIRED` or `MISSING_CONTEXT`.

## Output contract

Return source/target format, workflow purpose, preserved semantics, likely losses, unit and revision controls, transformation plan, verification checklist, blockers, and `REVIEW_REQUIRED` status when the result may influence manufacture.

## References

- `docs/formats/format-registry.md`
- `docs/standards/interoperability-standard.md`
- `docs/architecture/execution-boundary.md`
