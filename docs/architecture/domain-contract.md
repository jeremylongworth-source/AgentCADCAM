# CAD/CAM Skills Domain Contract

## Status

Draft foundation contract for `CADCAM_01_DOMAIN_CONTRACT_READY`. It becomes frozen when the Phase 0 exit criteria are met.

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

The repository may provide intake, review, planning, static inspection, simulation-readiness analysis, source-backed recommendations, and human-review packages. Outputs remain draft or reviewable unless all applicable gates are satisfied and a human explicitly approves them.

## Prohibited capabilities

The repository must not control or start physical machines, activate spindles or beams, bypass guards or interlocks, configure safety PLCs, deploy posts autonomously, perform autonomous probing, or claim engineering, regulatory, export-control, or safety certification.

## Evidence and vendor neutrality

Claims about machines, controllers, materials, tooling, processes, safety, and regulation require source metadata. Core contracts describe capabilities and relationships, not a particular commercial product. Profiles and adapters may add vendor-specific detail without becoming required runtime dependencies.

## Approval model

Approval is explicit, scoped to a job revision and context fingerprint, time-bounded where appropriate, and invalidated by consequential input changes. A generated artifact cannot self-approve. `REVIEW_REQUIRED` is the default for manufacturing guidance.

## Relationship to AgentManufacturing

This repository is an independent sibling project with its own taxonomy, router, state model, fixtures, tests, and versioning. Future interoperability must use explicit handoff schemas. No required import, installation, or runtime dependency on AgentManufacturing is permitted.

## Validation notes

The contract is implemented by the schemas in `contexts/schemas/`, the router contract in `router/`, and the standards in `docs/standards/`. Phase 0 remains open until personas, workflow definitions, and the taxonomy have been reviewed together.

## Open questions

- Which AgentSkills metadata conventions should be adopted as a compatibility profile without coupling the core to one host implementation?
- Which minimum evidence fields are required for each jurisdiction specialization?
- Which machine-readable approval states should be shared across all four workflow families?
