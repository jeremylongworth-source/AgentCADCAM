# CNC Milling Evaluation Plan

## Scope

This evaluation covers three-axis planning and static NC review against explicit synthetic machine, controller, setup, tooling, postprocessor, and job contexts. It does not execute NC, prove machine behavior, or replace CAMotics, LinuxCNC, machine simulation, or qualified operator review.

## Acceptance matrix

| Case | Expected result |
| --- | --- |
| Positive NC with matching identity, G21, G54, T1, and bounded coordinates | Block only on `SIMULATION_REQUIRED` and `HUMAN_APPROVAL_REQUIRED` |
| Wrong units | `MISSING_CONTEXT` |
| Wrong post | `SOURCE_VERIFICATION_REQUIRED` |
| Wrong controller | `MACHINE_CONTEXT_REQUIRED` |
| Missing WCS | `MISSING_CONTEXT` |
| Unknown or incorrect tool | `MISSING_CONTEXT` |
| Revision mismatch | `MISSING_CONTEXT` |
| Machine-limit conflict | `MACHINE_CONTEXT_REQUIRED` |
| Unverified post validation | `SOURCE_VERIFICATION_REQUIRED` |
| Missing tool context | `MISSING_CONTEXT` |

## Hard gates

- A static pass never sets `execution_allowed` to true.
- Simulation and human approval remain independent blockers.
- Machine/controller/post mismatches cannot be downgraded to warnings.
- The fixture contains no machine connector or execution path.

## Evidence status

The positive program and eight declared mutations, plus missing-tool and unverified-post checks, are exercised by the test suite. Real machine/controller compatibility and simulation remain external qualified-review responsibilities.

## Literal-word and modal-prerequisite follow-up — 2026-09-17

The first 19 new test methods reproduced 35 failing assertions/subtests in the old scanner, including skipped compact out-of-bounds coordinates, comment-supplied declarations, hidden unknown tools and modes supplied too late. The [replacement reader and its boundary](../architecture/nc-static-review-scope.md) inspect actual literal words and block order. Five additional test methods cover comment placement/extensions, delimiter errors, valid modal continuation, empty input and profile allowlists that cannot enable unimplemented semantics.

The focused suite passes 29 tests (five existing and 24 new methods). Positive controls retain only the existing simulation/human-approval blockers. Negative controls assert their specific added blocker, not merely a blocked status that the baseline already has. Unsupported syntax remains blocking even when caller declarations say simulation verified and approval approved. All inputs are inert synthetic text; no NC execution or independent controller run occurred.

This is partial Phase 3 evidence. The coordinate comparison remains a declared fixture bound check, not machine-space travel verification. Feed/spindle semantics, complete context/approval evidence binding, composed skill outputs, practical independent-tool evidence and the complete gate audit remain required work. The original acceptance matrix is not a production-readiness certificate.

Executed repository validation: `python -m unittest discover -s tests -q` passed all 281 tests in 46.222 seconds. Foundation validation passed (58 required files, ten context schemas, five skillsets); schema-instance validation passed (eleven definitions, 26 instances). The unchanged fixture CLI still reports only simulation and human-approval blockers, with review required and execution prohibited. `git diff --check` passed. These are local software checks, not machine or simulation evidence.
