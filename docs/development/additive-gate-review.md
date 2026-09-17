# Phase 4 additive manufacturing gate review — 2026-09-17

## Decision and audience

For maintainers deciding whether to proceed to Phase 5: the inspected evidence
supports `CADCAM_05_ADDITIVE_ALPHA_READY` for repository development against the
initial additive corpus in [ROADMAP.md](../../ROADMAP.md#phase-4---additive-manufacturing-alpha).
This accepts the FDM review/planning skill and its bounded evidence path, not
general mesh/3MF conformance, an approved sliced build, production readiness,
public-alpha readiness or independent practitioner acceptance. REVIEW_REQUIRED.

Baseline: `33f62ac`, plus the isolated gate tests accompanying this review.
The reviewer is the same Codex agent that implemented the evidence path. This
is not an independent manufacturing verdict. Accepted foundation, CAD and CNC
boundaries remain unchanged. Earlier blanket synthetic gate claims are not proof.

## Deliverable and responsibility map

The current [skill contract](../../skills/additive-job-preflight/SKILL.md),
single-skill manifest, byte/preflight implementations, twelve retained reviews,
their input/state/handoff records, native observations and regression cases were
inspected. The [packet index](../evaluation/additive-runs/README.md) links every
review; [STL](../architecture/additive-stl-evidence.md),
[3MF](../architecture/additive-3mf-evidence.md) and
[retained-state](../architecture/additive-retained-evidence.md) documents explain
the implementation boundaries, not alternative exit criteria.

| Roadmap responsibility | Observable evidence and finding |
| --- | --- |
| Mesh/package intake | Actual bounded STL/3MF bytes, explicit format and whole-file hash are required. Malformed bytes, unsupported structures, absent bytes and identity conflicts block. CLI tests exercise real temporary input files; labels cannot replace parsing. |
| Source provenance | Each retained handoff preserves source and derivative descriptors, hashes, revision and units. Source A versus job B remains a conflict. Review identifies absent functional intent and authenticated derivation rather than treating a hash as proof of design equivalence or permission. |
| STL versus 3MF handling | STL requires external units. 3MF preserves explicit/default model-unit origin, relationships, resources, instances and transforms. It is not flattened to STL before inspection. Cross-labeled bytes block in the isolated matrix. |
| Printer profile matching | The selected printer must match the supplied ID; the wrong-printer case blocks. Full reviews additionally reject synthetic/unverified lifecycle and applicability claims as physical evidence. |
| Material profile matching | Selection must match the supplied material and both compatibility lists. Missing selection cannot borrow the candidate PLA profile. Full reviews request actual grade/manufacturer/printer/slicer evidence and do not populate missing material properties. |
| Model validity | File-derived topology checks surface open, repeated/degenerate, winding, edge, vertex-fan and signed-volume defects. Actual open-STL and open-3MF mutations remain blocked with valid labels and freshly bound test hashes. Success is explicitly partial geometry; unsupported validity questions require follow-up. |
| Build-volume compatibility | Exact measured extents and explicit unit conversion are compared with declared dimensions. Supported 3MF build transforms contribute actual placement bounds. Tests cover exact boundaries, exceedances, metadata lies and tiny differences that rounded displays would hide. Usable bed, supports and clearance are not inferred. |
| Orientation considerations | Every review identifies missing orientation rationale, intended-feature/acceptance context and placement evidence; it requests design/additive review without inventing an angle. Missing declaration blocks independently in the matrix; a reviewed label is not a reviewed plan. |
| Support requirements | Every review requests support strategy, removal/access and clearance assessment. No support threshold/settings are fabricated. Missing support declaration blocks independently; label-only adequacy remains unresolved in the full handoff. |
| Slicer readiness | A fixture verified flag and named compatible profile are not actual profile content/version or sliced-build evidence. Every handoff requires applicable slicing/preview/build verification. Native geometry export is explicitly not slicing. |
| Environmental considerations | The unknown-job-environment case blocks despite a generic known material label. All full reviews identify absent applicable job/site evidence and request manufacturer documentation and qualified operator/site review. No material-safety or legal conclusion is inferred. |
| Atomic skill and composition | `skills/additive-job-preflight/SKILL.md` implements the one roadmap contract; `skillsets/additive-print-prep.yaml` contains exactly that skill. No speculative split or mandatory vendor dependency is introduced. |
| PrusaSlicer and open models | The [executed reference experiment](prusaslicer-windows.md) retains seven fixed CC0 geometry cases and nine child-process observations with runtime/input identity. It independently exposes open meshes, unit conversion and transformed placement. Native success does not clear unsupported extensions or a malformed exported package. No native rerun is claimed for this audit. |

These are review responsibilities, not a claim that the synthetic jobs have
complete physical context. Missing evidence produces a blocked handoff and
specific reviewer actions. A useful review can identify that work is not ready;
it must not manufacture the missing facts to produce a positive job verdict.

## Required negative cases and isolation

The [gate matrix](../../tests/safety/test_additive_gate_matrix.py) changes only
the legacy utility's synthetic approval flag to `approved`. This is deliberately
not an approval record or evidence renewal. The two clean format controls then
have no utility blockers but remain `review_required`, non-executable and only
`checked_partial_geometry`. Each negative is compared with that control, so
missing-human-approval cannot hide failure to detect its actual discrepancy.
No fixture, retained packet or real approval is changed by the tests.

| Required case | Independent observed blocker/finding |
| --- | --- |
| Non-manifold geometry | Actual final-facet removal exposes three boundary edges/nonmanifold vertices; `MISSING_CONTEXT` despite valid mesh label and new test hash. |
| Unsupported material | Selected material conflicts with supplied profile and printer list; `MISSING_CONTEXT`. |
| Missing material profile | Null selection cannot use the candidate profile; `MISSING_CONTEXT`. |
| Incompatible printer profile | Wrong supplied printer identity and reciprocal compatibility conflict; `MACHINE_CONTEXT_REQUIRED`. |
| Revision mismatch | Source A does not satisfy submitted job B; `MISSING_CONTEXT`. |
| Unsupported build volume | Measured 60/40/30 exceeds supplied 50/50/20 on X and Z; `MACHINE_CONTEXT_REQUIRED`. |
| Missing environmental information | Unknown job environment remains unresolved; `MISSING_CONTEXT`. |

All seven required cases yield their specific failure without a missing-human
flag or hash-mismatch fallback. Additional matrix cases isolate three 3MF
semantic failures, missing planning declarations, both compatibility directions,
source revision and hash conflicts, and cross-format labels. Existing parser,
numeric, topology, package-security and transformed-boundary tests remain
separate evidence; the matrix does not replace them.

## Exit criteria

| Exit requirement | Given / when / then evidence | Decision |
| --- | --- | --- |
| STL and 3MF distinctions preserved | Given either actual format, inspection retains its unit/provenance/geometry semantics; wrong labels fail. Embedded inch cannot be overridden by job mm, and translated build placement cannot be replaced with local extents. STL/3MF suites, matrix and retained unit/placement reviews. | Met within the explicitly bounded subset. |
| Material parameters never invented without authoritative context | Given synthetic profiles with empty properties and no actual slicer configuration, full reviews retain those gaps and request primary evidence, with no temperatures, speeds, cooling or support settings. Replay/preflight do not mutate inputs; packet tests check unchanged profiles/properties. | Met in the inspected outputs and implementation; not a universal guarantee of future agent behavior. |
| Printer/material incompatibility detected | Given mismatched selection or either absent compatibility direction, preflight returns the specific blocker independently of human approval; retained skill reviews explain the actual discrepancy and required reconciliation. | Met for the required cases and isolated compatibility matrix. |
| Model defects surfaced | Given altered mesh bytes with fresh test identity and valid labels, open geometry still blocks. Dedicated suites additionally inspect winding, degeneracy, duplicates, edge/vertex defects and malformed/unsupported package structures. Native open-mesh export success does not clear defects. | Met for the curated defect corpus; unsupported geometry validity remains review-required. |
| Provenance preserved | Given revision/unit conflicts or changed whole-file identity, preserve both claims and block rather than relabel. Packet tests bind actual source/derivative bytes, submitted context and handoff; context changes invalidate the evaluation fingerprint. | Met for identity/record preservation, not authenticated derivation or ownership. |
| Unresolved material or environmental risk blocks manufacturing-ready status | Given missing/incompatible material or unknown environment, isolated preflight blocks. Even matching synthetic labels leave all twelve full handoffs blocked with unresolved assumptions and inconclusive verification; changing only approval/status labels cannot promote them through the handoff schema. | Met for inspected utility and retained skill outputs. Composed additive approval integration remains a separate Phase 6 requirement. |

## Limits reconciled, not waived

- Self-intersection, positive-fill/union, wall thickness and dimensional design
  equivalence are not proved by partial topology. Every full review requests
  qualified geometry/design follow-up; none labels the part printable.
- The declared rectangular envelope is not the actual usable bed or support/brim
  clearance. STL extents do not prove placement. 3MF transformed bounds are only
  the supported declared zero-origin comparison. No automatic recentering,
  scaling, rotation, welding or repair is performed.
- Unsupported extensions, material assignments and vendor/auxiliary package
  semantics require further review. The inspector is not a general conformant
  3MF consumer. The reference export's missing-thumbnail relationship and content
  types are retained as failures, not excused because PrusaSlicer exited zero.
- Preflight evaluates some declarations; it does not authenticate evidence or
  approvals. A no-blocker utility result is still review-required. Full agent
  findings and generic routing are retained separately. Phase 6 must prove the
  composed byte-aware workflow; the evaluation-only setup wrapper is not a new
  production API.
- No applicable sliced build or manufacturing approval was produced. No printer
  connection, G-code generation, process parameters or machine action was added.
  The optional native probe remains fixed offline geometry actions, with no
  claim of an OS sandbox or security audit of third-party binaries.

## Validation and progression

Seven gate-matrix methods passed in 4.790 seconds, including the multiple
controlled cases above. Full-suite and repository-validator results are recorded
in the [evaluation follow-up](../evaluation/additive-fdm-evaluation.md). Counts
are not reasoning-quality scores. All twelve original packets remain unchanged.

No further Phase 4 acceptance contradiction was demonstrated in this inspected
scope. This supports progression to Phase 5 actual laser geometry/scale mutations
and retained reviews. Phase 6 integration, Phase 7 source/governance/adversarial
acceptance and Phase 8 real-input qualified-practitioner evaluation remain open.
Unseen-case reliability, baseline improvement and reviewer edit burden are not
established by same-agent controlled synthetic outputs.

Reopen this gate for changed skill/evidence/approval contracts, new geometry or
package semantics, new process scope, input/runtime identity drift, or a
consequential false-ready counterexample. Preserve historical evidence and add
new findings; do not promote old jobs to satisfy a development milestone.
