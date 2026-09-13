---
name: nc-static-safety-review
description: Inspect CNC NC/G-code text for units, modal and coordinate assumptions, unsupported commands, tool references, offsets, spindle/coolant commands, suspicious motion, and machine/controller mismatches.
metadata:
  version: "0.1.0"
  owner: "AgentCADCAM maintainers"
  supported-consequence-levels: "execution_adjacent"
  short-description: Perform static CNC NC review
---

# NC Static Safety Review

Use this skill for static inspection of an NC artifact against explicit machine, controller, setup, tool, and post context.

## Review

- Identify dialect, units, coordinate/WCS assumptions, tool changes, offsets, modes, canned cycles, and unsupported commands.
- Check coordinate extents against explicit machine limits and setup envelope.
- Reconcile tool numbers with the declared tool library and postprocessor/controller identity.
- Flag spindle, coolant, rapid, probing, and other consequential commands for human review; static inspection does not prove safe operation.
- Preserve program hash, source job revision, post identity, and review findings.

## Hard rules

- Missing machine, controller, setup/WCS, tooling, post, or verification context blocks readiness as applicable.
- Unknown commands, units, modal state, offsets, or tool references are not guessed.
- Suspicious motion or a limit conflict returns a blocking outcome.
- Static review cannot approve physical execution and must return `REVIEW_REQUIRED`.

## Output contract

Return artifact identity, parsed findings, context reconciliation, severity, blockers, simulation requirement, reviewer checklist, and approval status. Never upload or execute the program.
