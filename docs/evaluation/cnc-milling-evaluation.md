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
