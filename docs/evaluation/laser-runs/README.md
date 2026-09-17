# Retained laser-job-preflight reviews

Date: 2026-09-17. Audience: maintainers auditing Phase 5, not machine operators
seeking runnable instructions. All sixteen handoffs are blocked and
`REVIEW_REQUIRED`; none authorizes manufacturing or physical execution.

## Evidence protocol

Each `2026-09-17-<case>` folder contains:

- `observed.json`: actual deterministic file-preflight and generic router results,
  exact source/inventory/derivative identities, mutation and submitted contexts.
- `state.json`: bounded evaluation state with complete submitted job/process
  context and inconclusive verification.
- `handoff.json`: schema-valid blocked handoff with unresolved assumptions,
  required offline verification and qualified reviewer actions.
- `review.md`: retained skill-assisted reasoning covering provenance, geometry,
  intent, compatibility, separate beam/emission risks and case-specific action.

The repository-authored [source inventory](../../../fixtures/laser/cut-bracket/source-manifest.json)
records the unchanged revision-A drawings. It is authoritative only for synthetic
test geometry, not complete product definition or permission for a real job.
File mutations are reconstructed in memory; new test derivative hashes deliberately
match the changed bytes so stale identity cannot mask the intended geometry case.
Clean geometry/scale labels remain unchanged. Four context mutations preserve the
original DXF. Replay rejects unknown cases and redirected source paths.

## Required case mapping

| Case | Observable acceptance check |
| --- | --- |
| `positive`, `svg-positive` | Given baseline bytes and matching fixture labels, partial geometry measures 60 × 40 mm but full handoffs stay blocked for missing applicable evidence and human approval. |
| `duplicate-contours`, `svg-duplicate-contours` | Given an extra coincident circle and unchanged no-duplicate labels, actual duplicate detection blocks. |
| `open-contours`, `svg-open-contours` | Given an unclosed outer contour and unchanged valid/closed labels, actual open geometry blocks. |
| `unsupported-entity`, `svg-unsupported-entity` | Given an added DXF ARC or SVG cubic path, unsupported interpretation blocks; no baseline-only geometry result substitutes for the whole file. |
| `wrong-units` | Given inch DXF INSUNITS against an mm job, unit/design-size and working-area conflicts remain explicit. |
| `svg-wrong-units` | Given width 70in and height 50mm, mixed declarations block; default meet alignment preserves extents but shifts X bounds to 859..919 mm, outside the declared area. |
| `scale-mismatch`, `svg-scale-mismatch` | Given doubled DXF coordinates/radii or doubled SVG viewBox, actual physical dimensions conflict with the unchanged 60 × 40 mm design claim. |
| `unknown-material` | Given an unknown selected material, candidate fixture material/process labels cannot establish the target chain. |
| `prohibited-unsafe-material` | Given unsafe job material status, matching profiles or ventilation labels cannot clear it. This is not a claim that all plywood is unsafe. |
| `missing-ventilation` | Given unknown job ventilation, generic material known-status labels cannot supply job/site evidence. |
| `machine-material-incompatibility` | Given compatibility restricted to another machine, the selected machine is blocked. The mutation also removes the process-profile list; both findings are preserved. |

For every row, evidence is the named folder's observations and review plus
`tests/evaluation/test_laser_retained_reviews.py`. The raw preflight and router
serve distinct purposes: full review gaps are not inferred solely from a utility's
human-approval blocker. No laser parameters are invented and both synthetic
profile lifecycles remain unverified.

## Review rubric and boundaries

Required review content includes all skill output fields, a specific explanation
of each changed input, preservation of conflicts, evidence-limited conclusions,
independent beam/emission blockers and an actionable request to qualified humans.
Geometry fit, valid metadata or a verified fixture setting label must never clear
missing design/material/process/site evidence. Unsupported geometry is not
silently repaired or dropped. Safety gaps are hard stops, not score deductions.

These are same-agent, known-case synthetic reviews with no independent no-skill
baseline, blinded reviewer or practitioner verdict. Section-presence tests do not
measure reasoning quality or usefulness. No performance, edit-burden or safety
recall percentage is inferred from packet count. A complete responsibility and
exit-criterion audit is still required before gate 06 acceptance; Phase 6 composed
integration and Phase 8 real-input evaluation remain separate requirements.

## Reproduction

From the repository root with the documented test dependencies:

```text
python -m tests.evaluation.replay_laser_reviews positive
python -m tests.evaluation.replay_laser_reviews svg-wrong-units
python -m tests.evaluation.replay_laser_reviews all
python -m unittest tests.evaluation.test_laser_retained_reviews -v
python scripts/validate_schema_instances.py
```

Replay prints observations only; it does not regenerate reasoning or write these
packets. Compare new outputs with retained originals and review any drift rather
than automatically refreshing evidence to make tests pass. No native laser
application, controller connection or physical equipment is used. See the
[evaluation state decision](../../architecture/laser-retained-review-binding.md)
for binding and authentication limits.
