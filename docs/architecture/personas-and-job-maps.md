# Personas and Job Maps

## Personas

| Persona | Job to be done | Primary risk |
| --- | --- | --- |
| CAD designer | Preserve design intent through exchange and handoff | Lost semantics, stale revisions, missing PMI |
| CAM programmer | Plan a process with machine-aware context | Wrong post, WCS, tool, or machine assumptions |
| Machinist | Review setup and execution-adjacent artifacts | Unsafe motion, workholding, or undocumented assumptions |
| Manufacturing engineer | Assess process fit and evidence | Unvalidated capability or tolerance claims |
| Additive user | Prepare a reproducible FDM job | Mesh, material, printer, or environmental mismatch |
| Laser operator | Prepare a safe 2D cutting package | Wrong scale, geometry, material, or ventilation context |
| DFM reviewer/supplier | Receive a traceable manufacturing package | Ambiguous authority, tolerances, or acceptance criteria |
| Maintainer/evaluator | Author and test reusable skills | Unsafe defaults, missing evidence, false-ready states |

## Common job map

1. Define the job and consequence level.
2. Establish authoritative source artifacts and revision.
3. Identify units, material, process, machine, controller, setup, tooling, and jurisdiction context.
4. Review representation and manufacturing implications.
5. Generate a draft plan or review package.
6. Verify applicable static, compatibility, and simulation requirements.
7. Resolve blockers or escalate to a qualified reviewer.
8. Record scoped human approval and hand off the bounded package.

## Stop conditions

Stop and return a blocking state when authority, revision, units, material, machine, controller, setup, post, verification, authorization, or safety context is consequentially missing or conflicting.

## Initial workflow definitions

These are the frozen workflow contracts, not claims of completed practitioner validation. Each ends at a reviewable package; none includes transmitting instructions to physical equipment.

| Family and primary reviewer | Required intake | Review sequence | Handoff and blocking outcome |
| --- | --- | --- | --- |
| `cad_handoff`: designer and DFM reviewer | Authorized native/exchange files, source hierarchy, revision, units, drawings/PMI, intended manufacturing process | Establish provenance; compare representations and design intent; review manufacturability; document semantic losses and required checks | Artifact/revision inventory, interoperability plan, DFM findings, and unresolved drawing/PMI questions. Conflicting dimensions, revisions, authority, or consequential missing definition require review. |
| `cnc_milling`: CAM programmer and setup reviewer | Controlled design/NC identities; three-axis machine/controller, stock/setup/WCS/workholding, tools, CAM/post/version, material, and verification context | Match capabilities and identities; review setup/tool strategy; inspect static NC within declared dialect scope; require applicable simulation and scoped approval | Setup and review package with NC findings, simulation requirements, source evidence, and approval dependencies. Missing/mismatched consequential context blocks readiness. |
| `additive`: FDM user and qualified process reviewer | Controlled STL/3MF package, units, source revision, printer/build volume, material/slicer profile, and environmental context | Preserve package/mesh distinctions; inspect geometry and dimensions; compare printer/material profiles; identify orientation/support and slicer verification needs | Preflight findings and reproducible review context. Defects, incompatible profiles, or unresolved material/environmental risk block a manufacturing-ready claim. No guessed print parameters. |
| `laser_cutting`: laser operator and process reviewer | Controlled DXF/SVG, units/scale/path intent, machine and material identities, process profile, ventilation/emissions context | Check representation and contours; compare material/machine/process; assess beam and emission concerns separately; request scoped human review | Geometry/material/process findings and outstanding verification. Unknown material, unresolved ventilation, incompatible profiles, or unverified geometry remain blockers. No guessed laser settings. |

Unprovided values remain explicit gaps; a complete intake list is not evidence that the supplied values are correct. See the [current evidence gaps](../development/roadmap-reconciliation.md) before treating any sequence as a validated implementation.
