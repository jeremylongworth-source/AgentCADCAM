# Prohibited Capability Contract

The initial repository must not implement or expose capabilities that can make physical manufacturing self-authorizing or directly actuate equipment.

## Prohibited in v0.x

- direct CNC, printer, laser, robot, or machine-network control;
- jogging, program upload, offset changes, cycle start, spindle activation, or beam activation;
- guard/interlock bypass or safety PLC configuration;
- autonomous probing or postprocessor deployment;
- claims of engineering signoff, certification, final regulatory classification, or final export-control classification.

## Enforcement

Any request for a prohibited capability resolves to `BLOCK_EXECUTION`. A future live integration would require a separate threat model, authorization model, machine safety review, human-control model, recovery model, and audit model before consideration.
