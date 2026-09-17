# Integrated four-family development reviews

Subsequent status: the [full Phase 6 audit](../../development/integration-gate-review.md)
accepts the integration development gate. The packet observations and limitations
below describe this evaluation milestone and remain unchanged; no manufacturing
handoff is promoted by the later gate decision.

Four actual skill-assisted reviews are retained with structured decisions,
bounded states, blocked handoffs and reproducible observations. They use the
unchanged synthetic fixture declarations, not the reviewed test controls.
All four manufacturing handoffs remain REVIEW_REQUIRED and non-executable.

The replay mirrors the consumer's optimistic `*_known: true` request flags to
exercise reconciliation with bounded state. Those harness flags are not reviewer
findings that missing context is known or that a profile is verified. Actual
profile lifecycle records and missing state fields remain unchanged and binding.

The [protocol and rubric](protocol.md) were written before the authored reviews.
Baseline implementation: `30eaeef`. These are same-agent, known-case development
evaluations; there is no blinded no-skill comparison or practitioner verdict.

| Case | Selected bundle | Consequential unresolved evidence |
| --- | --- | --- |
| [CAD](2026-09-17-cad/review.md) | cadcam-design-handoff | Process/material/requirements and controlled drawing/PMI basis; full source/receiver equivalence |
| [CNC](2026-09-17-cnc/review.md) | cnc-milling-planning | CAD A / NC B conflict; stock/setup scope, profiles, WCS, tooling, post and applicable simulation |
| [Additive](2026-09-17-additive/review.md) | additive-print-prep | Selected slicer/settings, orientation/support and applicable printer/material/environment evidence |
| [Laser](2026-09-17-laser/review.md) | laser-cut-preflight | Empty process settings, material/site applicability, independent beam/emission and output reviews |

## Rubric observations

- Routing: all four resolve to the selected bundle at execution-adjacent level;
  router and consumer remain non-executable.
- Identity: actual byte hashes, source/derivative authority and declared units
  are retained. CNC's conflicting revisions are preserved and detected, not
  relabeled to satisfy the consumer.
- Skill outputs: CAD covers five ordered skills; CNC covers seven; additive and
  laser each cover their complete preflight responsibility groups. Each review
  gives case-specific evidence, missing inputs and reviewer decisions. This is
  an inspectable same-agent judgment, not an independent completeness score.
- Evidence quality: raw checks, declared status labels, authored conclusions and
  integrated outcomes are separate. All four lack sufficient context for a fresh
  integrated parser run; their earlier raw checks are not promoted to one.
- Missing context: no settings, qualified profile reviews, simulation success or
  human approval were invented. Incomplete readiness inputs remain represented
  in valid draft state; nested contracts block rather than silently fill them.
- Integration: current-input-bound findings and state-bound review details are
  retained in all packets. Consumer output preserves all declared/router blockers,
  review fingerprints and artifact inventories.
- Usefulness: the reviews identify concrete design, process, setup and reviewer
  actions beyond tool diagnostics. No measured improvement over a no-skill agent,
  edit-burden reduction or practitioner usefulness claim is supported.

No concrete skill-contract defect was exposed by these four known cases, so no
skill was edited. This does not demonstrate robustness on unseen inputs. The
remaining integration gate requires its full requirement-by-requirement audit;
these packets alone do not close gate 07 or any later gate.

## Separate approval-lifecycle controls

[approval-controls.json](approval-controls.json) retains 24 observations: six
transitions for each family, constructed only by the explicitly test-only
`tests/routing/handoff_fixture.py` factory. They are not the packet reviews above.
The factory includes artificial passed evidence/profile declarations, a dummy
CNC source hash and non-operational slicer/laser setting markers. None is
applicable manufacturing evidence or an issued approval.

| Transition | Observed result in all four families |
| --- | --- |
| Matching test record | Record recognized; review required, execution forbidden |
| Changed state-bound review, old packet/record | Invalidated; old reviewed fingerprints preserved |
| Updated test packet/approval, old verification | Still invalidated; a new approval checksum cannot cure stale evidence |
| Renewed test-only verification and record | Consistent again; still review-only, never physical authorization |
| Different actual artifact bytes | Invalidated despite unchanged declared identities |
| Live execution | BLOCK_EXECUTION |

The observations retain current, supplied and returned fingerprints, blocker
sets and findings. Replay also checks that the consumer did not mutate inputs.
These controls exercise consistency logic, not reviewer identity or evidence
authentication. A test helper that rebinds synthetic declarations is not a
review/approval service and must never be used to repair an actual job packet.

## Reproduction

Run from the repository root:

```text
python -m tests.evaluation.replay_integration_reviews all
python -m tests.evaluation.replay_integration_controls
python -m unittest tests.evaluation.test_integration_reviews -v
python scripts/validate_schema_instances.py
```

The replay commands only print JSON, read fixed repository cases and call offline
review APIs. They do not fetch evidence, execute CAD scripts/NC, write packets,
invoke native tools or issue approvals. Tests compare retained records exactly
and exercise changed handoff content; they do not reproduce agent reasoning.
Artifact hashes use raw bytes. Review/skill/manifest text hashes explicitly
normalize line endings to LF for cross-platform checkouts; this does not change
the artifact hash policy. Original family packets and source fixtures remain
unchanged.

## Validation of this milestone

- Nine integration packet/lifecycle test methods passed.
- Full portable suite: 617 tests passed in 229.640 seconds on 2026-09-17.
- Foundation validator passed: 58 required files, 14 context schemas, five
  skillset manifests.
- Schema-instance validator passed: 15 schema definitions and 108 instances.
- Staged whitespace checks passed; source fixtures, skills, skillsets and prior
  family review packets were unchanged from `30eaeef`.

These results validate the inspected development assertions and record integrity,
not qualified manufacturing review, evidence authenticity or pilot thresholds.
