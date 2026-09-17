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

## Feed/spindle and numeric-context follow-up — 2026-09-17

The first 17 new test methods failed before implementation (39 failing assertions/subtests and two numeric-context exceptions). They covered unsupported new explicit modes as well as missing F/S checks and malformed coordinate bounds. Five further methods cover controller-unit support, malformed job units, unknown initial spindle state, malformed numeric containers and input immutability. These add 22 methods to the 29 existing CNC checks.

The [scope decision](../architecture/nc-static-review-scope.md#feed-spindle-and-numeric-context-follow-up--2026-09-17) specifies finite numeric limits, unit matching, mode/value ordering, conservative commanded spindle-state checks and remaining physical-verification gaps. Tests assert specific findings/blockers so the baseline simulation/approval blocks cannot hide a missing detection. Positive boundary and modal-value tests guard against rejecting every input.

The fixture is now version 2, NC/job revision B, with machine/controller profile revision 2; all remain synthetic and unapproved. This updates test declarations, not real machine settings. No source CAD geometry changed, and no machine, simulator or external interpreter was run. Gate 04 remains open.

Executed validation: all 303 portable tests passed in 45.832 seconds; the 22 new methods also passed independently. Foundation validation passed (58 required files, ten context schemas, five skillsets), schema-instance validation passed (eleven definitions, 26 instances), and `git diff --check` passed. An initial foundation scan flagged the local state variable's name as a possible control API; it was renamed to `commanded_spindle_state` to describe inert text review, without changing or weakening the validator. The fixture CLI continues to report simulation and human-approval blockers and prohibits execution.

## Actual NC artifact and approval composition — 2026-09-17

A regression first reproduced effective approval without NC bytes despite a matching state fingerprint. The [composed artifact gate](../architecture/nc-artifact-approval-binding.md) now requires nonempty raw bytes and a matching artifact-schema descriptor for execution-adjacent CNC. It reruns static review using the same state context and selected WCS, merges actual findings, and invalidates previously recognized matching records on failure. Supplied paths are not opened; record fingerprints and declared hashes are not repaired.

The 17 new artifact-gate test methods cover valid/missing/changed bytes, altered line endings, malformed input/encoding, missing/conflicting metadata, consequence/family-label bypasses, selected WCS, multi-tool refusal, existing simulation/verification gates and prohibited live actions. Nine altered-program variants include all eight roadmap CNC negatives plus overspeed, each with a deliberately re-signed synthetic declaration to ensure the live static findings cannot be hidden by a matching fingerprint. These are software tests, not real approvals or retained seven-skill workflow reviews.

The existing 28 context-routing tests now explicitly provide the synthetic NC bytes for CNC cases through a shared in-memory helper. Other families do not inherit a CNC artifact declaration. Physical coordinate transforms, authentic simulation evidence, independent tooling where practical, retained CNC skill outputs and the gate audit remain open. No external interpreter or machine was run. Gate 04 remains open.

Executed validation: all 320 portable tests passed in 52.616 seconds; the 45 focused routing tests also passed. Foundation validation passed (58 required files, ten context schemas, five skillsets), schema-instance validation passed (eleven definitions, 26 instances), and the staged diff passed whitespace checks. These results establish the inspected software behavior, not the truth of synthetic approval or simulation declarations.
