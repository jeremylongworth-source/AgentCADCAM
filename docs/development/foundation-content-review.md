# Foundation content review — 2026-09-13

## Decision and review boundary

`CADCAM_01_DOMAIN_CONTRACT_READY` is supported for repository architecture development. The 2026-09-14 follow-up below records `CADCAM_02_FOUNDATION_READY` for repository development after the handoff and reusable-profile contract gaps were addressed. Neither decision awards a workflow, public-alpha, or practitioner-pilot gate.

This is a Codex document/code review against [ROADMAP.md](../../ROADMAP.md), based on `07058e8` plus this change. It is not a qualified manufacturing, legal, safety, or practitioner review. It replaces neither the roadmap nor downstream evidence requirements. Historical gate handoffs are not used as proof of their own acceptance.

## Phase 0 acceptance

| Roadmap requirement | Inspected evidence and decision |
| --- | --- |
| Complete domain contract | [Domain contract](../architecture/domain-contract.md) now covers mission, users, four families, allowed/conditional/prohibited capabilities, evidence, vendor neutrality, approval, and sibling independence. Conditional boundaries and deferred processes are explicit. Met for architecture scope. |
| Taxonomy reviewed | [Taxonomy v1](../architecture/master-taxonomy-v1.md) defines all 24 roadmap concepts: design intent, geometry, assemblies, product definition, drawings, PMI, GD&T, revisions, manufacturability, materials, machines, controllers, setups, workholding, tooling, CAM strategies, process parameters, posts, NC, simulation, additive preparation, 2D cutting, verification, and handoff. Extra provenance/approval/jurisdiction terms support governance without enabling new processes. Met as vocabulary, not implementation of every concept. |
| Initial personas documented | [Personas](../architecture/personas-and-job-maps.md) identify eight reviewer/user roles with jobs and risks. Met; no user-research or pilot usefulness claim. |
| Initial workflows defined | The same document now defines four bounded intake/review/handoff sequences and their stop conditions. Routes cover those families plus `unknown`; no additional manufacturing family is enabled. Met as workflow contracts. |
| Execution boundary explicit | [Execution boundary](../architecture/execution-boundary.md), [consequence model](../architecture/consequence-model.md), and router contract distinguish reviewable output from live execution. Generated manufacturing artifacts cannot lower consequence below execution-adjacent. Met as architecture boundary. |
| Prohibited capabilities explicit | Domain and [prohibited capability](../standards/prohibited-capability-contract.md) contracts exclude physical actuation, safeguards bypass, autonomous posts/probing, and final certification/classification. The specialization model cannot weaken those blocks. Met. |
| No unresolved AgentManufacturing dependency | Requirements files, router/state/scripts, skill and skillset manifests, and context schemas contain no required sibling dependency. The domain contract mandates independent taxonomy/router/state/testing/versioning and explicit future handoff schemas. Met for inspected repository architecture. |

The metadata compatibility, common approval-state vocabulary, and minimum jurisdiction evidence policy are now recorded decisions rather than stale open questions. Canada remains a reserved opt-in research location, not an activated legal capability. Reopen Phase 0 for a new process, weaker execution boundary, or new required sibling/vendor dependency.

## Phase 1 acceptance and discovered gaps

| Requirement / contract | Current evidence | Remaining acceptance work |
| --- | --- | --- |
| Repository structure | Required architecture, standards, schemas, routes/state, fixture/evaluation directories, public contribution/security/license files exist; foundation validator checks required paths. | No structure gap found in this review. File presence does not prove content. |
| Seven authoring/architecture standards | All seven roadmap standards were read together with approval, source-freshness, fixture licensing, execution boundary, and router contracts. Handoff and reusable-profile lifecycle representations now implement the identified missing fields. | Process-specific applicability, source truth, and composed workflow evaluation remain separate evidence responsibilities. |
| Evidence hierarchy and source metadata | Hierarchy distinguishes primary sources from community discovery. The nine format policies cite scoped registry evidence. The shared profile source schema now requires publication availability, date, scope, and claims. | Source authority, truth, freshness, and applicability remain review judgments. Unmapped process-context objects are not covered by generic profile validation. |
| Nine context schemas and state schema | Local Draft 2020-12 validation checks definitions, local references, examples, and declared profile fixtures. All five reusable profile types now require source metadata and lifecycle revision/applicability/units/verification records. Routing checks reviewed/current revision equality. | The identified profile-representation gap is addressed. Arbitrary nested dimensional meaning, actual unit conversion, profile applicability, and reviewer authentication are not established by lifecycle declarations. |
| Execution-adjacent handoff fields | The extended [handoff contract](../architecture/handoff-contract.md) now carries artifact/context identity, assumptions, performed verification, blockers, simulation requirements, and human review action. Schema tests reject missing fields and contradictory status declarations while retaining explicit unknowns. | The Phase 1 field-representation gap is addressed. Schema validation does not bind the serialized handoff to external evidence, current job state, or an authenticated approval record; composed handoff evaluation remains downstream integration work. |
| Safety standard | Hard blocks, explicit human review, refusal of live execution, and non-self-authorizing artifacts are documented and tested in the curated corpus. | Passing schema or router tests is not complete safety recall, reviewer authentication, or proof of input authorization. These broader behavior checks remain downstream gate work. |
| Nine-format registry | All eight required policy fields and source citations are present and checked by the format validator. STEP-NC remains research-only. | Actual file-derived semantic preservation is workflow evidence, not established by policy presence. |
| Validation scripts | YAML/JSON, metadata, manifests, schema instances, local references, source records, and fixture references have explicit validators and negative tests. | The foundation CLI does not replace the separate schema-instance CLI. Keep renderer, nested-object, and harness-input exclusions visible. |
| Consequential invalidation | State implementation and YAML rules agree; tests mutate source/revision, units, process, machine/controller, setup/workholding, tools, post, material, generated output, verification, and authorization context. | No field-coverage gap found for the Phase 1 invalidation list. Authentication and completeness of supplied evidence are separate limitations. |

## Source-contract regression evidence

Before the fix, a matching CNC approval record was recognized even when the machine source lacked scope and claims. The old source schema also prohibited a `claims` field. Regression tests reproduced both behaviors.

The new shared source shape is exercised by `tests/schema/test_source_contract.py` across machine, controller, material, tool, and post profiles. Routing tests show that incomplete source metadata blocks recognition of approval and that changed embedded claims invalidate the old fingerprint. Ten synthetic source records were migrated with test-only scope; their declarations are not manufacturing facts. See the [migration instructions](source-contract-migration.md).

## Verification and next work

```text
python scripts/validate_foundation.py
python scripts/validate_schema_instances.py
python -m unittest discover -s tests
```

Recorded for this change: foundation validation passed (58 required files, nine context schemas, five skillsets); schema validation passed (ten definitions, thirteen declared instances); all 180 tests passed. These counts report executed checks, not a completion percentage or proof of manufacturing readiness.

Follow-up: the handoff schema now expresses the mandatory review fields, with 20 dedicated schema tests and a [migration guide](handoff-contract-migration.md). The original 180-test count above records the source-contract review, not this later follow-up.

## Phase 1 follow-up and exit decision — 2026-09-14

Baseline for this follow-up is `9b2fb81` plus the profile-lifecycle changes. The shared lifecycle record closes the last schema/document mismatch identified in this review. Nine fixture profiles remain explicitly unverified. Tests reproduce and reject approval recognition when a profile review references an old revision, and exercise unverified-profile blocking across all five profile types, four families, and review consequence levels.

| Phase 1 exit requirement | Observable evidence and assessment |
| --- | --- |
| Repository structure established | The foundation validator checks 58 required files and five skillset manifests; architecture, standards, contexts, router/state, source/fixture, and evaluation directories have their required contracts. Met. |
| Schemas validate | Draft 2020-12 definition/reference/instance checks pass for ten definitions and thirteen declared instances. Handoff/source/lifecycle negative tests and runtime approval conformance tests pass. Met for the declared schema scope. |
| Authoring standards established | Seven standards define skill contracts/metadata, evidence, interoperability, safety, testing, evaluation, and context lifecycle. Metadata checks cover all 14 existing skills. Met; this is not behavioral validation of the skills. |
| Evidence hierarchy established | Primary-source hierarchy, claim/scope metadata, source review process, fixture provenance/licensing rules, and missing-source rejection are implemented. Synthetic sources are labeled and are not primary manufacturing evidence. Met as repository evidence architecture. |
| Safety standard established | Live actions remain blocked, handoffs require review and prohibit execution, profile verification cannot be bypassed by a matching job approval, and consequential invalidation tests pass. Met as foundation architecture; full workflow safety recall remains a later gate. |
| Format registry established | Nine roadmap formats carry all eight policy fields and scoped source references; the format/source validator passes. STEP-NC remains research-only. Met as handling policy, not proof of all parsers or conversions. |
| Validation scripts operational | YAML/JSON, source/skill metadata, skillsets, schemas, local Markdown references, and fixture manifests have working positive/negative checks. All 211 tests pass. The documented CLI and test scopes remain explicit. Met. |

The separate Phase 1 invalidation requirement is also covered: source/revision, units, process, machine/controller, setup/workholding, tooling, post, material, and generated-output changes invalidate dependent approval. Lifecycle changes participate in the containing profile's fingerprint. No fingerprint algorithm change or automatic re-signing was introduced.

**Decision: `CADCAM_02_FOUNDATION_READY` for repository development.** This accepts the original Phase 1 architecture/validator deliverables, not a reduced manufacturing-ready claim. The earlier historical gate evidence alone was insufficient; this decision relies on the subsequent source, metadata, reference, schema, handoff, lifecycle, and invalidation work. Reopen the gate if those contracts cease to agree or their validators regress.

Next, validate the existing CAD handoff workflow against its required negative cases with file-derived findings and retained review output, then continue CNC/FDM/laser evidence work. Do not expand the 14-skill inventory merely because the foundation is ready. The full [roadmap gap register](roadmap-reconciliation.md) retains source applicability, process-specific validation, cross-package binding, adversarial behavior, and practitioner-pilot work. None of those are closed by the foundation decision.
