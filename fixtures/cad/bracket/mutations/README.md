# CAD Bracket Mutations

Each mutation is applied to a copy of the positive fixture and must preserve the original bundle. The expected hard outcomes are recorded in `../expected/outcomes.yaml`.

- `revision-mismatch`: drawing or metadata revision differs from the design master.
- `missing-units`: one or more artifacts omit unit identity.
- `stale-derived-file`: mesh or drawing revision/hash no longer traces to the current source.
- `stl-treated-as-design-master`: the derivative mesh is incorrectly declared authoritative.
- `missing-pmi`: the handoff claims dimensional intent without PMI or drawing support.
- `conflicting-dimensions`: source and drawing disagree on a critical dimension.
