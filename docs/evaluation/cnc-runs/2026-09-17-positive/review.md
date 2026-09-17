# Seven-skill CNC baseline review

Decision: **blocked manufacturing handoff; REVIEW_REQUIRED**. This is Codex's actual controlled review under the [request and rubric](../README.md), not practitioner approval or an independent benchmark. The word `positive` identifies a syntactic test control, not a manufacturing-ready job. The raw reports and complete supplied NC/context are in [observed.json](observed.json); identity and unresolved context are retained in [state.json](state.json) and [handoff.json](handoff.json).

## 1. machine-capability-match

Requested process: three-axis milling. Selected CNC job: `cnc-mill-bracket`, revision B, mm. Linked editable CAD is the revision-A synthetic L-bracket, not a new revision-B design. Requirements include the complete part/stock definition, access, tooling interface and intended operations. The source declares 60 × 40 × 6 base dimensions, an upright height of 30 and four nominal diameter-6 holes; critical tolerances and manufacturing intent are absent.

| Comparison | Supplied evidence | Finding |
| --- | --- | --- |
| Axes/target | fixture-mill-3axis, three axes; fixture-controller | Identity matches the NC headers, but both profiles are unverified synthetic declarations |
| Bounds | Machine-axis X 0–60, Y 0–40, Z 0–30 mm | Not proof of usable work envelope, stock clearance or tool/holder reach; coordinate model and setup are unverified |
| Spindle/feed | Declared 500–12000 RPM and feed ceiling 1000 mm/min; NC S5000, F100/F200 | Numeric fixture comparison only, not material/tool suitability or observed behavior |
| Tool interface | fixture-holder in machine and tool declarations | Matching labels do not establish a physical interface or availability |
| Source coverage | L-bracket source versus an NC rectangle | No evidence that this program manufactures all source features |

Severity: blocker for manufacturing readiness. `SOURCE_VERIFICATION_REQUIRED` and `MISSING_CONTEXT` remain. Obtain applicable OEM/controller and actual setup evidence before claiming a machine match. Alternate path: continue offline fixture review; do not silently choose another machine or change limits to fit this program.

## 2. cnc-setup-planner

Supplied sequence is only “face/base setup” followed by “review vertical features.” Stock is declared 60 × 40 × 6 mm, orientation maps part axes by label, and workholding is `fixture-only` with `clamps_clear: null`. This does not establish how the linked 30-mm upright is supplied or produced. Request raw/preformed stock geometry and a feature/setup allocation rather than assuming that the base dimensions describe a complete blank.

The model selects G54 and declares zero translation plus an initial X0 Y0 Z25 position after the first tool change. Its lifecycle is unverified, setup WCS is only `defined`, and neither datum location nor physical establishment/measurement method is supplied. Do not treat those test numbers as a usable offset sheet. No fixture geometry, support surface, clamp placement, accessible-face analysis or repeatability evidence is available. Collision/access and re-fixturing remain unresolved.

Reviewable sequence: first establish design/stock intent; then have the setup reviewer define workholding, datum/axes and supported coordinate mapping; review access for each feature and any re-fixturing; only then review a controlled CAM setup and its verification. The qualified setup reviewer must specify the applicable measurement method and acceptance criteria; no probing commands or fabricated method are provided here. Blockers: `MISSING_CONTEXT`, `SOURCE_VERIFICATION_REQUIRED`, `HUMAN_APPROVAL_REQUIRED`.

## 3. tooling-plan-review

| Item | Supplied value | Disposition |
| --- | --- | --- |
| Identity/number | fixture-tool-1 / T1, lifecycle revision 1 | NC T1 M6 reconciles with the sole supplied tool; no full CAM library/setup sheet is supplied |
| Geometry | Endmill, nominal diameter 6, two flutes; declared length units mm | No cutter/flute length, supplier applicability or tolerance evidence |
| Holder/reach | fixture-holder / 20 | No holder envelope, stickout, assembly or feature-access evidence; do not infer reach adequacy from one number |
| Availability | fixture-only | Not confirmed inventory or a loaded tool |

The tool review/source are unverified and explicitly synthetic. No statement establishes cutter/material suitability, clearance at the upright, hole production method, or whether one tool can produce the required features. Severity: blocker. Require the tooling/CAM reviewer to reconcile controlled tool assembly and numbering across library, CAM setup, setup sheet and new NC. Do not fabricate another tool, feed, RPM or availability. `MISSING_CONTEXT`, `SOURCE_VERIFICATION_REQUIRED`; human tooling review required.

## 4. toolpath-strategy-planner

Feature-to-strategy mapping is conditional: base surfaces would need a reviewed facing/finishing decision; the outer shape a contouring decision; base and upright holes a feature-specific hole-making and access decision. The NC supplies a rectangle at Z0 after a Z25 approach and return, not evidence of those manufacturing operations or a verified stock-removal sequence. No roughing allowance, finish requirement, engagement limit, entry/exit clearance or chip-management evidence is supplied.

Planning alternatives are to obtain a complete blank/stock model or a controlled preformed-part definition before allocating operations. Which is appropriate remains unresolved. Sequence design/stock definition, fixture/access review, tooling selection and CAM planning before post/static/simulation review. Authoritative machine, tool, material and CAM sources must support any eventual process inputs. This review supplies no feeds, speeds, stepovers, depths, coolant or generated paths. `MISSING_CONTEXT` and `SOURCE_VERIFICATION_REQUIRED` block strategy acceptance; the CAM programmer must resolve these inputs and verify residual stock, feature coverage, entry/exit and collisions.

## 5. postprocessor-readiness-review

Identity chain: fixture-cam → fixture-post-v1 version 1.0 → fixture-controller → fixture-mill-3axis. The NC headers match the supplied target labels. CAM version and separate controller software version are not established. No actual post implementation, test output provenance or simulator/controller validation artifact is supplied.

The post's `validation_state: verified` is expressly synthetic; lifecycle revision 1 is **unverified** with no reviewer/evidence. It cannot satisfy post validation. Scope remains the [bounded literal dialect](../../../architecture/nc-static-review-scope.md), not generic controller compatibility. Units, G90/G54, T1 M6 and selected feed/RPM/spindle declarations are inspectable; compensation, coolant and fuller controller behavior are not thereby validated. Require qualified representative post validation with matching versions and exact output identity, then separate static/simulation review. No post edit or deployment is proposed. `SOURCE_VERIFICATION_REQUIRED`, `HUMAN_APPROVAL_REQUIRED`.

## 6. nc-static-safety-review

The exact supplied NC SHA-256 is retained in both observations and handoff. G21, G90/G17/G54, G94/G97, initial M5, T1 M6, S5000 M3, G0/G1, final M5 and M30 are present in the supported order. Literal declarations match selected job/machine/controller/post/setup labels. No coolant, probing or canned-cycle command appears; absence does not establish a physical machine state. Rapids and spindle declarations require human review and are never executed by this review.

The raw fixture checker returns only `SIMULATION_REQUIRED` and `HUMAN_APPROVAL_REQUIRED`. That does **not** reconcile physical setup or approve the program. Explicit coordinate-model review returns `not_run` / `SOURCE_VERIFICATION_REQUIRED`; no mapped targets are checked because current review evidence is absent. Composed routing likewise refuses static progression on unresolved profiles, WCS, workholding, availability and verification. It preserves the NC hash and reports no schema errors, not manufacturing readiness.

Severity: blocker. Reviewer checklist: authenticate the target/version chain and design-to-NC derivation; establish stock/fixture/tool/offset/initial-position evidence; recheck exact bytes after corrections; review all rapid and cutting moves, tool changes and spindle state; retain applicable simulation evidence. Approval remains `not_requested`, no approval record or ID. Raw bound checks cannot be presented as physical machine travel verification.

## 7. simulation-readiness-review

Available evidence is only the retained offline literal/static and routing diagnostics plus synthetic profiles. There is no machine/fixture/tool-holder simulation model, authentic stock/material-removal result or controller/post execution trace. Source/NC feature coverage is also unresolved. The following reviews are required after matching context is established:

- Model/coordinate applicability and the complete path, including approach/retract and tool-change motion, against machine, fixture and tool/holder geometry.
- Stock removal and remaining-feature comparison with the controlled design, stock condition and setup sequence.
- Post/controller compatibility for exact generated bytes and all selected modes/commands.

Results must identify model/tool/post/software versions, reviewed input hashes, conditions and limitations. A result for another revision/setup/target cannot stand in for this job. Simulation alone cannot supply physical clamp/datum/tool observation or human authority. `SIMULATION_REQUIRED` and `HUMAN_APPROVAL_REQUIRED` remain, alongside context/source blockers. Required approval scope is manufacturing handoff and its context/simulation review—not permission for this project to operate equipment.

## Evidence and outcome

Source basis: inspected repository CAD and NC bytes and the source/lifecycle records embedded in the supplied profiles. Those records support synthetic labels only; no real OEM, tooling or material claims are made. Geometry observations above are source declarations, not a fresh CAD-kernel verification. No native generator, controller interpreter, simulator or physical machine was run in this evaluation. The existing [CAD intent review](../../cad-runs/2026-09-17-manufacturing-intent/review.md) records unresolved product-definition requirements; the present CNC fixture does not resolve them.

The skill-guided review adds feature/stock/intent, tooling, setup and evidence-quality findings beyond the raw checker output. No skill-contract defect requiring an edit was identified in this controlled run. That is not a claim about unseen-case reliability. The handoff preserves unresolved assumptions and explicit qualified-review actions; no profile or approval is promoted. Gate 04 remains open for independent-tool evidence and a complete requirement audit.
