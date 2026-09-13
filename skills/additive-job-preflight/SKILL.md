---
name: additive-job-preflight
description: Preflight an FDM additive job for STL/3MF provenance, mesh integrity, printer and material profile compatibility, build volume, orientation/support needs, slicer readiness, and environmental safety context.
metadata:
  version: "0.1.0"
  owner: "AgentCADCAM maintainers"
  supported-consequence-levels: "manufacturing_planning execution_adjacent"
  short-description: Preflight an FDM print job
---

# Additive Job Preflight

Use this skill for FDM additive preparation before slicing or handing a package to an operator.

## Review

- Identify the authoritative design source and distinguish STL/3MF print derivatives from complete product intent.
- Check mesh integrity status, units/scale, model dimensions, build volume, orientation, support needs, and package revision.
- Match an explicit printer profile, material identity/grade, and slicer profile; record missing or conflicting compatibility data.
- Check environmental, ventilation, thermal, material-handling, and operator-safety context appropriate to the stated material and printer.

## Hard rules

- Never invent material, printer, slicer, temperature, cooling, or support parameters.
- Non-manifold or otherwise invalid mesh status blocks print readiness.
- Unknown or incompatible printer/material/profile/environment context blocks manufacturing-ready status.
- STL/3MF geometry does not replace design intent, PMI, tolerances, or authorization.
- Return `REVIEW_REQUIRED` and `HUMAN_APPROVAL_REQUIRED` before printing.

## Output contract

Return artifact/provenance findings, mesh and scale status, printer/material/profile compatibility, orientation/support considerations, environmental checks, blockers, required reviewer actions, and approval state.
