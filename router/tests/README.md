# Router verification entry point

The Phase 6 roadmap names `router/tests/`. Executable router tests live in the
canonical repository-wide [tests/routing](../../tests/routing/README.md) package,
as specified by the roadmap's target repository structure. This entry point maps
the router deliverable to that suite; it does not create a second test collector
or exclude routing tests from the normal full-suite command.

Run from the repository root:

```text
python -m unittest tests.routing.test_integration_gate -v
python -m unittest discover -s tests/routing -v
python -m unittest discover -s tests -v
```

The [integration gate matrix](../../tests/routing/test_integration_gate.py) checks
all declared consequence levels, live actions, four workflow selections, bounded
state fields, key-order determinism, artifact consequence floors, and every
Phase 6 invalidating input across all four workflows. Lower-level routing,
file/context/evidence and serialized-handoff tests remain in the same package.

Current record recognition in these tests uses explicitly synthetic declarations,
not qualified human approval. All outcomes require review and forbid execution.
Retained actual skill-assisted development reviews and their limitations are
documented [separately](../../docs/evaluation/integration-runs/README.md).
