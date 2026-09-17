# Phase 6 router/state integration gate review — 2026-09-17

## Decision and authority

Accept `CADCAM_07_INTEGRATION_READY` for repository development against the
initial corpus. The deliverable inventory and all six exit requirements below
have supporting inspected code, retained evidence and passing verification.
This permits progression to Phase 7; it does not approve any manufacturing job.

Audience: maintainers deciding whether to advance from integration to Phase 7
hardening. Authority: [ROADMAP.md Phase 6](../../ROADMAP.md#phase-6---router-and-state-integration).
Baseline: `670939e`, plus the acceptance matrix and router test entry point
accompanying this audit. No runtime, fixture, skill, process setting or human
approval was changed by this audit.

Phases 0–5 have separate requirement reviews recorded in the
[reconciliation](roadmap-reconciliation.md). This review covers all Phase 6
deliverables and six exit criteria, not a fresh certification of earlier phases,
an authenticated approval service, public-alpha readiness or practitioner utility.

## Deliverable inventory

| Roadmap deliverable | Inspected implementation and evidence |
| --- | --- |
| `router/router-contract.md` | Defines all eight minimum inputs, five families, five consequence levels, normalization, triage versus integrated review and refusal behavior |
| `router/routes.yaml` | Exactly CAD, CNC, additive, laser and unknown entries; family, artifact classes, bundle and default consequence are explicit |
| `router/tests/` | [Verification entry point](../../router/tests/README.md) maps this named location to canonical `tests/routing`, consistent with the roadmap's overall repository structure; commands run actual tests, not a parallel collector |
| Bounded state | [Schema](../../state/state.schema.json), example, canonical fingerprint/invalidation implementation and [dependency register](../../state/invalidation-rules.yaml) |
| Integrated workflow | [Job router](../../router/job_router.py), four file/evidence gates and [handoff consumer](../../router/handoff_review.py); no free-form memory or implicit physical state lookup |
| Evaluation | Four [retained skill-assisted reviews](../evaluation/integration-runs/README.md), exact replay tests, separate 24-case synthetic approval controls and the new gate matrix |

### Minimum routing inputs

| Input | Observable behavior and verification |
| --- | --- |
| `process_family` | Selects one route; unknown/unsupported family returns missing context and no bundle. Integrated state owns the family; a conflicting request or wrong-family bytes cannot bypass a process gate. |
| `artifact_class` | Checked against the selected route; NC/toolpath and explicit generated-output context enforce an execution-adjacent floor. Actual supplied process bytes also enforce the floor. |
| `machine_known` | Boolean triage flag; integrated routing reconciles it with schema-valid machine context and independently checks profile lifecycle. A true flag cannot supply a missing profile. |
| `controller_known` | Boolean triage flag; required for CNC; integrated controller context and current profile review cannot be replaced by the flag. |
| `material_known` | Boolean triage flag; process-specific material/profile/evidence failures remain blockers even with a matching approval record. |
| `jurisdiction_known` | Explicit boolean; when `jurisdiction_required` is true, absent state jurisdiction produces regulatory review. It is not a legal determination or source-adequacy check; governance remains Phase 7. |
| `consequence_level` | Five explicit levels; missing/invalid values block and use the route default. Recognized live actions override lower labels; actual manufacturing artifacts cannot be down-classified. |
| `approval_state` | Low-level triage declaration only. Integrated routing ignores caller/state approval flags and derives effective status from the supplied scoped, timestamped, current-fingerprint record plus context/evidence checks. |

Evidence: inspected `router.py`/`job_router.py`,
[triage tests](../../tests/routing/test_router.py),
[integrated context tests](../../tests/routing/test_job_router.py),
[CAD](../../tests/routing/test_cad_artifact_gate.py),
[CNC](../../tests/routing/test_nc_artifact_gate.py),
[additive](../../tests/routing/test_additive_artifact_gate.py) and
[laser](../../tests/routing/test_laser_artifact_gate.py) file-gate tests, and
[gate matrix](../../tests/routing/test_integration_gate.py). Structured routing
does not parse arbitrary natural-language intent; the intake contract supplies
family/action/artifact context. No output grants physical execution regardless
of the caller's classification.

### Process and consequence coverage

| Family | Selected bundle |
| --- | --- |
| `cad_handoff` | `cadcam-design-handoff` |
| `cnc_milling` | `cnc-milling-planning` |
| `additive` | `additive-print-prep` |
| `laser_cutting` | `laser-cut-preflight` |
| `unknown` | None; explicit missing-context outcome |

The matrix checks `informational`, `design_advisory`, `manufacturing_planning`,
`execution_adjacent` and `live_execution` for all five entries. Explanations
without generated artifacts retain their declared level; classifications are
not silently downgraded. Twenty integrated family/level controls confirm that
actual supplied bytes raise all lower levels to execution-adjacent, while live
execution stays live and blocked. CAD `prepare_handoff` and the serialized
manufacturing-handoff consumer also enforce this boundary.

### Every required state field

| Required fields | Representation and checks |
| --- | --- |
| `job_id`, `revision`, `source_artifact_hashes`, `units`, `process_family` | Explicit root identity, version and process fields; process-specific source/job/output comparisons and handoff inventory checks |
| `material`, `machine_profile`, `controller_profile` | Structured nullable profiles; supplied reusable profiles require source/lifecycle contracts and current review |
| `setup`, `work_coordinate_system`, `tool_library` | Explicit structured context; CNC requires stock/workholding/WCS/tool readiness; other families have typed process setup inputs and scoped review roles |
| `cam_system`, `postprocessor`, `post_version` | Explicit identities and post profile; CNC reconciles applicability, versions and validation state |
| `simulation_status`, `verification_results` | Persisted declared outcomes; CNC requires distinct current simulation/verification evidence, other families require their named roles; handoff compares exact records and simulation disposition |
| `jurisdiction`, `ip_status`, `export_review_status` | Explicit fingerprinted review context; classification/authorization adequacy remains governance and qualified review, not inferred from possession |
| `approval_status` | Explicit lifecycle field; effective status is derived from the record and checks, not trusted as a self-approval flag |

The gate matrix explicitly checks all twenty roadmap field names in the schema
and complete controls. The root rejects an arbitrary `agent_memory` property.
Optional nulls permit honest drafts, not readiness: integrated typed-context and
evidence checks reject incomplete consequential inputs. Additional explicit
`workholding` and `generated_manufacturing_output` fields preserve dependencies
already required by the foundation. Schema shape alone does not prove field
meaning, evidence truth or manufacturing suitability.

## Required invalidation behavior

| Roadmap change | Bound field checked in every workflow |
| --- | --- |
| Design revision | `revision` |
| Source hash | `source_artifact_hashes` |
| Units | `units` |
| Machine | `machine_profile` |
| Controller | `controller_profile` |
| Setup | `setup` |
| Tool | `tool_library` |
| Post | `postprocessor` |
| Material | `material` |

The new matrix starts each family with a consistent, review-only synthetic
control, then changes exactly one field without renewing evidence or approval.
All 36 family/change combinations are checked both with and without the previous
snapshot: 72 integrated stale-record checks. Inputs remain schema-valid, so a
schema rejection cannot mask missing invalidation. Returned records explicitly
identify the fingerprint mismatch; with a previous snapshot, `changed_fields`
names exactly the changed field. Old approval and package fingerprints and
caller inputs are preserved. Returned approval and handoff copies validate and
are invalidated, never re-signed.

The [foundation invalidation tests](../../tests/foundation/test_state_invalidation.py)
also check the complete extended dependency set and exact agreement with the
YAML register, canonical key ordering, finite JSON, type-sensitive changes and
pending-record preservation. Verification has its own input fingerprint,
excluding outcomes to avoid self-reference; approval binds the outcomes too.
The [CNC evidence tests](../../tests/routing/test_cnc_verification_binding.py),
other family gates and [retained lifecycle controls](../evaluation/integration-runs/approval-controls.json)
show that merely replacing an approval checksum cannot renew stale verification.

## Exit criteria and evidence decisions

| Exit requirement | Given / when / then evidence | Inspected scope |
| --- | --- | --- |
| Deterministic routing | Given the same request, state, record and artifact bytes, repeated routing and consumer calls return identical results, including after recursive object-key reordering. Inputs remain unchanged; fingerprints use finite canonical JSON. | Fixed route configuration and explicit inputs; no promise of deterministic future agent prose |
| Correct consequence classification | Given every declared level and family, classification preserves valid levels unless artifact/action requires escalation. Given NC/toolpath/generated output or actual bytes, lower labels cannot evade execution-adjacent gates. Missing/invalid levels block rather than silently becoming informational. | Structured routing contract, not unrestricted natural-language intent recognition |
| State schemas validate | Given declared schema references, fixtures/examples and retained state/handoff packets, local schema validation succeeds. Unknown root memory fields, invalid nested readiness contracts and nonfinite/non-JSON fingerprint data are rejected at their respective boundaries. | Valid declarations and conservative refusal, not proof of physical truth |
| Invalidation behavior tested | Given each of the nine required changes and an old record, the four-family matrix returns invalidated copies with preserved reviewed identity, with or without previous state. Separate controls reject stale verification even under a newly matching approval. | Fingerprint/scoped-record consistency, not reviewer authentication |
| All four workflows route correctly | Given matching test controls, all four select the manifest bundle and apply fresh family checks. Given unchanged real fixture declarations, four authored reviews preserve missing context and blocked handoffs. Family negatives also block under newly matching test records. | Initial corpus and supported file subsets; blocked jobs are legitimate workflow results |
| Live requests resolve to `BLOCK_EXECUTION` | Given ten explicit prohibited actions, every family and declared level is tested, including normalized uppercase/whitespace forms and an approved flag: 250 triage combinations. Family integration tests and handoff controls retain the same refusal with actual bytes/current synthetic records. | No machine-control capability or physical authorization is added |

The six focused gate methods passed in 33.741 seconds. Their assertions close
the coverage gap identified during this audit; no runtime correction was needed.
The full-suite and repository validation below support final development acceptance.

## Limits and later gates

- CAD uses the explicit bracket adapter, not general CAD interpretation; CNC
  has a bounded dialect/coordinate model and single-tool review; additive and
  laser readers cover their documented subsets. Unsupported semantics block.
- The four actual fixture-context reviews remain blocked. Incomplete CAD
  manufacturing intent, CNC A/B revision conflict, missing slicer settings and
  empty laser settings were not repaired to obtain passing controls. Raw checks
  remain distinct from integrated parser checks stopped by missing context.
- Separate positive controls deliberately fabricate test-only review records,
  non-operational setting markers and a dummy CNC source hash. They prove code
  paths and state consistency, not physical applicability or qualified approval.
- The system returns copies; it does not persist a database transaction, fetch
  evidence, authenticate reviewers, verify signatures or authorize disclosure.
  Future service concurrency, retention and identity controls require separate
  design. No such hosted service or machine connector is a Phase 6 deliverable.
- Phase 7 must reconcile safety/adversarial coverage, source claims, unauthorized
  input/export handling and public-alpha governance. Phase 8 still requires
  real/sanitized practitioner-reviewed packets and its measured thresholds.
- Reopen this gate for changed routing, state/evidence/approval contracts, file
  adapters or scope; a consequential false-ready case; or identity/replay drift.
  Add new evidence without rewriting historical manufacturing verdicts.

## Validation and progression

Executed from the repository root using the project virtual environment:

| Command | Observed result |
| --- | --- |
| `python -m unittest tests.routing.test_integration_gate -v` | Six methods passed in 33.741 seconds, including the 72 integrated invalidation checks |
| `python -m unittest discover -s tests -v` | 623 tests passed in 261.981 seconds |
| `python scripts/validate_foundation.py` | Passed: 58 required files, 14 context schemas, five skillset manifests |
| `python scripts/validate_schema_instances.py` | Passed: 15 schema definitions, 108 instances |

No runtime implementation, source fixture, skill, process setting or retained
review verdict was changed. There is no identified Phase 6 blocker in the
inspected scope. Proceed to Phase 7 safety, governance and adversarial hardening,
then the qualified real-input pilot. Public-alpha acceptance, any release action
and the practitioner verdict remain separate gates and authorities.
