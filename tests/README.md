# Tests

Foundation tests validate repository contracts, JSON schema syntax, YAML manifests, source metadata requirements, broken references, and hard safety invariants. Schema tests add Draft 2020-12 definition and instance validation, local reference resolution, timestamp checks, and runtime approval conformance. Workflow tests cover curated fixtures; pilot tests exercise the evaluation tooling.

Create and activate a local virtual environment, then run:

```text
python -m pip install -r requirements-test.txt
python scripts/validate_foundation.py
python scripts/validate_schema_instances.py
python -m unittest discover -s tests -p "test_*.py"
```

The portable suite includes ezdxf for its existing laser geometry checks but does not require CadQuery. Install `requirements-dev.txt` when regenerating STEP/STL geometry with CadQuery. The generator CLI tests use an export double to catch orchestration errors; they do not validate CAD-kernel geometry.

Foundation documentation checks use markdown-it-py and mdurl to parse links and decode local destinations without fetching URLs. See [reference coverage and limits](../docs/development/foundation-validation.md#markdown-reference-scope), including Markdown heading anchors, reference definitions, and code-example exclusions.

For actual native generation and process-exit verification, run `python -m tests.native.check_cadquery_runtime` using a CadQuery environment. Windows users should follow the [tested Python 3.12 setup](../docs/development/cadquery-windows.md), which records the solver dependency constraint and regression findings.
