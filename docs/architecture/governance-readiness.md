# Governance readiness — Phase 7 increment

## Decision

`route_job` and `review_handoff` must not recognize a matching manufacturing
review record as effective approval when source authorization or export review
is unresolved. This is an offline repository policy, not a legal determination.
All results remain `REVIEW_REQUIRED` and non-executable.

The reproduced pre-change counterexample used the CNC test-only review factory,
then set ownership to `disputed`, licence to `expired`, and export review to
`blocked`. Rebinding the synthetic verification/approval records returned an
approved handoff with no blockers. The new checks reject that counterexample
without relying on a stale fingerprint or a missing machine profile.

## Readiness contract

Draft state remains schema-valid with unknown or incomplete governance. At
`manufacturing_planning`, `execution_adjacent`, `live_execution`, or any
`prepare_handoff` request, these bounded declarations are required:

| Field | Locally resolved declaration | Otherwise |
| --- | --- | --- |
| `ip_status.ownership_status` | `owned`, `licensed`, `third_party` | Source review required |
| `ip_status.licence_status` | `permitted` | Source review required |
| `ip_status.confidentiality` | `public`, `internal`, `confidential`, `restricted` | Source review required |
| `ip_status.third_party_restrictions` | Empty array | Source review required |
| `ip_status.redistribution_authorized` | Explicit boolean, including `false` | Source review required |
| `export_review_status` | `not_required`, `reviewed` | Regulatory review required |

Possession and ownership alone are insufficient: every consequential case needs
the other declarations too. Unknown, denied, expired, disputed, malformed and
unsupported values cannot become permissions through a matching approval.
Nonempty restrictions remain unresolved because this version has no structured
restriction-clearance contract. Free text cannot waive a blocker.

Informational/design-advisory intake may omit these fields, but supplied
unresolved declarations still produce blockers. Actual output bytes and declared
manufacturing outputs retain the existing execution-adjacent consequence floor.
Root state owns the decision; request-only permission claims cannot replace it.
Conflicting declarations in supported CAD metadata, additive/laser preflight
jobs and `setup.submitted_job` also block.

Source failures return `SOURCE_VERIFICATION_REQUIRED`; export failures return
`REGULATORY_REVIEW_REQUIRED`. Both require human approval. A provisionally
approved record is returned as an invalidated copy, retaining its reviewed
fingerprint. The handoff consumer propagates blockers and invalidates an approved
package copy. No caller inputs or stored reviews are changed.

An explicitly requested jurisdiction review cannot be satisfied by whitespace.
Jurisdiction is never inferred from a filename, machine or user location.

## Local review versus disclosure

Known confidential/restricted inputs and `redistribution_authorized: false` do
not by themselves prohibit local, non-executing review. They do not authorize
publication, external processing, manufacture, or redistribution. The API has no
transfer implementation; unknown publish/upload actions are not supported, and
machine program upload remains a prohibited live action.

Diagnostics contain fixed field paths, not restriction text or supplied values.
Returned state/package copies still contain the caller's data: they are not
redacted telemetry and must not be sent to public logs. No new network access,
file fetching, or content publication is introduced.

## Evidence and remaining authority

`tests/safety/test_governance.py` isolates missing/unresolved declarations,
explicit denials, supported local-review controls, nested conflicts, unchanged
caller inputs, fingerprint invalidation and blank jurisdiction. Twenty adverse
four-family cases each exercise direct routing and handoff consumption with
fresh synthetic approval/evidence records. The positive controls remain
review-only, never machine-executable.

See the [governance evaluation record](../evaluation/governance-runs/README.md)
for historical replay deltas and the separate synthetic lifecycle snapshot.

These checks do not authenticate rights, reviewers, evidence or export
classifications. `reviewed` and `not_required` are bounded declarations, not
legal clearance. Qualified reviewers must establish their truth and applicable
scope. No jurisdiction-specific legal rules are encoded here. The full Phase 7
source/freshness audit and curated safety coverage reconciliation remain open;
this increment does not accept the public-alpha gate or the practitioner pilot.
