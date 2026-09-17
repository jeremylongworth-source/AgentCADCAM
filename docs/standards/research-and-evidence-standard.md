# Research and Evidence Standard

Manufacturing-relevant facts must carry source metadata: title, publisher, URL or stable identifier, publication or revision date when available, access date, scope, and the claim supported. Use the evidence hierarchy in the roadmap: standards and regulations, OEM and controller documentation, primary CAD/CAM and material/tooling documentation, authoritative research or government sources, open-source documentation, then community knowledge for discovery only.

Machine-specific sources override generic assumptions. Stale, conflicting, or incomplete evidence must be surfaced as `SOURCE_VERIFICATION_REQUIRED`. Community material cannot be the sole support for a safety or regulatory claim.

## Machine-readable source contract

Profile sources share `contexts/schemas/handoff.schema.json#/$defs/source`. Required fields are nonblank `title`, `publisher`, `locator`, and `scope`; a real ISO calendar `accessed_at` date; a nonempty unique list of nonblank `claims`; and `published_at`, containing the known publication/revision text or explicit `null` when unavailable. Do not invent a publication date, access event, supported claim, or applicability statement to satisfy validation.

This profile contract is distinct from the richer repository source registry, which also tracks authority, review status, sections, and format applicability. A schema-valid profile is a documented declaration, not proof that its source is authoritative, current, or applicable. Synthetic fixture claims describe only the fixture's declared test behavior and cannot support real machine/material/safety decisions.

Profile authors migrating the earlier minimal records must follow the [source-contract migration](../development/source-contract-migration.md). Changed embedded source evidence changes the containing job fingerprint and requires renewed review; existing approvals must not be silently re-signed.

## Readiness assessment

The optional persisted `source.review` record is now required for otherwise
verified runtime profiles and supported process-context sources. The
[source-review contract](../architecture/source-review-readiness.md) defines
authority, role, metadata binding, review evidence and UTC freshness checks.
Missing/stale/conflicted/non-primary assessments block matching job approvals.
Schema validity alone still cannot prove a source's truth or actual applicability.
