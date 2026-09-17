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
