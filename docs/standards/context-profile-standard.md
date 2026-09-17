# Context Profile Standard

Context profiles are explicit, versioned, and bounded. They must identify their authority, revision, units where relevant, source metadata, applicability, and verification status. Unknown, missing, conflicting, and unverified values must not be collapsed into a permissive default.

Changes to source artifact, revision, units, process, machine, controller, setup, workholding, tool, postprocessor, material, or generated output invalidate dependent approvals.

## Reusable profile lifecycle

Machine (including printer), controller, material, tool, and post profiles require a shared `lifecycle` object. The definition lives beside the shared source/artifact definitions in `handoff.schema.json`; it does not make a profile a handoff instance.

| Field | Contract |
| --- | --- |
| `revision` | Controlled profile-record revision, or explicit `null` when unknown. This is separate from design revision, source publication revision, controller firmware, and executable post version. |
| `applicability` | Nonblank scope and limitations. Identify the intended machine/process/version and whether this is synthetic test data. Do not claim broader applicability than the evidence supports. |
| `units` | Map of quantity names to declared unit strings; use null for a named unresolved unit. Use an empty map only when the profile declares no dimensional quantities. Machine/tool fixture lengths use `length`; CNC spindle speed uses `spindle_speed`. No conversion or consistency is inferred from this map. |
| `verification.status` | `unknown`, `unverified`, `verified`, `conflicted`, or `rejected`; none is a machine-operation authorization. |
| `verification.reviewed_revision` | Revision actually inspected, or null when no review has established it. |
| `verification.reviewer`, `reviewed_at` | Declared reviewer and ISO timestamp, or null when unavailable. These fields are not authentication. |
| `verification.evidence`, `notes` | Unique nonblank evidence references and an explicit scope/findings note; references are not fetched automatically. |

A `verified` declaration requires known current/reviewed revisions, a reviewer, timestamp, and nonempty evidence. Schema validation checks their shape. `route_job` also requires the reviewed revision to equal the current profile revision and blocks effective approval for unverified, conflicted, rejected, missing, or malformed supplied profiles. It retains copied review records and original fingerprints; it persists nothing. Declared `*_known` flags cannot replace profile verification. The checks apply to supplied reusable profiles across families and consequence levels, not just CNC NC review.

Maintain profile revision control when content changes. The complete embedded profile also participates in the version-2 job fingerprint, so changing lifecycle revision, applicability, units, or verification invalidates the previous job approval even if a caller forgets to bump a revision. A new matching job approval cannot override a profile review of another revision.

Setup is a job-specific context, controlled by the parent job revision/fingerprint and setup/WCS/workholding checks, not a reusable profile under this header. Workflow-specific process harness files are not silently recast as one of the five profile schemas.

## Evidence and validation limits

The profile's separate `source` identifies evidence publisher, locator, scope, and claims. A reviewer must assess authority, actual applicability, dimensional meaning, and conflicting facts before declaring verification. Shape checks cannot authenticate the reviewer, prove a source is true or fresh, or determine units for arbitrary nested capability/property objects. A declared verified record is not machine readiness. Process-specific geometry, package, parameter, and unit-conversion checks remain required downstream.

Nine reusable synthetic fixture profiles are initialized at profile-record revision `1` and remain `unverified`. Positive routing tests construct synthetic review declarations in memory; no practitioner review is implied. See the [migration guide](../development/profile-lifecycle-migration.md).

```text
python scripts/validate_schema_instances.py
python -m unittest tests.schema.test_profile_lifecycle tests.routing.test_job_router -v
```
