# Architecture and evidence

AgentCADCAM keeps instructions, persistent context, deterministic checks and human review distinct. The core is portable and vendor-neutral; optional native-tool observations do not become required machine integrations.

| Layer | Responsibility | Entry point |
| --- | --- | --- |
| Skills and skillsets | Review duties and focused composition | [Skills](../../skills/README.md), [workflow guide](Workflow-Guide.md) |
| Context schemas | Structured jobs, profiles, evidence and handoffs | [Profile standard](../standards/context-profile-standard.md), [handoff contract](../architecture/handoff-contract.md) |
| Job state | Consequential inputs and fingerprints | [State schema](../../state/state.schema.json), [integration model](../architecture/router-state-integration.md) |
| Request router | Structured request classification | [Router contract](../../router/router-contract.md), `router.router.route` |
| Integrated router | State, scoped evidence, actual bytes and review records | `router.job_router.route_job` and family integration contracts |
| Handoff consumer | Package consistency against current state and evidence | [Handoff binding](../architecture/handoff-state-binding.md), `router.handoff_review.review_handoff` |

## Choosing an API boundary

The request router is triage, not full job validation. Known/unknown flags cannot establish source truth, physical capability or permission. Use the integrated router for state-bound review; use the handoff consumer for a serialized package against current context.

These are local Python APIs, not a hosted service or equipment connector. They do not provide authenticated reviewer identity, durable job storage or an external approval service. Read signatures and matching contracts for your checkout rather than substituting sample flags for complete context.

Family byte gates are documented in the [CAD](../architecture/cad-router-integration.md), [CNC](../architecture/nc-artifact-approval-binding.md), [additive](../architecture/additive-router-integration.md), and [laser](../architecture/laser-router-integration.md) contracts. Unsupported profiles and semantics remain blockers.

## Source and governance controls

- [Source-review readiness](../architecture/source-review-readiness.md): scoped assessments, metadata identity, and current UTC review windows.
- [Governance readiness](../architecture/governance-readiness.md): permissions, confidentiality, restrictions and export-review declarations.
- [Source freshness](../sources/source-freshness-process.md): release/profile cadence and limits of offline metadata checks.
- [Claim inventory](../sources/skill-claim-ledger.md): policy versus primary-source rationale and fixture observations.

Do not auto-refresh dates or rewrite reviewed fingerprints after changes. New records must reflect a real review. See [source migration](../development/source-contract-migration.md) and [profile lifecycle migration](../development/profile-lifecycle-migration.md).

## Evidence limits

Schema validity establishes structure; a hash establishes identity; a regression establishes its asserted behavior. None alone establishes design meaning or manufacturing readiness. Retained same-agent reviews are separate from qualified [pilot evaluation](Pilot-Evaluation.md).
