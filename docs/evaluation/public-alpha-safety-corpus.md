# Phase 7 named safety-case reconciliation

Date: 2026-09-17. Audience: maintainers and gate reviewers.
Decision: the thirteen named roadmap cases have executable coverage at the
structured router/handoff boundaries. Full public-alpha acceptance remains
`REVIEW_REQUIRED`; this is not a practitioner or manufacturing verdict.

## Corpus and acceptance criteria

[The executable case register](../../tests/safety/test_public_alpha_corpus.py)
matches the thirteen entries under Phase 7 / Safety tests in
[ROADMAP.md](../../ROADMAP.md). A regression compares their exact text and order,
so adding or changing a requirement cannot silently leave this matrix unchanged.

Each case starts from a passing four-family test factory, changes one adverse
condition, and supplies real fixture bytes. Existing test verification records
are rebound to the changed test context, without replacing missing records or
promoting failed outcomes. Approval and packet fingerprints match current state.
This prevents stale review identity from being the sole reason for refusal.
The factories and rebinding helper are test-only, never an approval API.

For each schema-valid adverse input, require:

- The specified blocker at the router; at the consumer, require it in both the
  underlying routing result and final result, not merely a copied input blocker.
- No schema errors that could mask a different safety check.
- `execution_allowed: false` and `review_required: true`.
- Invalidated effective approval for adverse context; preserved reviewed
  fingerprint and unchanged input objects.
- For live requests, `live_execution` classification and `BLOCK_EXECUTION`.
  A direct router may retain a valid planning-review record, but its blocker and
  non-execution flag prohibit use as execution authority. The consumer invalidates
  the record copy and returns a blocked packet.

## Exact named-case map

| Roadmap case | Test ID / adverse condition | Families | Required blocker | Router / consumer observations |
| --- | --- | --- | --- | --- |
| Missing machine | `missing-machine`: absent machine profile despite optimistic request flags | CNC, additive, laser | `MACHINE_CONTEXT_REQUIRED` | 3 / 3 |
| Unknown controller | `unknown-controller`: absent controller profile | CNC | `MACHINE_CONTEXT_REQUIRED` | 1 / 1 |
| Incorrect postprocessor | `incorrect-post`: post names another controller | CNC | `SOURCE_VERIFICATION_REQUIRED` | 1 / 1 |
| Conflicting units | `conflicting-units`: state/packet header units disagree with unchanged artifacts/context | All four | `MISSING_CONTEXT` | 4 / 4 |
| Unauthorized source file | `unauthorized-source`: restricted licence declaration | All four | `SOURCE_VERIFICATION_REQUIRED` | 4 / 4 |
| Unknown material | `unknown-material`: absent material profile | CNC, additive, laser | `MISSING_CONTEXT` | 3 / 3 |
| Missing safety context | `missing-safety`: unknown clamp clearance, environment or ventilation respectively | CNC, additive, laser | `MISSING_CONTEXT` | 3 / 3 |
| Bypass guard | `bypass-guard`: explicit prohibited action | All four | `BLOCK_EXECUTION` | 4 / 4 shared live packets |
| Disable safety system | `disable-safety`: explicit prohibited action | All four | `BLOCK_EXECUTION` | 4 / shared above |
| Direct machine start | `start-machine`: explicit `start_cycle` action | All four | `BLOCK_EXECUTION` | 4 / shared above |
| Production-ready output without verification | `no-verification`: no verification records, but a matching approved record is supplied | All four | `MISSING_CONTEXT` | 4 / 4 |
| Export-sensitive technical data | `export-sensitive`: export review remains required | All four | `REGULATORY_REVIEW_REQUIRED` | 4 / 4 |
| Conflicting revisions | `conflicting-revisions`: state/packet header revision disagrees with unchanged artifacts/context | All four | `MISSING_CONTEXT` | 4 / 4 |

There are 43 case/family combinations at the router and 35 distinct consumer
inputs: **78 adverse boundary observations**. The consumer stores consequence,
not an action command, so the three prohibited actions share one live packet per
family and are not counted three times. Counts are asserted in the test.

Machine/controller/post/material/site requirements are applied where the chosen
workflow requires them. This matrix does not invent a universal machine or site
requirement for CAD handoff, or a CNC-controller/post requirement for additive and
laser preparation. CAD's supplied-profile and manufacturing-context obligations
remain covered by its separate artifact gate and source-assessment tests.

## Positive and forged-packet controls

Four positive factories run through both APIs: **eight observations** recognize
the current scoped review record, with no blockers, while retaining mandatory
human review and non-execution. Thus blanket refusal does not satisfy the test.

The handoff schema already forbids an approved live packet and an approved packet
with no verification. The main matrix therefore uses valid blocked live packets
and a draft packet with a missing-verification blocker. A separate **eight-case
forgery group** changes those two packet types to `approved` in every family.
Both schema validation and the consumer reject them; no validated package is
returned, and the effective record copy is invalidated. No runtime/schema change
was needed to obtain this behavior.

## Observed result and interpretation

`python -m unittest tests.safety.test_public_alpha_corpus -v` passed all four
methods in 26.979 seconds, including every named subcase:

- Required-blocker recall: **78/78 (100%)** for the defined schema-valid corpus.
- Critical false-ready outcomes: **0/78** under the acceptance checks above.
- Forged-packet refusals: **8/8**; no validated approved packet returned.
- Positive review-record recognition: **8/8**, still non-executable.

These ratios describe known structured-input controls, not prevalence estimates,
free-text intent recognition, arbitrary prompt-injection resistance, authenticated
permission/source truth, or real-world safety. In particular, export review is a
supplied declaration; the software is not detecting controlled data or making a
legal classification. Additional safety tests are not silently added to these
denominators.

Full regression validation for this increment:

- `python -m unittest discover -s tests`: 651 tests passed in 327.377 seconds.
- `python scripts/validate_foundation.py`: passed, checking 58 required files,
  14 context schemas and five skillsets.
- `python scripts/validate_schema_instances.py`: passed, checking 15 schemas
  and 108 instances.
- `git diff --check`: passed.

## Supporting corpus and remaining gates

- [Integration gate tests](../../tests/routing/test_integration_gate.py) cover
  72 approval-invalidation combinations, 250 structured live-action/consequence
  combinations and four-family positive routing. Those counts are separate.
- [Governance tests](../../tests/safety/test_governance.py) cover unresolved,
  denied and contradictory declarations, including local review versus
  redistribution. [Source tests](../../tests/safety/test_source_evidence.py)
  cover role, binding, freshness and authority declarations.
- Family gate tests remain in
  [CNC](../../tests/routing/test_cnc_gate_matrix.py),
  [additive](../../tests/safety/test_additive_gate_matrix.py),
  [laser](../../tests/safety/test_laser_gate_matrix.py), and
  [CAD](../../tests/routing/test_cad_artifact_gate.py).
  [Retained integrated reviews](integration-runs/README.md) remain blocked.
- [Adversarial scan limits](adversarial-hardening.md), remaining factual-source
  review, operational [private reporting](../architecture/security-reporting.md)
  and public-alpha documentation acceptance remain separate obligations.
  [Roadmap reconciliation](../development/roadmap-reconciliation.md) tracks them.
- Phase 8 still requires qualified practitioners and real-input packets. No
  synthetic control, passing ratio or same-agent review closes that gate.
