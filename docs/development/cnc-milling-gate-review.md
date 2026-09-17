# Phase 3 CNC milling gate review — 2026-09-17

## Decision and audience

For maintainers deciding whether to proceed to Phase 4: the inspected evidence
supports `CADCAM_04_CNC_ALPHA_READY` for repository development against the initial
CNC corpus in [ROADMAP.md](../../ROADMAP.md#phase-3---cnc-milling-alpha).
The decision covers the seven review skills, their composition and the curated
machine-aware blocking behavior. It is not manufacturing approval, general NC
compatibility, public-alpha readiness or practitioner acceptance. REVIEW_REQUIRED.

Baseline is `835116a`, plus the gate-isolation tests accompanying this review.
The reviewer and implementer are the same Codex agent, not an independent or
qualified manufacturing evaluator. The earlier blanket synthetic gate claim is
not used as proof. The [CAD gate](cad-handoff-gate-review.md) and foundation
acceptances remain prerequisites, with their original boundaries intact.

## Deliverable evidence map

All seven current `SKILL.md` contracts and all nine retained seven-skill outputs
were inspected. The [baseline review](../evaluation/cnc-runs/2026-09-17-positive/review.md)
contains the shared assessment; each [negative packet](../evaluation/cnc-runs/README.md)
applies the complete ordered workflow to its specific changed bytes.

| Required deliverable | Inspected behavior and evidence | Decision |
| --- | --- | --- |
| Machine capability: requirements/profile; travel, axes, spindle, envelope, suitability | Skill and baseline section 1 compare three axes, declared bounds, spindle/feed, interface and source-feature coverage. Unverified OEM/context and unusable envelope assumptions block a capability conclusion. Numeric and coordinate tests exercise known conflicts and missing limits. | Met for reviewed corpus, not inferred physical capability. |
| Setup: stock assumptions, sequence, orientation, workholding, WCS | Baseline section 2 identifies the 6-mm stock versus upright-feature gap, incomplete setup sequence, unverified datum/translation/initial position and absent fixture geometry. It orders required reviewer decisions without inventing a setup. Composed tests independently block missing/unverified WCS and incomplete stock/workholding. | Met; no executable setup sheet is claimed. |
| Tooling: availability, holder, geometry, reach, compatibility, numbering | Baseline section 3 preserves fixture-only availability, missing cutter/holder dimensions and unknown access/material suitability. T9 and T2 reviews refuse substitution. Tool-field and duplicate-ID/number tests block absent consequential context. | Met; tool presence is not clearance or cutting suitability. |
| Strategy: roughing, finishing, contouring, drilling, entry/exit, sequencing | Baseline section 4 maps surfaces, contours and holes to conditional decisions; it identifies absent roughing allowance, finish, engagement and entry/exit evidence. It sequences design/stock/access/tooling/CAM review and requests authoritative parameter sources. All eight follow-ups preserve those uncertainties without inventing feeds/speeds/paths. | Met as review/planning guidance. No fabricated manufacturing parameters. |
| Post: CAM, machine/controller, identity/version, validation | Baseline section 5 and wrong-post/controller packets reconcile the target chain and distinguish a synthetic validation flag from current lifecycle evidence. The isolated gate matrix checks each target link, CAM/version and unverified validation despite renewed test-only approval/verification. | Met; matching labels do not validate a post implementation. |
| Static NC: units, coordinates, unsupported commands, suspicious motion, tools, spindle, offsets, modes, target mismatch | Actual byte binding and fresh composed review are covered by `test_nc_artifact_gate.py`; literal/order/feed/spindle tests inspect actual changed program text. `test_nc_coordinate_gate.py` covers reviewed transforms, initial position, translated bounds and refusal of unsupported offset/tool-change semantics. Baseline section 6 distinguishes raw fixture checks from usable model review. | Met within the explicit static scope; unsupported constructs block rather than receive invented semantics. |
| Simulation readiness: level, models, fixtures, unverified NC, assumptions | Baseline section 7 specifies full-path/model, stock-removal/feature, and controller/post checks; absent machine/fixture/tool-holder context remains unresolved. [Verification binding](../architecture/cnc-verification-binding.md) now blocks wrong-context/stale/failed records independently of approval. | Met as simulation requirements and evidence-consistency gating, not a completed physical-job simulation. |
| Seven-skill composition | `skillsets/cnc-milling-planning.yaml` lists exactly the seven roadmap skills in order. Nine retained outputs apply each contract; packet tests check preservation, not reasoning quality. | Met. |
| CNC fixture and eight required mutations | The fixture links the existing CAD source through `source_job`, stores contexts, expected outcomes and positive NC, and encodes eight reproducible mutations as YAML rather than separate directory copies. Replays retain each exact changed program/hash/state/handoff. The roadmap's example directory layout is not treated as a requirement to duplicate source. | Met: wrong-units, wrong-post, wrong-controller, missing-wcs, unknown-tool, revision-mismatch, machine-limit-conflict, incorrect-tool-number. |
| Independent open-source evidence where practical | [CAMotics experiment](../architecture/camotics-evidence-boundary.md) retains actual interpreter and synthetic stock-removal results for nine cases, with pinned runtime/project/NC identity. All negative cases also completed natively, exposing defaults that must not override the skill gates. FreeCAD CAM/LinuxCNC were not run; their availability checks and limits are recorded. Portable dependencies contain none of these native runtimes. | Met through actual independent CAMotics evidence; no job simulation or controller equivalence inferred. |

## Hard rule and exit criteria

The hard manufacturing rule is evaluated through the composed job-review path,
not the triage router's input flags or schema validity alone. Actual NC bytes,
current profile/context/model declarations, current verification bindings and a
matching scoped review record are separately checked. Caller-supplied assertions
remain unauthenticated; an effective record is never permission to manufacture.

The new [gate matrix](../../tests/routing/test_cnc_gate_matrix.py) deliberately
renews synthetic verification and approval after each controlled mutation. This
prevents a stale-record blocker from hiding a broken context/static gate. It
does not renew real evidence or modify any retained packet. Its clean positive
control has no software blockers but remains review-required and non-executable.

| Exit requirement | Given / when / then and actual evidence | Finding |
| --- | --- | --- |
| 100% detection of curated machine/controller/post mismatches | Given current test-only context/verification/approval, when each of three NC target headers changes, fresh static review reports the expected target blocker: 3/3. When each of four post chain fields (machine, controller, CAM, version) conflicts, composed review blocks: 4/4. Gate matrix plus retained wrong-controller/post findings. | Met for those explicit curated cases; not a general recall estimate. |
| Zero critical false-ready decisions in negative fixtures | Given each of the eight exact YAML mutation recipes, when actual changed bytes are routed with fresh test-only records, all 8 produce their expected static blocker and cannot retain effective approval. All nine original packet handoffs also remain blocked. | 0/8 false-effective-approval results in the required negative set. No unseen-case claim. |
| Missing WCS blocks | Given missing state WCS, unverified WCS or omitted program G54, when reviewed, context/static checks return `MISSING_CONTEXT` and refuse approval. Gate matrix, coordinate tests and missing-WCS packet. | Met; no inherited/default G54 assumption. |
| Missing consequential tooling blocks | Given missing library or missing holder, reach, availability, number or geometry, when reviewed with renewed test-only records, approval is refused. Unknown/incorrect tools and duplicate identities are independently covered. | Met; multi-tool semantics remain unsupported and block the current composed static path. |
| Simulation gate works | Given not-run/unknown/failed simulation status despite passed current records, gate matrix blocks. Given bare, wrong-context, stale, malformed, failed, duplicate or incomplete records, verification-binding regressions block. Changed NC, setup, machine, post, tooling and other dependencies invalidate the verification basis. | Met for declared-context consistency; authentic reports and applicable physical models still require qualified review. |
| Post validation explicit | Given unverified validation despite current test records, gate matrix returns `SOURCE_VERIFICATION_REQUIRED`. Separate lifecycle tests reject unreviewed/stale post evidence even when the simple flag says verified; baseline review identifies exactly that defect. | Met. |
| No physical machine execution capability | Inspected router/state/CNC script paths only classify, parse, compare and report. The schema registry has no remote retrieval callback. All ten prohibited actions are tested with complete context/approval and return `BLOCK_EXECUTION`; all outputs remain non-executable. The optional native probe accepts only fixed synthetic cases and offline simulator executables, not machine targets or control commands. Core dependency/import and tracked executable inventories reveal no machine connector. | Met for the inspected repository, not a security audit of third-party native binaries or the host. |

## Validation, limits and progression

The eight gate-matrix test methods passed in 9.292 seconds. Full portable-suite,
schema, foundation and whitespace results are retained in the accompanying
[evaluation follow-up](../evaluation/cnc-milling-evaluation.md). The tests include
multiple controlled cases per method; their count is not a quality score.
No native simulator or physical equipment was rerun for this audit. Native
observations retain their original software/input/runtime identities.

The verification-binding false-effective-approval counterexample was fixed in
`835116a`, not waived. This audit also exposed a test-isolation weakness, corrected
by the matrix above. No further Phase 3 acceptance contradiction was demonstrated
in the inspected scope. Historic review and native packets remain unchanged;
current replay permits only the three explicit additional binding findings.

The initial checker handles a bounded single-tool literal dialect and reviewed
fixed Cartesian translation; unsupported arcs, compensation, variable programs,
multi-tool changes and other unimplemented semantics require further review and
cannot be cleared by an allowlist. It does not prove actual machine state,
collision clearance, post/controller behavior, stock/feature completion or true
material/tool applicability. These limitations are visible in the skill outputs,
not hidden behind successful parsing or synthetic simulation. No new source,
machine or process claims, manufacturing parameters or production approvals are
introduced by this gate decision.

This acceptance does not waive remaining Phase 4 additive, Phase 5 laser,
Phase 6 integration, Phase 7 governance/public-alpha or Phase 8 real-input and
qualified-practitioner requirements. General usefulness, baseline comparison,
reviewer edit burden, independent human verdicts and broader safety-corpus
metrics remain unproven. The next required work is Phase 4 file-derived mesh and
3MF package validation with the specified additive reference ecosystem.

Reopen Phase 3 if its skills/context/execution contracts change, supported
machine/dialect/tool/coordinate scope expands, evidence identities drift, or a
consequential false-ready counterexample appears. Preserve old records and add
new evidence; do not relabel prior jobs as approved to satisfy a development gate.
