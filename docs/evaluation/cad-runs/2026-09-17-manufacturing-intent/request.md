# Controlled CAD handoff evaluation request

This is a synthetic development evaluation selected under the roadmap, not a customer manufacturing order. Baseline repository: `042cb3e`. Run date: 2026-09-17. Evaluator: Codex, applying the five repository skill files at that revision plus the installed CAD/DFM-review checklist. No independent agent, human reviewer, or practitioner verdict is claimed.

## Prompt

> Review the complete synthetic revision-A bracket bundle for a manufacturing-handoff planning decision. Apply cadcam-intake-and-scope, design-file-provenance-review, file-format-interoperability-plan, cad-manufacturability-review, and drawing-pmi-handoff-review in that order. Identify known, missing, conflicting, and unverified context. Distinguish successful file checks from complete manufacturing intent. Preserve source/derivative identity, do not invent tolerances, material, process, machine parameters, or authorization, and return a review-only handoff with blocking findings where required. Do not generate machine output or operate equipment.

## Inputs and purpose contrast

- Input bundle: [fixture manifest](../../../../fixtures/cad/bracket/fixture.yaml), [revision metadata](../../../../fixtures/cad/bracket/metadata/revision.json), [declared byte binding](../../../../fixtures/cad/bracket/metadata/derivation.json), and the four design/drawing/exchange files they identify.
- Selected skillset: [cadcam-design-handoff](../../../../skillsets/cadcam-design-handoff.yaml).
- Positive control: the unchanged bundle passes the bounded file-review CLI and remains `review_required`. This permits continued prototype/design review, not a manufacturing handoff.
- Negative decision: this prompt asks whether the same package supplies the intent needed for manufacturing-handoff planning. The actual source/drawing lack controlled tolerances, datums, material/process selection, mating requirements, and inspection acceptance criteria. The absence is not simulated by merely deleting a `pmi_status` field.

The [review](review.md) preserves the five sequential skill outputs and evidence limits. [State](state.json) records the context assembled by this review, not pre-existing approved job memory. [Handoff](handoff.json) preserves the resulting blocked decision and its computed version-2 fingerprint. None of these files belongs to the real-input pilot corpus.
