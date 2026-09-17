# Public-alpha gate review

Reviewed: 2026-09-17. Baseline: `4591509`; this increment changes documentation only.
Decision: **HOLD — `REVIEW_REQUIRED`**. Do not award
`CADCAM_08_PUBLIC_ALPHA_READY` or announce a release from this review.

Subsequent configuration update (2026-09-17): the repository is now public,
the wiki is enabled, and private vulnerability reporting is enabled with a
visible public reporting link. The authenticated form and notification/triage
path remain unverified. The historical observations below describe the original
review; the [reporting decision](../architecture/security-reporting.md) records
the updated evidence. Public visibility does not award this gate.

## Scope and evidence

This review reconciles the nine Phase 7 exit requirements against the initial
four-family, structured-input corpus. It follows the accepted
[integration review](integration-gate-review.md), not the historical blanket
gate claims. “Evidenced” below means the bounded repository requirement has
support; it does not certify arbitrary agent behavior or manufacturing safety.

| Roadmap requirement | Evidence and finding | Status |
| --- | --- | --- |
| Adversarial tests pass | Full portable suite at the baseline: 651 tests passed. [Hardening review](../evaluation/adversarial-hardening.md) describes the import/text checks and their limits; parser and schema controls are mapped below. | Evidenced for inspected corpus |
| Prohibited live actions blocked | [Named safety corpus](../evaluation/public-alpha-safety-corpus.md) exercises guard bypass, safety-system disabling and machine start at both structured boundaries; routing tests cover the registered live actions. No result authorizes execution. | Evidenced for registered inputs |
| 100% critical safety failure recall | All thirteen named roadmap cases are mapped: 43 router plus 35 distinct handoff-consumer observations produce their required blockers (78/78). | Evidenced for declared denominator only |
| Zero critical false-ready states | Zero in those 78 observations; eight separately forged approved packets are rejected. Eight positive controls establish scoped review-record recognition, never execution authority. | Evidenced for declared corpus only |
| Authoritative-source requirement enforced | [Source assessments](../architecture/source-review-readiness.md) enforce authority declarations, scope, metadata binding and freshness for nine roles. [Claim inventory](../sources/skill-claim-ledger.md) separates policies, factual references and fixture observations. | Evidenced as declaration/consistency enforcement, not authentication |
| SECURITY.md complete | Scope, exclusions, report contents and confidentiality rules exist. The selected private reporting channel is not operationally confirmed. | **Open release prerequisite** |
| CONTRIBUTING.md complete | Contribution scope, evidence, tests, safety review, migration notes and human review are required. Sensitive reports route to SECURITY.md. | Evidenced as contribution policy |
| Public limitations documented | README consolidates partial parser coverage, unauthenticated evidence, synthetic evaluations, optional native tools and deferred processes; linked contracts retain exact limits. | Evidenced as documentation |
| Source freshness process documented | [Freshness process](../sources/source-freshness-process.md) distinguishes release/profile review cadence from offline metadata validation and runtime UTC expiry checks. | Evidenced as process; release-time recheck still required |

## Broader adversarial review

The following implementation evidence complements the named-case matrix. It is
not an additional numerical recall claim and must not be merged into its denominator.

| Attack or failure surface | Inspected regression evidence | Boundary |
| --- | --- | --- |
| Embedded artifact content | `tests/safety/test_three_mf_review.py`, `test_laser_svg_review.py`, `test_nc_word_review.py`, and CAD drawing-consistency tests under `tests/interoperability/` | Metadata/comments do not provide approvals; supported parsers reject tested active/unsupported XML and NC semantics. This is not a general prompt-injection benchmark. |
| Archive/XML resource and reference abuse | 3MF and SVG safety tests | Tested traversal, external relationships, entity declarations and size/depth/expansion limits fail closed. Not proof against every parser exploit or dependency vulnerability. |
| Approval substitution and stale evidence | `tests/routing/test_handoff_review.py`, source-evidence and governance safety tests | Current byte/context/record consistency is checked; copied invalidations preserve reviewed fingerprints. Reviewer identity, permission and source truth are not authenticated. |
| Schema reference access | `tests/schema/test_schema_instances.py` and `scripts/validate_schema_instances.py` | Local schema registry; no configured remote retrieval. This is not an OS network sandbox. |
| Capability drift | `tests/adversarial/test_repository_hardening.py` | Selected explicit network/process import roots in portable code are checked recursively. Dynamic imports, alternate APIs, dependencies and optional native probes are outside that proof. |

The [threat model](../architecture/threat-model.md) remains the authority for
these trust boundaries. Native-tool observations establish only their recorded
experiments. A green suite cannot validate a machine, operator, site or source.

## Release hold and maintainer decisions

The repository API still reported private visibility on 2026-09-17. No tags or
GitHub releases were listed in this check. Publishing is a separate consequential
action; permission to commit and push does not authorize changing visibility.

Before public-alpha acceptance, the maintainer must:

1. Decide whether to authorize publication. Confirm that the intended contents
   and history are suitable for disclosure; this review is not a repository-wide
   secrets, licensing or export-clearance audit.
2. Resolve the [private reporting prerequisite](../architecture/security-reporting.md).
   The authorized enable attempt returned HTTP 404. If publication is authorized,
   coordinate enablement and verify both the setting and private report form
   before announcement. If staying private, designate an interim private contact
   when intake is needed. Do not post sensitive reports publicly.
3. Assign responsibility for receiving and triaging those reports. No response
   SLA or monitored mailbox is established by this document.
4. Review the bounded acceptance evidence, recheck applicable source freshness,
   and validate the exact release commit. Record the decision and commit identity;
   do not infer acceptance from this table or from test counts.

If a consequential defect is reported, maintainers should pause distribution
and affected readiness claims, preserve sanitized reproduction and old evidence,
and review a correction with regression coverage. Do not downgrade evidence
schemas or restore invalidated approvals to recover a passing result. Public
downloads cannot be recalled by making the repository private again.

No live deployment or machine rollout is part of this milestone. Existing
[source migration](source-contract-migration.md) and
[profile lifecycle migration](profile-lifecycle-migration.md) boundaries still
apply. Do not automatically rewrite user job data or historical review packets.

## Validation of this documentation increment

- Foundation validator passed: 58 required files, 14 context schemas, five skillsets.
- Schema-instance validator passed: 15 schemas and 108 instances.
- Focused adversarial, schema, 3MF, SVG, NC-word and CAD drawing-consistency group:
  103 tests passed in 2.186 seconds.
- `git diff --check` passed. The full 651-test suite was not rerun for this
  documentation-only increment; the baseline result above is the prior run.
- Pilot evaluator returned the expected `not_ready` result (exit 1): zero completed
  packets and no workflow-family coverage. This is an open gate, not a passed pilot.

## Next gate

Phase 8 requires real or appropriately sanitized inputs and qualified reviewer
findings under the [pilot protocol](../evaluation/README.md). Synthetic test
factories, same-agent reviews and passing YAML cannot close that gate. Obtain
the user's inputs and reviewer arrangements; do not fabricate pilot evidence.
