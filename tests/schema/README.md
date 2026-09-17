# Schema Tests

Run `python scripts/validate_schema_instances.py` after installing `requirements-test.txt`.

The validator checks all eleven context/state definitions against Draft 2020-12, validates context examples and the state example, and validates machine/printer, controller, material, post, setup, and tool fixture profiles plus declared derivation records. References resolve through a local schema registry; unresolved references fail without remote retrieval. Timestamp format checks are enabled. See the [jsonschema validator API](https://python-jsonschema.readthedocs.io/en/latest/api/jsonschema/protocols/) for registry and format-checker behavior.

Regression tests additionally reject malformed hashes, missing source metadata, invalid state fields and timestamps, and verify that runtime invalidation outputs conform to the approval schema.

Source records require publication/revision availability (explicit null is allowed), a valid calendar access date, scope, and nonempty supported claims in addition to title/publisher/locator. `test_source_contract.py` checks the common contract and its five profile consumers. Routing tests reject incomplete source metadata even with a matching approval fingerprint and invalidate changed claims. See the [breaking source-contract migration](../../docs/development/source-contract-migration.md).

Scope limits: workflow-specific `job.json` and laser `process.json` files are harness inputs with separate shapes, not instances of the generic job schema. CAD revision metadata also has a separate shape. This validator does not check those against unrelated schemas or claim that arbitrary nested capability objects satisfy manufacturing requirements.

CAD derivation records use `derivation.schema.json`, which reuses the shared artifact shape and requires source/derivative roles, units, raw-byte hash policy, and permanent review/non-execution flags. Shape validation does not read files. The separate fixture checker compares the record to file bytes and context; see the [binding decision](../../docs/architecture/derivation-binding.md) and `tests/interoperability/test_cad_derivation.py`.

Reusable profiles now require revision, applicability, units, and declared verification under `lifecycle`. Schema tests cover all five profile types, required fields, explicit unknowns, and verified-record prerequisites. Routing tests additionally check reviewed/current revision equality and invalidation after lifecycle changes. Fixture profiles remain unverified; positive tests create synthetic review records only in memory. See the [lifecycle migration](../../docs/development/profile-lifecycle-migration.md).

The handoff schema now requires context identity, assumptions, verification, simulation requirements, and human review action along with permanent review/non-execution flags. Twenty tests in `test_handoff_contract.py` cover required fields, explicit unknowns, status contradictions, nested evidence declarations, four-family representation, and live-action refusal. Schema validity does not resolve evidence references or authenticate the referenced review record. See the [handoff contract and consumer responsibilities](../../docs/architecture/handoff-contract.md).
