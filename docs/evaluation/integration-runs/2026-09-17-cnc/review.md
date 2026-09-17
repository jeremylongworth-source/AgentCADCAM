# Integrated CNC milling review — 2026-09-17

REVIEW_REQUIRED. Block the manufacturing handoff. This applies the seven skills
in `cnc-milling-planning` order to the actual positive fixture under the
[protocol](../protocol.md). All quantities below are supplied synthetic data,
not machining recommendations.

## 1. Machine capability match

| Requirement / declaration | Supplied evidence | Finding |
| --- | --- | --- |
| Three-axis milling | Machine declares three axes | Identity/category match only; lifecycle unverified |
| Design envelope | CAD source 60 x 40 x 30; stock 60 x 40 x 6 | Full bracket versus stock/setup scope unresolved |
| Machine-axis limits | X0–60, Y0–40, Z0–30 | Declared bounds, not verified physical travel or clearance |
| Spindle / interface | 500–12000 rpm, fixture-holder | Synthetic limits; no OEM applicability or cutting capability evidence |

The coordinate model is unverified, so programmed positions cannot be accepted
as verified machine-space targets. Require machine-specific evidence and review
of access, stock/fixture envelope and intended operations. Severity: blocker;
the alternate path is context collection, not choosing another machine by name.

## 2. CNC setup planner

The supplied sequence is face/base setup, then review vertical features. Preserve
it as a draft, not a proven complete setup plan. Part-axis orientation labels,
G54 and zero translation are declarations. WCS status is `defined`, not verified;
initial X0 Y0 Z25 after tool change has not been observed. Clamp clearance is
null and workholding is `fixture-only`; no actual fixture geometry is supplied.

Reviewer actions: resolve whether this is a base-only exercise or the full
30-high bracket; supply stock and fixture geometry, a controlled datum/axis
definition, and the applicable method/evidence for establishing and verifying
G54. Review tool access to both faces and any re-fixturing requirement without
inventing a vise, clamp arrangement, offset or probing sequence.

## 3. Tooling plan review

| Tool | Declared geometry / holder / reach | Numbering and readiness |
| --- | --- | --- |
| fixture-tool-1 / T1 | Endmill, diameter 6, two flutes; fixture-holder; reach 20 mm | T1 matches program and library; availability fixture-only and lifecycle unverified |

The supplied reach is not a clearance calculation. Missing holder envelope,
applicable supplier/tool data, actual availability and setup-relative feature
access prevent tooling approval. Obtain these and reconcile the CAM tool table,
setup sheet and final output; no feeds, speeds or tool substitutions are supplied.

## 4. Toolpath strategy planner

The source describes an L bracket with holes on two faces; the NC describes a
rectangular perimeter at Z0. This is not evidence of a complete manufacturing
plan or material removal matching the design. Revision B in job/NC conflicts
with revision A in the supplied CAD bundle; retain both and request a controlled
source-to-CAM revision decision before strategy selection.

Planning alternatives for the CAM reviewer: distinguish base-facing/contouring
scope from full bracket roughing/finishing, and assess separate access for the
base and back-face holes. A second orientation could change access but requires
new workholding and datum evidence; no second setup is selected here. Sequence,
entry/retract, residual stock, engagement, chip evacuation and finish depend on
the unresolved design/setup/material/tool evidence. No stepover, depth, feed,
spindle or coolant recommendation follows from this program.

## 5. Postprocessor readiness review

| Identity | Supplied value | Limit |
| --- | --- | --- |
| CAM | fixture-cam | CAM version/job evidence absent |
| Machine | fixture-mill-3axis | Unverified synthetic lifecycle |
| Controller | fixture-controller / controller-v1 | Unverified bounded test dialect, not physical controller qualification |
| Post | fixture-post-v1 / 1.0 | IDs match; validation_state verified is not supported by lifecycle review |

Require applicable CAM/controller/post-version evidence and representative
validation for this job. Do not deploy or modify the post. The declared
`verified` label cannot override its unverified lifecycle.

## 6. NC static safety review

Actual bytes of [positive.nc](../../../../fixtures/cnc/mill-bracket/programs/positive.nc)
were inspected. The synthetic dialect checker recognizes G21, G90/G17/G54,
G94/G97, T1 M6, M3/M5 and the bounded linear program. The supplied S5000 and
F100/F200 are observed program values only. M3 and M5 require spindle-state human
review; this evaluation never executes them.

The raw fixture check reports explicit mm, G54 and reconciled T1. Its scoped
coordinate-model run returns `coordinate_review.status: not_run` because the
model lacks current revision-scoped evidence. Thus no mapped-target, collision,
physical offset or cutting-suitability success is claimed. Artifact hashes and
the A/B conflict remain in [observed.json](observed.json).
The integrated router does not rerun the static parser while required CNC
context is unresolved; these raw observations remain a separate evidence layer.

## 7. Simulation readiness review

Job-applicable simulation is required but has not run. The submitted job's
`not_run` value remains in observed contexts; the assembled review state uses
`required` to express the review conclusion, not a newly performed simulation.
Obtain current machine/controller/post, stock, fixtures, tool/holder, WCS and NC
identities; review mapped motion, collisions, material removal, entry/retract
and spindle/feed behavior at the applicable level. Historical CAMotics lab
observations are not current qualified verification of this job.

## Integrated handoff and human action

Seven current-input-bound findings remain inconclusive, failed or not_run.
Binding the record does not make it pass. The state preserves unverified profiles,
unknown clamp clearance and the supplied WCS. The handoff preserves revision-A
source artifacts alongside revision-B NC; the consumer detects the revision
conflict in addition to routing blockers. The reviewer must resolve provenance,
setup/tool/post applicability and simulation before any scoped approval.

No approval record is supplied, and both APIs retain review-required,
non-executable outcomes. This same-agent known-case review is neither an
independent practitioner verdict nor an assessment of physical machining safety.
