---
name: design-file-provenance-review
description: Review CAD, drawing, mesh, and manufacturing artifacts for authoritative source identity, revision consistency, derivative traceability, ownership, licensing, confidentiality, and export-review gaps.
metadata:
  short-description: Verify design artifact provenance
---

# Design File Provenance Review

Use this skill when a job contains multiple design or manufacturing artifacts, derived exports, revision claims, or uncertain authorization.

## Review

- Identify the authoritative product definition and distinguish it from STEP, IGES, STL, 3MF, DXF, SVG, NC, G-code, screenshots, and measured/prototype derivatives.
- Compare revision identifiers, file timestamps when relevant, hashes, units, and declared applicability across the bundle.
- Trace each derivative to its source and record transformations that may lose design intent, PMI, tolerances, or material information.
- Check ownership, licence status, confidentiality, third-party restrictions, redistribution authorization, and export-review status.
- Report conflicting, stale, unauthorized, or unexplained artifacts as blockers when they could affect manufacture or disclosure.

## Hard rules

- Possession of a file does not imply authorization to manufacture, modify, publish, or redistribute it.
- A mesh cannot silently become the design master.
- Conflicting revisions return `MISSING_CONTEXT` or `BLOCK_EXECUTION` when the output is execution-adjacent.
- Never expose confidential or export-sensitive source data in a public report or fixture.

## Output contract

Return an artifact authority table, revision/derivative trace, IP and confidentiality findings, evidence references, severity (`blocker`, `high`, `medium`, `low`), required corrections, and `REVIEW_REQUIRED` status. State whether the bundle can proceed to interoperability or DFM review.

## References

- `docs/architecture/ip-and-provenance-model.md`
- `docs/standards/research-and-evidence-standard.md`
- `docs/standards/interoperability-standard.md`
