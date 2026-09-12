---
name: drawing-pmi-handoff-review
description: Review drawing and model consistency, PMI availability, datums, tolerances, GD&T intent, revision identity, and manufacturing interpretation risks before CAD/CAM handoff.
metadata:
  short-description: Check drawing and PMI handoff integrity
---

# Drawing and PMI Handoff Review

Use this skill when a drawing, model-based definition, PMI set, or dimensioned handoff is part of the manufacturing package.

## Review

- Compare drawing/model identifiers, revisions, units, geometry, critical dimensions, material, finish, notes, and applicability.
- Identify datum references, tolerance zones, GD&T controls, inspection expectations, and whether the supplied representation preserves the stated intent.
- Flag missing or ambiguous PMI, conflicting dimensions, missing mating-part information, and drawing notes that cannot be traced to the authoritative definition.
- Separate nominal geometry from measurement data and distinguish design intent from manufacturing interpretation.
- Identify where qualified engineering, inspection, supplier, or regulatory review is required.

## Hard rules

- Do not reinterpret ambiguous GD&T or claim compliance from visual similarity.
- A drawing/model mismatch or revision conflict blocks a manufacturing handoff until resolved.
- Missing PMI does not imply no tolerance or datum intent exists.
- Return `REVIEW_REQUIRED` for every manufacturing-facing package.

## Output contract

Return a consistency matrix, PMI/datum/tolerance findings, revision and provenance findings, interpretation risks, missing reviewer inputs, severity, required corrections, and a bounded handoff recommendation.

## References

- `docs/architecture/master-taxonomy-v1.md`
- `docs/architecture/ip-and-provenance-model.md`
- `docs/standards/interoperability-standard.md`
