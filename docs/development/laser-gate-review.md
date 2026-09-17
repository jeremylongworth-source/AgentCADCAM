# Phase 5 laser cutting gate review — 2026-09-17

## Decision and audience

For maintainers deciding whether to proceed to Phase 6: the inspected evidence
supports `CADCAM_06_LASER_ALPHA_READY` for repository development against the
initial laser corpus in [ROADMAP.md](../../ROADMAP.md#phase-5---laser-cutting-alpha).
This accepts the laser review/planning skill and its bounded evidence path, not
general DXF/SVG conformance, a manufacturing-ready job, public-alpha readiness
or independent practitioner acceptance. REVIEW_REQUIRED.

Baseline: `3711059`, plus the isolated gate-edge tests accompanying this review.
The reviewer is the same Codex agent that implemented the evidence path, not an
independent laser/process practitioner. Foundation, CAD, CNC and additive
acceptance boundaries remain unchanged. Historical blanket gate claims are not
the evidence for this decision.

## Deliverable and responsibility map

Inspected: the [skill](../../skills/laser-job-preflight/SKILL.md), its
[single-skill manifest](../../skillsets/laser-cut-preflight.yaml), DXF/SVG readers,
preflight, sixteen retained reviews and their input/state/handoff records,
replay helper and relevant parser, context, identity and invalidation tests.
The [packet index](../evaluation/laser-runs/README.md),
[file-evidence contract](../architecture/laser-file-evidence.md) and
[state-binding decision](../architecture/laser-retained-review-binding.md)
describe their scope and reproducible evidence.

| Roadmap responsibility | Observable evidence and finding |
| --- | --- |
| DXF/SVG intake | Actual bytes, explicit format, source revision and exact drawing hash are required. DXF tags and SVG XML have separate readers; cross-labeled bytes fail despite matching hashes. Unsupported entities, attributes and external/active semantics require review rather than being dropped. |
| Units | DXF insertion-unit and SVG physical viewport declarations are retained and compared with job units. Explicit machine units govern the working-area comparison. Missing/unsupported/conflicting declarations block; no host defaults or silent unit conversion establish design intent. |
| Scaling | Exact rational physical dimensions are compared with expected dimensions. Doubled DXF coordinates/radii and doubled SVG viewBox produce specific size failures despite verified scale labels. Mixed SVG viewport units can preserve extents but displace geometry; that placement conflict remains explicit. |
| Geometry closure | Actual LWPOLYLINE flags, exact LINE chains and supported SVG contours determine closure. Open outer paths block with clean metadata and fresh hashes. No edge is invented and no endpoint is welded by tolerance. |
| Duplicate geometry | Repeated undirected edges and coincident circles block. DXF/SVG actual duplicate-circle cases and reversed-path/transform tests detect duplicates without depending on element count or optimistic labels. |
| Path intent | The utility requires explicit cut intent and placement frame; score/mark semantics are not inferred. Every full review requests per-path intent, order, multiplicity, orientation, nesting, kerf and controlled output comparison. Layer/group names do not supply an approved strategy. |
| Machine compatibility | Machine selection must match the supplied profile; material-machine compatibility must explicitly include it. Unit-aware actual bounds are checked against the declared working rectangle, including translated placement and exact boundaries. Full reviews identify absent OEM/calibration/applicability evidence. |
| Material compatibility | Unknown selection cannot borrow the candidate plywood profile. Material/process compatibility and the process target chain are separately checked. Reviews request actual stock identity, grade, thickness and applicable primary evidence, preserving unsafe or conflicting claims. |
| Process profile readiness | Selected profile/machine/material IDs must agree; unresolved job or process review flags block. Even matching verified labels with empty settings remain an evidence gap in all full handoffs. No power, speed, frequency, kerf or focus is guessed. |
| Safety requirements | Every review separately retains unresolved beam-risk and process-emission evidence and qualified reviewer actions. Utility output always requires review and forbids execution; no reader, replay or preflight activates equipment or changes safety systems. |
| Ventilation/fume concerns | Unknown or malformed job or material environmental statuses block independently. Full reviews reject generic known-status fixture labels as applicable site/emission evidence. Known ventilation does not clear unsafe-material status or resolve the independent beam review. |
| Atomic skill and skillset | `laser-job-preflight` supplies the roadmap output contract; `laser-cut-preflight.yaml` contains exactly that skill. No new skill split, vendor runtime requirement or machine-control capability was introduced. |

These responsibilities concern review and refusal, not a requirement to invent
the missing physical facts. A blocked synthetic handoff with specific reviewer
actions is distinct from an incomplete implementation of the review contract.

## Required negative cases

The retained-packet tests isolate all nine named negatives from the missing-human
flag by applying a synthetic `approved` declaration in memory. This is neither a
real approval record nor evidence renewal. Fresh derivative hashes also prevent
stale-identity refusal from concealing missed file defects. Both baseline formats
have no utility blockers under this control but remain partial, review-required
and non-executable; their full retained handoffs remain blocked.

| Required case | Specific retained and independently isolated result |
| --- | --- |
| Duplicate contours | Extra coincident circle in actual DXF and SVG; `duplicate_circles: 1`, `MISSING_CONTEXT`. |
| Open contours | Actual unclosed outer path in both formats; `open_contours: 1`, `MISSING_CONTEXT`. |
| Unsupported entity | Added DXF ARC or SVG cubic path; `SOURCE_VERIFICATION_REQUIRED`, without substituting the baseline contour result. |
| Wrong units | DXF inch against job mm exposes declaration, physical-size and working-area conflicts. Mixed-unit SVG exposes declaration and placement conflicts despite unchanged extents. |
| Scale mismatch | Actual DXF extents double to 120 × 80 mm; actual SVG extents halve to 30 × 20 mm. Both conflict with the unchanged expected 60 × 40 mm and return `MISSING_CONTEXT`. |
| Unknown material | Unknown job selection conflicts with candidate material/process chain; `MISSING_CONTEXT`. |
| Prohibited/unsafe material | Unsafe job status cannot be cleared by the material's not-indicated label; `MISSING_CONTEXT`. This test is not a safety claim about all plywood. |
| Missing ventilation context | Unknown job ventilation cannot borrow the material's known-status label; `MISSING_CONTEXT`. |
| Machine/material incompatibility | Compatibility lists another machine; `MACHINE_CONTEXT_REQUIRED`. The retained mutation also omits process compatibility, so both findings are retained; the new matrix isolates each list independently. |

Eight additional [gate-matrix methods](../../tests/safety/test_laser_gate_matrix.py)
cover both partial controls, cross-format bytes, missing/uncertain/malformed safety
statuses in either context, ventilation, independent compatibility lists, each
process review flag, cut/placement declarations and separate beam/emission
findings. No fixture, retained packet, process settings or approval was changed.

## Exit criteria

| Exit requirement | Given / when / then evidence | Decision |
| --- | --- | --- |
| Geometry defects reliably detected | Given altered bytes and optimistic metadata with a matching new test hash, file inspection detects open/duplicate geometry and blocks unsupported semantics. Dedicated tests also cover degeneracy, crossings, touches, overlap, nonplanarity, visibility, numeric extremes and parser limits. Packet replay preserves the specific results. | Met for the curated corpus and explicitly supported geometry subset, not arbitrary-format conformance. |
| Unknown material cannot receive production-ready status | Given unknown, absent or mismatched material context, preflight blocks even with an approved flag. All full handoffs preserve unresolved material/process evidence and remain blocked; schema tests reject status-only promotion. | Met in inspected implementation and retained outputs; generic router composition remains Phase 6 work. |
| Unsafe-material uncertainty triggers blocking state | Given unsafe, unknown, missing or malformed status on either job or material, the matrix returns the material-safety blocker independently of human approval. Known ventilation and valid geometry cannot clear it. | Met for inspected declarations and full-review evidence gaps. |
| Laser settings are not guessed | Given empty settings and unverified synthetic profiles, review outputs request applicable primary evidence without supplying parameters. Preflight/replay preserve inputs; regression tests retain empty settings/properties and invalidate changed process context. | Met in inspected code and outputs, not a universal guarantee of future agent behavior. |
| Beam and process-emission risks represented independently | Given either clean format control, utility findings retain both concerns. Each full review has distinct evidence gaps and reviewer actions, and each handoff retains separate unresolved beam and emission assumptions. Neither can be averaged away or satisfied by resolving the other. | Met in utility findings and complete retained reviews; no real installation has been assessed. |

## Limits reconciled, not waived

- These are bounded readers, not general DXF/SVG consumers. Unsupported geometry,
  paint, transform, layer or package semantics require further review. DXF unused
  sections are inventoried and byte-bound, not interpreted as manufacturing intent.
- Exact contour measurements do not prove product definition, tolerances, kerf,
  calibrated placement, axis equivalence, safe cut order or an applicable process.
  The symmetric fixture does not prove general DXF/SVG orientation equivalence.
- Utility checks include declaration consistency, not authenticated source or
  process truth. Full reviews keep fixture flags separate from applicable
  design/material/process/site evidence. No handoff is promoted by this gate.
- The generic router and file preflight remain separate observations. The
  evaluation-only setup wrapper binds job/process input records but is not a
  production composition API. Phase 6 must propagate file and reviewer failures
  through integrated approval and invalidation paths across all four families.
- No controller output, applicable process simulation, parameters, machine action
  or qualified human approval was produced. Synthetic known-case reviews do not
  establish unseen-case reliability, user usefulness or reduced reviewer effort.

## Validation and progression

The focused matrix plus retained-packet suite passed 25 methods in 5.355 seconds.
Full-suite and repository-validator results are recorded in the
[evaluation follow-up](../evaluation/laser-cut-evaluation.md). Test counts and
section-presence checks are not reasoning-quality scores.

The evidence above supports progression to Phase 6 file-aware workflow composition.
Phase 7 governance/source/adversarial acceptance and Phase 8 qualified real-input
practitioner validation remain open. Reopen Phase 5 for changed skill, file,
evidence or approval contracts; new entities/transforms or process scope;
identity drift; or a consequential false-ready counterexample. Preserve
historical blocked packets and add applicable new evidence rather than rewriting
old outcomes to satisfy a development milestone.
