# Source Freshness Process

## Purpose

Source-backed manufacturing claims can become stale as machine manuals, controller behavior, material profiles, standards, and regulations change.

## Required source record

Every non-trivial claim should record publisher, title, locator, publication or revision date when available, access date, scope, and supported claim. The source registry is `docs/sources/source-registry.yaml`.

## Review cadence

- Recheck safety and regulatory sources before each public release and whenever a jurisdiction specialization changes.
- Recheck machine, controller, postprocessor, tooling, and material sources when a profile or adapter changes.
- Mark a source `stale`, `conflicted`, or `verification_required` instead of silently substituting a generic assumption.
- Record the review date and affected skills or fixtures in the change or handoff record.

## Limits

Freshness checks do not prove that a source is applicable to a particular machine, material, job, or jurisdiction. Applicability remains a separate review decision.
