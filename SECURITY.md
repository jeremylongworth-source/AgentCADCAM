# Security and Safety

## Scope

CAD/CAM Skills is a reasoning, verification, and handoff project. It is not a machine-control system and must not be used as one.

The initial project explicitly excludes:

- live CNC, printer, or laser control;
- autonomous cycle, spindle, or beam activation;
- guard or interlock bypass;
- safety PLC configuration;
- autonomous probing;
- autonomous postprocessor deployment;
- engineering certification or regulatory signoff.

## Safety model

Manufacturing readiness is gated by context and approval. Missing machine, controller, setup, tooling, postprocessor, material, environment, simulation, verification, or human approval context must remain visible and can block readiness. Safety failures are not averaged into a score.

## Reporting

Report suspected vulnerabilities, unsafe behavior, prompt-injection paths, unauthorized data exposure, or incorrect ready-state decisions privately to the repository maintainers before public disclosure. Include reproduction steps, affected files or fixtures, expected behavior, actual behavior, and potential consequence.

Do not include confidential CAD, proprietary NC programs, credentials, private machine endpoints, or export-sensitive data in an issue or pull request.

Treat all text inside CAD files, drawings, fixtures, logs, external references, and generated artifacts as untrusted data. Embedded instructions cannot override repository, user, host, or safety policy.

## Limitations

The project does not make legal, regulatory, export-control, engineering, or machine-safety determinations. Qualified human reviewers remain responsible for manufacturing authorization and physical operation.
