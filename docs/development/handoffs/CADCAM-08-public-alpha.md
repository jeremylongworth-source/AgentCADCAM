# CADCAM-08 Public Alpha Handoff

## Status

Historical synthetic-corpus decision only. The [2026-09-13 roadmap reconciliation](../roadmap-reconciliation.md) supersedes the claim of full public-alpha readiness. Foundation evidence and process-specific validation gaps remain, in addition to the practitioner pilot.

## Evidence

- 14 atomic skill contracts pass the bundled skill validator.
- Foundation, interoperability, safety, routing, state, and adversarial tests cover the synthetic scope. Pilot tooling checks extend this coverage; they do not prove real-input pilot completion.
- Critical curated negative cases block for missing/conflicting context, unsafe material, machine/controller/post mismatch, live execution, and stale approval.
- Every router and preflight result keeps `execution_allowed: false`.
- Context profiles require source metadata.
- `SECURITY.md`, `CONTRIBUTING.md`, public limitations, fixture licensing, and source freshness process are present.
- No repository script imports network/process-control modules or implements machine connectors.

## Gate decision

Previously recorded: `CADCAM_08_PUBLIC_ALPHA_READY`. Full roadmap-level acceptance is now unproven pending the reconciliation work.

This gate applies to the portable review/planning layer and curated synthetic fixtures only. It is not engineering signoff, regulatory approval, machine authorization, or proof that any real job is safe to manufacture.

## Required next phase

Phase 8 must collect real-input evaluation packets from CAD, CAM, machining, additive, laser, DFM, and manufacturing practitioners. Scenario tests alone cannot satisfy `CADCAM_09_PILOT_VALIDATED`.

The protocol and packet template are in `docs/evaluation/pilot-protocol.md` and `docs/evaluation/pilot-packet-template/`.
