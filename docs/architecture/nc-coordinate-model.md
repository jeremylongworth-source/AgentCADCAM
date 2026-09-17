# Declared NC coordinate model — 2026-09-17

## Decision and scope

For maintainers and callers of the execution-adjacent CNC router: require a reviewed coordinate model before comparing programmed positions with machine-axis bounds. Raw X/Y/Z values alone do not identify machine positions. Regression cases demonstrate both a hidden limit conflict after translation and a false rejection when translated targets actually fit the declared bounds.

The implemented `cartesian_translation_v1` contract covers one tool, three Cartesian axes, absolute G90/G54 coordinates and the existing literal G0/G1 subset. It is a declared arithmetic model, not a controller interpreter or physical verification. REVIEW_REQUIRED; gate 04 remains open.

Keeping raw comparisons or assuming zero offsets would preserve the ambiguity. A general transform/interpreter is deferred until its semantics and independent evidence are available. The chosen model makes a fixed mapping explicit and blocks missing or unsupported context without introducing a vendor runtime dependency.

## Contract and responsibilities

`setup.coordinate_model` uses the existing setup schema and shared source/profile-lifecycle definitions. It records model identity, units, machine/controller/setup/tool/WCS identities, three-component translation, initial machine position, initial-position stage, source and revision-scoped review. Draft setup records may omit it; execution-adjacent CNC review may not.

For each explicitly programmed axis:

```text
machine_target = programmed_absolute_target + translation
```

The reviewer must establish the aggregate mapping, including applicable work, tool and local/global offset effects. The model does not discover offsets, read a controller, assume cancellations, or establish the absence of rotation/scaling. If a constant Cartesian translation cannot be supported by the supplied evidence, leave the model unresolved; do not fit an invented translation or mark it verified. `kind` asserts this bounded model, not just an axis count.

The initial position is explicitly **after the first tool change and before the first explicit axis move**. It is not inferred from the first target or assumed to be home. Unmentioned axes retain the prior machine-axis position. Another M6 blocks because it requires new position/transform evidence; implicit motion associated with the first M6 is outside this check.

Required context includes matching canonical `mm`/`in` units (no conversion), three axes, and `machine.limits.coordinate_frame: machine_axes` with finite ordered X/Y/Z limits. Both coordinate vectors require all three finite JSON numbers; booleans and numeric-looking strings are not values. The model review must be verified against its current revision with the shared required reviewer/time/evidence fields. These are checked declarations, not authenticated review or source truth.

## Components and returned evidence

1. [NC artifact binding](nc-artifact-approval-binding.md) checks actual bytes and required state context, then requires the model. Missing models cannot fall back to raw-coordinate comparisons.
2. [The static reviewer](../../scripts/nc_static_checks.py) retains its lexical, modal, feed/RPM, post and approval checks. It passes parsed inert words and numeric bounds to [the coordinate helper](../../scripts/nc_coordinate_checks.py), which validates the model using the existing local schema registry. No remote schema resolution is introduced.
3. The helper checks identity, units, review currency, initial position and translated targets. Decimal addition preserves literal precision, including tiny exceedances. Offset-changing or other unimplemented commands retain blocking findings; additional tool changes and missing coordinate prerequisites block.
4. `report.coordinate_review` returns status, scope, blockers, findings and line-numbered `machine_target` vectors as decimal strings. `checked_declared_bounds` concerns only that arithmetic; other report/router blockers remain authoritative. A `not_run` result with blockers is not a successful check.

The existing state fingerprint includes the entire setup and machine profile, so model/source/review or limit changes invalidate dependent approval records. No report mutates supplied inputs, repairs a fingerprint, persists an approval or enables execution.

## Migration and standalone boundary

Existing execution-adjacent CNC states need the complete model and explicitly framed bounds, followed by renewed scoped review where state changes. Do not copy the synthetic fixture's zero translation or initial position into a physical job, or re-sign an old record to hide missing evidence.

The standalone `review_program` utility accepts an optional `coordinate_model` argument. Without it, the historical raw fixture-bound check remains available with `coordinate_review: null`; the current CLI uses this path. That partial utility is not an approval evaluator. The composed router always supplies a model or blocks, so it cannot use the legacy path to recognize an approval.

Fixture version 3 adds an unverified model at revision 1 and advances the machine profile to revision 3 for explicit frame identity. Controller revision 2, NC/job revision B and CAD revision A are unchanged. These are synthetic test declarations, not OEM parameters or observed setup data.

## Validation and unresolved work

[Routing tests](../../tests/routing/test_nc_coordinate_gate.py) cover translated positive/negative boundaries, initial position, identity/unit/frame conflicts, missing/stale reviews, malformed models, unsupported offset commands, extra tool changes and old approval invalidation. [Direct utility tests](../../tests/safety/test_nc_coordinate_checks.py) cover nonfinite values, missing context, immutability and the legacy boundary. Test-only verified declarations stay in memory; checked-in profiles remain unverified. Run results are recorded in the [CNC evaluation](../evaluation/cnc-milling-evaluation.md).

This does not check swept volumes, tool/holder/fixture collisions, controller interpolation or overshoot, homing, actual axis positions, tool-change motion, cutting feasibility, actual feed/spindle behavior or simulation truth. Initial position and endpoint bounds cannot establish those facts. Retained seven-skill reviews, independent-tool evidence where practical and the full gate audit remain required. Revisit the model before supporting more tools, coordinate systems, rotation/scaling, arcs, incremental coordinates or dynamic compensation.

## Reference evidence

[Coordinate Systems](https://linuxcnc.org/docs/html/gcode/coordinates.html), publisher LinuxCNC; last updated **2026-09-13 12:07:03 UTC**, accessed **2026-09-17**. Scope: distinction between machine/work coordinates and offset interactions, not this synthetic controller's compatibility. The documentation distinguishes work offsets from machine coordinates and describes additional local/global offsets and rotation interactions. This informs the decision to require explicit mapping evidence; it does not validate our implementation or any physical setup. LinuxCNC was not executed.
