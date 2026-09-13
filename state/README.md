# Bounded Job State

The persistent source of truth for a manufacturing job is the explicit context package, not free-form agent memory. The integrated state schema and deterministic invalidation implementation are in `state/state.schema.json` and `state/state.py`.

Approval dependencies include job identity, source/revision, units, process, machine, controller, setup, workholding, WCS, tools, CAM system, post/version, material, generated output, simulation, verification, jurisdiction, IP status, and export-review status. The rule register and runtime field set are tested for exact agreement. Workholding can be part of `setup` or the explicit `workholding` state field; both are fingerprinted.

Fingerprints use canonical finite JSON with an explicit version-2 domain. Unsupported values and non-string object keys raise errors; they are never silently stringified. Object key order does not change the fingerprint. Approval lifecycle status is excluded so recording approval does not itself alter the reviewed context. Missing and null optional fields both represent unspecified context.

The low-level `invalidate_approval(previous, current, approval)` detects a context transition; callers must supply the approval of the previous snapshot. For persisted records, use the [integrated router](../router/router-contract.md), which checks the actual reviewed fingerprint and scope, including when no prior snapshot is available. Read the [version-2 migration note](../docs/development/fingerprint-v2-migration.md) before using existing approval records.
