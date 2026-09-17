# Retained additive skill-assisted reviews

Controlled development evaluation by Codex on 2026-09-17 against baseline
`63e8f54`, plus the replay/packet changes in this milestone. REVIEW_REQUIRED.
The reviewer is the implementing agent, not an independent practitioner.

## Request and rubric

The inspected contract is `skills/additive-job-preflight/SKILL.md`; the
`additive-print-prep` skillset contains that single skill. Controlled request:

> Review the supplied synthetic FDM source and actual STL/3MF bytes with their
> submitted job, printer and material context. Apply additive-job-preflight to
> provenance, mesh/package validity, units/scale, build volume, printer/material
> compatibility, orientation/support, slicer readiness, environmental context
> and human review. Preserve conflicting claims and exact input identity. Explain
> blockers and actionable reviewer requirements. Do not repair geometry, choose
> missing parameters, trust status labels as evidence, promote approvals or print.

Acceptance requires each output to cover all contract areas, identify the case's
specific discrepancy, retain baseline evidence gaps and provide a blocked,
non-executable handoff with matching state/artifact identity. Geometry quality
or fluent wording cannot compensate for unresolved consequential context.
The known mutation set is not a blinded or unseen-case test. No no-skill agent
baseline, independent score, usefulness estimate or edit-burden benefit is claimed.

## Cases and observed distinctions

| Case | Controlled input and required finding |
| --- | --- |
| [positive](2026-09-17-positive/review.md) | Actual bracket STL: partial geometry control, not a manufacturing-ready job |
| [non-manifold-geometry](2026-09-17-non-manifold-geometry/review.md) | Actual facet removal creates three boundary edges/nonmanifold vertices; valid label cannot hide it |
| [unsupported-material](2026-09-17-unsupported-material/review.md) | Selected material is absent from the supplied profile/printer compatibility |
| [missing-material-profile](2026-09-17-missing-material-profile/review.md) | Null job material selection cannot borrow a candidate PLA profile |
| [incompatible-printer-profile](2026-09-17-incompatible-printer-profile/review.md) | Wrong supplied printer identity conflicts with job and material |
| [revision-mismatch](2026-09-17-revision-mismatch/review.md) | Job B conflicts with source/derivative A; retain both |
| [unsupported-build-volume](2026-09-17-unsupported-build-volume/review.md) | Measured 60/40/30 exceeds submitted 50/50/20 on X and Z |
| [missing-environment](2026-09-17-missing-environment/review.md) | Unknown job environment cannot be supplied by a generic material label |
| [3mf-positive](2026-09-17-3mf-positive/review.md) | Minimal package retains Core-default unit provenance and built geometry |
| [3mf-unit-conflict](2026-09-17-3mf-unit-conflict/review.md) | Embedded inch conflicts with submitted job/source mm even though the envelope fits |
| [3mf-build-placement](2026-09-17-3mf-build-placement/review.md) | Unit-size object translated to X=200..201 exceeds a 200-unit envelope |
| [3mf-required-extension](2026-09-17-3mf-required-extension/review.md) | Unsupported required extension prevents a geometry-readiness claim |

The STL source is the existing CC0 revision-A bracket. The new explicit CC0
`fixtures/additive/prusaslicer-lab/tetrahedron-source.json` binds the same geometry
used in the prior minimal-package tests; a regression verifies exact generated
mesh XML equality with that earlier test definition. LF checkout keeps source
identity portable. Neither definition supplies full product intent or functional
manufacturing acceptance criteria.

## Reproduction and packet identity

```text
python -m tests.evaluation.replay_additive_reviews all
python -m unittest tests.evaluation.test_additive_retained_reviews -v
python scripts/validate_schema_instances.py
```

The replay accepts only the twelve listed case IDs, reads fixed repository
inputs, constructs controlled mutations in memory and prints measurements.
It does not run an agent, generate the retained reasoning, rewrite inputs, start
a slicer or create approvals. The existing metadata-only non-manifold mutation
remains a separate earlier test; this packet deliberately changes actual bytes
while keeping its metadata label valid. Changed test derivatives receive their
own declared test identity, never an automatic renewal of a real job hash.

Each packet retains `observed.json`, `state.json`, `handoff.json` and the actual
agent-authored `review.md`. Observations contain the complete supplied parsed
contexts, mutation recipe, source/derivative inventory, partial preflight report
and separate generic-routing result. `replay:additive/<case>/input.stl` or `.3mf`
is a reconstruction locator, not an external path to fetch or a printer command.

State and handoff use existing schemas. The [evidence-binding decision](../../architecture/additive-retained-evidence.md)
explains the evaluation-only setup wrapper and its limits. Fingerprints bind
parsed context, source hashes and the generated derivative descriptor, not JSON
whitespace or authenticated reviewer identity. The source/derivative revision A
is not changed when the selected job claims B. Embedded inch is preserved on
the affected artifact even while state/job units remain mm.

## Review outcome and remaining authority

All twelve handoffs are blocked, review-required, non-executable and have no
approval ID. The baseline raw preflight reports only the missing human approval,
but the full skill review also identifies unverified profile applicability,
missing actual slicer configuration/version, unsupported orientation/support
labels, unresolved job/site environmental evidence and missing product intent.
These are hard stops, not quality deductions. Material properties stay empty;
no print temperatures, speeds, cooling or support settings are invented.

The [PrusaSlicer observations](../additive-independent/prusaslicer-2.9.6-windows.json)
support bounded independent geometry comparisons, not job-specific slicing,
extension correctness or physical approval. Self-intersection/positive-fill
semantics, usable-bed/support clearance and unsupported vendor packages remain
qualified-review obligations. The handoffs explicitly request those follow-ups.

Tests establish packet consistency, known-case blockers, schema validity and
input/state binding. Heading checks only confirm retained output structure;
they do not score reasoning quality or prove general skill effectiveness.
This packet set does not by itself accept gate 05. The complete Phase 4 audit,
cross-workflow approval integration, public-alpha safety corpus and real-input
practitioner review retain their separate requirements.
