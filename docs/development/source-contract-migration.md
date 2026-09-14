# Profile source-contract migration

## Change and affected users

This change tightens the shared source definition in `handoff.schema.json`, used by machine, controller, material, tool, and post profiles. It replaces the contract present at `07058e8`; schema identifiers are unchanged during this unreleased development series. No release date or migration deadline is promised. Consumers must migrate before validating profiles with the tightened schema or routing jobs that embed them.

Previously, a record could omit scope and publication availability, could not declare a `claims` field, and accepted any nonempty access-date string. The new required fields are:

| Field | Required value |
| --- | --- |
| `title`, `publisher`, `locator` | Nonblank identifying text; a locator may be a stable identifier or local evidence reference, not necessarily a public URL |
| `published_at` | Known publication/revision text, or explicit `null` if unavailable |
| `accessed_at` | Actual access date in `YYYY-MM-DD` calendar form |
| `scope` | Nonblank applicability and limitations statement |
| `claims` | Nonempty array of distinct nonblank supported statements |

## Required migration

1. Preserve the old profiles, job state, and original approval records in their existing controlled storage. Do not copy confidential evidence into this public repository.
2. Inspect the actual source. Fill the new fields from evidence, including limitations. If the source cannot be accessed or does not support the claim, keep the job blocked and request source verification; do not insert placeholder claims to obtain a pass.
3. Preserve a known publication/revision value. Use `null` only when it is unavailable. Keep the recorded access date accurate rather than replacing it automatically with today's date.
4. Validate the complete profile using its profile schema with format checking enabled. Repository examples and declared profile fixtures are checked by the command below; external profiles are not automatically discovered.
5. Re-route jobs with migrated embedded profiles. Their fingerprint changes because source metadata is part of profile content. Obtain a new scoped review when appropriate; retain the original reviewed fingerprint and invalidation evidence. The fingerprint algorithm remains version 2.

```text
python scripts/validate_schema_instances.py
python -m unittest tests.schema.test_source_contract tests.routing.test_job_router -v
```

The repository's synthetic profiles now describe only their test declarations. Their metadata does not turn synthetic limits, compatibility labels, or verified-status fields into OEM or practitioner evidence.

## Compatibility and fallback

Old consumers that prohibit unknown properties will reject the new `claims` field; old minimal profiles will fail the new schema. Keep incompatible versions separate while consumers migrate. There is no lossless automatic downgrade of the evidence contract. If migration cannot be completed, retain the old artifacts for audit and keep affected jobs review-required; do not remove evidence fields or weaken validation to recover an approved state.

Schema checks establish field shape and calendar syntax, not source truth, freshness, reviewer authority, or safety. The broader source registry has additional review controls. Unmapped process-specific context objects and arbitrary nested values still need their own contracts. Report migration issues through the repository's contribution process without attaching confidential files.
