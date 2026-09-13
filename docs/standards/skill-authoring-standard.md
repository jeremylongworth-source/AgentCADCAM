# Skill Authoring Standard

Every skill must define a narrow purpose, intended users, supported inputs, outputs, assumptions, source requirements, stop conditions, review status, and test fixtures. Skill metadata must identify its name, version, owner, and supported consequence levels.

Skills must be composable and vendor-neutral by default. They may report `MISSING_CONTEXT`, `SOURCE_VERIFICATION_REQUIRED`, `SIMULATION_REQUIRED`, `HUMAN_APPROVAL_REQUIRED`, or `BLOCK_EXECUTION`. They must not invent consequential parameters or claim certification.

## Metadata contract

Keep `name` and `description` at the frontmatter root. Store repository-specific fields under `metadata`, whose keys and values are strings in the [AgentSkills specification](https://agentskills.io/specification). This avoids adding unsupported top-level fields or encoding a YAML list where clients expect text.

```yaml
metadata:
  version: "0.1.0"
  owner: "AgentCADCAM maintainers"
  supported-consequence-levels: "manufacturing_planning execution_adjacent"
  short-description: Review a bounded manufacturing plan
```

The repository requires:

- `version`: a quoted [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) value. The skill's documented inputs, outputs, stop conditions, and supported scope form its contract. Record contract changes in the changelog; initial `0.x` versions do not promise stability or prove a release gate.
- `owner`: a nonempty maintainer identity or maintenance role. The initial value names the repository maintenance role, not a job reviewer, safety officer, or engineering approver. It grants no authority over manufacturing decisions.
- `supported-consequence-levels`: a whitespace-separated, nonempty list of unique review levels from `informational`, `design_advisory`, `manufacturing_planning`, and `execution_adjacent`. Choose the levels supported by the skill's actual contract, not every possible topic it could explain.

`live_execution` is not supported. Intake may recognize and refuse that intent without declaring it a supported operation. Metadata is descriptive; it must never lower the router's consequence classification, clear a blocker, replace evidence, or authorize tools or machine actions. An execution-adjacent declaration means the skill can review that context, not execute it.

Preserve optional string metadata such as `short-description` and client-specific extension fields. No UI invocation policy change is required to add these fields. Existing workflow instructions remain the authority for inputs, findings, and stop conditions.

## Validation

Run `python scripts/validate_foundation.py` and `python -m unittest tests.foundation.test_skill_metadata -v`. Checks cover required fields, string metadata, name/description constraints, version syntax, placeholders, duplicate/unknown consequence levels, and routed skillset default-level coverage in the test suite. The bundled skill-creator quick validator provides a separate packaging check when available; it does not replace behavioral evaluation.

The metadata addition initializes previously undeclared per-skill versions to `0.1.0`. It does not retroactively version earlier artifacts or change approval fingerprints. No skill workflow, tool permission, or machine-control capability is added by this migration.
