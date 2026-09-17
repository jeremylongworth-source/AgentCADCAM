# CAD/CAM Skills

CAD/CAM Skills is a standalone, vendor-neutral AgentSkills-style repository for reasoning about digital designs and manufacturing handoffs.

The project connects:

`design intent -> representation -> process -> machine -> controller -> postprocessor -> verification -> human approval -> manufacturing handoff`

It provides structured review and planning guidance for:

- CAD and manufacturing handoff
- Three-axis CNC milling
- FDM additive manufacturing
- Laser cutting

It does not replace CAD/CAM software, qualified manufacturing professionals, machine safety systems, or human approval. Physical machine execution is outside the initial project boundary.

## Project status

The repository implements 14 skill contracts, five skillsets, and local review/routing utilities for the four initial workflow families. Automated tests cover a curated synthetic corpus; they do not establish full roadmap completion or manufacturing readiness.

The [current roadmap reconciliation](docs/development/roadmap-reconciliation.md) supersedes the earlier blanket claim that gates `CADCAM_01` through `CADCAM_08` were complete. Subsequent requirement reviews support gates `CADCAM_01` through `CADCAM_04` for repository development against the initial domain, foundation, CAD and CNC corpus; see the [CNC gate audit](docs/development/cnc-milling-gate-review.md). Additive/laser file validation, composed workflow evidence, and governance verification still need work before public-alpha acceptance and the real-input practitioner pilot. `CADCAM_09_PILOT_VALIDATED` requires qualified real-input review. [ROADMAP.md](ROADMAP.md) remains the governing requirements document.

## Repository map

| Directory | Purpose |
| --- | --- |
| `skills/` | Atomic AgentSkills contracts and implementations |
| `skillsets/` | Composable workflow manifests |
| `router/` | Deterministic workflow selection and consequence classification |
| `state/` | Bounded job-state model and invalidation rules |
| `contexts/` | Machine-readable job, machine, process, and approval context |
| `specializations/` | Optional process and jurisdiction-specific knowledge |
| `docs/` | Architecture, standards, formats, sources, evaluation, and handoffs |
| `fixtures/` | Reproducible positive and negative test inputs |
| `tests/` | Schema, routing, safety, interoperability, and evaluation tests |
| `scripts/` | Repository validation and maintenance utilities |

## Safety status

All manufacturing outputs are reviewable artifacts, never self-authorizing instructions. Missing or unverified consequential context must produce an explicit blocking outcome such as `MISSING_CONTEXT`, `SIMULATION_REQUIRED`, `HUMAN_APPROVAL_REQUIRED`, or `BLOCK_EXECUTION`.

See [SECURITY.md](SECURITY.md) and [docs/standards/safety-governance-standard.md](docs/standards/safety-governance-standard.md).

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a change. New skills must follow the authoring, evidence, interoperability, safety, testing, and evaluation standards.
