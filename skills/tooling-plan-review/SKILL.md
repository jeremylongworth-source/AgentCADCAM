---
name: tooling-plan-review
description: Review a CNC milling tooling plan for tool identity, holder, geometry, reach, availability, compatibility, numbering, and traceability to an explicit tool library.
metadata:
  short-description: Review CNC tooling context
---

# Tooling Plan Review

Use this skill when a CNC milling plan references cutting tools, holders, tool numbers, or reach-sensitive operations.

## Review

- Confirm each tool has an identity, tool number, geometry, holder, reach, availability, and source or library revision.
- Compare tool diameter, length, flute/cutter form, holder clearance, and reach with the planned feature and setup.
- Check numbering consistency across tool library, CAM plan, setup sheet, and NC artifact.
- Surface unsupported or unavailable tool assumptions and request supplier/operator confirmation when consequential.

## Hard rules

- Unknown, duplicated, or incorrect tool numbers block NC readiness where the tool reference is consequential.
- Do not fabricate tool geometry, reach, material, feeds, speeds, or availability.
- Tool presence does not prove correct toolpath, holder clearance, or safe cutting.
- Return `REVIEW_REQUIRED` for every manufacturing-facing plan.

## Output contract

Return a tooling table, compatibility findings, numbering reconciliation, missing evidence, severity, blockers, and required human/tooling review.
