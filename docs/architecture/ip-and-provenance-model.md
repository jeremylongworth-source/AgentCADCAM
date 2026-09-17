# IP and Provenance Model

## Purpose

Manufacturing decisions must be traceable to an authorized source and controlled revision. Possession of a file does not imply permission to manufacture, modify, publish, or redistribute it.

## Required status fields

Job context should preserve:

```yaml
ownership_status: unknown | owned | licensed | third_party | disputed
licence_status: unknown | permitted | restricted | expired | disputed
confidentiality: public | internal | confidential | restricted | unknown
third_party_restrictions: []
redistribution_authorized: true | false | unknown
export_review_status: unknown | not_required | review_required | reviewed | blocked
```

## Provenance rules

- Identify the source authority, revision, path or locator, hash, units, and derivative relationship for each artifact.
- Keep authoritative design files distinct from derived STEP, IGES, STL, 3MF, DXF, SVG, NC, and G-code outputs.
- Conflicting revisions or unexplained derivatives produce a blocking provenance finding.
- Do not place confidential or export-sensitive source material in public fixtures, examples, tests, or telemetry.
- A handoff must preserve enough provenance for a reviewer to reproduce the artifact identity without exposing restricted content.

## Validation notes

The shared artifact and source structures are defined in `contexts/schemas/handoff.schema.json`. The [governance readiness contract](governance-readiness.md) now blocks unresolved source/export declarations during planning and handoff review. Draft state remains permissive; declaration consistency is not authenticated permission or jurisdiction-specific legal clearance.
