# Repository Agent Instructions

## Authority and scope

- `ROADMAP.md` is the governing project roadmap and defines phase gates.
- This repository is standalone. Do not introduce a required dependency on AgentManufacturing.
- Keep the core portable and vendor-neutral; put vendor-specific behavior in explicit adapters, profiles, examples, or fixtures.
- Preserve source provenance, revision identity, units, and design intent throughout every workflow.

## Safety boundary

- This project provides review, planning, verification, and handoff guidance only.
- Never add direct machine control, autonomous machine start, spindle or beam activation, interlock bypass, or safety-system disabling.
- Never label generated NC, G-code, toolpaths, slicer settings, or laser parameters production-approved without the required context, verification, and human approval.
- Treat unresolved consequential context as a blocking outcome, not as a quality deduction.

## Development workflow

1. Work in roadmap order and record the applicable exit-gate evidence.
2. Use machine-readable schemas for persistent job context; do not use free-form agent memory as a source of truth.
3. Cite authoritative sources for safety, regulatory, machine, controller, tooling, material, and process claims.
4. Add positive and negative fixtures for every consequential decision.
5. Run `python scripts/validate_foundation.py` before submitting foundation changes.
6. Keep assumptions explicit and mark draft guidance as `REVIEW_REQUIRED`.

## Change hygiene

- Do not silently broaden the initial scope.
- Do not invent machine parameters when authoritative inputs are missing.
- Changes to source files, units, process, machine, controller, setup, workholding, tool, postprocessor, material, or generated output invalidate dependent approvals.
- Document architectural decisions and unresolved questions in `docs/architecture/`.
