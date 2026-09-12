---
name: cad-manufacturability-review
description: Review CAD and drawing handoff information for basic process feasibility, feature accessibility, geometry complexity, tolerance/process alignment, assembly interfaces, material assumptions, and missing manufacturing context.
metadata:
  short-description: Triage CAD manufacturability gaps
---

# CAD Manufacturability Review

Use this skill for process-neutral DFM triage after intake and provenance are established. Route detailed molded-part, elastomer, tooling, or process-specific concerns to the appropriate specialization.

## Review areas

- Model integrity: solid/mesh status, missing features, broken surfaces, non-manifold geometry, slivers, gaps, duplicate bodies, and ambiguous bodies.
- Geometry and access: thin features, sharp internal corners, deep pockets, inaccessible holes, undercuts, and tool or process access assumptions.
- Function and assembly: mating parts, clearances, fastener/insert assumptions, seals, clips, hinges, connectors, serviceability, and tolerance-stack risks.
- Tolerance and inspection: critical-to-function dimensions, datums, general tolerance basis, inspection method, cosmetic surfaces, finish, and acceptance criteria.
- Material and process: stated material/grade, target process, volume, finish, and whether claims require authoritative evidence.

## Hard rules

- Do not declare a part production-ready, tool-ready, dimensionally correct, or safe solely from file readability or checklist completion.
- Do not invent wall thickness, tolerance, feeds, speeds, material grade, or process capability.
- Missing mating interfaces, critical dimensions, datums, material, or process context must remain visible and can block the handoff.
- Use `REVIEW_REQUIRED` before tooling, ordering, production, or regulated use.

## Output contract

Return artifact/process assumptions, findings grouped by function, geometry, tolerance, assembly, material, finish, and inspection; severity; missing inputs; selected downstream specialization; supplier/reviewer questions; blockers; and review status.

## References

- Apply the CAD DFM checklist from the repository’s architecture and interoperability standards.
- Route molded-part concerns to the relevant specialization only when its process assumptions are explicit.
