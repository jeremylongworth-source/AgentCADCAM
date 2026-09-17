# Getting started

Start with the supplied synthetic fixture before adapting the project to your own evidence. No machine connection is needed or supported.

## 1. Set up the checkout

Install Git and Python with `venv` and `pip`. The current portable development environment uses Python 3.14; this is an exercised environment, not a compatibility guarantee for every version or platform.

```sh
git clone https://github.com/jeremylongworth-source/AgentCADCAM.git
cd AgentCADCAM
python -m venv .venv
```

In PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

In a POSIX shell:

```sh
source .venv/bin/activate
```

If activation is unavailable, invoke `.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on POSIX directly. Do not weaken system execution policy just to activate an environment.

```sh
python -m pip install -r requirements-test.txt
python scripts/validate_foundation.py
python scripts/validate_schema_instances.py
```

The test dependencies include YAML, schema and Markdown validation, and the existing DXF checks. Optional CAD generation is separate; see [Development and validation](Development-and-Validation.md).

## 2. Inspect a fixture

Run from the repository root:

```sh
python scripts/cad_handoff_checks.py fixtures/cad/bracket/fixture.yaml
```

This reviews the initial bracket bundle and its supported source/derivative checks. Inspect `status`, `blockers`, `findings`, and `file_checks` in the JSON output. The command returns 1 for a blocked review and 0 otherwise. A non-blocked result still requires review and is not a complete integrated handoff or manufacturing approval.

Selected fields from the supplied fixture's current result:

```json
{
  "status": "review_required",
  "blockers": [],
  "review_required": true,
  "execution_allowed": false,
  "geometry_equivalence_verified": false
}
```

The empty blocker list is scoped to these fixture checks. Independent geometry
verification and manufacturing interpretation remain outside this result.

Fixture values are test data, not machining recommendations. Do not replace missing evidence with fixture declarations to make a real job pass.

## 3. Select skills deliberately

Use the [workflow guide](Workflow-Guide.md) to select a manifest in `skillsets/`. Read each referenced `skills/<name>/SKILL.md`, repository instructions, and relevant contracts. Configure your agent host to load those resources using its supported mechanism.

There is no universal installation command or default all-skills bundle here. YAML manifests describe composition; they do not execute an agent, install dependencies, or enforce host permissions. Deterministic utilities and skill instructions are complementary layers.

For a first agent-assisted exercise, ask:

> Review the supplied CAD bracket fixture using the design-handoff skillset. Preserve artifact identity, revisions and units. Report missing evidence and required reviewer actions. Treat fixture data as synthetic; do not approve manufacture or operate equipment.

Check the response against the actual artifacts and [safety contract](Safety-and-Approvals.md). The prompt alone is not a test result.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Missing Python module | Confirm the active interpreter and install `requirements-test.txt` into it. |
| File not found | Run from the repository root; preserve the fixture layout. |
| Review returns blockers or exit 1 | Read the findings. Missing evidence and unsupported semantics are expected blocking outcomes. |
| Source or review record is stale | Follow the migration contracts; do not refresh dates or fingerprints without a real review. |
| Native CAD import/export failure | Use the separate native environment; portable tests do not verify a CAD-kernel installation. |

Next: [Workflow guide](Workflow-Guide.md) or [Architecture and evidence](Architecture-and-Evidence.md).
