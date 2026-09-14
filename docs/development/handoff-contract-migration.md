# Handoff review-field migration

## Who must migrate

Producers and consumers of `handoff.schema.json` packages from `fe097d0` or earlier must update before using the extended schema. This is an unreleased development change with the same schema identifier, not a promised stable-version upgrade or a new release deadline. Shared source and artifact definitions retain their existing contracts.

Old packages could carry only IDs, status, artifacts, blockers, a review flag, and an optional approval ID. The extended contract requires routing/units, fingerprint/version, assumptions, verification, simulation, human review action/scope/role, an explicit approval reference or null, and `execution_allowed: false`. See the [field contract](../architecture/handoff-contract.md).

## Required steps

1. Preserve original packages, job snapshots, evidence, and approval records in their authorized storage. Do not publish private job data to obtain a test fixture.
2. Populate the new fields from the actual reviewed job and records. Use fingerprint version 2 only with its defined bounded-state algorithm; do not relabel an old hash. If current context is unavailable, use a null fingerprint and an explicit blocker.
3. Record unknown units as null, unresolved assumptions with their actual status, missing verification as an empty list or `not_run` checks, and undecided simulation as `unknown`. Add the corresponding blockers. Do not fabricate evidence or declare simulation unnecessary just to satisfy validation.
4. Describe the required human action, scope, and reviewer role. Use a null approval ID when no review record exists. Preserve old review references for audit without counting them as current approval.
5. Retain `draft`, `review_required`, `blocked`, or `invalidated` as appropriate until applicable review work is complete. A migration must not automatically promote a package to `approved`.
6. Validate the migrated package with `validator_for("handoff.schema.json")` from the local schema catalog. The repository command below checks its declared examples, not arbitrary external files. Consumers must separately perform the identity, evidence, scope, and routing reconciliation in the field contract.

```text
python -m unittest tests.schema.test_handoff_contract -v
python scripts/validate_schema_instances.py
```

The repository example was migrated with explicit missing context and no invented evidence. These commands test record consistency; they do not obtain a human approval or run a manufacturing simulation.

## Compatibility, fallback, and support

Older strict consumers will reject the new fields, and older minimal packages will fail the extended schema. Coordinate producer/consumer versions. If migration cannot be completed, retain the original package for audit and keep the job review-required or blocked; do not strip review evidence or disable validation to recover a ready state. No automatic or lossless downgrade is provided.

This serialization change alone does not alter the version-2 state fingerprint algorithm or re-sign approvals. Actual changes to reviewed job context still require invalidation and renewed scoped review. Handoff-only narrative edits also require comparison with what the reviewer actually accepted; unchanged state hashes are not proof that edited handoff text was reviewed.

Report schema or compatibility issues through the repository contribution process using synthetic reproductions. Reviewer authority, private evidence access, required simulation scope, and physical suitability cannot be supplied by migration tooling.
