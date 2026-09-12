# Physical Execution Boundary

## In scope

CAD/CAM Skills may inspect files and metadata, reason about design intent and interoperability, compare supplied context, plan processes and setups, perform static checks, identify simulation requirements, and assemble a human-review package.

## Out of scope

The system must not connect to or operate a CNC machine, printer, laser, spindle, beam, robot, safety PLC, probe, offset table, or machine network. It must not start cycles, jog axes, upload programs, change offsets, activate energy sources, bypass guards, or disable interlocks.

## Output boundary

NC, G-code, toolpaths, slicer settings, laser parameters, posts, and setup plans are artifacts for review. Generation or successful parsing does not imply safety, correctness, certification, or authorization; generated manufacturing artifacts are not self-authorizing.

## Required handoff

Every execution-adjacent output must identify source artifacts, context identity, assumptions, verification performed, unresolved blockers, required simulation, and the human approval action. Physical execution remains the responsibility of qualified personnel using the machine’s own safety and operating procedures.

## Review status

`REVIEW_REQUIRED` is mandatory before tooling, ordering, production, or regulated use. `BLOCK_EXECUTION` is mandatory for any live-control request.
