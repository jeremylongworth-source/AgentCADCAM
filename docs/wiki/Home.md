# AgentCADCAM documentation

AgentCADCAM provides reusable review instructions and local validation utilities for moving digital designs toward a traceable manufacturing handoff. It is intended for agent developers, CAD/CAM contributors, and manufacturing reviewers—not unattended machine operation.

**Pre-release:** public-alpha acceptance and qualified real-input validation remain open. The [roadmap reconciliation](../development/roadmap-reconciliation.md) records the current evidence and remaining gates.

## Choose your starting point

| Your goal | Guide |
| --- | --- |
| Set up a checkout and try a supplied fixture | [Getting started](Getting-Started.md) |
| Choose a workflow and understand required inputs | [Workflow guide](Workflow-Guide.md) |
| Interpret blockers, evidence, and review records | [Safety and approvals](Safety-and-Approvals.md) |
| Integrate the structured Python APIs | [Architecture and evidence](Architecture-and-Evidence.md) |
| Develop and validate a change | [Development and validation](Development-and-Validation.md) |
| Evaluate usefulness on real input | [Pilot evaluation](Pilot-Evaluation.md) |

## Scope and authority

The initial families are CAD/design handoff, three-axis CNC milling, FDM additive manufacturing, and laser cutting. Physical control, autonomous activation, safety-system bypass, certification, and final legal determinations are excluded. A passing check is never permission to manufacture.

These pages explain the project. The [roadmap](../../ROADMAP.md), [repository instructions](../../AGENTS.md), checked-in schemas, and scoped architecture contracts govern behavior. Follow those contracts when an overview is less specific; report inconsistencies rather than inventing context.

Wiki source is versioned alongside the code in `docs/wiki/`. See [publication and maintenance](../development/wiki-publishing.md). Use contracts from the revision matching your checkout; the hosted wiki and `main` may describe newer development.
