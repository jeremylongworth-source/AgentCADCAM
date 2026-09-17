# Pilot evaluation

The real-input pilot measures whether skills help qualified reviewers outside synthetic fixtures. It is the final initial-roadmap gate, not a machine trial or waiver of public-alpha requirements.

## What is needed

- Real or appropriately sanitized inputs, with consent and documented provenance.
- Comparable baseline and skill-assisted outputs for the same bounded task.
- A practitioner or suitably qualified reviewer with recorded relevant experience.
- Findings, required edits, safety observations, measurements and a final verdict.

Do not publish client files or controlled technical data to obtain an evaluation. Agree on the minimum safe packet and disclosure rights first. Synthetic inputs test the tooling but cannot satisfy this gate.

## Packet structure

Start from the [packet template](../evaluation/pilot-packet-template/README.md) and follow the [pilot protocol](../evaluation/pilot-protocol.md):

```text
<packet-id>/
  input/
  baseline-output/
  skill-output/
  reviewer-findings/
  required-edits/
  safety-findings/
  final-verdict/
```

Each evidence directory needs substantive records. Explicitly recording no edits or no safety defects is acceptable; an empty directory is not. Leave unmeasured verdict fields unset and the packet in draft rather than inventing passing values.

## Validation and interpretation

```sh
python scripts/validate_pilot_packet.py docs/evaluation/pilot-packets/<packet-id>
python scripts/evaluate_pilot_gate.py docs/evaluation/pilot-packets
```

Replace `<packet-id>` with the actual submitted directory. The aggregate must cover all four initial families. With no completed submissions, `not_ready` and exit 1 are expected.

The protocol defines measurements for schema validity, routing, provenance/revision defects, interoperability, handoff completeness, unsupported assumptions, critical safety detection, false-ready decisions, authoritative sourcing, usefulness and reviewer edit burden. Use its exact definitions and roadmap thresholds; report sample size and sampling limitations.

`thresholds_met` describes submitted measurements only. The evaluator always returns `gate_awarded: false`; it cannot authenticate reviewers or judge whether cited evidence supports a claim. Qualified reviewers must inspect evidence and record acceptance separately.

No completed practitioner pilot was established by the current development review. Check [roadmap status](../development/roadmap-reconciliation.md) before describing the project as pilot-validated.
