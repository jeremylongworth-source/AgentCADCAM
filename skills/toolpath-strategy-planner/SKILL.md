---
name: toolpath-strategy-planner
description: Recommend reviewable three-axis CNC milling strategies for roughing, finishing, contouring, drilling, entry/exit, and sequencing without inventing unsupported machine parameters.
metadata:
  version: "0.1.0"
  owner: "AgentCADCAM maintainers"
  supported-consequence-levels: "manufacturing_planning execution_adjacent"
  short-description: Plan CNC toolpath strategy
---

# Toolpath Strategy Planner

Use this skill to organize CAM strategy decisions after design, machine, setup, and tooling context are known enough for planning.

## Workflow

- Map features and stock condition to roughing, finishing, contouring, drilling, entry/exit, and sequencing strategies.
- Identify accessibility, engagement, chip evacuation, workholding, residual stock, and finish risks.
- Record the parameter inputs that must come from authoritative machine, tool, material, and CAM sources.
- Produce alternatives and tradeoffs where strategy depends on unresolved geometry or setup information.

## Hard rules

- Never invent feeds, speeds, stepovers, depths of cut, spindle speed, coolant, or material parameters.
- Missing authoritative process inputs return `SOURCE_VERIFICATION_REQUIRED` or `MISSING_CONTEXT`.
- A strategy recommendation is not a toolpath, simulation result, NC program, or approval.
- Return `REVIEW_REQUIRED` and identify the CAM programmer/manufacturing reviewer.

## Output contract

Return feature-to-strategy mapping, sequencing, assumptions, source requirements, alternatives, risks, blockers, and verification/simulation needs.
