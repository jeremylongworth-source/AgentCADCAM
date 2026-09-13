---
name: simulation-readiness-review
description: Determine the required simulation and verification level for a three-axis CNC job, including machine model, fixture geometry, tooling, post validation, and unverified NC assumptions.
metadata:
  version: "0.1.0"
  owner: "AgentCADCAM maintainers"
  supported-consequence-levels: "manufacturing_planning execution_adjacent"
  short-description: Gate CNC simulation readiness
---

# Simulation Readiness Review

Use this skill before any execution-adjacent CNC handoff where toolpath or NC behavior could cause harm, scrap, collision, or machine damage.

## Review

- Identify whether the required check is static parsing, kinematic simulation, material-removal simulation, machine simulation, or qualified dry-run/verification.
- Confirm availability and revision of machine model, stock, fixture/workholding geometry, tool/holder geometry, postprocessor output, and NC artifact.
- Separate simulated evidence from assumptions and state what simulation cannot establish.
- Define the reviewer’s required checks and unresolved conditions before approval.

## Hard rules

- Missing simulation evidence where consequential returns `SIMULATION_REQUIRED`.
- A simulation using the wrong machine, controller, post, fixture, tool, stock, or revision does not satisfy the gate.
- Simulation success never authorizes machine execution by itself.
- Return `HUMAN_APPROVAL_REQUIRED` and `REVIEW_REQUIRED` for execution-adjacent output.

## Output contract

Return required simulation level, available evidence, mismatches, remaining assumptions, blockers, human-review actions, and approval scope.
