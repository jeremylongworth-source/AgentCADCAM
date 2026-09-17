# Evaluation

Evaluation plans and packets measure routing, completeness, provenance, safety recall, false-ready decisions, factual support, and reviewer burden. Synthetic fixtures do not satisfy the real-input pilot gate.

Retained development reviews are separate from practitioner pilot packets: [CAD reviews](cad-runs/README.md) and [seven-skill CNC reviews](cnc-runs/README.md). Their replay/identity tests check evidence integrity, not independent reasoning quality or manufacturing readiness.

[Integrated four-family reviews](integration-runs/README.md) retain current router/consumer outcomes alongside authored reviews and separate test-only approval-lifecycle controls. They preserve missing context and blocked handoffs. The subsequent [full integration gate audit](../development/integration-gate-review.md) accepts Phase 6 for repository development, not public-alpha or practitioner validation.

Copy `pilot-packet-template/` into `pilot-packets/<packet-id>/` for each consented, sanitized evaluation. Run `python scripts/validate_pilot_packet.py <packet-path>` for one packet or `python scripts/evaluate_pilot_gate.py [packet-root]` to produce the aggregate readiness report. Completed packets must preserve evidence and cover all four initial workflow families. `thresholds_met` means submitted measurements meet the roadmap thresholds; it does not award the pilot gate. Follow the measurement definitions and reviewer decision process in [the pilot protocol](pilot-protocol.md).
