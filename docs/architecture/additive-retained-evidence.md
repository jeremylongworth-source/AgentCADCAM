# Additive retained-review evidence boundary

Follow-up: the [Phase 6 additive integration](additive-router-integration.md)
now requires explicit typed inputs, actual bytes and scoped evidence. This
document records the historical evaluation convention, not that runtime API.
Original packets remain unchanged; exact replay tests permit only the new gate's
additional missing-input/evidence diagnostics.

Status: implemented development-evaluation path; `REVIEW_REQUIRED`. No production
approval or machine execution is introduced. Audience: maintainers auditing
Phase 4 review evidence and later Phase 6 integration.

## Context and decision

The additive checker reads STL/3MF bytes and selected context declarations;
the generic bounded-state router validates records, profile lifecycles and
approval consistency. Neither is the skill's full review of unsupported design,
slicer, orientation/support or environmental evidence. Retain their reports
separately, then preserve the actual agent review and its blocked handoff.
Do not relabel the raw checker output as the agent's reasoning or infer approval
from one successful check.

`tests/evaluation/replay_additive_reviews.py` reconstructs twelve fixed cases.
It records source/derivative identities and parses existing contexts without
modifying them. The explicit tetrahedron source is test geometry, not a product
specification. The non-manifold case changes actual STL facets, not only status.
The replay is read-only and never starts the optional native tool.

## State and identity

Reuse `state.schema.json` and `handoff.schema.json` without adding production
state fields. Store the complete submitted additive job under:

```text
setup.context_kind = additive_evaluation_input
setup.evaluation_only = true
setup.submitted_job = the supplied parsed additive job
setup.source_revision = the independently supplied source revision
```

The existing version-2 fingerprint includes `setup`, source hashes, profiles,
units, job revision, generated-output descriptor and verification. This binds
orientation/support/environment/status/profile-selection claims that would
otherwise be absent from the generic state. The derivative descriptor preserves
its own source revision and embedded unit rather than forcing agreement with
conflicting job claims. No approval record is created or updated.

This wrapper is an **evaluation convention**, not a typed additive production
context API. Root schema validation does not validate all nested additive job
semantics. Tests compare the wrapper exactly with supplied inputs and exercise
fingerprint changes, but they do not turn generic routing into a byte-aware
additive approval service. Full composed integration remains Phase 6 work.

## Evidence, validation and limits

The retained handoff is a review conclusion, not emitted by the replay helper.
It preserves every raw and routed blocker and adds missing-context/source
findings from the skill review. Verification stays inconclusive, applicable
slicer/build verification stays required and profiles remain unverified. Source
truth, physical applicability and human identity are not authenticated by hashes.

`tests/evaluation/test_additive_retained_reviews.py` checks exact replay, schemas,
state/handoff relationships, byte identities, case-specific findings, unchanged
profiles and consequential invalidation. The repository schema-instance command
now includes additive packet states/handoffs. Tests reject attempts to promote
these unresolved packets by changing only status/approval labels.

Rejected alternatives: trust fixture readiness labels as evidence; substitute a
generic route result for mesh/package checks; invent material/slicer parameters;
or add a production approval API before the composed workflow has been validated.
The [packet rubric](../evaluation/additive-runs/README.md) records the controlled
review request and acknowledges same-agent, known-case evaluation limitations.

Reopen this convention when adding typed additive context, full byte-aware
approval integration, changed source/fixture identities or new package/process
semantics. Preserve historical packets; do not silently regenerate prior
conclusions to satisfy a changed gate.
