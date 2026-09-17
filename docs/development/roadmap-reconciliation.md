# Roadmap reconciliation — updated 2026-09-17

## Current decision

Full public-alpha readiness is **not yet proven**. Historical handoffs recorded gates 01–08 against a bounded synthetic corpus. Those results remain useful evidence, but do not establish every requirement in [ROADMAP.md](../../ROADMAP.md). This reconciliation supersedes their blanket completion claims and does not change the roadmap. The [foundation content review](foundation-content-review.md), [CAD gate audit](cad-handoff-gate-review.md), [CNC gate audit](cnc-milling-gate-review.md), [additive gate audit](additive-gate-review.md), [laser gate audit](laser-gate-review.md), and [integration gate audit](integration-gate-review.md) support Phases 0–6 acceptance for repository development against the initial corpus. Public-alpha and practitioner-pilot acceptance remain open.

This is a gap register for maintainers, not an exhaustive completion certificate. Baseline: commit `3377549`, plus the CNC context-hardening changes accompanying this document. The repository has 14 atomic skill contracts and five skillset manifests. Their existence and metadata validation do not prove practitioner usefulness or correct agent behavior.

## Requirement and evidence map

| Phase / gate | Evidence available | Required evidence still incomplete or unproven |
| --- | --- | --- |
| 0 / 01: domain contract | Content review covers the six architecture documents, all required taxonomy concepts, explicit conditional boundaries, and four intake/review/handoff definitions. Phase 0 is accepted for repository architecture development. | No Phase 0 content blocker remains in the inspected scope. Reopen for process expansion, weakened boundaries, or new required sibling/vendor dependencies. This is not practitioner approval. |
| 1 / 02: foundation | The follow-up acceptance review checks all seven exit requirements plus consequential invalidation. Handoff review fields and reusable-profile lifecycles now have schema/routing regressions. Phase 1 is accepted for repository development. | No identified Phase 1 representation/validator blocker remains. Source truth, actual dimensional meaning, cross-package evidence binding, and machine applicability remain downstream workflow/evaluation responsibilities, not schema guarantees. |
| 2 / 03: CAD handoff | Five skill contracts; complete initial artifact family; restricted source/SVG checks and declared byte binding; retained five-skill reviews and state-bound blocked handoffs for all six named negative cases. The [gate audit](cad-handoff-gate-review.md) checks each deliverable and exit criterion and accepts Phase 2 for repository development. | No identified gate-03 blocker remains for the initial corpus. Byte identity is not authenticated derivation truth; general drawing/PMI interpretation and independent practitioner assessment are not proven. Preserve these limits and reopen for scope/contract changes, drift or false-ready counterexamples. |
| 3 / 04: CNC alpha | The [requirement-by-requirement audit](cnc-milling-gate-review.md) accepts Phase 3 for repository development. Seven skills and nine retained reviews, actual NC/static/coordinate checks, current verification bindings, isolated gate regressions and independent CAMotics observations support all listed deliverables and curated exit criteria. | No identified gate-04 blocker remains for the initial corpus. Declared mappings and synthetic simulation do not prove physical state, collisions, true feed/spindle behavior or applicable job simulation. Unsupported multi-tool/dialect semantics still block. Retained agent outputs are not practitioner verdicts; reopen on scope/contract changes, identity drift or false-ready counterexamples. |
| 4 / 05: additive alpha | The [requirement-by-requirement audit](additive-gate-review.md) accepts Phase 4 for repository development. FDM skill, STL/bounded 3MF inspection, actual PrusaSlicer observations, twelve retained reviews and isolated gate tests support all responsibilities and six exit criteria against the initial corpus. | No identified gate-05 blocker remains in the inspected scope. Partial geometry is not self-intersection, usable-bed or full package/vendor validation; unsupported semantics and missing applicable profile/slicer/environment evidence remain review obligations. Same-agent synthetic outputs are not a sliced build, production approval or practitioner verdict. Composed record consistency is covered by the separate Phase 6 audit. |
| 5 / 06: laser alpha | The [requirement-by-requirement audit](laser-gate-review.md) accepts Phase 5 for repository development. DXF/SVG byte inspection, sixteen retained reviews, isolated negatives and gate-edge tests support the skill responsibilities and all five exit criteria against the initial corpus. | No identified gate-06 blocker remains in the inspected scope. Partial geometry and declaration consistency do not establish path intent, design equivalence, applicable process/site evidence or manufacturing approval. Separate beam/emission gaps remain in all blocked handoffs. Phase 6 adds explicit composition without rewriting the older evaluation-only wrappers. |
| 6 / 07: integration | The [requirement-by-requirement audit](integration-gate-review.md) accepts Phase 6 for repository development. Four-family byte/scoped-evidence routing, state-bound handoff consumption, retained skill-assisted reviews, separate approval-lifecycle controls and the 72-case integrated invalidation matrix support all deliverables and six exit criteria. | No identified gate-07 blocker remains in the inspected scope. Scoped file/record consistency is not general CAD interpretation, reviewer identity or evidence truth. All actual fixture handoffs remain blocked. Reopen for contract/scope changes, identity drift or consequential false-ready counterexamples; governance/public-alpha and qualified practitioner gates remain separate. |
| 7 / 08: hardening | The [public-alpha gate review](public-alpha-gate-review.md) reconciles all nine exit requirements, broader parser/adversarial controls and fourteen skill contracts' claim boundaries. The [named safety-case matrix](../evaluation/public-alpha-safety-corpus.md) covers all thirteen roadmap cases with 78 distinct adverse boundary checks. Governance and source assessments enforce declarations, scoped evidence, metadata binding and freshness. | **Release hold:** confirm operational private reporting and obtain the maintainer's explicit publication/release decision, including release-time evidence checks. The matrix's 100% required-blocker recall and zero false-ready outcomes apply only to its declared structured-input corpus. Declaration consistency does not authenticate permission, source truth or controlled-data classification. |
| 8 / 09: real-input pilot | Packet template, protocol, packet validator, and aggregate threshold evaluator. | No completed packets in `docs/evaluation/pilot-packets/`. Real/sanitized inputs, baseline and skill outputs, qualified reviewer findings, edits, safety findings, and final verdicts are required. Synthetic submissions cannot close this gate. |

## Concrete acceptance checks for the current change

- Given a matching CNC approval fingerprint but missing setup, tool library, postprocessor, WCS, CAM identity, or units, routing must not return an effective `approved` state. Evidence: `tests/routing/test_job_router.py`.
- Given conflicted post identity, duplicate tool identity/number, unresolved workholding, unsupported WCS, failed simulation, or failed verification, routing must return explicit blockers and require review. A previously approved record is returned as an invalidated copy; input records and the reviewed fingerprint are preserved.
- Given a complete synthetic CNC context and a current scoped record, routing may recognize the review record but must still return `review_required: true` and `execution_allowed: false`. This is not authorization to manufacture.
- Given missing, malformed, or conflicting nested context, checks must fail closed without inventing values. See the [CNC context contract](cnc-context-approval.md) for the exact accepted structure and limitations.

## Required next work, in order

The [Phase 6 audit](integration-gate-review.md) supports progression to Phase 7.
Earlier family packets and all four integrated skill-assisted handoffs remain
blocked and non-executable; no source, profile or approval was promoted.

GitHub private vulnerability reporting is now enabled after the repository became
public; its public reporting link is verified. The available browser reaches
GitHub sign-in, so the authenticated form and notification/triage path still need
maintainer confirmation. The [reporting-channel decision](../architecture/security-reporting.md)
records both the earlier HTTP 404 and the successful follow-up. Public visibility
alone is not public-alpha gate acceptance.

The [scoped non-format audit](../sources/nonformat-claim-audit.md) now supplies
primary evidence for CNC review context, tooling considerations, additive
emissions and independent laser hazard categories. The expanded
[adversarial import check](../evaluation/adversarial-hardening.md) covers nested
portable code and corrects the HTTP module-root gap. These increments do not
alone close the complete factual-claim audit. The subsequent
[skill-contract inventory](../sources/skill-claim-ledger.md) reviews all fourteen
contracts and distinguishes policy, primary-source rationales and software or
fixture observations. It does not certify every generated or historical statement.

The [named safety-case reconciliation](../evaluation/public-alpha-safety-corpus.md)
now covers every one of the thirteen Phase 7 cases: 43 router and 35 distinct
consumer observations, eight forged-packet refusals, and eight positive controls.
Required-blocker recall is 78/78 with zero critical false-ready outcomes in that
declared corpus. This closes the named-case mapping gap at the structured APIs,
not general agent behavior, source authentication or practitioner validation.

1. Resolve the remaining maintainer decisions in the [public-alpha release hold](public-alpha-gate-review.md): confirm the authenticated private-report form, notification/triage responsibility and explicit alpha acceptance. Repository visibility is now public; no further visibility change is needed or authorized by this reconciliation.
2. Before accepting or announcing public alpha, review the bounded gate evidence, recheck applicable source freshness and validate the exact release commit. Preserve each corpus's scope and denominator; do not extrapolate structured-input results to arbitrary free-text requests or malicious artifacts. Retained approvals remain unchanged.
3. Run the practitioner pilot and evaluate every roadmap threshold using real/sanitized inputs and qualified reviewer findings. A reviewer must judge evidence quality, not merely supply a passing YAML verdict. Do not expand the skill inventory or process scope without the required evaluation and review.

FreeCAD CAM, LinuxCNC, and CAMotics are independent evidence sources **where practical**, not mandatory runtime dependencies. Canada specialization is optional and cannot supply legal approval. Additional processes, skill splits, machine connectors, and direct physical execution remain outside this milestone.

## Verification boundaries

Run from the repository root with the documented test dependencies:

```text
python -m unittest discover -s tests -v
python scripts/validate_foundation.py
python scripts/validate_schema_instances.py
python scripts/evaluate_pilot_gate.py docs/evaluation/pilot-packets
```

The pilot evaluator should report not ready while the packet root is empty. Green unit tests establish only their inspected assertions. Native CAD verification is separately opt-in; see [the Windows runtime notes](cadquery-windows.md). Neither a test count nor the fraction of historical gate labels is a reliable percentage of remaining work.
