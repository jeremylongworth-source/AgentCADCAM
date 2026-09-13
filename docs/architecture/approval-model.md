# Approval Model

## Purpose

Approval records establish human accountability for a bounded manufacturing handoff. They do not certify a design, process, machine, or legal status.

## Approval lifecycle

```text
not_requested -> pending -> approved
                      \-> rejected
approved -> invalidated
```

An approval is valid only for the exact job revision, source artifact hashes, units, process, machine, controller, setup, workholding, tooling, postprocessor, material, generated-output identity, and verification evidence in its context fingerprint.

## Rules

- Execution-adjacent outputs default to `REVIEW_REQUIRED`.
- Approval must identify the reviewer, scope, timestamp, context fingerprint, and notes or findings.
- An approval cannot suppress a safety, authorization, provenance, or regulatory-review blocker.
- Any field listed in `state/invalidation-rules.yaml` invalidates dependent approval.
- `approved` means a human accepted the stated review scope; it does not mean safe for every machine, operator, material, jurisdiction, or future revision.
- Live-execution requests remain `BLOCK_EXECUTION` regardless of approval state.

## Required reviewer action

The handoff must state what the reviewer inspected, what remains unresolved, and what machine or process procedure controls the final physical operation. Approval is never inferred from a successful generation, parse, or simulation step.

## Validation notes

The machine-readable approval record is `contexts/schemas/approval.schema.json`. The implementation in `state/state.py` returns `invalidation_reason` and `changed_fields` when an approved context changes. These audit fields are declared in the schema, while the original reviewer and reviewed context fingerprint remain preserved. Runtime-to-schema regression tests exercise this transition.

For persisted job routing, `route_job` verifies the record against the current fingerprint, required scope, and review timestamp before counting it as approval. Simulation and verification failures remain blockers even when a record matches. Version-1 fingerprints require a new review under the [version-2 migration](../development/fingerprint-v2-migration.md).
