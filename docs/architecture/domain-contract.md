# CAD/CAM Skills Domain Contract

## Status

The four-family domain contract is frozen for initial repository development under `CADCAM_01_DOMAIN_CONTRACT_READY`. The [2026-09-13 content review](../development/foundation-content-review.md) records the Phase 0 requirement checks and their evidence. This is a repository architecture decision, not practitioner validation, a foundation Phase 1 closeout, or manufacturing approval.

## Audience and scope

This contract is for skill authors, reviewers, router maintainers, evaluation authors, and users preparing digital manufacturing handoffs. It defines what the standalone repository may reason about and what it must refuse to authorize.

## Mission

Provide reusable, vendor-neutral reasoning and verification capabilities connecting design intent to a reviewable manufacturing handoff. The system can inspect supplied artifacts, identify missing context, recommend process or interoperability checks, classify consequences, and prepare approval packages.

## Users

- CAD and mechanical designers preparing manufacturing data.
- CAM programmers and machinists reviewing planning context.
- Manufacturing engineers reviewing process assumptions.
- Additive users and laser operators preparing digital jobs.
- DFM reviewers, suppliers, educators, and makers needing structured handoffs.
- Maintainers and evaluators authoring safe, evidence-backed AgentSkills.

## Supported workflow families

1. `cad_handoff`: design files, drawings, PMI, provenance, revisions, interoperability, and manufacturing handoff.
2. `cnc_milling`: three-axis milling planning and verification readiness.
3. `additive`: FDM print preflight using STL/3MF, printer, material, and slicer context.
4. `laser_cutting`: 2D DXF/SVG preflight, material compatibility, and process readiness.

## Allowed capability classes

The repository may provide intake, review, planning, static inspection, simulation-readiness analysis, source-backed recommendations, and human-review packages. A scoped human review record may be recognized only when its applicable checks pass. Even then, outputs remain reviewable and physical execution remains outside this system.

## Conditional capabilities

| Capability | Required condition | Missing or conflicting condition |
| --- | --- | --- |
| Artifact inspection or offline conversion | User-authorized files, established source/revision/units, declared transformation, and preserved original | Request context or source verification; do not silently promote a derivative to design authority |
| Machine, controller, material, or tooling recommendations | Applicable primary evidence, bounded process context, and explicit assumptions | Return source/machine/context blockers; do not invent consequential values |
| Static NC, slicer, or laser review | Known artifact identity and declared dialect/profile limits | Return scoped findings and required verification; parsing is not readiness |
| Independent offline simulation or geometry tooling | Explicit local scope, available tool, and traceable input/output identities; no live-machine connection | Report missing verification or simulation; do not fabricate a successful run |
| Recognition of human approval | Matching current fingerprint, scope, reviewer record, required context, and verification | Require review and preserve invalidation evidence; approval cannot suppress other blockers |
| Jurisdiction research routing | Explicitly selected jurisdiction and applicable authoritative sources | Request research or qualified review; make no final legal/export classification |

These conditions describe the permitted boundary, not a claim that every tool adapter or check is implemented. Integration status is recorded separately in the roadmap reconciliation.

## Prohibited capabilities

The repository must not control or start physical machines, activate spindles or beams, bypass guards or interlocks, configure safety PLCs, deploy posts autonomously, perform autonomous probing, or claim engineering, regulatory, export-control, or safety certification.

The initial process boundary is three-axis milling, FDM, 2D laser cutting, and CAD handoff. Other manufacturing processes and advanced variants listed in [the roadmap's v0.x exclusions](../../ROADMAP.md#4-explicit-v0x-exclusions) remain deferred; naming a taxonomy concept does not enable that process. Future expansion requires the roadmap's post-pilot domain-risk review.

## Evidence and vendor neutrality

Claims about machines, controllers, materials, tooling, processes, safety, and regulation require source metadata. Core contracts describe capabilities and relationships, not a particular commercial product. Profiles and adapters may add vendor-specific detail without becoming required runtime dependencies.

## Approval model

Approval is explicit, scoped to a job revision and context fingerprint, time-bounded where appropriate, and invalidated by consequential input changes. A generated artifact cannot self-approve. `REVIEW_REQUIRED` is the default for manufacturing guidance.

## Relationship to AgentManufacturing

This repository is an independent sibling project with its own taxonomy, router, state model, fixtures, tests, and versioning. Future interoperability must use explicit handoff schemas. No required import, installation, or runtime dependency on AgentManufacturing is permitted.

## Validation notes

The taxonomy, personas, four workflow definitions, consequence model, specialization rules, and execution boundary were reviewed together in the linked content review. Context schemas and routing implement parts of this contract; schema coverage gaps remain explicitly open under Phase 1. A new process, weaker boundary, or required sibling/vendor runtime dependency must reopen the architecture decision rather than silently alter it.

## Resolved foundation decisions

- AgentSkills compatibility: standard root fields and string-valued repository metadata are defined in the [skill authoring standard](../standards/skill-authoring-standard.md); no host-specific execution permission is implied.
- Jurisdiction evidence: the shared source contract requires title, publisher, locator, explicit publication/revision availability, access date, scope, and supported claims. Any future jurisdiction specialization must additionally identify its jurisdiction in scope and require explicit job selection. The Canada directory remains a reserved research location, not an active source-backed legal module.
- Shared job approval states: `not_requested`, `pending`, `approved`, `invalidated`, and `rejected`. A record is absent at `not_requested`; record schemas use the other four states. The [approval model](approval-model.md) defines review scope and invalidation, not machine authorization.

Unfinished foundation implementation and evidence questions are tracked in the content review rather than left as unresolved decisions already implemented elsewhere.
