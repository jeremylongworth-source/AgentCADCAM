# Bounded Job State

The persistent source of truth for a manufacturing job is the explicit context package, not free-form agent memory. The Phase 1 schemas define the reusable records. Phase 6 will add the integrated state schema and deterministic invalidation implementation.

Approval dependencies are invalidated when source file or revision, units, process, machine, controller, setup, workholding, tool, postprocessor, material, or generated output changes.
