---
name: cnc-setup-planner
description: Prepare a reviewable three-axis CNC setup plan covering stock, orientation, workholding, work coordinate system, setup sequence, access, and verification requirements.
metadata:
  version: "0.1.0"
  owner: "AgentCADCAM maintainers"
  supported-consequence-levels: "manufacturing_planning execution_adjacent"
  short-description: Plan a reviewable CNC setup
---

# CNC Setup Planner

Use this skill when a CNC milling job needs a bounded setup and WCS plan before toolpath or NC review.

## Workflow

- State stock material and dimensions, datum/orientation assumptions, setup sequence, workholding, accessible faces, and re-fixturing risks.
- Define the WCS location, axes, offsets, and how the datum will be established and verified.
- Identify fixture/clamp collision risks, unsupported stock, tool access limits, and any required probing or manual measurement.
- Separate stated facts from assumptions and ask for missing fixture or mating geometry.

## Hard rules

- Missing, conflicting, or unverified WCS is a blocker for execution-adjacent NC readiness.
- Do not invent stock, fixture, clamp, datum, probing, or repeatability details.
- Do not assume a vise, clamps, or sacrificial material are available.
- No setup plan authorizes machine operation; return `REVIEW_REQUIRED`.

## Output contract

Return setup sequence, stock and workholding assumptions, WCS definition and verification method, access/collision risks, missing context, blockers, and reviewer questions.
