# Laser Cutting Evaluation Plan

## Scope

This evaluation covers DXF/SVG units, scale, contour closure, duplicate and unsupported geometry, machine/material/process compatibility, ventilation, material safety status, and human approval. It does not activate a beam or certify a material/process profile.

## Acceptance matrix

| Case | Expected result |
| --- | --- |
| Valid paired SVG/DXF with known material, machine, process, and ventilation | Block only on `HUMAN_APPROVAL_REQUIRED` |
| Duplicate or open contours | `MISSING_CONTEXT` |
| Unsupported entity | `MISSING_CONTEXT` |
| Wrong units or scale | `MISSING_CONTEXT` |
| Unknown or unsafe material | `MISSING_CONTEXT` |
| Missing ventilation context | `MISSING_CONTEXT` |
| Machine/material incompatibility | `MACHINE_CONTEXT_REQUIRED` |

## Hard gates

- Laser parameters are never guessed.
- Unknown or unsafe materials cannot receive manufacturing-ready status.
- Beam activation and process-emission risks are reported independently.
- Preflight never activates equipment and never sets `execution_allowed` to true.

## Evidence status

The paired synthetic SVG/DXF fixture and all nine declared negative mutations are exercised by the test suite. Real material safety, ventilation, machine profile, and operator review remain external responsibilities.

## File-derived SVG follow-up — 2026-09-17

The earlier matrix describes metadata-level checks; it is not proof of general
DXF/SVG defect detection. The new [SVG evidence reader](../architecture/laser-svg-evidence.md)
measures actual bytes, physical viewport scale, exact transformed contours and
geometry defects. The unchanged fixture measures a 60 × 40 mm outer rectangle
with two radius-3 mm circles at (17,25) and (53,25). Its 70 × 50 mm viewport is
not confused with the geometry's extents.

Nineteen SVG methods plus four existing laser methods passed together: 23 tests
in 0.237 seconds. Cases include actual open and duplicate geometry, crossings,
touching/overlapping segments and circles, viewBox/physical-unit scale changes,
nested transforms, altered hole position/radius, unsupported curves/styling,
ambiguous viewport units, malformed input and resource limits. The paired fixture
validator also passed against the unchanged source files. Temporary-copy mutations
are rejected without changing the job's valid labels or rewriting original files.

An additional boundary probe exposed an uncaught Decimal conversion exception
for an exponent beyond the library's representable range. The reader now checks
the lexical exponent before conversion; a regression exercises positive/negative
extreme exponents in geometry, transforms, stroke width and viewport length.
Those inputs now produce an explicit review blocker rather than an exception.

After that fix, the full portable suite passed 500 tests in 102.925 seconds.
Foundation validation passed (58 required files, ten context schemas, five
skillsets), schema-instance validation passed (eleven definitions, 68 instances),
and whitespace checks passed. No native renderer or physical equipment was run.

The SVG reader reports partial geometry, not source equivalence, path intent,
kerf, working-area compatibility or applicable process readiness. DXF remains
under the previous limited fixture checks, and laser_preflight remains metadata-
level until the readers are composed with explicit job identity/revision/scale.
All nine roadmap negatives, complete retained skill reviews and gate 06 acceptance
remain required; this change does not close Phase 5.

## DXF and byte-aware preflight follow-up — 2026-09-17

The [file-evidence contract](../architecture/laser-file-evidence.md) adds bounded
ASCII DXF inspection and composes both readers with explicit job identity,
source revision, design extents, unit declarations and working-area placement.
Fixture version 2 binds the unchanged DXF bytes and explicitly selects cut intent,
placement frame and process profile. Whole-file identity is preserved with LF
checkout rules; no fixture drawing, material setting or approval was regenerated.

Ten DXF methods and nine new file-preflight methods were added. Combined with
the existing SVG/laser tests, all 42 focused methods passed in 1.258 seconds.
Actual altered files expose open/duplicate/unsupported geometry, unit and scale
conflicts while labels remain valid and test-only hashes match. Further cases
cover exact LINE chains, visibility/layers, nonplanar/curved DXF semantics,
extreme numbers, malformed contexts, source revision/hash, independent process
target mismatches, material/environment conflicts, exact machine-unit boundaries
and translated geometry. CLI tests use the explicitly named job with no adjacent
default job.json and check blocked JSON/exit status in script and module forms.

The paired fixture validator passed using the two actual byte readers. Foundation
validation passed (58 required files, ten context schemas, five skillsets), and
schema-instance validation passed (eleven definitions, 68 instances).

The utility remains partial evidence, not authenticated process or manufacturing
approval. Both fixture profiles remain unverified and process settings remain
empty. Complete retained skill reviews and the requirement-by-requirement gate
audit remain necessary before Phase 5 acceptance.

The full portable suite passed all 519 tests in 115.026 seconds. Whitespace checks
passed. No native CAD renderer, laser controller or physical equipment was run.

## Retained full laser reviews — 2026-09-17

The [sixteen retained packets](laser-runs/README.md) include DXF and SVG baselines,
all nine roadmap negatives and five additional SVG geometry/unit/scale cases.
Ten cases alter actual drawing bytes while keeping optimistic metadata labels
and binding fresh test hashes. Four context mutations retain the original DXF.
The mixed-unit SVG is deliberately not described as uniform scaling: width 70in
and height 50mm retain 60 × 40 mm extents under default meet alignment but move
X bounds to 859..919 mm, outside the declared working area.

Every review covers the full laser skill contract, including per-path intent and
placement limitations, unverified synthetic profiles, empty settings and separate
beam/emission evidence gaps. No profile flag is upgraded into applicable process
or site evidence. Handoffs retain the union of utility/router blockers, unresolved
assumptions, inconclusive verification and required offline output review. Even
the two geometry baselines remain blocked; no manufacturing approval is created.

The [state-binding decision](../architecture/laser-retained-review-binding.md)
preserves complete job/process inputs in an evaluation-only setup wrapper. A new
synthetic source inventory records the existing revision-A drawings independently
of job claims and is itself byte-bound; original drawings remain unchanged.
This does not turn the generic router into a file-aware laser workflow or settle
the Phase 6 production process/evidence contract.

Seventeen focused packet methods passed in 5.272 seconds. They check exact replay,
schema/input/hash agreement, each specific negative independent of missing human
approval, preserved conflicts, state invalidation, source immutability and refusal
of source-inventory drift/redirects. Foundation validation passed (58 files, ten
context schemas, five skillsets), schema-instance validation passed (eleven
definitions, 100 instances), and the paired laser geometry validator passed.

These are same-agent known-case reviews, not a blinded benchmark, qualified human
verdict or real-input pilot. Section-presence checks do not grade reasoning.
The complete gate audit is still required before Phase 5 acceptance.

The full portable suite passed all 536 tests in 120.836 seconds. Staged whitespace
checks passed. No fixture source drawing changed and no native laser application,
controller connection or physical equipment was used.

## Phase 5 exit-gate audit — 2026-09-17

The [requirement-by-requirement audit](../development/laser-gate-review.md)
maps the skill, manifest, all eleven responsibilities, nine required negatives
and five exit criteria to current implementations, actual observations, complete
retained reviews and regression evidence. It supports
`CADCAM_06_LASER_ALPHA_READY` for repository development against the initial
corpus, not a manufacturing approval, public-alpha release or practitioner verdict.

Eight gate-edge methods supplement the existing isolated negative/replay tests.
They check both nonexecuting controls, cross-format bytes, missing/uncertain or
malformed unsafe-material and ventilation statuses in either context, separate
machine/process compatibility, each unresolved process review flag, cut/placement
declarations and independent beam/emission findings. The matrix and retained
reviews passed 25 focused methods in 5.355 seconds. No production implementation,
fixture, retained review packet or real approval changed during this audit.

The full portable suite passed all 544 tests in 116.513 seconds. Foundation
validation passed (58 files, ten context schemas, five skillsets), schema-instance
validation passed (eleven definitions, 100 instances), and the paired laser
geometry validator passed. These counts do not measure reasoning quality or
prove general format conformance. No native laser application or equipment was run.

All sixteen handoffs remain blocked with separate design, process, beam and
emission evidence gaps. Next is Phase 6 file-aware composition and current-context
approval/invalidation across all four families. Phase 7 governance acceptance and
Phase 8 qualified real-input evaluation remain open.

## Phase 6 laser file/evidence composition — 2026-09-17

The [integrated laser gate](../architecture/laser-router-integration.md) now runs
inside `route_job` for execution-adjacent laser jobs. It requires explicit bytes,
source/job/output identity, structured process inputs and six independent current
evidence roles. Raw job approval flags cannot override the scoped record decision.
Fresh file/context/evidence failures invalidate a matching approved record copy
without changing its reviewed fingerprint. Re-signing approval alone cannot renew
stale evidence. No machine operation, settings generation or source fetch is added.

Fourteen new integration methods passed in 10.917 seconds. Cases include both
format controls and every retained negative with newly bound test-only evidence,
missing/wrong bytes, identity/source conflicts, empty settings, each evidence
role, malformed/failed/duplicate/stale records, process-change invalidation,
raw-flag refusal, consequence/family bypass and every prohibited live action.
Positive controls use a non-operational test marker, not actual laser parameters.

An existing profile test initially failed because its laser approval control had
no drawing or laser evidence. The control now supplies complete synthetic inputs;
its unverified-profile rejection assertion is preserved. Historical packets are
unchanged. Their replay test permits exactly the new missing input/byte/evidence
diagnostics and still checks every original raw observation, state and hash.

The full portable suite passed 558 tests in 132.801 seconds. Foundation validation
passed (58 files, eleven context schemas, five skillsets) and schema-instance
validation passed (twelve definitions, 100 instances). Whitespace checks passed.
No physical equipment or native laser application was used. Phase 6 remains open
for additive/CAD composition, integrated handoffs and the full four-family audit.
