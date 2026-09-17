# Retained synthetic CAD skill runs

These packets retain actual AI-assisted applications of the five-skill CAD bundle to controlled repository fixtures. They are development evidence, not independent reviewer verdicts or real-input pilot packets. Each run states its request, baseline, inspected input, skill outputs, executed checks, and remaining limitations.

| Run | Decision and evidence |
| --- | --- |
| [2026-09-17 manufacturing intent](2026-09-17-manufacturing-intent/request.md) | Five sequential skill outputs; missing manufacturing intent blocks a handoff despite passing file/native checks. Artifact hashes, bounded state, and serialized handoff are retained. |
| [Revision mismatch](2026-09-17-revision-mismatch/review.md) | A source/B drawing conflict is preserved and blocked. |
| [Missing units](2026-09-17-missing-units/review.md) | Unknown mesh/bundle units remain null despite passing numeric envelopes. |
| [Stale derivative](2026-09-17-stale-derived-file/review.md) | Source-hole edit with old derivatives fails consistency and byte binding. |
| [STL as design master](2026-09-17-stl-treated-as-design-master/review.md) | Actual mesh-only input cannot establish complete design authority. |
| [Conflicting dimensions](2026-09-17-conflicting-dimensions/review.md) | Visible 61 mm annotation conflicts with 60 mm source/description/projection. |

The schema-instance validator checks `state.json` and `handoff.json` in each run directory. `tests/interoperability/test_cad_retained_review.py` checks the first packet's artifact identities, fingerprint, declared evidence and blockers, including invalid approval promotion. These checks do not rerun a model, authenticate a reviewer, or score the quality of reasoning. Do not automatically rewrite archived findings or hashes after fixture changes; inspect their applicability and preserve the previous record.

The [shared protocol](negative-cases-protocol.md) defines the five fixed replay inputs and their evaluation-only `replay:` artifact locators. `tests/interoperability/test_cad_negative_reviews.py` checks reproduction, unchanged positive fixture bytes, identities, fingerprints, unknown units, conflicting revisions and blocked outcomes. These locators are not permanent job-file paths.

All six named roadmap cases are retained. The [Phase 2 gate audit](../../development/cad-handoff-gate-review.md) records development acceptance and its limits. Practitioner evaluation, baseline comparisons, reviewer edits, safety findings and final human verdicts belong to the separate pilot process.
