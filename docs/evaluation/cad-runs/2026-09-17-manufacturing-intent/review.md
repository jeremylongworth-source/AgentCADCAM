# Five-skill CAD manufacturing-intent review

**Decision: blocked manufacturing handoff; REVIEW_REQUIRED.** The package can continue in bounded design/prototype review. It does not establish manufacturing intent or authorize manufacturing. This is the actual AI-assisted output for the [controlled request](request.md), not an independent human/practitioner assessment, a blinded benchmark, or a pilot result.

## 1. cadcam-intake-and-scope

Goal: assess whether the synthetic bracket package supports manufacturing-handoff planning. Stage: nominal design/prototype. Family: `cad_handoff`; consequence: `manufacturing_planning`. The metadata's `cnc_milling_or_fdm_prototype` is an unresolved choice, not a selected process. Route to `cadcam-design-handoff`; do not start a CNC or additive planning job by inference.

Known: revision A, explicit mm declarations, nominal bracket parameters, public synthetic provenance, and four identified artifacts. Missing: product function, loads/environment/life, critical interfaces, volume, material/grade, process, required tolerance/datum/finish/inspection intent, supplier constraints, and applicable jurisdiction for any real job. Conflicting: no conflict found in the supported source/drawing declarations. Unverified: general geometry/semantic equivalence, actual process feasibility, and applicability to a physical product.

Reviewer questions: What function and mating geometry must be preserved? Which process/material and quantity are intended? Which dimensions are critical, what acceptance limits apply, and what inspection plan establishes conformance? Are any safety-sensitive uses or regulatory constraints involved? Until answered, retain `MISSING_CONTEXT` and `HUMAN_APPROVAL_REQUIRED`; no machine control or manufacturing output is requested.

## 2. design-file-provenance-review

| Artifact | Role and observed evidence | Disposition |
| --- | --- | --- |
| [bracket.scad](../../../../fixtures/cad/bracket/source/bracket.scad) | Declared editable design authority; revision-A mm header and six literal parameters; nominal geometry operations | Preserve as source, not an approved product specification |
| [bracket.step](../../../../fixtures/cad/bracket/source/bracket.step) | Declared CadQuery reconstruction; header states `AUTOMOTIVE_DESIGN` / AP214, not AP242 | Preserve as a derivative and verify receiver-specific geometry/semantics |
| [bracket.stl](../../../../fixtures/cad/bracket/source/bracket.stl) | Binary mesh derivative; mm comes from controlled metadata, not from its extension | Never promote to complete design master |
| [bracket.svg](../../../../fixtures/cad/bracket/source/bracket.svg) | Revision-A mm reference drawing; base projection and nominal text; explicit review-only notice | Not a controlled manufacturing drawing with complete tolerance intent |

The full SHA-256 identities, revision, units, kinds, and authority roles are preserved in [handoff.json](handoff.json). The declared source/derivative association matches current bytes. The generator reconstructs geometry from its own parameters; this is not evidence that it imported OpenSCAD. The STEP timestamp is normalized to 1970 for fixture reproducibility and is not evidence of design age or review time.

IP/confidentiality: the fixture manifest declares synthetic CC0-1.0 data and revision metadata declares owned/permitted/public, redistribution authorized, no third-party restrictions, and export review not required. These support this public synthetic evaluation only; no external job authorization or legal classification is inferred. Severity: **blocker** for manufacturing use of an incomplete product definition; **high** for unverified source-to-consumer semantic fidelity. Proceed only to bounded interoperability/DFM triage, preserving those limitations and the authoritative source.

## 3. file-format-interoperability-plan

For continued review, retain OpenSCAD plus the controlled metadata and reference drawing. The supplied STEP is a candidate geometry exchange after agreement with the receiver, not an AP242/PMI deliverable. For a subsequently selected FDM workflow, STL may be a mesh input only with separate unit/provenance/profile information and mesh validation; do not select FDM merely because STL exists. Follow the [repository format policy](../../../formats/format-registry.md).

Expected distinction: the source has editable parameters; the reconstructions do not establish preserved source feature history, tolerance intent, material definition, or acceptance criteria. The SVG supplies a nominal reference projection, not proof of complete design intent. No conversion was performed for this review; the independent native probe generated temporary test derivatives only.

NIST distinguishes computer-interpretable semantic PMI from graphical annotation appearance and describes syntax checking separately from PMI analysis. Consequently, a readable STEP header or matching nominal shape is not evidence that this fixture carries the required manufacturing information. [NIST STEP File Analyzer and Viewer](https://www.nist.gov/services-resources/software/step-file-analyzer-and-viewer). The scoped source metadata is retained in [source.json](source.json); the NIST analyzer itself was not run.

Transformation/verification plan: preserve current identities; select the actual receiver and process; agree the exchange representation and units; compare critical dimensions/features, topology and scale after import; inventory required drawing/PMI and any lost semantics; review differences before accepting a new derivative. Required corrections remain `MISSING_CONTEXT`, with qualified review before interpreting manufacturing intent. No new machine/material/process parameters are proposed.

## 4. cad-manufacturability-review

| Area | Observation and severity | Required next input or action |
| --- | --- | --- |
| Function | **Blocker:** no service function, load/environment, lifetime, or acceptance requirement | Designer establishes the intended use and consequential constraints |
| Geometry/access | Nominal 60 × 40 × 6 mm base, 30 mm upright height, and four nominal 6 mm holes are specified by the source. Native probe checks the reconstructed solid, not arbitrary source changes. **High:** process access and workholding remain unassessed | After process selection, assess access, orientations and fixture interference; no setup is invented here |
| Tolerances/datums | **Blocker:** nominal dimensions have no supplied controlled limits, datum scheme or critical-to-function classification | Designer and inspection reviewer supply the applicable drawing/PMI or explicit controlled dispositions |
| Assembly | **Blocker:** no mating-part or fastener/interface requirements | Supply interface geometry and fit/clearance requirements; nominal hole diameter is not a fit specification |
| Material/process | **Blocker:** process alternatives remain unresolved and no material/grade is selected | Select and document the intended process and material before capability claims |
| Finish | **Blocker for handoff:** finish/cosmetic requirements or a reviewed not-required disposition are absent | Establish the requirements; do not invent a finish |
| Inspection | **Blocker:** no acceptance criteria or inspection method for the important features | Define measurable acceptance and inspection responsibility |

Detailed CNC or FDM preparation is deferred until those choices and requirements are supplied. No molded-part/tooling specialization applies to this bounded scope. These are missing-context findings, not claims that the bracket is impossible to make. REVIEW_REQUIRED before tooling, ordering, production, or regulated use.

## 5. drawing-pmi-handoff-review

| Consistency item | Evidence and finding | Manufacturing disposition |
| --- | --- | --- |
| Revision/units | Source, SVG and metadata agree on A/mm within the fixture checks | Retain identity; no conflict observed in the supported declarations |
| Base dimensions/projection | Supported text/rectangle/base-hole checks agree with source parameters | Nominal consistency only; no tolerance acceptance implied |
| Upright features | OpenSCAD specifies upright holes; SVG is a base reference view | Request the controlled views/definition needed to inspect all critical features |
| PMI/tolerance/datum intent | Metadata says `not_present`; source and reference drawing do not supply controlled tolerances/datums or inspection acceptance | **Blocker:** absence is unresolved, not proof that tolerances/datums are unnecessary |
| Material/finish/assembly | No selected material, controlled finish disposition, or mating definition is supplied | **Blocker:** obtain requirements from the design authority |

Embedded semantic PMI is not universally mandatory: a suitably controlled drawing or another agreed authoritative product definition may carry the needed intent. Neither sufficient PMI nor an adequate alternative was supplied here. Do not fill gaps with defaults or reinterpret nominal numbers as tolerances. Obtain designer/engineering and inspection review, then repeat provenance, interoperability and process-specific evaluation. The result remains blocked for manufacturing handoff even though the portable file checks pass.

## Executed checks

On 2026-09-17, from the checked-out repository:

| Command | Observed result | Limit |
| --- | --- | --- |
| `.venv/Scripts/python.exe scripts/cad_handoff_checks.py` | Exit 0; four checks passed; report `review_required`, geometry equivalence false, execution false | Bounded declarations/envelopes/byte binding; not complete manufacturing intent |
| `.venv/Scripts/python.exe scripts/validate_schema_instances.py` | Exit 0; eleven definitions and fourteen existing instances validated before this packet was added | Record shape, not truth or approval |
| `venv/cad312/Scripts/python.exe -m tests.native.check_cadquery_runtime` | Exit 0 including child shutdown; temporary generated solid/STEP round-trip checks passed; reported volume `22361.41598682455 mm³`, STEP 36571 bytes, STL 102684 bytes | Fixed generator and temporary derivatives; no independent execution of OpenSCAD, complete tracked-mesh topology check, or PMI assessment |

Native versions reported: CadQuery 2.8.0, cadquery-ocp 7.9.3.1.1, CasADi 3.6.7, NLopt 2.11.0, VTK 9.6.2. The runner removed its own temporary files; no tracked geometry was regenerated. The portable positive report is retained [with the fixture](../../../../fixtures/cad/bracket/expected/file-review.json).

## Handoff and evaluation limit

[handoff.json](handoff.json) serializes `blocked`, `MISSING_CONTEXT`, `HUMAN_APPROVAL_REQUIRED`, review required, execution prohibited, and no approval ID. It references the fingerprint of [state.json](state.json); unresolved assumptions are not silently resolved. The simulation need remains unknown until the process and function are selected.

This run demonstrates application of all five skill contracts to the actual synthetic package and missing manufacturing-intent case. Contract tests can check schema, hashes, fingerprint and retained blockers; they cannot replay or grade this model's reasoning as an independent evaluation. Other negative-case skill outputs, reviewer edit burden, independent practitioner findings, and complete gate acceptance remain separate work.
