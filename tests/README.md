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
