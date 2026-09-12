# Master Taxonomy v1

## Purpose

This taxonomy is the canonical vocabulary for skills, router routes, context schemas, fixtures, and evaluation. It is intentionally process-oriented and vendor-neutral.

## Design and definition

- `design_intent`: functional, dimensional, performance, cosmetic, and compliance intent.
- `cad_geometry`: parametric or explicit geometric representation.
- `assemblies`: relationships, interfaces, mating parts, and assembly constraints.
- `product_definition`: the authoritative product definition and its controlled derivatives.
- `drawings`: 2D views, notes, dimensions, title blocks, and revision data.
- `pmi`: product manufacturing information attached to a model or drawing.
- `gd_t`: datum systems, tolerances, and geometric controls; interpretation requires qualified review.
- `revisions`: controlled change identity, applicability, and supersession.

## Manufacturing planning

- `manufacturability`: process feasibility, accessibility, tolerance/process fit, and missing-context analysis.
- `materials`: material identity, grade/profile, state, compatibility, and evidence.
- `machines`: capabilities, envelope, axes, limits, and operating constraints.
- `controllers`: supported syntax, modes, offsets, units, and machine relationship.
- `setups`: stock, orientation, workholding, WCS, sequence, and repeatability assumptions.
- `workholding`: fixtures, clamps, jaws, supports, and collision/access assumptions.
- `tooling`: tool identity, geometry, holder, reach, availability, and numbering.
- `cam_strategies`: roughing, finishing, contouring, drilling, entry/exit, and sequencing intent.
- `process_parameters`: feeds, speeds, layer/process settings, power/speed, and their sources.
- `postprocessors`: CAM-to-controller translation identity, version, and validation state.
- `nc_programs`: generated NC/G-code artifacts and their provenance.
- `simulation`: static, kinematic, material-removal, or process simulation evidence.

## Workflow-specific preparation

- `additive_preparation`: mesh/package integrity, orientation, supports, printer, material, and slicer readiness.
- `two_d_cutting`: DXF/SVG units, contours, entities, layers, kerf/process intent, and machine profile.

## Verification and handoff

- `verification`: checks, evidence, findings, severity, and unresolved assumptions.
- `manufacturing_handoff`: a bounded package linking source artifacts, context, outputs, approvals, and reviewer actions.
- `provenance`: source authority, hashes, revisions, ownership, licensing, and derivative relationships.
- `approval`: human decision, scope, identity, timestamp, evidence fingerprint, and invalidation state.
- `jurisdiction`: explicit regional or regulatory context; never an implicit legal determination.

## Taxonomy rules

1. Terms identify domain concepts, not software screens or vendor product names.
2. A derivative artifact never silently replaces the authoritative design definition.
3. `unknown`, `missing`, and `unverified` are distinct states where the distinction affects consequence.
4. Safety, approval, and blocking outcomes are orthogonal to quality or completeness scores.
5. New terms require a definition, owning schema or contract, examples, negative cases, and a deprecation plan if replacing an existing term.

## Validation notes

The initial vocabulary is cross-checked against the four workflow families in the router contract and the context schemas. It is a v1 contract, not a claim that every term is already implemented.
