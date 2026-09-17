# Reviewable handoff contract

## Purpose and boundary

`contexts/schemas/handoff.schema.json` defines a portable review package for the four initial workflow families. It now represents every handoff field required by the [execution boundary](execution-boundary.md), including incomplete findings. The [example](../../contexts/examples/handoff.example.json) is intentionally review-required with unknown context, not a manufacturing-ready fixture.

The schema checks record shape and declared-status consistency. It does not create an approval, authenticate a reviewer, inspect evidence references, match a package to current job state, or enable physical execution. Every status requires `review_required: true` and `execution_allowed: false`.

## Required fields

| Field | Meaning and unknown representation |
| --- | --- |
| `handoff_id`, `job_id`, `revision` | Nonblank package and controlled-job identifiers |
| `process_family`, `consequence_level` | Explicit routing context; unknown family requires a blocker, and live execution is representable only as a blocked refusal |
| `units` | Declared job units, or `null` with a blocker when unavailable; this does not prove unit consistency across files |
| `artifacts` | Controlled identities using the shared artifact contract, including path, kind, SHA-256, revision, and authority; an empty inventory requires a blocker |
| `context_fingerprint`, `context_fingerprint_version` | Current reviewed bounded-state fingerprint using version 2, or `null` fingerprint with a blocker; a correctly shaped hash is not proof of a match |
| `assumptions` | Statements with `unresolved`, `resolved`, or `rejected` status and evidence references; use an explicit empty list only when no assumptions remain to report |
| `verification` | Check IDs, `not_run`/`passed`/`failed`/`inconclusive` statuses, summaries, and evidence references; no performed checks means an empty list and a blocker |
| `simulation` | Status, reason, required-check descriptions, and evidence references; `unknown` preserves an undecided requirement rather than asserting simulation is unnecessary |
| `human_review` | Nonblank next action, nonempty unique review scope tokens, and responsible reviewer role; this identifies required work, not an authenticated reviewer |
| `blockers` | Explicit nonblank unique blocker strings; do not drop consequential findings to obtain a schema pass |
| `approval_id` | Referenced review-record identity, or `null`; an old record may remain referenced by an invalidated package for audit |
| `status`, `review_required`, `execution_allowed` | Package declaration and mandatory non-execution boundary |

Evidence references are nonblank unique strings. They may identify controlled local records or stable external evidence without embedding confidential contents. Validation does not open or dereference them.

## Consistency rules

- A `resolved` assumption, `passed` verification check, or `verified` simulation must reference evidence, even in a draft.
- Unresolved/rejected assumptions, absent or non-passing verification, unknown/required/failed simulation, missing context fingerprint/units, unknown family, and empty artifact inventory require at least one blocker. The schema does not infer which blocker or assess its adequacy.
- Simulation states `required`, `failed`, and `verified` need a nonempty `required_checks` list. `not_required` needs an explicit reason and an empty required-check list. A reason string is not an expert judgment of applicability.
- `blocked` and `invalidated` statuses require blockers. Live-execution declarations must be `blocked` and include `BLOCK_EXECUTION`, regardless of any review-record reference.
- `approved` requires no blockers, known units/family/fingerprint, a nonblank approval reference, a nonempty inventory containing an authoritative source and no unknown authority labels, only resolved assumptions, and nonempty passed verification with evidence.
- An approved simulation declaration must be either verified or explicitly not required. Approved execution-adjacent CNC handoffs require verified simulation; lowering a supplied consequence label must never bypass the router's classification.

## Consumer responsibilities

Before recognizing a handoff's declared approval, a consumer must independently establish authorization to inspect its contents, check artifact identities and revisions, compare the bounded-state fingerprint and version, resolve the approval record, and verify its scope and current routing result. It must also reconcile the handoff's assumptions, findings, simulation, and verification statements with the evidence and reviewed job context. A copied hash, approval ID, or `approved` label cannot establish any of these facts.

The existing `route_job` evaluates bounded state and approval records; it does **not** consume this serialized handoff or authenticate its evidence. Full cross-package binding and retained skill-assisted handoffs remain integration/pilot work. Do not treat a schema-valid package as a validated composed workflow. Physical operating procedures and qualified human decisions remain outside this repository's authority.

This contract leaves process-specific evidence details open rather than inventing universal simulation or inspection requirements. Reusable profile lifecycle records and their routing checks are now defined in the [profile standard](../standards/context-profile-standard.md); the [foundation review](../development/foundation-content-review.md) distinguishes those declared records from downstream evidence verification.

## Verification and compatibility

`tests/schema/test_handoff_contract.py` covers complete declared packages, explicit unknowns, required fields, nested shape, contradictory approval states, simulation checks, evidence references, and refusal behavior. Its approved specimen uses dummy references to demonstrate that shape validation is not authentication.

```text
python -m unittest tests.schema.test_handoff_contract -v
python scripts/validate_schema_instances.py
```

Old minimal packages need the [handoff migration](../development/handoff-contract-migration.md). Changes to required review fields, supported processes, fingerprint semantics, or approval meaning require a contract review and regression updates; do not silently weaken a block for compatibility.
