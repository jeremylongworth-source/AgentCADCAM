# Pilot packets

Place one copied and sanitized `pilot-packet-template/` directory here for each real-input evaluation, using a non-identifying packet directory name. Do not commit confidential CAD, proprietary NC/G-code, credentials, private machine endpoints, or export-sensitive data.

Run from the repository root:

```text
python scripts/evaluate_pilot_gate.py docs/evaluation/pilot-packets
```

The evaluator reports `not_ready` or `thresholds_met` and always leaves `gate_awarded: false`. Qualified practitioners must verify the evidence before the pilot gate can be awarded. An empty directory is expected until practitioners contribute evidence. All immediate subdirectories are treated as submissions, so keep supplemental tests and unrelated directories outside this root.
