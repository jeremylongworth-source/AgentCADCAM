# Schema Tests

Run `python scripts/validate_schema_instances.py` after installing `requirements-test.txt`.

The validator checks all ten context/state definitions against Draft 2020-12, validates context examples and the state example, and validates machine/printer, controller, material, post, setup, and tool fixture profiles. References resolve through a local schema registry; unresolved references fail without remote retrieval. Timestamp format checks are enabled. See the [jsonschema validator API](https://python-jsonschema.readthedocs.io/en/latest/api/jsonschema/protocols/) for registry and format-checker behavior.

Regression tests additionally reject malformed hashes, missing source metadata, invalid state fields and timestamps, and verify that runtime invalidation outputs conform to the approval schema.

Source records require publication/revision availability (explicit null is allowed), a valid calendar access date, scope, and nonempty supported claims in addition to title/publisher/locator. `test_source_contract.py` checks the common contract and its five profile consumers. Routing tests reject incomplete source metadata even with a matching approval fingerprint and invalidate changed claims. See the [breaking source-contract migration](../../docs/development/source-contract-migration.md).

Scope limits: workflow-specific `job.json` and laser `process.json` files are harness inputs with separate shapes, not instances of the generic job schema. CAD revision metadata also has a separate shape. This validator does not check those against unrelated schemas or claim that arbitrary nested capability objects satisfy manufacturing requirements.
