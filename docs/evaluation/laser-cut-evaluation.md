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
