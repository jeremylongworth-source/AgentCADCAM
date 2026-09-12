# Bounded Job State

The persistent source of truth for a manufacturing job is the explicit context package, not free-form agent memory. The integrated state schema and deterministic invalidation implementation are in `state/state.schema.json` and `state/state.py`.

Approval dependencies are invalidated when source file or revision, units, process, machine, controller, setup, workholding, tool, postprocessor, material, or generated output changes.
