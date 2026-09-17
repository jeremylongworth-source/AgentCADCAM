# Profile lifecycle migration

## Affected contracts

Profiles from `9b2fb81` or earlier need a `lifecycle` record before use with the tightened machine, controller, material, tool, or post schemas. This is an unreleased breaking change with unchanged schema IDs, not a stable-release compatibility promise or a dated rollout commitment. Shared source requirements still apply.

The [profile standard](../standards/context-profile-standard.md) defines revision, applicability, quantity-unit declarations, and revision-scoped verification. A source publication revision and a post's executable `post_version` are not substitutes for the controlled profile revision.

## Required steps

1. Preserve existing profiles, job snapshots, and approval records in authorized storage. Do not publish private manufacturer or job evidence as part of migration.
2. Assign the controlled profile-record revision, or use null if it cannot be established. Record actual applicability and units; do not derive units from filenames or insert defaults to obtain a pass.
3. Initialize verification as unknown or unverified when no qualifying review exists. Use null reviewer/timestamp/reviewed-revision fields, an empty evidence list, and notes stating the missing review. Never infer verification from a previously set job approval or post validation flag.
4. When a review exists, preserve the actual reviewer, timestamp, reviewed revision, references, scope, and limitations. A verified declaration requires nonempty evidence and its reviewed revision must match the current profile revision for routing to recognize approval.
5. Validate the full profile with its schema, then re-route affected jobs. New lifecycle content changes the embedded profile and therefore the version-2 job fingerprint. Preserve the old reviewed fingerprint and require renewed job review when applicable; do not automatically re-sign approvals.

```text
python scripts/validate_schema_instances.py
python -m unittest tests.schema.test_profile_lifecycle tests.routing.test_job_router -v
```

These commands validate declared repository instances and regression cases, not arbitrary external profiles or physical equipment. The committed fixture profiles remain unverified. Test-only review records are generated in memory and are not migration defaults for real jobs.

## Compatibility and fallback

Old strict consumers reject the new field; new validators reject older minimal profiles. Coordinate producer/consumer versions rather than stripping lifecycle evidence. If review or migration cannot be completed, retain the old artifacts for audit and keep the affected job review-required or blocked. No automatic downgrade or approval restoration is provided.

`route_job` reports `SOURCE_VERIFICATION_REQUIRED` and `HUMAN_APPROVAL_REQUIRED` for unverified or revision-mismatched supplied profiles. A provisionally matching approved record becomes an invalidated copy; malformed profile schemas may prevent recognition of approval before that stage. Neither path mutates original inputs. General job simulation/tooling/setup gates remain independent, and successful lifecycle checks do not clear those blockers.

Reviewer authentication, source truth/freshness, actual unit conversions, and applicability to the intended machine/process remain external review responsibilities. Report compatibility problems using synthetic reproductions through the contribution process.
