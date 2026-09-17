# CNC Milling Evaluation Plan

## Scope

This evaluation covers three-axis planning and static NC review against explicit synthetic machine, controller, setup, tooling, postprocessor, and job contexts. It does not execute NC, prove machine behavior, or replace CAMotics, LinuxCNC, machine simulation, or qualified operator review. The original matrix below describes standalone raw-fixture checks; subsequent sections record composed approval and coordinate checks with additional prerequisites.

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

## Declared coordinate-frame review — 2026-09-17

The [coordinate contract](../architecture/nc-coordinate-model.md) closes the raw-coordinate assumption in composed routing: an explicit reviewed fixed translation, initial machine position and machine-axis bounds are required. The first 12 routing test methods reproduced 13 failing assertions/subtests and one missing-report error before implementation. They exposed both falsely retained approvals (missing/unreviewed models, hidden translated overflow, additional tool changes) and falsely blocked in-bounds translated targets. This is evidence about software behavior, not actual offset measurement.

The completed coordinate suite has 16 routing methods and four direct utility methods. Added controls cover negative/fractional translation, exact decimal boundary exceedance, first-move omitted axes, missing review/source evidence, conflicting lifecycle units, nonfinite inputs, missing context, immutability and the standalone partial-evidence boundary. The direct missing-context test first reproduced five exceptions in the new helper; those are now blocking diagnostics. All 20 coordinate methods passed in 9.276 seconds. Matching synthetic approvals are deliberately regenerated in negative tests so findings cannot depend solely on stale fingerprints.

Fixture version 3 retains NC/job B and CAD A, adds unverified coordinate model revision 1, and advances the machine profile to revision 3 for explicit frame identity. Controller revision 2 is unchanged. No real offsets or machine parameters were supplied or inferred. No simulator, independent interpreter or equipment was run. Declared endpoint arithmetic does not establish tool-change motion, collisions, physical state or simulation truth. Retained seven-skill workflow reviews and the gate audit remain open; gate 04 is not accepted by this change.

Executed validation: all 340 portable tests passed in 72.763 seconds. Foundation validation passed (58 required files, ten context schemas, five skillsets), schema-instance validation passed (eleven definitions, 26 instances), and `git diff --check` passed. The standalone fixture CLI still returns simulation/human-approval blockers with `coordinate_review: null`, review required and execution prohibited. These results do not establish independent controller compatibility, authentic simulation or manufacturing approval.

## Retained seven-skill development reviews — 2026-09-17

The [controlled request, rubric and replay protocol](cnc-runs/README.md) now accompany nine retained packets: the original NC baseline and all eight required negative mutations. Codex inspected the seven skill contracts, actual fixture contexts, linked CAD source and every replayed report, then authored the case-specific skill outputs and blocked handoffs. The replay helper only reconstructs fixed in-memory NC mutations and returns existing offline checker/router measurements; it does not execute an agent, manufacture review conclusions, run NC or write retained evidence.

Each case preserves the exact input program/hash, mutation recipe, parsed source/context declarations, partial raw static report, explicit-model report, composed routing diagnostics, bounded state, fingerprint and schema-valid handoff. All original profiles remain unverified, tool availability remains fixture-only, WCS remains defined but unverified, and simulation remains not_run. The declared coordinate checker therefore records no reviewed targets; composed static review does not proceed. Raw fixture findings expose each intended negative separately. Handoffs retain the union of software blockers and unresolved review assumptions, not just a generic blocked verdict.

The skill-assisted review identifies additional deficiencies in the baseline: absent complete CAD-to-NC operation coverage, unresolved relation between the 6-mm stock declaration and the linked upright geometry, missing manufacturing intent, unknown workholding/access, insufficient tool/holder geometry, and synthetic post-validation claims without actual version-scoped evidence. It does not infer that the rectangle produces the L-bracket or that matching numeric labels prove machine suitability. No new process parameters or NC corrections were generated. No concrete skill-instruction defect was demonstrated, so skill files and metadata remain unchanged.

The twelve focused packet tests passed in 5.377 seconds. They check deterministic replay, exact NC/source identities, state/handoff agreement, specific negative findings, retained unit/revision conflicts, non-promotion of profiles/approval, blocked simulation, original-fixture immutability and rejected hash reuse. Seven output sections are required per packet as a presence check, not a reasoning-quality score. This is a known-case, non-blinded development evaluation with no independent no-skill agent baseline or practitioner result; no usefulness/recall/edit-burden percentage is inferred. Independent-tool evidence where practical and the requirement-by-requirement gate audit remain open. Gate 04 is not accepted by these packets.

Executed repository validation: all 352 portable tests passed in 78.939 seconds. Foundation validation passed (58 required files, ten context schemas, five skillsets), schema-instance validation passed (eleven definitions, 44 instances including the nine new state/handoff pairs), and `git diff --check` passed. The seven skill contracts were not modified. No independent simulator/controller or native CAD probe was run for these packets.

## Independent CAMotics experiment — 2026-09-17

Subsequent to the retained skill packets, the pinned Windows CAMotics `1.2.0-release` G-code utility and simulator were actually run on the same nine NC byte sequences. The [runtime/experiment boundary](../architecture/camotics-evidence-boundary.md) records source review, signed archive/hash observations, non-global extraction, DLL startup failure and recovery, exact invocation, synthetic project settings, version-string discrepancy and remaining limits. No machine/controller connection occurred. The runtime remains optional; portable test discovery never starts it.

The [retained native report](cnc-independent/camotics-1.2.0-windows.json) captures both streams, exit codes, NC/project/runtime identities and measured STL properties. All eighteen case processes exited zero. Wrong post/controller/revision comments and missing G54 produced the baseline's normalized trace and triangle payload. Wrong units produced converted metric extents/feeds. X100 survived interpreter processing. Missing tools 2/9 were auto-created with explicit warnings and different simulated surfaces. Those observations justify keeping provenance, known tooling, units, coordinate and machine-limit review independent of simulator completion.

The prism/cutter/resolution are newly declared software-test settings, not inferred physical job context; actual cutter length, stock placement, fixtures, holder, machine state and offsets are not supplied to CAMotics. The jobs retain `simulation_status: not_run`, `approval_status: not_requested` and their existing router blockers. This is evidence of software interpretation and a controlled stock-removal experiment, not a validated simulation of the L-bracket job. No historical packet or source/profile was promoted or silently rewritten.

Eleven portable evidence/utility tests passed in 0.033 seconds: native record-to-input binding, runtime/project identity, preserved actual version strings, specific default/negative-case observations, non-promotion of jobs, binary mesh measurements, rejected malformed/nonfinite meshes, runtime hash refusal, and propagated process failures/timeouts. These tests inspect retained evidence and utility behavior; they do not rerun CAMotics or independently attest native binary semantics. The native probe itself ran twice with clean exits, the second retaining triangle-payload hashes in addition to whole-STL hashes. Independent evidence is now available, but the complete gate-04 audit remains open.

Executed repository validation: all 363 portable tests passed in 73.305 seconds. Foundation validation passed (58 required files, ten context schemas, five skillsets), schema-instance validation passed (eleven definitions, 44 instances), and the staged whitespace check passed. Runtime binaries and temporary simulated meshes were not staged; the optional extracted runtime remains under ignored `venv/camotics120/`. These checks do not award a manufacturing, public-alpha or practitioner gate.

## Verification-binding counterexample and fix — 2026-09-17

The gate audit at `730a40f` found that a matching approval could remain effective
with a passed simulation record naming another job/machine, a bare passed label,
or stale verification after changed NC/machine inputs. The initial focused run
reproduced four failures out of five tests. No execution was enabled, but the
effective approval contradicted the required verification-context gate.

The [implemented contract](../architecture/cnc-verification-binding.md) requires
separate passed simulation and verification records, nonempty evidence locators,
unique check identities and versioned input-context bindings. It checks every
record, keeps fresh NC checks independent, and invalidates matching approvals
when verification is stale or incomplete. The existing approval fingerprint
still covers evidence and outcomes. Approved CNC handoff schemas require both
bound kinds; blocked legacy drafts remain representable.

The regression expansion tests the original counterexamples, every consequential
fingerprint input, canonical/nonfinite inputs, malformed and failed records,
extra/duplicate records, separate renewal of verification and approval, changed
evidence, planning scope, private-value diagnostics and caller immutability.
Historical packets were not rewritten. Current replay must match every original
field except exactly three added missing-binding findings. The original native
CAMotics observations remain unchanged; no native runtime was rerun here.

Executed validation: all 381 portable tests passed in 82.841 seconds. Foundation
validation passed (58 required files, ten context schemas, five skillsets),
schema-instance validation passed (eleven definitions, 44 instances), and
`git diff --check` passed. These are software consistency/regression results,
not authentication of evidence contents or physical verification. The complete
Phase 3 gate audit remains open; public-alpha and practitioner acceptance are
not inferred from this fix or the passing test count.

## Phase 3 gate audit and isolated acceptance checks — 2026-09-17

The [completed gate review](../development/cnc-milling-gate-review.md) inspects
every Phase 3 deliverable, all seven current skill contracts, all nine retained
outputs, the native CAMotics evidence boundary, and each exit criterion at
`835116a` plus the new acceptance tests. It supports
`CADCAM_04_CNC_ALPHA_READY` for repository development against the initial corpus,
not manufacturing, public-alpha or practitioner approval. Historical packets
and their blocked outcomes are unchanged.

The audit added `tests/routing/test_cnc_gate_matrix.py` because some older
context-negative tests could also fail from stale verification after their input
mutations. The matrix renews only in-memory test declarations, including both
verification records and the approval, to isolate the intended gate. All eight
roadmap mutation recipes still fail fresh composed static review with their
specific expected blockers and no effective approval. Three NC target-header
conflicts and four post target-chain conflicts are detected independently;
post validation, six missing-context fields, five missing-tool fields, unverified
WCS/simulation and all ten prohibited live actions are also checked. A clean
positive control has no software blockers but remains non-executable.

Executed validation: the eight new test methods passed in 9.292 seconds; all
389 portable tests passed in 96.101 seconds. Foundation validation passed
(58 required files, ten context schemas, five skillsets), schema-instance
validation passed (eleven definitions, 44 instances), and `git diff --check`
passed. Native tools were not rerun. These results support the explicit curated
gate criteria, not general recall, physical safety or authentication of evidence.

The gate review records parser/model limits, unsupported multi-tool semantics,
same-agent evaluation and the remaining human/practitioner authority. Next is
Phase 4: actual mesh and 3MF package defects, unit-aware printer volume checks,
the specified additive reference ecosystem and retained preflight outputs.
