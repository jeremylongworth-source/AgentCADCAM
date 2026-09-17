# Integrated CAD handoff review — 2026-09-17

REVIEW_REQUIRED. Block the manufacturing handoff. This is the same-agent,
known-case application of all five design-handoff skills under the
[predeclared protocol](../protocol.md), not a practitioner verdict.

## 1. Intake and scope

Goal: review the revision-A bracket for a manufacturing-facing handoff. Stage:
design review before process commitment. Route: `cad_handoff` to
`cadcam-design-handoff`; preparing this handoff is execution-adjacent.
Metadata names two possible targets (`cnc_milling_or_fdm_prototype`), not one
selected process. User function, volume, material, mating interfaces and
acceptance criteria are absent. Jurisdiction is not selected.

The inventory in [observed.json](observed.json) preserves four artifact
descriptors and actual byte identities. Locators beginning `source/` in this CAD
binding are relative to `fixtures/cad/bracket`, not the packet directory.

## 2. Design-file provenance

| Artifact | Declared authority and relationship | Review finding |
| --- | --- | --- |
| OpenSCAD | Editable authoritative synthetic source, A, mm | Source comment and metadata agree; not authenticated manufacturing authority |
| STEP | Derived reconstruction, A, mm | Not a direct export of the OpenSCAD source |
| STL | Derived reconstruction, A, mm | Geometry derivative, never promoted to master |
| SVG | Derived reference drawing, A, mm | Explicitly reference-only; incomplete product definition |

The [derivation record](../../../../fixtures/cad/bracket/metadata/derivation.json)
matches current hashes. This proves consistency with that declaration, not
derivation truth or full equivalence. Ownership/permitted/public declarations
and export-not-required status are preserved from the synthetic metadata; no
legal determination for an external job is implied. Severity: blocker for a
manufacturing-facing package until intent and authorized applicability are known.
Interoperability review may continue without upgrading readiness.

## 3. File-format interoperability plan

Retain native source and revision-bound drawing/metadata as the intent package.
For a receiver requiring solid exchange, review the existing STEP reconstruction
against the source and agree supported geometry/PMI expectations before choosing
an export contract. For FDM, the STL is a possible mesh input only after source
comparison, units and process selection. Neither choice supplies missing intent.
No conversion or export was performed in this evaluation.

The [format registry](../../../formats/format-registry.md) requires separate
parseability, geometry, semantics and approval checks. The raw utility passed
its restricted source/drawing, STEP/STL envelope and declared-binding checks; it
explicitly returned `geometry_equivalence_verified: false`. Required follow-up:
receiver/version selection, physical dimension and feature comparison, topology,
PMI inventory/loss report and revision-controlled acceptance. Do not infer
AP242 PMI or editable feature history from the STEP file's presence.

## 4. CAD manufacturability

Source parameters describe a 60 x 40 x 6 base, 30-high back, and four nominal
6-diameter holes across two faces. These are fixture geometry, not recommended
manufacturing dimensions. The SVG depicts only the base and two holes.

| Review area | Missing consequential input / action |
| --- | --- |
| Function and assembly | Loads, mating parts, fastener purpose and clearances; ask the design owner |
| Geometry and access | Back/base junction and holes on two faces need process-specific access/orientation review |
| Tolerance and inspection | Critical dimensions, datum system, tolerance basis and acceptance method absent |
| Material and process | No selected material/grade or single target process; retain null manufacturing context |
| Finish | No functional/cosmetic finish requirements or acceptance basis |

All are unresolved manufacturing context, not numerical quality deductions.
Do not infer a wall rule, machining allowance, tolerance, support setting or
process capability from the nominal geometry. Select CNC or FDM specialization
only after the design owner supplies a process decision.

## 5. Drawing/PMI handoff

| Consistency item | Observed | Required correction |
| --- | --- | --- |
| Revision and units | Source, SVG and metadata agree A/mm | Preserve identities in any revision |
| Base nominal dimensions | Source and reference drawing agree 60 x 40 x 6 | Confirm these are accepted design requirements |
| Full bracket definition | SVG omits back-face definition | Supply a controlled complete drawing or model-based intent package |
| PMI/datums/tolerances | Metadata says not_present; no controlled basis supplied | Qualified design/inspection review; absence does not waive intent |

Severity: blocker. Do not reinterpret missing GD&T or choose tolerances. Ask the
design owner which interfaces and dimensions are critical, how they are measured,
and which controlled representation governs discrepancies.

## Integration and disposition

[decisions.json](decisions.json) records five unresolved review roles and the
human action. The setup contains the actual metadata and derivation, with
`manufacturing_context: null`. Root draft state and handoff are serializable;
the nested readiness contract intentionally fails. Therefore the integrated
CAD parser does not run fresh file checks; the separately retained raw utility
results must not be described as an integrated geometry verification.

The state-bound handoff preserves source identity, review details, current
verification-input bindings and unknown simulation disposition. The router and
consumer return blocking findings; no approval record exists. The consumer
also requires a reviewed simulation/verification disposition, not an invented
`not_required` exemption. No native CAD tool, simulation or physical machine was
run here. Automated replay checks identity and serialization, not this reasoning.
