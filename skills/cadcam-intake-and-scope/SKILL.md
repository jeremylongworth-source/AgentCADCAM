---
name: cadcam-intake-and-scope
description: Turn a CAD/CAM manufacturing request and supplied artifacts into a bounded job brief, workflow classification, artifact inventory, missing-context report, and consequence level.
metadata:
  version: "0.1.0"
  owner: "AgentCADCAM maintainers"
  supported-consequence-levels: "informational design_advisory manufacturing_planning execution_adjacent"
  short-description: Bound a CAD/CAM job before review
---

# CAD/CAM Intake and Scope

Use this skill at the start of a CAD/CAM request, before making process or manufacturing claims.

## Workflow

1. Identify the requested outcome, user, current stage, target process, expected volume, and jurisdiction if relevant.
2. Inventory every supplied artifact and record kind, path/locator, revision, units, authority, derivative relationship, and hash when available.
3. Select exactly one initial process family: `cad_handoff`, `cnc_milling`, `additive`, `laser_cutting`, or `unknown`.
4. Classify consequence as `informational`, `design_advisory`, `manufacturing_planning`, `execution_adjacent`, or `live_execution`.
5. Separate known, missing, conflicting, and unverified context.
6. Route to the narrowest next skill or return a blocking outcome.

## Hard rules

- A request to jog, upload, start, activate, or control physical equipment returns `BLOCK_EXECUTION`.
- Do not treat a supplied file as authorized for manufacture or redistribution without provenance and IP status.
- Do not infer units, revision, material, machine, controller, or process from filename or file extension.
- Execution-adjacent work defaults to `REVIEW_REQUIRED`.

## Output contract

Return a job brief containing: goal, stage, process family, artifact inventory, known context, missing/conflicting context, consequence level, selected next skillset, blockers, and reviewer questions. Use explicit outcomes such as `MISSING_CONTEXT`, `SOURCE_VERIFICATION_REQUIRED`, `HUMAN_APPROVAL_REQUIRED`, and `BLOCK_EXECUTION`.

## References

- Apply `docs/architecture/domain-contract.md` and `docs/architecture/consequence-model.md`.
- Preserve fields required by `contexts/schemas/job.schema.json` and `contexts/schemas/handoff.schema.json`.
