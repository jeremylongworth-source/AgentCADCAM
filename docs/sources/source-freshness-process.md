# Source Freshness Process

## Purpose

Source-backed manufacturing claims can become stale as machine manuals, controller behavior, material profiles, standards, and regulations change.

## Required source record

Every non-trivial claim should record publisher, title, locator, publication or revision date when available, access date, scope, and supported claim. The source registry is `docs/sources/source-registry.yaml`.

The version-2 registry uses unique stable `id` values, `title`, `publisher`, HTTPS `locator`, `publication_or_revision` (explicit null when not established), quoted ISO `accessed_at`, `authority`, `review_status`, `scope`, `sections`, `applies_to`, and a nonempty list of `claims`. Do not infer publication dates from a search engine's crawl date. Archived documentation may support a narrowly scoped historical fact, but cannot establish current software compatibility.

`reviewed` records that the listed claims were checked against the indicated source sections on the access date. It is not human engineering signoff, a general endorsement of the source's other statements, or automatic certification of currentness. A format reference must declare that format in `applies_to`; a title and URL alone do not establish applicability.

## Offline validation

`python scripts/validate_format_registry.py` checks all nine format entries and their source links. It also runs inside `python scripts/validate_foundation.py`. The checks reject empty registries, absent policy fields, duplicate source IDs/YAML keys, missing claim metadata, invalid/future access dates, citation mismatches, and referenced sources marked stale, conflicted, or verification-required. Community references cannot supply primary format evidence.

The format registry uses one `## Format name` section per roadmap format, with single-line `- Field label: value` entries for its eight policy fields and `Sources`. Each source citation uses the source ID as its Markdown link label and the exact registry locator as its target. This convention makes missing fields and reference drift testable without duplicating the policies in another data file.

These checks perform no network requests and do not read the linked source contents. Reviewers must still confirm claim support, version, conflicts, and applicability. The initial populated records cover format semantics only; machine/tool/material, safety, regulatory, and jurisdiction-specific claims still require their own evidence review.

## Review cadence

- Recheck safety and regulatory sources before each public release and whenever a jurisdiction specialization changes.
- Recheck machine, controller, postprocessor, tooling, and material sources when a profile or adapter changes.
- Mark a source `stale`, `conflicted`, or `verification_required` instead of silently substituting a generic assumption.
- Record the review date and affected skills or fixtures in the change or handoff record.

## Limits

Freshness checks do not prove that a source is applicable to a particular machine, material, job, or jurisdiction. Applicability remains a separate review decision.
