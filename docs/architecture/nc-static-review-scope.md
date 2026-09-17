# Literal NC static review boundary

## Decision — 2026-09-17

For maintainers implementing Phase 3: replace whole-program regex searches in [nc_static_checks.py](../../scripts/nc_static_checks.py) with an inert literal-word reader and ordered block checks. The previous implementation could miss compact coordinates, count comments as required modes/tool changes, and accept declarations placed after the first motion. The regression suite reproduced these failures before the change.

Keeping regex searches was insufficient because lexical identity and declaration order matter. A full controller interpreter is not introduced: it would require explicit dialect, parameter, offset and machine semantics plus separate validation. The current implementation remains portable, offline and non-executing, with unsupported syntax explicitly blocking. It does not load a controller, run NC or connect to equipment.

## Current data flow and responsibilities

1. Read the supplied string and separate ordinary parenthesized/semicolon comments from words. Accept unique standalone prologue identity declarations; duplicate or late headers block. Comments never establish required modes or tools.
2. Parse literal decimal `G M N X Y Z T F S` words with case/spacing normalization. Preserve decimal command identity rather than truncating it. Reconcile actual commands with both the supplied controller allowlist and the reviewer's implemented subset.
3. Walk blocks, checking duplicate words/modal conflicts, explicit units, absolute mode, selected WCS, motion mode and tool change before axis words. Retain G0/G1 across subsequent axis-only blocks. Tool selection can precede M6 or share its block; every selected tool must reconcile with the one supplied fixture tool.
4. Compare explicit axis values with declared fixture coordinate bounds. Return findings and existing context/post/simulation/approval-declaration blockers. Every output remains review-required and non-executable; a new `validation_scope` field states the limits.

Dependencies remain Python's standard library and the caller's context dictionaries. The input contexts are the existing synthetic fixture structures, not authenticated or schema-validated profiles inside this function. CLI context loading is unchanged.

## Supported subset and conservative refusals

The implemented command set is G0, G1, G17, G20, G21, G54, G90, M3, M5, M6 and M30, further restricted by the supplied profile. G20 is recognized for unit-conflict review, not automatic conversion of fixture limits. Decimal G codes such as G54.1 remain distinct and unsupported. Adding a command to a profile cannot add its semantics to this checker.

Expressions, parameters, macros, subprograms, block delete, additional axes/word types, incremental motion and unimplemented commands return `SOURCE_VERIFICATION_REQUIRED`. Controller-unsupported commands also return `MACHINE_CONTEXT_REQUIRED`. Malformed/nested comments, comments splitting words, recognized active-comment extensions, duplicate headers, repeated words and conflicting modal groups block. Extra executable words after M30 or a closing percent delimiter block rather than being silently ignored. Percent delimiters, when supplied, must be paired.

Comments and numeric spelling are lexical support, not support for every controller's extensions. The reviewer deliberately applies stricter rules than an interpreter in some cases (for example trailing executable content and repeated words). Reports can contain parsed observations from an invalid block, but the parsing blocker cannot be removed by those observations.

## Evidence source

Source: [G-code Overview](https://www.linuxcnc.org/docs/html/gcode/overview.html), publisher LinuxCNC; page last updated **2026-09-13 12:07:03 UTC**, accessed **2026-09-17**. Scope: reference syntax and ordering, not the synthetic controller's compatibility or any machine-safety claim. Supported claims: words may be compact and case-insensitive; comments are separate from words; modal groups constrain coexisting commands; tool selection precedes change within a block. Sections on comments also distinguish active comment extensions. This source informed lexical tests; LinuxCNC itself was not run and is not a runtime dependency.

## Remaining risks and roadmap work

- Literal coordinate bounds are not physical machine travel checks. No work/tool-offset transform, starting machine position, swept volume, fixture collision or reach model is implemented.
- F/S values are parsed, but feed/spindle limits, spindle transitions, feed-mode assumptions, stopping behavior and cutting feasibility still need explicit checks and evidence. Merely listing M3/M5 is not spindle-state verification.
- G90 and G54 declarations do not prove actual offsets, machine state, workholding or applicability. Supplied profile lifecycles, post identity/version and evidence truth need the composed context review, not just this parser.
- Approval and simulation strings are declarations. This function does not authenticate reviewers, check an approval fingerprint, bind an NC artifact to simulation, or serialize a qualified manufacturing handoff.
- Full CNC negative-case skill outputs, independent-tool evidence where practical, and a requirement-by-requirement gate audit remain open. This parser milestone does not accept gate 04 or any later gate.

The [unit regressions](../../tests/safety/test_nc_word_review.py) cover positive spelling/comment/modal controls and the corresponding negatives without mocks, external services or physical data. Revisit this decision when supporting a new dialect, richer expressions, multiple tools, offsets or new process scope; add explicit semantics and independent evidence rather than weakening the unknown-syntax blocker. REVIEW_REQUIRED.
