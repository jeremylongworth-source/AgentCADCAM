# CAD/CAM Skills Development Roadmap

## Project status

**Project:** CAD/CAM Skills
**Type:** Standalone open-source AgentSkills-style repository
**Status:** Pre-development planning
**Development authority:** `ROADMAP.md`
**Relationship to AgentManufacturing:** Independent sibling project
**Initial release target:** Public alpha with validated CAD handoff, CNC milling, FDM additive, and laser-cutting workflows

---

# 1. Project mission

CAD/CAM Skills will provide AI agents with reusable, vendor-neutral skills for moving digital designs toward manufacturing through structured:

* CAD review
* design-intent preservation
* file interoperability
* DFM analysis
* CAM planning
* machine and controller context
* tooling and setup reasoning
* postprocessor review
* NC/G-code inspection
* simulation and verification
* additive manufacturing preparation
* laser-cutting preparation
* manufacturing handoff
* safety and human-approval gates

The project is not intended to replace CAD/CAM software, machine operators, manufacturing engineers, CAM programmers, or machine safety systems.

The primary value is the reasoning and verification layer connecting:

`design intent -> representation -> manufacturing process -> machine -> controller -> postprocessor -> verification -> human approval -> manufacturing handoff`

Physical machine execution remains outside the initial project boundary.

---

# 2. Core architecture principles

Development must preserve the following principles throughout the repository.

## 2.1 Standalone architecture

CAD/CAM Skills must:

* install independently
* operate independently
* maintain its own taxonomy
* maintain its own router
* maintain its own state model
* maintain its own testing and fixtures
* maintain independent versioning
* have no required dependency on AgentManufacturing

Future interoperability with other skill repositories can be introduced through explicit handoff schemas.

## 2.2 Vendor neutrality

Core skills must describe capabilities and workflows rather than depend on a particular CAD or CAM product.

Vendor-specific knowledge belongs in adapters, profiles, examples, fixtures, or optional specializations.

Supported reference ecosystems may include:

* FreeCAD
* LibreCAD
* SolveSpace
* OpenSCAD
* LinuxCNC
* CAMotics
* PyCAM
* PrusaSlicer

Commercial CAD/CAM platforms may be documented as interoperability targets without becoming architectural dependencies.

## 2.3 Evidence before assumption

Manufacturing-relevant facts must come from an appropriate source.

Priority should generally be:

1. applicable regulatory or normative standards
2. machine OEM documentation
3. controller documentation
4. CAD/CAM vendor primary documentation
5. tooling and material manufacturer documentation
6. authoritative research or government sources
7. open-source project documentation
8. community knowledge for discovery only

Machine-specific documentation overrides generic assumptions.

## 2.4 Safety as a hard gate

Safety cannot be averaged into an overall quality score.

A workflow with excellent documentation but unresolved machine, tooling, material, postprocessor, or safety context is not production-ready.

The system must be capable of returning:

* `MISSING_CONTEXT`
* `SOURCE_VERIFICATION_REQUIRED`
* `MACHINE_CONTEXT_REQUIRED`
* `SIMULATION_REQUIRED`
* `HUMAN_APPROVAL_REQUIRED`
* `REGULATORY_REVIEW_REQUIRED`
* `BLOCK_EXECUTION`

These are legitimate workflow outcomes.

## 2.5 Manufacturing output is reviewable, not self-authorizing

Generated:

* NC code
* G-code
* postprocessor modifications
* toolpaths
* setup plans
* feeds and speeds
* slicer parameters
* laser process parameters

must never become approved manufacturing instructions solely because they were generated successfully.

---

# 3. Initial release scope

The first meaningful release will support four workflow families.

## 3.1 CAD and manufacturing handoff

Capabilities:

* intake and scope definition
* design file provenance
* revision checks
* format selection
* interoperability review
* design-intent preservation
* drawing and PMI review
* DFM review
* manufacturing handoff generation

## 3.2 Three-axis CNC milling

Capabilities:

* machine capability matching
* stock and setup planning
* WCS review
* workholding assumptions
* tooling plan review
* toolpath strategy planning
* postprocessor readiness
* static NC review
* simulation requirements
* approval package generation

## 3.3 FDM additive manufacturing

Capabilities:

* STL and 3MF intake
* mesh integrity checks
* model provenance
* printer capability review
* material/profile compatibility
* orientation and support planning
* slicer readiness
* environmental and safety checks
* manufacturing package generation

## 3.4 Laser cutting

Capabilities:

* DXF/SVG intake
* units and scaling checks
* contour validation
* duplicate/open geometry detection
* material compatibility
* machine profile review
* process readiness
* fume and ventilation considerations
* human approval package

---

# 4. Explicit v0.x exclusions

The following should not be part of the initial alpha:

* direct CNC machine control
* direct printer control
* direct laser control
* autonomous machine start
* automated spindle activation
* automated beam activation
* bypassing machine guards or interlocks
* safety PLC configuration
* simultaneous five-axis machining
* advanced turning
* Swiss machining
* EDM
* plasma
* waterjet
* robotic machining
* industrial metal additive manufacturing
* production resin workflows
* autonomous probing
* full metrology systems
* autonomous postprocessor deployment
* certification or engineering signoff
* final regulatory classification
* final export-control classification

These can be evaluated after the core architecture has real-user validation.

---

# 5. Target repository structure

```text
CADCAMSkills/
│
├── README.md
├── ROADMAP.md
├── AGENTS.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── CHANGELOG.md
├── LICENSE
│
├── skills/
│
├── skillsets/
│
├── router/
│
├── state/
│
├── contexts/
│   ├── schemas/
│   └── examples/
│
├── specializations/
│   ├── cnc-milling/
│   ├── additive-fdm/
│   ├── laser-cutting/
│   └── jurisdictions/
│       └── canada/
│
├── docs/
│   ├── architecture/
│   ├── standards/
│   ├── formats/
│   ├── sources/
│   ├── evaluation/
│   └── development/
│       └── handoffs/
│
├── fixtures/
│   ├── cad/
│   ├── cnc/
│   ├── additive/
│   └── laser/
│
├── tests/
│   ├── schema/
│   ├── routing/
│   ├── interoperability/
│   ├── safety/
│   ├── golden/
│   └── evaluation/
│
└── scripts/
```

---

# 6. Development gates

Development should proceed through hard gates.

No later phase should silently redefine decisions from an earlier gate.

---

# PHASE 0 - DOMAIN CONTRACT FREEZE

## Objective

Convert the research into a formal architecture contract before implementing skills.

## Deliverables

Create:

```text
docs/architecture/domain-contract.md
docs/architecture/master-taxonomy-v1.md
docs/architecture/consequence-model.md
docs/architecture/execution-boundary.md
docs/architecture/personas-and-job-maps.md
docs/architecture/specialization-model.md
```

### Domain contract must define

* project mission
* users
* supported workflow families
* in-scope capabilities
* conditional capabilities
* prohibited capabilities
* physical execution boundary
* vendor-neutrality policy
* evidence requirements
* human approval model
* relationship to AgentManufacturing

### Master taxonomy must cover

* design intent
* CAD geometry
* assemblies
* product definition
* drawings
* PMI
* GD&T
* revisions
* manufacturability
* materials
* machines
* controllers
* setups
* workholding
* tooling
* CAM strategies
* process parameters
* postprocessors
* NC programs
* simulation
* additive preparation
* 2D cutting
* verification
* manufacturing handoff

## Required decision

Freeze the first four supported workflow families:

1. CAD/manufacturing handoff
2. CNC milling
3. FDM additive
4. laser cutting

## Exit gate

`CADCAM_01_DOMAIN_CONTRACT_READY`

Requirements:

* domain contract complete
* taxonomy reviewed
* initial personas documented
* initial workflows defined
* execution boundary explicit
* prohibited capabilities explicit
* no unresolved architectural dependency on AgentManufacturing

---

# PHASE 1 - FOUNDATION AND REPOSITORY CONTRACTS

## Objective

Build the reusable architecture on which every skill will depend.

## Deliverables

### Repository standards

```text
docs/standards/skill-authoring-standard.md
docs/standards/research-and-evidence-standard.md
docs/standards/interoperability-standard.md
docs/standards/safety-governance-standard.md
docs/standards/testing-standard.md
docs/standards/evaluation-standard.md
docs/standards/context-profile-standard.md
```

### Format registry

Establish canonical handling for:

* native CAD
* STEP AP242
* IGES
* DXF
* SVG
* STL
* 3MF
* NC/G-code
* STEP-NC as a research track

Each format entry should document:

* intended purpose
* semantics preserved
* semantics commonly lost
* unit handling
* revision implications
* suitable workflow
* unsuitable workflow
* validation requirements

### Context schemas

Create schemas for:

```text
contexts/schemas/job.schema.json
contexts/schemas/machine.schema.json
contexts/schemas/controller.schema.json
contexts/schemas/material.schema.json
contexts/schemas/tool.schema.json
contexts/schemas/post.schema.json
contexts/schemas/setup.schema.json
contexts/schemas/approval.schema.json
contexts/schemas/handoff.schema.json
```

### Validation scripts

Initial scripts should validate:

* YAML
* JSON
* skill metadata
* skillset manifests
* context schemas
* broken references
* missing source metadata
* fixture manifests

## State invalidation rule

Changes to any of these must invalidate dependent approvals:

* source file/revision
* units
* process
* machine
* controller
* setup
* workholding
* tool
* postprocessor
* material
* generated manufacturing output

## Exit gate

`CADCAM_02_FOUNDATION_READY`

Requirements:

* repository structure established
* schemas validate
* authoring standards established
* evidence hierarchy established
* safety standard established
* format registry established
* validation scripts operational

---

# PHASE 2 - CORE CAD AND DIGITAL HANDOFF SKILLS

## Objective

Prove that CAD/CAM Skills can reliably reason about design information before adding machine-specific CAM complexity.

## Atomic skills

### 1. `cadcam-intake-and-scope`

Produces:

* job brief
* artifact inventory
* target workflow
* missing-context report
* consequence classification

### 2. `design-file-provenance-review`

Checks:

* source authority
* revisions
* derived artifacts
* ownership/licensing status
* conflicting versions
* traceability

### 3. `file-format-interoperability-plan`

Determines:

* suitable exchange format
* expected semantic losses
* transformation risks
* required verification

### 4. `cad-manufacturability-review`

Evaluates:

* basic manufacturing feasibility
* accessibility
* feature complexity
* tolerance/process alignment
* missing manufacturing context

### 5. `drawing-pmi-handoff-review`

Evaluates:

* drawing/model consistency
* PMI availability
* datum/tolerance intent
* revision consistency
* manufacturing interpretation risks

## First skillset

```text
skillsets/cadcam-design-handoff.yaml
```

Recommended composition:

```text
cadcam-intake-and-scope
design-file-provenance-review
file-format-interoperability-plan
cad-manufacturability-review
drawing-pmi-handoff-review
```

## Fixture family

Create a simple reproducible mechanical part.

Provide:

* editable/open CAD source
* STEP
* STL
* drawing
* revision metadata

Negative mutations:

* revision mismatch
* missing units
* stale derived file
* STL treated as design master
* missing PMI
* conflicting dimensions

## Exit gate

`CADCAM_03_DESIGN_HANDOFF_READY`

Requirements:

* CAD bundle operational
* source hierarchy respected
* revision mismatches detected
* format semantics correctly distinguished
* negative fixtures correctly blocked
* no silent assumption that mesh geometry equals complete manufacturing intent

---

# PHASE 3 - CNC MILLING ALPHA

## Objective

Build the first execution-adjacent workflow while proving machine-aware safety controls.

## Atomic skills

### 6. `machine-capability-match`

Inputs:

* manufacturing requirements
* machine profile

Evaluates:

* travel
* axis configuration
* spindle capability
* envelope
* process suitability

### 7. `cnc-setup-planner`

Produces:

* stock assumptions
* setup sequence
* orientation
* workholding requirements
* WCS requirements

### 8. `tooling-plan-review`

Checks:

* tool availability
* holder information
* geometry
* reach
* compatibility
* tool numbering

### 9. `toolpath-strategy-planner`

Produces strategy recommendations for:

* roughing
* finishing
* contouring
* drilling
* entry/exit
* sequencing

It should not fabricate machine parameters when authoritative inputs are missing.

### 10. `postprocessor-readiness-review`

Verifies:

* CAM system
* machine
* controller
* postprocessor
* post version
* validation state

Mismatch must be treated as blocking.

### 11. `nc-static-safety-review`

Performs static inspection for:

* units
* coordinate assumptions
* unsupported commands
* suspicious motion
* tool references
* spindle commands
* offsets
* modal assumptions
* machine/controller mismatch

Static review does not prove safe operation.

### 12. `simulation-readiness-review`

Determines:

* required simulation level
* missing machine model
* missing fixture geometry
* unverified code
* remaining assumptions

## Skillset

```text
skillsets/cnc-milling-planning.yaml
```

## Initial open-source test ecosystem

Use independent tools where practical:

* FreeCAD CAM
* LinuxCNC
* CAMotics

These should provide fixture and interoperability evidence, not become mandatory runtime dependencies.

## CNC golden fixture

Example:

```text
fixtures/cnc/mill-bracket/
├── source/
├── contexts/
├── expected/
└── mutations/
```

Mutations must include:

```text
wrong-units/
wrong-post/
wrong-controller/
missing-wcs/
unknown-tool/
revision-mismatch/
machine-limit-conflict/
incorrect-tool-number/
```

## Hard manufacturing rule

An NC artefact cannot receive an approved state unless all required:

* machine
* controller
* setup
* tooling
* postprocessor
* verification

contexts are known.

## Exit gate

`CADCAM_04_CNC_ALPHA_READY`

Requirements:

* 100% detection of curated machine/controller/post mismatches
* zero critical false-ready decisions in negative fixtures
* missing WCS blocks readiness
* missing tooling data blocks readiness where consequential
* simulation gate works
* postprocessor validation tracked explicitly
* no physical machine execution capability exists

---

# PHASE 4 - ADDITIVE MANUFACTURING ALPHA

## Objective

Extend the architecture into a non-CNC digital manufacturing process while preserving the same evidence and safety model.

## Atomic skills

### 13. `additive-job-preflight`

Core responsibilities:

* mesh/package intake
* source provenance
* STL vs 3MF handling
* printer profile matching
* material profile matching
* model validity
* build-volume compatibility
* orientation considerations
* support requirements
* slicer readiness
* environmental considerations

Future split candidates:

```text
mesh-integrity-review
print-orientation-support-plan
slicer-profile-review
```

These should only become separate skills if repeated usage justifies distinct contracts.

## Skillset

```text
skillsets/additive-print-prep.yaml
```

## Reference ecosystem

Use PrusaSlicer and open test models for deterministic fixtures.

## Negative fixtures

Include:

* non-manifold geometry
* unsupported material
* missing material profile
* incompatible printer profile
* revision mismatch
* unsupported build volume
* missing environmental information

## Exit gate

`CADCAM_05_ADDITIVE_ALPHA_READY`

Requirements:

* STL and 3MF distinctions preserved
* material parameters are never invented when authoritative context is absent
* printer/material incompatibility detected
* model defects surfaced
* provenance preserved
* unresolved material or environmental risk blocks manufacturing-ready status

---

# PHASE 5 - LASER CUTTING ALPHA

## Objective

Validate CAD/CAM Skills against a 2D manufacturing workflow with material-specific safety concerns.

## Atomic skills

### 14. `laser-job-preflight`

Responsibilities:

* DXF/SVG intake
* units
* scaling
* geometry closure
* duplicate geometry
* path intent
* machine compatibility
* material compatibility
* process profile readiness
* safety requirements
* ventilation/fume concerns

## Skillset

```text
skillsets/laser-cut-preflight.yaml
```

## Negative fixtures

Include:

* duplicate contours
* open contours
* unsupported entity
* wrong units
* scale mismatch
* unknown material
* prohibited/unsafe material
* missing ventilation context
* machine/material incompatibility

## Exit gate

`CADCAM_06_LASER_ALPHA_READY`

Requirements:

* geometry defects reliably detected
* unknown material cannot receive production-ready status
* unsafe-material uncertainty triggers blocking state
* laser settings are not guessed
* beam and process-emission risks are represented independently

---

# PHASE 6 - ROUTER AND STATE INTEGRATION

## Objective

Turn independent skills into a coherent AgentSkills-style domain system.

## Router

Create:

```text
router/
├── router-contract.md
├── routes.yaml
└── tests/
```

Minimum router inputs:

```yaml
process_family:
artifact_class:
machine_known:
controller_known:
material_known:
jurisdiction_known:
consequence_level:
approval_state:
```

Process families:

```text
cad_handoff
cnc_milling
additive
laser_cutting
unknown
```

Consequence levels:

```text
informational
design_advisory
manufacturing_planning
execution_adjacent
live_execution
```

## State system

Create bounded job state for:

```yaml
job_id:
revision:
source_artifact_hashes:
units:
process_family:
material:
machine_profile:
controller_profile:
setup:
work_coordinate_system:
tool_library:
cam_system:
postprocessor:
post_version:
simulation_status:
verification_results:
jurisdiction:
ip_status:
export_review_status:
approval_status:
```

Avoid free-form persistent agent memory as a manufacturing source of truth.

## Required invalidation behavior

If a validated job changes its:

* design revision
* source hash
* units
* machine
* controller
* setup
* tool
* post
* material

the router must invalidate downstream approvals.

## Exit gate

`CADCAM_07_INTEGRATION_READY`

Requirements:

* deterministic routing
* correct consequence classification
* state schemas validate
* invalidation behavior tested
* all four initial workflows route correctly
* live-execution requests resolve to `BLOCK_EXECUTION`

---

# PHASE 7 - SAFETY, GOVERNANCE, AND ADVERSARIAL HARDENING

## Objective

Make failure handling as deliberate as successful workflow completion.

## Build

```text
tests/safety/
tests/adversarial/
docs/architecture/approval-model.md
docs/architecture/regulatory-review-model.md
docs/architecture/ip-and-provenance-model.md
```

## Safety tests

Test:

* missing machine
* unknown controller
* incorrect postprocessor
* conflicting units
* unauthorized source file
* unknown material
* missing safety context
* request to bypass guard
* request to disable safety system
* request to directly start machine
* request to produce production-ready output without verification
* export-sensitive technical data
* conflicting revisions

## Regulatory architecture

Core project remains jurisdiction-neutral.

Jurisdiction-specific knowledge must be selected explicitly.

Initial optional specialization:

```text
specializations/jurisdictions/canada/
```

It may cover:

* Canadian occupational safety sources
* Canadian export-control research routing
* applicable manufacturing references

It must not claim to make final legal determinations.

## IP and confidentiality model

Manufacturing jobs should support:

```yaml
ownership_status:
licence_status:
confidentiality:
third_party_restrictions:
redistribution_authorized:
export_review_status:
```

Possession of a CAD file must never automatically imply authorization to manufacture or redistribute it.

## Exit gate

`CADCAM_08_PUBLIC_ALPHA_READY`

Requirements:

* adversarial tests pass
* prohibited live actions blocked
* critical safety failure recall is 100% on curated corpus
* zero critical false-ready states
* authoritative-source requirement enforced
* SECURITY.md complete
* CONTRIBUTING.md complete
* public limitations documented
* source freshness process documented

---

# PHASE 8 - REAL-INPUT PILOT

## Objective

Prove practical usefulness outside synthetic fixtures.

## Pilot groups

Seek evaluation from users representing several of:

* CAD designers
* mechanical designers
* CAM programmers
* machinists
* manufacturing engineers
* additive users
* laser operators
* makers
* DFM reviewers

## Required evaluation packet

Each pilot should preserve:

```text
input/
baseline-output/
skill-output/
reviewer-findings/
required-edits/
safety-findings/
final-verdict/
```

## Measure

* output completeness
* routing accuracy
* revision defect detection
* interoperability recommendation accuracy
* machine/post mismatch detection
* unsafe assumptions
* reviewer edit burden
* usefulness
* false-ready decisions

## Target outcomes

### Mandatory

* 100% schema validity
* 100% critical known-safety-case detection
* zero critical false manufacturing-ready decisions
* 100% authoritative sourcing for safety/regulatory claims

### Pilot targets

* router accuracy >= 97%
* handoff completeness >= 98%
* revision/provenance detection >= 98%
* interoperability recommendation accuracy >= 95%
* unsupported factual assumptions < 2%
* reviewer usable-with-minor-or-no-edits >= 90%
* reviewer edit burden reduced by at least 30% against baseline

## Exit gate

`CADCAM_09_PILOT_VALIDATED`

Scenario testing alone cannot satisfy this gate.

Real manufacturing practitioners or suitably qualified reviewers must evaluate real input packets.

---

# 7. Initial atomic skill inventory

The first development generation should remain intentionally constrained.

```text
skills/
├── cadcam-intake-and-scope/
├── design-file-provenance-review/
├── file-format-interoperability-plan/
├── cad-manufacturability-review/
├── drawing-pmi-handoff-review/
│
├── machine-capability-match/
├── cnc-setup-planner/
├── tooling-plan-review/
├── toolpath-strategy-planner/
├── postprocessor-readiness-review/
├── nc-static-safety-review/
├── simulation-readiness-review/
│
├── additive-job-preflight/
└── laser-job-preflight/
```

Total initial skills: **14**

Do not create dozens of narrow skills before the evaluation corpus demonstrates that they are necessary.

---

# 8. Initial skillsets

```text
skillsets/
├── cadcam-design-handoff.yaml
├── cnc-milling-planning.yaml
├── additive-print-prep.yaml
├── laser-cut-preflight.yaml
└── cadcam-verification.yaml
```

## `cadcam-verification`

This should compose verification-related capabilities across workflows rather than implement another process.

Likely composition:

* provenance review
* interoperability review
* machine capability review where applicable
* postprocessor readiness
* static NC review where applicable
* simulation readiness
* approval validation

No universal `all` bundle should be the default installation.

---

# 9. Phase 2 expansion candidates

After `CADCAM_09_PILOT_VALIDATED`, evaluate adding:

### CAD

* assembly manufacturability
* advanced PMI/GD&T interpretation
* change-impact analysis
* tolerance/process capability analysis
* model-based definition validation

### CNC

* turning
* mill-turn
* indexed multi-axis
* simultaneous five-axis
* probing
* advanced workholding
* feeds/speeds sourcing
* machine simulation
* postprocessor development review

### Additive

* resin
* industrial polymer
* metal additive
* powder handling
* production qualification

### Cutting and fabrication

* plasma
* waterjet
* CNC router
* sheet processing

### Quality

* inspection planning
* metrology
* CMM handoff
* inspection result comparison
* closed-loop manufacturing feedback

### Interoperability

* deeper STEP-NC support
* AP242 validation
* digital thread integration
* PLM/MES handoff

Each expansion requires a separate domain-risk review before inclusion.

---

# 10. MCP and external integrations

External tool integration should come after the portable skill layer is proven.

## Early integrations

Prefer read-only or offline capabilities such as:

* file inspection
* geometry metadata
* CAD conversion validation
* CAM job analysis
* G-code parsing
* simulation invocation
* slicer analysis

## Later integrations

Potential integrations:

* FreeCAD
* LinuxCNC simulation/test environments
* CAMotics
* PrusaSlicer
* commercial CAD/CAM APIs

## Explicitly deferred

Live machine connectors capable of:

* jogging
* loading programs
* changing offsets
* activating spindle
* activating laser
* starting cycles

must not be introduced during the initial development roadmap.

Any future live integration requires a separate:

* threat model
* authorization model
* machine safety review
* human control model
* recovery model
* audit model

---

# 11. Development sequence summary

```text
CADCAM-01
Domain Contract
        |
        v
CADCAM-02
Foundation and Schemas
        |
        v
CADCAM-03
CAD / Design Handoff
        |
        v
CADCAM-04
CNC Milling Alpha
        |
        +----------------+
        |                |
        v                v
CADCAM-05          CADCAM-06
Additive Alpha     Laser Alpha
        |                |
        +--------+-------+
                 |
                 v
CADCAM-07
Router + State Integration
                 |
                 v
CADCAM-08
Safety + Public Alpha
                 |
                 v
CADCAM-09
Real-Input Validation
                 |
                 v
      EXPANSION ROADMAP
```

---

# 12. Development gate register

| Gate                              | Meaning                                                      |
| --------------------------------- | ------------------------------------------------------------ |
| `CADCAM_01_DOMAIN_CONTRACT_READY` | Scope, taxonomy, personas, safety boundary frozen            |
| `CADCAM_02_FOUNDATION_READY`      | Repository contracts, schemas and standards operational      |
| `CADCAM_03_DESIGN_HANDOFF_READY`  | CAD and interoperability workflow validated                  |
| `CADCAM_04_CNC_ALPHA_READY`       | Three-axis CNC planning and verification validated           |
| `CADCAM_05_ADDITIVE_ALPHA_READY`  | FDM additive preflight validated                             |
| `CADCAM_06_LASER_ALPHA_READY`     | Laser preflight validated                                    |
| `CADCAM_07_INTEGRATION_READY`     | Router/state model works across initial domain               |
| `CADCAM_08_PUBLIC_ALPHA_READY`    | Safety, governance and public release requirements satisfied |
| `CADCAM_09_PILOT_VALIDATED`       | Real-input practitioner validation complete                  |

---

# 13. First development pack

Implementation should not begin by creating all 14 skills.

The first development wave should be:

## `CADCAM-01-domain-contract-and-foundation`

### Pack 01 - Repository bootstrap

Create:

* repository root
* README skeleton
* ROADMAP
* AGENTS
* LICENSE
* CONTRIBUTING
* SECURITY
* CODE_OF_CONDUCT
* CHANGELOG
* directory structure

### Pack 02 - Domain contract

Create:

* domain contract
* execution boundary
* consequence model
* personas
* initial workflow definitions

### Pack 03 - Master taxonomy

Create the canonical CAD/CAM taxonomy and definitions.

### Pack 04 - Evidence and interoperability

Create:

* source hierarchy
* evidence standard
* format registry
* interoperability standard

### Pack 05 - Context architecture

Implement initial schemas for:

* job
* machine
* controller
* material
* tool
* post
* setup
* approval
* handoff

### Pack 06 - Safety architecture

Create:

* safety governance standard
* approval model
* prohibited capability contract
* regulatory review model
* provenance/IP model

### Pack 07 - Foundation tests

Add:

* schema tests
* validation scripts
* negative tests
* routing-contract tests
* broken-reference checks

### Pack 08 - Foundation closeout

Perform:

* architecture audit
* roadmap reconciliation
* unresolved-question review
* readiness decision

Expected closeout token:

`CADCAM_02_FOUNDATION_READY`

Only after this token should implementation proceed to the first production skill wave.

---

# 14. Development-ready definition

CAD/CAM Skills should be considered ready for sustained skill implementation only when:

* standalone scope is frozen
* taxonomy is stable enough for v0.1
* execution boundary is explicit
* safety rules are machine-readable where practical
* evidence hierarchy is documented
* formats are classified
* context schemas validate
* state invalidation rules exist
* router contract exists
* pilot fixture architecture exists
* prohibited capabilities are documented
* licensing policy for third-party fixtures/code is documented
* repository validators pass

Until these conditions are satisfied, development should remain in foundation work rather than expanding the skill inventory.

---

# 15. Long-term project direction

The long-term opportunity is broader than a collection of CAD/CAM prompts.

CAD/CAM Skills can become a reusable digital-manufacturing reasoning layer that understands relationships among:

* design requirements
* geometry
* PMI
* manufacturing process
* machines
* controllers
* materials
* tooling
* setups
* CAM strategies
* posts
* NC instructions
* simulations
* inspection
* revisions
* approvals

The project should advance toward that goal incrementally while preserving one fundamental rule:

**No AI-generated manufacturing artefact becomes physically actionable merely because the software reports that generation or simulation succeeded.**

Human manufacturing authority remains part of the workflow.
