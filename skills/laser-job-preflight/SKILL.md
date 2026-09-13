---
name: laser-job-preflight
description: Preflight a laser-cutting job for DXF/SVG units, scaling, contour closure, duplicate or unsupported geometry, material and machine compatibility, process profile readiness, ventilation, and human approval.
metadata:
  version: "0.1.0"
  owner: "AgentCADCAM maintainers"
  supported-consequence-levels: "manufacturing_planning execution_adjacent"
  short-description: Preflight a laser-cutting job
---

# Laser Job Preflight

Use this skill for 2D laser-cutting preparation before handing a file to an operator.

## Review

- Identify the authoritative 2D source, format, units, scale, revision, layers, path intent, and contour geometry.
- Check closed contours, duplicate paths, unsupported entities, open geometry, and source/derivative consistency.
- Match explicit machine, material, process profile, kerf/setting evidence, and ventilation/fume context.
- Separate cut/score/mark intent from geometry and require human confirmation of material safety.

## Hard rules

- Unknown or unsafe material cannot receive manufacturing-ready status.
- Do not guess laser power, speed, frequency, kerf, focus, or material settings.
- Open/duplicate/unsupported geometry, wrong units/scale, or machine/material mismatch blocks readiness.
- Beam and process-emission risks are independent findings.
- Preflight never activates a laser and returns `REVIEW_REQUIRED` and `HUMAN_APPROVAL_REQUIRED` before cutting.

## Output contract

Return source/format findings, units and scale, contour validation, path intent, machine/material/process compatibility, ventilation and fume findings, blockers, reviewer actions, and approval status.
