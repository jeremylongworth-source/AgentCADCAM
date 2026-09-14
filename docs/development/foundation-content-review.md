# Foundation content review — 2026-09-13

## Decision and review boundary

`CADCAM_01_DOMAIN_CONTRACT_READY` is supported for repository architecture development. `CADCAM_02_FOUNDATION_READY` remains open because the implemented schemas do not yet express all mandatory foundation document contracts.

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
| Seven authoring/architecture standards | All seven roadmap standards were read together with approval, source-freshness, fixture licensing, execution boundary, and router contracts. | Resolve the schema/document mismatches below before claiming operational conformance. |
| Evidence hierarchy and source metadata | Hierarchy distinguishes primary sources from community discovery. The nine format policies cite scoped registry evidence. The shared profile source schema now requires publication availability, date, scope, and claims. | Source authority, truth, freshness, and applicability remain review judgments. Unmapped process-context objects are not covered by generic profile validation. |
| Nine context schemas and state schema | Local Draft 2020-12 validation checks definitions, local references, examples, and declared profile fixtures. Source constraints now reject incomplete metadata in all five profile schema consumers. | Profile standard calls for versioned, applicable, verified context, but machine/controller/material/tool profiles lack a consistent explicit profile-revision and verification contract. A source publication revision is not a profile revision. |
| Execution-adjacent handoff fields | Execution boundary requires artifact/context identity, assumptions, performed verification, unresolved blockers, simulation requirements, and human approval action. | `handoff.schema.json` currently allows artifacts/blockers/status and an approval ID but cannot carry all those fields because it rejects unknown properties. Extend and test the handoff contract, preserving incomplete/draft reporting without implying approval. |
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

Complete the handoff schema and profile lifecycle contracts first, with rejection and invalidation tests and migration notes. Then rerun this Phase 1 content review against actual implementations. Do not add workflow skills or reinstate public-alpha completion claims in the meantime. The full [roadmap gap register](roadmap-reconciliation.md) retains process-level evidence and practitioner-pilot work.
