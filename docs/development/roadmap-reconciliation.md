# Roadmap reconciliation — 2026-09-13

## Current decision

Full public-alpha readiness is **not yet proven**. Historical handoffs recorded gates 01–08 against a bounded synthetic corpus. Those results remain useful evidence, but do not establish every requirement in [ROADMAP.md](../../ROADMAP.md). This reconciliation supersedes their blanket completion claims; it does not change the roadmap or award a new gate.

This is a gap register for maintainers, not an exhaustive completion certificate. Baseline: commit `3377549`, plus the CNC context-hardening changes accompanying this document. The repository has 14 atomic skill contracts and five skillset manifests. Their existence and metadata validation do not prove practitioner usefulness or correct agent behavior.

## Requirement and evidence map

| Phase / gate | Evidence available | Required evidence still incomplete or unproven |
| --- | --- | --- |
| 0 / 01: domain contract | Six architecture documents define scope, taxonomy, consequences, execution boundary, personas, and specialization. | Reconfirm content-level acceptance during the final gate audit; file presence alone is not approval. No scope expansion is proposed. |
| 1 / 02: foundation | Seven standards, nine context schemas plus bounded-state schema, local validators, examples, and invalidation tests exist. Nine complete format policies and 11 scoped format references are present. Manifest shape/path failures, YAML/JSON syntax, required metadata for all 14 skills, and parsed local Markdown links/anchors now have regression coverage. | Content-level contract review and broader claim evidence remain. Reference checks are offline and renderer-bounded; see the foundation validation coverage notes. Metadata checks do not establish truth or machine applicability. |
| 2 / 03: CAD handoff | Five skill contracts; editable bracket source, STEP/STL derivatives, drawing/revision evidence, synthetic provenance mutations, and opt-in native CAD checks. | Demonstrate skill-assisted handling of the roadmap's negative cases with preserved output and review evidence. Geometry and metadata tests are not substitutes for evaluating source hierarchy, missing PMI, and conflicting design dimensions in an actual handoff. |
| 3 / 04: CNC alpha | Seven CNC contracts; curated NC mutations; scoped approvals; missing/conflicting setup, tooling, WCS, post, simulation, and verification now block effective approval. | Broaden static parser evidence for compact words, comments, modal state, and dialect limitations. Match all required negative cases to meaningful artifact-level checks and retained review output. Declared context values are not authenticated machine or simulation evidence. |
| 4 / 05: additive alpha | FDM skill and synthetic metadata preflight; STL fixture and printer/material compatibility mutations. | Actual non-manifold file mutations, 3MF package semantics, PrusaSlicer/open-model reference evidence, and verified unit-aware build-volume handling are not established by the metadata harness. Preserve real file-derived findings and skill output. |
| 5 / 06: laser alpha | Laser skill; positive paired DXF/SVG fixture check; metadata mutations for geometry, material, ventilation, and compatibility. | Open/duplicate/unsupported geometry and scale mutations must be tested against altered files, not only pre-labeled status fields. The positive fixture checker does not establish general DXF/SVG defect detection. |
| 6 / 07: integration | Four-family routing tests; version-2 fingerprints; local schema checks; stale-approval handling; prohibited live-action blocking. | Prove the composed workflows with file-derived evidence and retained handoffs, including all required context and authorization failures. Current checks establish record consistency, not reviewer identity or truth of supplied evidence. |
| 7 / 08: hardening | Safety/adversarial tests, approval/IP/regulatory models, security/contributing/limitations documents, and source-freshness process. Format claims now have scoped references. | Verify the remaining machine/material/tooling, safety, and regulatory claims; test unauthorized inputs and export-sensitive handling behavior. Reconcile the complete curated safety corpus before claiming 100% recall or zero critical false-ready states across the roadmap. |
| 8 / 09: real-input pilot | Packet template, protocol, packet validator, and aggregate threshold evaluator. | No completed packets in `docs/evaluation/pilot-packets/`. Real/sanitized inputs, baseline and skill outputs, qualified reviewer findings, edits, safety findings, and final verdicts are required. Synthetic submissions cannot close this gate. |

## Concrete acceptance checks for the current change

- Given a matching CNC approval fingerprint but missing setup, tool library, postprocessor, WCS, CAM identity, or units, routing must not return an effective `approved` state. Evidence: `tests/routing/test_job_router.py`.
- Given conflicted post identity, duplicate tool identity/number, unresolved workholding, unsupported WCS, failed simulation, or failed verification, routing must return explicit blockers and require review. A previously approved record is returned as an invalidated copy; input records and the reviewed fingerprint are preserved.
- Given a complete synthetic CNC context and a current scoped record, routing may recognize the review record but must still return `review_required: true` and `execution_allowed: false`. This is not authorization to manufacture.
- Given missing, malformed, or conflicting nested context, checks must fail closed without inventing values. See the [CNC context contract](cnc-context-approval.md) for the exact accepted structure and limitations.

## Required next work, in order

1. Complete the foundation content-level contract and evidence review. Required skill metadata, format/source, malformed-manifest, and parsed local Markdown reference checks are implemented; see [foundation validation coverage](foundation-validation.md) for their scope and remaining limitations. Do not add workflow skills while foundation acceptance remains open.
2. Strengthen CNC static artifact checks and their documented dialect scope; exercise composed job/approval behavior with resulting evidence.
3. Add real geometry/package mutation checks for FDM and laser, including 3MF distinctions and the specified additive reference ecosystem.
4. Preserve skill-assisted outputs and review evidence; reconcile every required safety case, source claim, handoff field, and gate criterion.
5. Run the practitioner pilot and evaluate all roadmap thresholds. A qualified reviewer must judge evidence quality, not merely supply a passing YAML verdict.

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
