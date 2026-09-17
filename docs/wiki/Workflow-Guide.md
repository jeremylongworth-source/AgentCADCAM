# Workflow guide

Select the narrowest relevant workflow. All families need a bounded request, artifact inventory, source/revision/units information, and permission to use the data. Unknown consequential context must remain visible.

| Family | Skillset | Contract status |
| --- | --- | --- |
| CAD/design handoff | [cadcam-design-handoff](../../skillsets/cadcam-design-handoff.yaml) | `validated_synthetic` |
| Three-axis CNC milling | [cnc-milling-planning](../../skillsets/cnc-milling-planning.yaml) | `validated_synthetic` |
| FDM additive | [additive-print-prep](../../skillsets/additive-print-prep.yaml) | `validated_synthetic` |
| Laser cutting | [laser-cut-preflight](../../skillsets/laser-cut-preflight.yaml) | `validated_synthetic` |
| Cross-workflow verification composition | [cadcam-verification](../../skillsets/cadcam-verification.yaml) | `planned`; not an accepted universal workflow |

These labels describe development evidence, not manufacturing readiness.

## CAD and design handoff

Five skills cover intake, provenance, format exchange, manufacturability, and drawing/PMI review. Supply the authoritative product definition, derivatives, drawing/PMI where applicable, revisions, units, material/process intent, and source permissions.

Expected output: an authority/derivative inventory, consistency findings, missing design intent, verification needs, and a bounded handoff recommendation. The implemented byte-aware adapter targets the initial bracket source/STEP/STL/SVG bundle. It does not prove arbitrary STEP geometry equivalence or interpret general GD&T.

Read the [CAD integration contract](../architecture/cad-router-integration.md) and [format registry](../formats/format-registry.md).

## Three-axis CNC milling

Seven skills cover machine matching, setup, tooling, strategy, post readiness, NC review, and simulation readiness. Supply sourced machine/controller/material/tool/post context, stock, setup, workholding, WCS, CAM identity, actual NC bytes, and applicable verification/simulation evidence.

Expected output: compatibility and setup findings, tool/post reconciliation, scoped static observations, required simulation, blockers, and human-review actions. The parser supports a restricted literal NC subset; unsupported semantics block. Coordinate checks do not prove swept-volume collision freedom or physical machine state.

Read the [NC scope](../architecture/nc-static-review-scope.md), [coordinate model](../architecture/nc-coordinate-model.md), and [CNC context contract](../development/cnc-context-approval.md).

## FDM additive manufacturing

The additive preflight skill reviews STL/3MF provenance, mesh findings, units/scale, printer/material compatibility, orientation/support considerations, slicer context, and environment. Supply actual mesh/package bytes, source revision, printer/material evidence, versioned slicer inputs, and current scoped review records.

Expected output: geometry/context findings, unresolved process and environmental evidence, reviewer actions, and approval state. Bounded mesh/package inspection is not complete self-intersection detection, slicing, usable-bed certification, or a printability guarantee.

Read the [additive integration contract](../architecture/additive-router-integration.md), [STL scope](../architecture/additive-stl-evidence.md), and [3MF scope](../architecture/additive-3mf-evidence.md).

## Laser cutting

The laser preflight skill reviews DXF/SVG source identity, scale, contours, path intent, machine/material/process compatibility, and environmental context. Supply drawing bytes, revision, intended operation, applicable settings evidence, and separate beam and process-emission review records.

Expected output: geometry and context findings, unsupported or conflicting inputs, independent safety evidence gaps, and reviewer actions. The utilities do not infer safe material, power, speed, focus, kerf, or ventilation settings.

Read the [laser integration contract](../architecture/laser-router-integration.md), [DXF scope](../architecture/laser-file-evidence.md), and [SVG scope](../architecture/laser-svg-evidence.md).

## Moving between workflows

A reviewed CAD package does not satisfy CNC, additive, or laser process gates. Changing process, artifacts, machine, materials, setup, tooling or outputs requires reassessment of dependent evidence and approvals. See [Safety and approvals](Safety-and-Approvals.md).
