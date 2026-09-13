---
name: machine-capability-match
description: Compare CNC milling requirements against an explicit three-axis machine profile, including travel, envelope, spindle capability, axis configuration, and process suitability.
metadata:
  version: "0.1.0"
  owner: "AgentCADCAM maintainers"
  supported-consequence-levels: "manufacturing_planning execution_adjacent"
  short-description: Match a job to a CNC machine
---

# Machine Capability Match

Use this skill when a CNC milling job must be assessed against a named, sourced machine profile.

## Review

- Confirm the process is three-axis milling and identify part envelope, stock envelope, access, required spindle/tool capability, and expected operations.
- Compare requirements with explicit machine travel, work envelope, axis configuration, spindle limits, tooling interface, and documented process limits.
- Distinguish a missing profile, unknown limit, and known incompatibility.
- Identify whether a machine-specific manual or OEM source is required to resolve a consequential claim.

## Hard rules

- Never infer machine capability from a model name, generic category, or nominal travel claim.
- A missing or conflicting machine profile returns `MACHINE_CONTEXT_REQUIRED`.
- A known envelope, axis, spindle, or process conflict blocks the plan.
- This skill does not connect to, configure, jog, or start a machine.

## Output contract

Return requirements, machine evidence, comparison matrix, gaps, severity, blockers, alternate review path, and `REVIEW_REQUIRED` status. A match is a planning finding, not permission to run a job.
