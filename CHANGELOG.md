# Changelog

## Unreleased

- Added bounded job routing with schema, approval fingerprint/scope, and verification checks. Corrected consequence floors and malformed-input handling.
- Breaking: version-2 fingerprints now include all declared review dependencies. Existing fingerprints require re-review; see `docs/development/fingerprint-v2-migration.md`.
- Restored the bracket's two upright holes in STEP/STL derivatives and added opt-in native geometry/process-exit verification. Added tested Windows/Python 3.12 dependency constraints for the CasADi/NLopt shutdown failure.
- Added offline Draft 2020-12 validation of context/state examples and fixture profiles, with a portable test dependency set.
- Fixed approval invalidation schema compatibility and the optional STEP/STL generator's export import regression.
- Added pilot packet validation and aggregate readiness reporting for roadmap thresholds, evidence references, sourcing, and reviewer measurements. Real practitioner validation remains outstanding.
- Bootstrapped the standalone CAD/CAM Skills repository.
- Added the Phase 0 domain contract and Phase 1 foundation standards.
- Added initial context schemas, format registry, router contract, and validation script.
- Validated the synthetic CAD design-handoff workflow through `CADCAM_03_DESIGN_HANDOFF_READY`.
- Validated the synthetic three-axis CNC planning workflow through `CADCAM_04_CNC_ALPHA_READY`.
- Validated the synthetic FDM additive preflight workflow through `CADCAM_05_ADDITIVE_ALPHA_READY`.
- Validated the synthetic laser-cutting preflight workflow through `CADCAM_06_LASER_ALPHA_READY`.
- Added deterministic router/state integration through `CADCAM_07_INTEGRATION_READY`.
- Hardened the portable workflow layer through `CADCAM_08_PUBLIC_ALPHA_READY`; real-input pilot validation remains outstanding.
