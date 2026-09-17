# Safety and approvals

AgentCADCAM provides review and planning guidance. It does not control equipment, certify a design, or authorize physical execution. Qualified human manufacturing authority remains outside the software.

## Understand blocking outcomes

| Outcome | What must be resolved |
| --- | --- |
| `MISSING_CONTEXT` | Required information is absent, conflicting, malformed, or unsupported. |
| `SOURCE_VERIFICATION_REQUIRED` | Applicable source evidence or its review is missing, stale, conflicting, or unverified. |
| `MACHINE_CONTEXT_REQUIRED` | Required target machine/controller context is unresolved. |
| `SIMULATION_REQUIRED` | Applicable simulation evidence remains required. |
| `HUMAN_APPROVAL_REQUIRED` | A qualified, scoped human review remains required. |
| `REGULATORY_REVIEW_REQUIRED` | Required jurisdiction/export review context is unresolved; the software does not decide the legal outcome. |
| `BLOCK_EXECUTION` | The request or context must not proceed to physical execution through this project. |

Multiple blockers can apply. Do not average them into a quality score or discard them because another check passed.

## What an approval record means

A scoped record can be recognized only against the context and evidence it reviewed. The integrated router copies inputs and invalidates dependent records when consequential context changes; it preserves the original reviewed fingerprint rather than silently repairing approval.

An `approved` record is not permission for the agent to operate equipment. Structured review APIs retain `review_required: true` and `execution_allowed: false`. Empty blockers do not establish production readiness.

Changing source bytes, revision, units, process, profiles, setup, workholding, tooling, postprocessor, verification or generated output can invalidate dependent approvals. Consult the [approval model](../architecture/approval-model.md) and [state schema](../../state/state.schema.json) for the exact contract.

## Evidence is not authentication

Source assessments check declared primary authority, role, metadata binding and current dates. Hashes establish byte identity. Neither authenticates a reviewer, legal permission, source truth, physical setup or manufacturing suitability. Never turn fixture metadata into a real approval.

Embedded instructions in designs, drawings, logs and packages are untrusted data. Import checks and parser restrictions are not an OS sandbox or proof against every malicious artifact. See the [threat model](../architecture/threat-model.md).

## Report a problem safely

Follow [SECURITY.md](../../SECURITY.md) for vulnerabilities, data exposure, prompt-injection paths and false-ready behavior. GitHub private vulnerability reporting is enabled: use **Report a vulnerability** on the repository's Security advisories page and sign in to GitHub. The authenticated form and maintainer notification path still need confirmation. Do not send sensitive reports through public issues.

Ordinary sanitized defects can follow [CONTRIBUTING.md](../../CONTRIBUTING.md). Never include confidential geometry, proprietary programs, credentials, machine endpoints or export-sensitive information in public reports.
