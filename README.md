# AgentCADCAM

**Evidence-driven CAD/CAM review for AI agents.**

AgentCADCAM helps agents review digital designs and prepare traceable manufacturing handoffs. It combines focused AgentSkills-style instructions, structured job context, deterministic routing, and local file checks across CAD handoff, three-axis CNC milling, FDM additive manufacturing, and laser cutting.

**Review and planning only.** AgentCADCAM does not control equipment or authorize manufacturing. Missing consequential evidence remains a blocker, not a lower confidence score.

[Getting started](docs/wiki/Getting-Started.md) · [Workflow guide](docs/wiki/Workflow-Guide.md) · [GitHub Wiki](https://github.com/jeremylongworth-source/AgentCADCAM/wiki) · [Roadmap](ROADMAP.md) · [Contributing](CONTRIBUTING.md)

## Why AgentCADCAM?

A readable file is not necessarily a complete product definition. A matching postprocessor name is not proof of compatible NC output. A successful check is not permission to run a machine.

AgentCADCAM makes those distinctions explicit. It helps reviewers:

- Preserve source identity, revisions, units, and design intent across a handoff.
- Identify missing or conflicting machine, material, tooling, setup, and process evidence.
- Keep findings tied to the artifact bytes and job context that were reviewed.
- Invalidate dependent review records when consequential inputs change.
- Produce clear blockers and reviewer actions instead of unsupported readiness claims.

The project is standalone and vendor-neutral. It has no required dependency on AgentManufacturing, a particular CAD/CAM application, or a live machine connection.

## Workflow coverage

| Workflow | Review focus | Current implementation boundary |
| --- | --- | --- |
| CAD and design handoff | Provenance, exchange formats, manufacturability, drawings and PMI | Five skill contracts; file-aware checks target the initial bracket adapter, not arbitrary CAD models. |
| Three-axis CNC milling | Machine match, setup, tooling, strategy, post identity, NC and simulation evidence | Seven skill contracts; static NC checks support a restricted literal dialect and explicit coordinate model. |
| FDM additive | STL/3MF intake, mesh findings, printer/material context, slicer and environmental evidence | One skill contract; bounded mesh/package inspection, not a slicer or printability guarantee. |
| Laser cutting | DXF/SVG geometry, units, path intent, material/process context, beam and emission review | One skill contract; bounded planar geometry checks, not a laser controller or safe-settings generator. |

The [workflow guide](docs/wiki/Workflow-Guide.md) maps each family to its skillset, inputs, evidence, and limitations.

## Project status

**Pre-release — public-alpha acceptance is pending.**

The repository contains 14 atomic skill contracts and five skillset manifests. Four workflow manifests are marked `validated_synthetic`; the cross-workflow verification manifest remains `planned`. Local routing, state, file-review, and handoff utilities are implemented and tested against curated fixtures.

Phases 0–6 are accepted for repository development within that bounded corpus. Phase 7 release requirements and Phase 8 qualified real-input pilot validation remain open. These are development milestones, not manufacturing approvals.

See the [current status and evidence](docs/development/roadmap-reconciliation.md) and [public-alpha gate review](docs/development/public-alpha-gate-review.md). Test counts and historical gate labels are not completion guarantees.

## Quick start

### Explore the skills

Start with a [workflow skillset](docs/wiki/Workflow-Guide.md), then read its referenced `SKILL.md` files and the repository's [agent instructions](AGENTS.md). Skillsets are composition manifests, not a universal installer. Host-specific loading and permissions must be configured separately; copying a skill does not install the Python review utilities.

### Run the local checks

You need Git and Python with `venv` and `pip`. The portable checks have been exercised in the development environment with Python 3.14; optional native CAD tooling uses a separate [documented environment](docs/development/cadquery-windows.md).

```sh
git clone https://github.com/jeremylongworth-source/AgentCADCAM.git
cd AgentCADCAM
python -m venv .venv
```

Activate the environment with `.venv\Scripts\Activate.ps1` in PowerShell, or `source .venv/bin/activate` in a POSIX shell. If PowerShell activation is restricted, use `.venv\Scripts\python.exe` directly rather than changing system execution policy.

```sh
python -m pip install -r requirements-test.txt
python scripts/validate_foundation.py
python scripts/validate_schema_instances.py
python -m unittest discover -s tests -p "test_*.py"
```

These commands validate the repository and its fixtures. They do not approve a real job or require equipment access.

### Try a bounded review

From the repository root, inspect the supplied CAD fixture:

```sh
python scripts/cad_handoff_checks.py fixtures/cad/bracket/fixture.yaml
```

Read the JSON findings and blockers. A `blocked` result returns exit code 1 and is an expected review outcome, not an instruction to remove the gate. Even `review_required` is not manufacturing approval. For setup details and result interpretation, see [Getting started](docs/wiki/Getting-Started.md).

## How it fits together

1. **Skills** define the review duties, evidence requirements, and stop conditions.
2. **Context and state** record the job, artifact identities, profiles, verification, and scoped review records.
3. **Routing and file checks** select the workflow and examine the supported inputs for missing, stale, or conflicting evidence.
4. **Handoff review** checks the package against current state and preserves unresolved blockers for qualified human review.

The structured APIs keep `review_required: true` and `execution_allowed: false`. An empty blocker list or a recognized review record never grants physical execution authority.

## Safety and limitations

- No machine control, program upload, autonomous start, spindle/beam activation, or guard/interlock bypass.
- No general CAD/PMI interpretation, full collision proof, engineering certification, or final legal/export classification.
- Source metadata and hashes establish recorded consistency, not authenticated reviewer identity, source truth, ownership, or physical machine state.
- Synthetic fixtures and retained development reviews do not establish practitioner usefulness or production suitability. Actual retained fixture handoffs remain blocked.
- Portable code checks are not an OS sandbox. Optional native-tool experiments have separate dependencies and limited evidence scope.
- Reserved specializations are not implemented process or jurisdiction modules.

Read [Safety and approvals](docs/wiki/Safety-and-Approvals.md) before using a result in a manufacturing-facing workflow. Report vulnerabilities or unsafe-ready-state behavior according to [SECURITY.md](SECURITY.md); check its current private-channel availability before sending sensitive information.

## Documentation

| Resource | Start here for |
| --- | --- |
| [Documentation hub / wiki source](docs/wiki/Home.md) | Guided onboarding and topic navigation |
| [Architecture and evidence](docs/wiki/Architecture-and-Evidence.md) | Router, state, source assessments, and handoff contracts |
| [Development and validation](docs/wiki/Development-and-Validation.md) | Contributor setup, checks, and optional tooling |
| [Pilot evaluation](docs/wiki/Pilot-Evaluation.md) | Real-input packets and qualified reviewer requirements |
| [Roadmap](ROADMAP.md) | Governing scope, phase gates, and deferred capabilities |
| [Changelog](CHANGELOG.md) | Development changes and compatibility notes |

Wiki content is maintained in this repository for publication to the [GitHub Wiki](https://github.com/jeremylongworth-source/AgentCADCAM/wiki). The [publishing guide](docs/development/wiki-publishing.md) records availability and the maintenance workflow.

## Contributing

Useful contributions include reproducible defect reports, supported format cases, source-backed review improvements, and consented, sanitized practitioner evaluations. Keep changes focused and include positive and negative evidence for consequential decisions.

Read [CONTRIBUTING.md](CONTRIBUTING.md), [AGENTS.md](AGENTS.md), and the [Code of Conduct](CODE_OF_CONDUCT.md). Do not include confidential CAD, proprietary NC, credentials, or export-sensitive information in public reports.

## License

AgentCADCAM is licensed under the [MIT License](LICENSE). Third-party sources and fixture inputs retain their own terms; see the [fixture licensing policy](docs/standards/fixture-licensing-standard.md). The repository license does not grant rights to manufacture or redistribute someone else's design.
