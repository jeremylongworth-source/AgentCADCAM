# Scoped safety and manufacturing-context claim audit

Reviewed: 2026-09-17. Audience: maintainers and public-alpha reviewers.
Status: `REVIEW_REQUIRED` for full Phase 7 acceptance.

This audit adds primary support for four review rationales beyond the format
registry. It does not certify every repository statement, any job, or legal
compliance. The linked source sections were read; access dates are not expiry
guarantees. Metadata is retained in [the source registry](source-registry.yaml).

Subsequent review: the [fourteen-skill claim inventory](skill-claim-ledger.md)
and [public-alpha gate review](../development/public-alpha-gate-review.md)
reconcile the bounded contract and broader documentation checks. The remaining
release hold is recorded there; the original scoped findings below are preserved.

## Claim-to-source map

| Repository location and rationale | Primary evidence inspected | Applicability boundary |
| --- | --- | --- |
| [Execution boundary](../architecture/execution-boundary.md): an example program is not a complete, authorized machining job. | [haas-mill-safety](https://www.haascnc.com/service/online-operator-s-manuals/mill-operator-s-manual/mill---safety.html), sections 3.1–3.2, distinguishes illustrative programs from tool/offset/material/fixture context and addresses operator training and safeguards. | OEM evidence for the rationale, not a universal operating procedure. Apply the actual machine's documentation; do not transfer Haas settings or procedures into generic profiles. |
| [Machine matching](../../skills/machine-capability-match/SKILL.md) and [tooling review](../../skills/tooling-plan-review/SKILL.md): tool presence alone is insufficient compatibility evidence. | [sandvik-milling-selection](https://epublications.sandvik.coromant.com/frontend/getcatalog.do?catalogId=1157651&catalogVersion=2&startpage=9), printed page 5, identifies machine capability, stability, power/torque, clamping, coolant and overhang considerations. | Supports checking context, not a specific tool recommendation, clearance result or numeric machining parameter. |
| [Additive preflight](../../skills/additive-job-preflight/SKILL.md): environmental/material review is separate from mesh validity. | [niosh-polymer-printing-emissions](https://stacks.cdc.gov/view/cdc/135072/cdc_135072_DS1.pdf), section 3.5, printed page 6, describes particles/VOCs from heated polymers and material/process/site dependence. | The separation is a repository inference from that evidence. No safe exposure threshold, universal filament clearance or ventilation capacity is inferred. Publication identity/date is confirmed by the [CDC catalogue](https://stacks.cdc.gov/view/cdc/135072). |
| [Laser preflight](../../skills/laser-job-preflight/SKILL.md): record beam and process-emission concerns separately. | [ccohs-laser-hazard-categories](https://www.ccohs.ca/topics/hazards/workplace/lasers), introductory hazard categories, distinguishes beam hazards from equipment/substance/emission hazards. | A general hazard distinction, not approval of a laser, enclosure, material or exhaust system. Citing a Canadian publisher does not select Canadian jurisdiction for a job. |

## What these citations do not establish

- Blocking unknown context, requiring human review, forbidding live control and
  invalidating changed approvals are repository policies from the roadmap and
  [domain contract](../architecture/domain-contract.md). They are not presented
  as verbatim regulatory requirements.
- [IP/provenance](../architecture/ip-and-provenance-model.md) and
  [regulatory review](../architecture/regulatory-review-model.md) define review
  states and escalation boundaries, not ownership or export classifications.
  [Canada](../../specializations/jurisdictions/canada/README.md) remains reserved,
  not an active legal module. Any future jurisdiction-specific claim needs its
  own current applicable primary evidence and qualified review.
- Synthetic machine limits, stock, tool dimensions, NC values, materials and
  process parameters remain fixture data. None is promoted to OEM-approved
  engineering data by adding these references. Existing source assessments,
  approval records, skill versions and retained review packets are unchanged.
- Format and dialect claims remain under the separate
  [format registry](../formats/format-registry.md). Software behavior and
  geometry/parser limitations require code/tests or tool observations, not a
  safety-source citation.
- [Threat-model](../architecture/threat-model.md) import scans provide limited
  implementation evidence. They do not prove absence of exfiltration or semantic
  prompt injection. Local native-tool experiments are not sandbox guarantees.

## Acceptance checks and remaining evidence

1. Given each of the four rationales above, a reviewer can find the exact source
   section, publisher, scope and access date. This scoped check is satisfied by
   the inspected pages and retained metadata; it is not a comprehensive audit.
2. Given a missing or expired job-context source assessment, matching approval
   must remain blocked. Evidence is separate in
   [source-assessment evaluations](../evaluation/source-evidence-runs/README.md);
   this document does not re-approve those test-only declarations.
3. The subsequent [named safety-case matrix](../evaluation/public-alpha-safety-corpus.md)
   reconciles all thirteen roadmap cases at the structured APIs. Before
   public-alpha acceptance, inspect remaining factual claims in public
   documentation and retained outputs, complete the broader adversarial review,
   and verify private reporting availability. These checks remain open in the
   [roadmap reconciliation](../development/roadmap-reconciliation.md).
4. Before a real job is accepted for review, qualified reviewers still need
   actual machine/controller/tool/material/process evidence. These general
   references cannot fill missing job-specific inputs or close the real-input
   practitioner gate.

The offline foundation validator checks registry shape and document links. It
does not fetch these pages, check this manual claim map against source content,
or authenticate truth. Recheck the claims under the
[source freshness process](source-freshness-process.md) before release and when
their affected scope changes.
