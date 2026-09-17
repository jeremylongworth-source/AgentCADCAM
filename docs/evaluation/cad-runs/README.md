# Retained synthetic CAD skill runs

These packets retain actual AI-assisted applications of the five-skill CAD bundle to controlled repository fixtures. They are development evidence, not independent reviewer verdicts or real-input pilot packets. Each run states its request, baseline, inspected input, skill outputs, executed checks, and remaining limitations.

| Run | Decision and evidence |
| --- | --- |
| [2026-09-17 manufacturing intent](2026-09-17-manufacturing-intent/request.md) | Five sequential skill outputs; missing manufacturing intent blocks a handoff despite passing file/native checks. Artifact hashes, bounded state, and serialized handoff are retained. |

The schema-instance validator checks `state.json` and `handoff.json` in each run directory. `tests/interoperability/test_cad_retained_review.py` checks the first packet's artifact identities, fingerprint, declared evidence and blockers, including invalid approval promotion. These checks do not rerun a model, authenticate a reviewer, or score the quality of reasoning. Do not automatically rewrite archived findings or hashes after fixture changes; inspect their applicability and preserve the previous record.

Complete the remaining roadmap negative-case skill runs before proposing CAD gate acceptance. Practitioner evaluation, baseline comparisons, reviewer edits, safety findings and final human verdicts belong to the separate pilot process.
