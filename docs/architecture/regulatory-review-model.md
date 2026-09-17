# Regulatory Review Model

## Scope

The core remains jurisdiction-neutral. It can identify that a jurisdiction or regulatory review is relevant and route to explicitly selected research sources, but it must not make final legal, regulatory, certification, or export-control determinations.

## Review states

- `not_applicable`: no jurisdictional claim is being made and the user has confirmed the workflow scope.
- `unknown`: relevance has not been established.
- `research_required`: an explicit jurisdiction or regulated use requires source review.
- `review_required`: qualified legal, regulatory, safety, or export reviewer must assess the claim.
- `cleared_for_stated_scope`: a qualified reviewer recorded a bounded decision outside the system.
- `blocked`: the request cannot proceed within the available evidence or authority.

## Rules

1. Jurisdiction must be explicit; do not infer it from the user, machine, or file location.
2. Regulatory claims require authoritative source metadata and freshness information.
3. A jurisdiction specialization can provide research routing and checklists only.
4. Export-sensitive or confidential data must be handled as a review concern, not copied into public fixtures or logs.
5. Regulatory review does not replace machine, process, material, or human manufacturing approval.

## Initial specialization

The [governance readiness contract](governance-readiness.md) interprets bounded
export-review declarations and rejects blank jurisdiction for an explicitly
required jurisdiction review. It does not infer applicability or issue legal
clearance, and source/export blockers cannot be waived by matching approval.

`specializations/jurisdictions/canada/` is an optional research-routing location. It is not a legal-advice module.
