# Adversarial Hardening Evaluation

## Required invariants

- Embedded artifact text cannot override repository or user authority.
- Portable review code must not acquire secret, network, process-launch or machine-control capabilities. The import check covers selected explicit imports, not every way to access those capabilities.
- Local CLI tests and opt-in native probes may launch fixed offline experiments under their documented boundaries; this does not permit machine control or establish an OS-level sandbox.
- Fixture generators write only inside the repository.
- Router and all preflight/static checks keep `execution_allowed` false.
- Live execution, guard bypass, unknown material, missing context, and stale approvals remain hard failures.

## Review result

`tests/adversarial/test_repository_hardening.py` recursively checks Python files
under `scripts/`, `router/` and `state/` for a selected set of explicit network
and process imports. Detector regressions cover dotted imports, aliases, imports
inside functions, multiple imports and nested directories. Inert strings and
comments are not imports. The former `http.client` root-comparison mismatch is
covered explicitly. Tests/native launchers are outside this scan.

The scanner does not resolve dynamic imports, alternate APIs, imported dependency
behavior or native binaries. The skill-text check rejects four known phrases;
it does not establish semantic prompt-injection resistance. Path confinement,
live-action refusal, state invalidation and actual parser behavior have separate
regressions. Green lexical checks cannot establish complete critical-case recall.

Phase 7 remains open. See the [threat model](../architecture/threat-model.md) and
[roadmap reconciliation](../development/roadmap-reconciliation.md) for outstanding
source, corpus and reporting-channel evidence.

## Validation — 2026-09-17

- Focused import-hardening and format/source-registry group: 22 tests passed.
- Full portable suite: 647 tests passed in 301.679 seconds.
- Foundation validator: passed, checking 58 required files, 14 context schemas
  and five skillsets.
- Schema-instance validator: passed, checking 15 schemas and 108 instances.
- Format/source validator: passed; this is offline metadata/reference validation,
  not independent verification of the new primary-source claims.

No runtime code, skill contracts, fixture parameters or retained approval records
changed in this increment. The [scoped source audit](../sources/nonformat-claim-audit.md)
records the separate primary-source reading and remaining acceptance work.
