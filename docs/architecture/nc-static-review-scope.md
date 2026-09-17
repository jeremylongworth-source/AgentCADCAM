# Literal NC static review boundary

## Decision — 2026-09-17

For maintainers implementing Phase 3: replace whole-program regex searches in [nc_static_checks.py](../../scripts/nc_static_checks.py) with an inert literal-word reader and ordered block checks. The previous implementation could miss compact coordinates, count comments as required modes/tool changes, and accept declarations placed after the first motion. The regression suite reproduced these failures before the change.

Keeping regex searches was insufficient because lexical identity and declaration order matter. A full controller interpreter is not introduced: it would require explicit dialect, parameter, offset and machine semantics plus separate validation. The current implementation remains portable, offline and non-executing, with unsupported syntax explicitly blocking. It does not load a controller, run NC or connect to equipment.

## Current data flow and responsibilities

1. Read the supplied string and separate ordinary parenthesized/semicolon comments from words. Accept unique standalone prologue identity declarations; duplicate or late headers block. Comments never establish required modes or tools.
2. Parse literal decimal `G M N X Y Z T F S` words with case/spacing normalization. Preserve decimal command identity rather than truncating it. Reconcile actual commands with both the supplied controller allowlist and the reviewer's implemented subset.
3. Walk blocks, checking duplicate words/modal conflicts, explicit units, absolute mode, selected WCS, motion mode and tool change before axis words. Retain G0/G1 across subsequent axis-only blocks. Tool selection can precede M6 or share its block; every selected tool must reconcile with the one supplied fixture tool.
4. Check finite, ordered numeric context and matching length/feed/RPM units; compare declared F/S values with supplied limits and track commanded spindle state. With an explicit [coordinate model](nc-coordinate-model.md), compare initial position and translated targets with declared machine-axis bounds. Without one, compare only raw fixture coordinates and return `coordinate_review: null`; the composed router cannot use that fallback. Return findings and existing context/post/simulation/approval-declaration blockers. Every output remains review-required and non-executable; `validation_scope` states the limits.

The lexical checks use Python's standard library and the caller's context dictionaries. The optional coordinate review also uses the existing local JSON Schema validator. That stage validates its model; it does not schema-validate every other profile inside this function or authenticate source claims. CLI context loading is unchanged.

## Supported subset and conservative refusals

The implemented command set is G0, G1, G17, G20, G21, G54, G90, G94, G97, M3, M5, M6 and M30, further restricted by the supplied profile. G20 is recognized for unit-conflict review, not automatic conversion of fixture limits. Decimal G codes such as G54.1 remain distinct and unsupported. Adding a command to a profile cannot add its semantics to this checker.

Expressions, parameters, macros, subprograms, block delete, additional axes/word types, incremental motion and unimplemented commands return `SOURCE_VERIFICATION_REQUIRED`. Controller-unsupported commands also return `MACHINE_CONTEXT_REQUIRED`. Malformed/nested comments, comments splitting words, recognized active-comment extensions, duplicate headers, repeated words and conflicting modal groups block. Extra executable words after M30 or a closing percent delimiter block rather than being silently ignored. Percent delimiters, when supplied, must be paired.

Comments and numeric spelling are lexical support, not support for every controller's extensions. The reviewer deliberately applies stricter rules than an interpreter in some cases (for example trailing executable content and repeated words). Reports can contain parsed observations from an invalid block, but the parsing blocker cannot be removed by those observations.

## Evidence source

Source: [G-code Overview](https://www.linuxcnc.org/docs/html/gcode/overview.html), publisher LinuxCNC; page last updated **2026-09-13 12:07:03 UTC**, accessed **2026-09-17**. Scope: reference syntax and ordering, not the synthetic controller's compatibility or any machine-safety claim. Supported claims: words may be compact and case-insensitive; comments are separate from words; modal groups constrain coexisting commands; tool selection precedes change within a block. Sections on comments also distinguish active comment extensions. This source informed lexical tests; LinuxCNC itself was not run and is not a runtime dependency.

## Remaining risks and roadmap work

- Literal coordinate bounds are not physical machine travel checks. The optional fixed Cartesian model checks declared starting position and translated targets only. Swept volume, fixture collision, reach and observed physical state remain unverified.
- F/S declarations and selected commanded-state transitions are checked as described below. Actual speed, feed override, acceleration, stopping time, tool/material suitability and cutting feasibility remain unverified. No state observation or physical spindle verification occurs.
- G90 and G54 declarations do not prove actual offsets, machine state, workholding or applicability. Supplied profile lifecycles, post identity/version and evidence truth need the composed context review, not just this parser.
- Approval and simulation strings are declarations. This function does not authenticate reviewers, check an approval fingerprint, bind an NC artifact to simulation, or serialize a qualified manufacturing handoff. The [composed router](nc-artifact-approval-binding.md) now binds actual NC bytes to the state fingerprint and reruns these checks; simulation truth and physical applicability remain unverified.
- Full CNC negative-case skill outputs, independent-tool evidence where practical, and a requirement-by-requirement gate audit remain open. This parser milestone does not accept gate 04 or any later gate.

The [unit regressions](../../tests/safety/test_nc_word_review.py) cover positive spelling/comment/modal controls and the corresponding negatives without mocks, external services or physical data. Revisit this decision when supporting a new dialect, richer expressions, multiple tools, offsets or new process scope; add explicit semantics and independent evidence rather than weakening the unknown-syntax blocker. REVIEW_REQUIRED.

## Feed, spindle and numeric-context follow-up — 2026-09-17

The reader now requires explicit G94 before interpreting F and G97 before interpreting S or a commanded spindle start. Values persist across blocks; a change of feed/spindle mode clears the corresponding stored value. Unknown initial spindle state is not assumed stopped. For this bounded milling review policy, tool changes require an earlier explicit M5; G1 axis motion requires a positive declared feed and an explicit commanded-on spindle state; commanded-on RPM must be positive and within declared limits. An explicit stop is required before M30 and at the end of supplied text. A later valid declaration does not remove an earlier finding. No input is repaired, clamped or approved by these checks.

These are conservative review conditions, not universal G-code validity rules. In particular, the reviewer does not infer that M6 or program termination will safely stop a physical spindle, and it blocks commanded-on S0 for this milling fixture even where an interpreter permits that combination. Noncutting G1 moves cannot be automatically distinguished from cutting moves here; they require review rather than an inferred exception. M4, G93/G95, G96 and override controls remain outside the implemented scope.

Required declared numeric context:

| Field | Check |
| --- | --- |
| `controller.supported_units` | Must explicitly support the job's units. |
| `machine.lifecycle.units.length` | Must match canonical job `mm` or `in`; no conversion or frame transform inferred. |
| `machine.lifecycle.units.spindle_speed` | Must be `rpm`. |
| `machine.limits.x/y/z.min/max` | Both finite JSON numbers, minimum no greater than maximum. Missing bounds are not infinite bounds. |
| `machine.limits.feed_rate.max/units` | Positive finite ceiling and matching `mm/min` or `in/min`. F must be positive and no greater than this declared ceiling. |
| `machine.capabilities.spindle_rpm_min/max` | Finite ordered nonnegative minimum and positive maximum; commanded-on S must also be positive. |

Nulls, booleans, numeric-looking strings, NaN/infinity and malformed numeric containers do not supply valid context and yield `MACHINE_CONTEXT_REQUIRED`. Missing required program values/modes yield `MISSING_CONTEXT`; unsupported semantics retain their existing source-verification blocker. The checks are specific runtime checks over the existing extensible profile objects, not a new universal machine-profile schema or authenticated limit source.

### Fixture identity and migration

The [CNC fixture](../../fixtures/cnc/mill-bracket/fixture.yaml) advances to version 2: NC/job revision B adds explicit G94/G97 and an initial M5. Source CAD remains revision A; this is an NC-fixture revision, not an engineering change to the bracket. Machine/controller lifecycle revisions advance to 2 and remain unverified. The feed ceiling of 1000 mm/min is an arbitrary test datum, not an OEM value or process recommendation. The prior RPM and coordinate bounds remain synthetic too. No actual approval existed to preserve: the fixture job is not requested for approval and profile review identities are null. External records using changed program/profile bytes require fresh review and fingerprint invalidation, not silent re-signing.

### Additional source evidence

Publisher LinuxCNC; all three pages below show **last updated 2026-09-13 12:07:03 UTC**, accessed **2026-09-17**. Scope: reference command semantics only, not machine compatibility, process limits or approval. [G-Codes](https://linuxcnc.org/docs/html/gcode/g-code.html), sections 59–60, distinguishes G94 units-per-minute from other feed modes and G97 RPM from constant-surface-speed mode. [Other Codes](https://linuxcnc.org/docs/html/gcode/other-code.html) describes F and S declarations. [M-Codes](https://linuxcnc.org/docs/html/gcode/m-code.html), sections 5–6, describes M3/M5 and M6 behavior, including interpreter-legal zero-speed starts. Our stricter review policy above is deliberately not attributed to these sources. No interpreter, machine or simulator was run.

Regression evidence is in [test_nc_feed_spindle.py](../../tests/safety/test_nc_feed_spindle.py). Subsequent [artifact binding](nc-artifact-approval-binding.md) and [coordinate review](nc-coordinate-model.md) add composed byte identity and declared translation/starting-position checks. Physical state, swept-volume verification and retained CNC skill outputs remain open Phase 3 work. Numeric completeness and unit agreement cannot establish those missing facts.
