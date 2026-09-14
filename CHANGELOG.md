# Changelog

## Unreleased

- Tightened shared profile source metadata to require scope, supported claims, publication/revision availability, and calendar access dates. Migrated synthetic records with test-only claims and added schema/routing regressions. This breaks older minimal source records; see `docs/development/source-contract-migration.md`.
- Reviewed the domain contract against Phase 0 requirements, added conditional capability boundaries and four workflow definitions, and recorded architecture acceptance. Phase 1 remains open for explicit handoff and profile lifecycle schema gaps.
- Replaced regex-only Markdown link checks with offline parsed reference/image links, heading/custom anchors, and decoded-path confinement. Added 21 regression checks; external pages and non-Markdown fragments still require separate review.
- Added AgentSkills-compatible version, maintenance owner, and supported review-level metadata to all 14 skills. Foundation checks reject missing/invalid declarations and live-execution scope; workflow instructions and permissions are unchanged.
- Hardened foundation validation against malformed/duplicate manifests, missing skill references, fixture path escapes, and invalid repository YAML/JSON. Added regression cases and documented the remaining metadata/reference coverage gaps.
- Completed the nine-format review policies and added 11 scoped source records. Foundation validation now rejects missing format fields, ambiguous YAML, incomplete source metadata, and stale or mismatched format citations; broader safety/source review remains outstanding.
- Enforced required CNC context before recognizing an approval, including setup, tooling, WCS, post identity, simulation, and verification. Incomplete matching approvals now require renewed review.
- Corrected public-alpha readiness claims: historical synthetic gate records do not prove full roadmap completion. Added a requirement/evidence gap register in `docs/development/roadmap-reconciliation.md`.
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
