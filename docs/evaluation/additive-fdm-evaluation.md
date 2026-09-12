# FDM Additive Evaluation Plan

## Scope

This evaluation covers metadata-level FDM preflight for STL/3MF provenance, mesh status, printer and material compatibility, build volume, orientation/support readiness, environmental context, and approval. It does not slice, print, or certify a material profile.

## Acceptance matrix

| Case | Expected result |
| --- | --- |
| Valid STL, printer, material, orientation/support, and environment | Block only on `HUMAN_APPROVAL_REQUIRED` |
| Non-manifold geometry | `MISSING_CONTEXT` |
| Unsupported or missing material profile | `MISSING_CONTEXT` |
| Incompatible printer profile | `MACHINE_CONTEXT_REQUIRED` |
| Revision mismatch | `MISSING_CONTEXT` |
| Model exceeds build volume | `MACHINE_CONTEXT_REQUIRED` |
| Missing environmental context | `MISSING_CONTEXT` |

## Hard gates

- STL and 3MF remain print derivatives, not complete design masters.
- Material parameters are never invented.
- Unknown printer, material, slicer, or environmental context cannot receive manufacturing-ready status.
- Preflight never starts a printer and never sets `execution_allowed` to true.

## Evidence status

The synthetic FDM fixture and all seven declared negative mutations are exercised by the test suite. Real printer/material/slicer compatibility and operator safety remain qualified-review responsibilities.
