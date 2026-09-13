---
name: postprocessor-readiness-review
description: Verify the identity and validation state of the CAM system, machine, controller, postprocessor, and post version before treating CNC NC output as reviewable for a target machine.
metadata:
  version: "0.1.0"
  owner: "AgentCADCAM maintainers"
  supported-consequence-levels: "manufacturing_planning execution_adjacent"
  short-description: Check CNC postprocessor readiness
---

# Postprocessor Readiness Review

Use this skill when a CAM job or NC artifact is associated with a machine/controller target.

## Review

- Identify CAM system/version, machine profile, controller model/version, postprocessor identity/version, and validation evidence.
- Compare the target machine/controller with the post’s declared applicability and output dialect.
- Check units, coordinate conventions, offsets, tool changes, canned cycles, spindle/coolant commands, and modal assumptions at the contract level.
- Record whether the post was tested on a representative simulator, controller test environment, or qualified review process.

## Hard rules

- Machine, controller, post, or version mismatch is blocking.
- Unknown or unverified post validation returns `SOURCE_VERIFICATION_REQUIRED` and `HUMAN_APPROVAL_REQUIRED`.
- Do not modify or deploy a postprocessor autonomously.
- A correct post identity does not prove safe NC motion; static review and simulation remain separate gates.

## Output contract

Return an identity matrix, applicability evidence, mismatch findings, validation state, blockers, required simulation, and explicit `REVIEW_REQUIRED` status.
