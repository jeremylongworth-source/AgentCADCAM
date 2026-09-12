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

The repository is in foundation development. Work is proceeding through the gates in [ROADMAP.md](ROADMAP.md). The first target is `CADCAM_02_FOUNDATION_READY`.

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
