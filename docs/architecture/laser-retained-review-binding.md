# Retained laser review binding

Status: evaluation-only decision, 2026-09-17. Audience: maintainers reviewing
Phase 5 evidence. This is not a production approval API or Phase 6 acceptance.

Historical evaluation architecture: the subsequent
[laser router integration](laser-router-integration.md) adds a distinct explicit
input and evidence contract. The original packet wrappers remain evaluation-only
and now receive additional missing-contract/byte/evidence blockers during replay.
The descriptions below record why those packets were built, not the current
router's complete capabilities.

## Context and current components

The [laser file preflight](laser-file-evidence.md) inspects actual drawing bytes
and declared context. The generic router does not invoke those readers for laser
jobs. A router result by itself therefore cannot represent the complete skill
review. The [retained reviews](../evaluation/laser-runs/README.md) preserve these
two observations separately and add case-specific skill reasoning and a blocked
handoff; no generic routing result overrides a file or reviewer finding.

The fixed [replay helper](../../tests/evaluation/replay_laser_reviews.py):

1. Reads the synthetic source inventory and selected original drawing, checks
   exact hash/revision and the fixed source path, then loads the four contexts.
2. Applies a named in-memory drawing or context mutation and records the exact
   derivative hash. It never repairs or overwrites source drawings.
3. Calls byte-aware preflight, constructs an evaluation state and calls routing.
4. Returns observations to stdout. It never writes reviews, runs equipment or
   generates process parameters.

The source inventory records existing test drawings as revision A independently
of the submitted job revision. Its authority covers repository test geometry,
not authenticated design requirements. Both it and the drawings have explicit LF
checkout rules because their raw bytes are evidence inputs.

## Decision and alternatives

Retain the complete submitted job and process objects under
`setup.submitted_job` and `setup.submitted_process`, marked
`context_kind=laser_evaluation_input` and `evaluation_only=true`. The existing
version-2 state fingerprint includes the entire setup value, machine/material
profiles, original source/inventory hashes and generated derivative descriptor.
This binds process settings, profile IDs/targets/source claims, units, expected
dimensions, path intent, placement and environmental declarations without
inventing a new root process field or claiming that the generic router validates
their laser-specific semantics.

Keeping only a drawing hash would omit consequential process/context changes.
Changing the production state schema here would couple an evaluation fixture to
unfinished Phase 6 integration. The bounded wrapper preserves the supplied
inputs while leaving that production contract decision explicit and open.

## Consequences and limits

Each retained handoff uses the current state fingerprint and the union of file
preflight and routing blockers. Inconclusive verification and unresolved
assumptions prevent a status-only promotion to approved under the handoff schema.
All handoffs remain blocked, with review required and execution forbidden.
Separate beam and emission evidence gaps are retained even for baseline geometry.

Fingerprints establish record consistency, not source authenticity, reviewer
identity, true physical setup, applicable process validation or approved output.
Review text is retained beside the input records; it is not cryptographically
authenticated by the state hash. Replay equality is an integrity regression, not
an independent assessment of reasoning quality. `replay:` locators describe
reproducible test bytes, not deployable manufacturing artifacts.

## Validation and review triggers

`tests/evaluation/test_laser_retained_reviews.py` checks exact replay, byte hashes,
schema validity, input binding, mutation-specific findings and invalidation after
submitted job/process changes. It preserves original approval records and source
files. Repository schema validation includes all 32 state/handoff instances.
Run the commands in the packet README; passing results must be recorded separately.

Revisit when the skill/reader/state contracts or source bytes change, when a
false-ready counterexample appears, or when composing the real four-family
workflow. Phase 6 must propagate actual reader/reviewer blockers through its
integrated approval path and decide how applicable process and evidence records
are represented. Phase 8 still requires qualified reviews of real inputs.
