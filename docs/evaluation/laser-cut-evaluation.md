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
