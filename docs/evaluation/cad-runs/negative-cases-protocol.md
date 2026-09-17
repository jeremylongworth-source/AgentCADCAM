# Five remaining CAD negative-case reviews

Controlled synthetic development evaluations performed by Codex on 2026-09-17, applying the five repository skill files at `fbc1916` in order, with the CAD/DFM-review checklist. The code helper replays inputs and file checks only; it does not run an agent or manufacture skill conclusions. The retained `review.md` files are this agent's actual case-specific outputs after inspecting the replayed evidence. They are not blinded tests, independent reviewers, practitioner approval, or pilot packets.

## Shared request

> Review this supplied synthetic CAD bundle for manufacturing-handoff planning. Apply cadcam-intake-and-scope, design-file-provenance-review, file-format-interoperability-plan, cad-manufacturability-review, and drawing-pmi-handoff-review in order. Inventory the supplied files and preserve hashes, units, revision and authority claims without silently accepting conflicting claims. Use the observed file evidence to identify missing/conflicting context, required corrections and reviewer questions. Do not invent units, geometry, tolerances, source authority, process/material parameters, or approval. Retain a blocked handoff whenever consequential context is unresolved. No machine control, physical manufacture or manufacturing output generation is requested.

## Reproduction and input identity

```text
python -m tests.interoperability.replay_cad_negative_cases all
python -m unittest tests.interoperability.test_cad_negative_reviews -v
```

The helper accepts only five fixed case identifiers. It creates private temporary copies of the [baseline fixture](../../../fixtures/cad/bracket/fixture.yaml), applies the operations below, reads actual files, and prints JSON. It cleans up only its own temporary directory. It cannot take arbitrary replacement paths, write retained evidence, execute CAD source, or call external tools. The mesh-only case supplies only the STL and synthetic inventory/metadata, not a hidden native source or drawing. Hash checks and replay equality detect drift in the baseline; do not regenerate recorded conclusions merely to make a comparison pass.

| Case | Input operation | Observed result |
| --- | --- | --- |
| [Revision mismatch](2026-09-17-revision-mismatch/review.md) | Change SVG title/annotation and its inventory revision to B; leave source/metadata A and old binding | Drawing/revision and binding failures; envelopes still pass |
| [Missing units](2026-09-17-missing-units/review.md) | Set STL inventory and binding units to null, plus bundle units in revision metadata; leave geometry files unchanged | Missing unit declaration and invalid binding block; numeric envelopes do not establish physical mesh scale |
| [Stale derivative](2026-09-17-stale-derived-file/review.md) | Change source hole diameter from 6 to 8; leave labels A, drawing, STEP/STL and binding unchanged | Parameter/projection/binding failures despite unchanged exchange envelopes |
| [STL as master](2026-09-17-stl-treated-as-design-master/review.md) | Supply only STL plus A/mm sidecar/inventory claiming authority | Mesh envelope passes; source-authority review blocks; final authority remains unknown |
| [Conflicting dimensions](2026-09-17-conflicting-dimensions/review.md) | Change visible SVG BASE width to 61, retaining source/description/rectangle width 60 and old binding | Structural annotation and byte-binding failures; exchange envelopes still pass |

Each `observed.json` records submitted declarations, complete supplied source/drawing text where present, actual file hashes and raw checker findings. Artifact locators of the form `replay:<case>/source/<name>` identify bytes reconstructed by this fixed helper. They are not network URLs or permanent filesystem paths; consumers must replay the named case, not treat these locators as ordinary job-file paths. The packet tests compare the reproduced inventory and observations with the retained record and compare handoff identities/fingerprint to the stored state.

## Common boundaries and sources

The baseline's synthetic CC0/public/owned/export-not-required declarations apply only to repository evaluation. Possession of an external file would not establish those permissions. All five runs remain `cad_handoff` / `manufacturing_planning`, `REVIEW_REQUIRED`, blocked and non-executable. Missing function, interfaces, tolerances/datums, material/process, finish and inspection intent remain explicit even when a more immediate defect stops progression. No native probe was rerun on these mutations; no process simulation or physical control occurred.

Apply the [format policy](../../formats/format-registry.md), [interoperability standard](../../standards/interoperability-standard.md), [source/authority rules](../../architecture/ip-and-provenance-model.md), and the [baseline five-skill review](2026-09-17-manufacturing-intent/review.md) with its scoped primary-source evidence. These case findings are observations of synthetic files and repository review policy, not new machine/material/process-capability claims.

## Evaluation boundary

All five tool runs returned blocked. The agent added explicit manufacturing-context and human-review findings where appropriate rather than presenting the tool report as a complete review. State/handoff schemas and packet tests check record integrity and retained outcomes; they do not independently score reasoning or predict future agent behavior. Combined with the earlier missing-manufacturing-intent run, these cover the six named CAD roadmap negatives for the initial fixture. The subsequent [requirement-by-requirement gate review](../../development/cad-handoff-gate-review.md) records development acceptance; practitioner/public-alpha/pilot gates remain separate.
