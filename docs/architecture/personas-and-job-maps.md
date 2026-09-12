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
