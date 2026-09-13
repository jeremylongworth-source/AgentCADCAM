# Foundation conformance follow-up

The review after `8011a4b` found two concrete regressions beneath the recorded synthetic gates:

- `invalidate_approval()` added `invalidation_reason` and `changed_fields`, but `approval.schema.json` rejected those properties. A valid approved record therefore became schema-invalid after a revision change.
- The CadQuery import was moved into `build_bracket()`, while `main()` still referenced the former global `cq`. Export orchestration raised `NameError`.

Both failures were reproduced with regression tests before applying fixes. The approval schema now declares the existing audit fields without removing its unknown-property guard. The export command imports exporters only after validating output paths; importing the path helper remains independent of CadQuery.

Validation in a local virtual environment:

- 73 tests passed with exit code 0.
- Draft 2020-12 validation passed for ten schemas and thirteen example/profile instances.
- The foundation validator passed.
- Cross-schema references, timestamp format enforcement, malformed hashes, missing provenance, and runtime approval output conformance are tested.

See [schema coverage and exclusions](../../../tests/schema/README.md) and [test setup](../../../tests/README.md). Shape validation does not establish the accuracy of manufacturing data, reviewer decisions, or arbitrary nested capability objects.

## Native runtime issue still open

The installed system Python 3.14 / CadQuery 2.8.0 runtime generated temporary STEP/STL files after the import fix, but its process terminated unsuccessfully afterward. A standalone `python -c "import cadquery"` also exited with `-1073741819` (`0xC0000005`, Windows access violation). This reproduces independently of repository geometry/export code. The temporary smoke-test artifacts were removed by their temporary-directory context; tracked geometry was unchanged.

The successful portable suite uses an export double for CLI orchestration. A clean native geometry-generation run remains unverified on this system. Do not treat printed export success as proof of a successful process exit.

This follow-up strengthens earlier gate evidence and awards no new gate. The real-input practitioner pilot remains outstanding.
