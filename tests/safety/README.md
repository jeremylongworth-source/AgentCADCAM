# Safety Tests

Validate hard blocks for missing context, unsafe requests, unresolved verification, and unauthorized execution.

`test_governance.py` covers declared source authorization and export-review
refusal, including matching-record controls across all four workflow families.
See the [acceptance map and limitations](../../docs/evaluation/governance-runs/README.md).

`test_source_evidence.py` covers all nine structured source roles, primary
authority declarations, review chronology/expiry, metadata binding and scoped
approval refusal. See its [acceptance map](../../docs/evaluation/source-evidence-runs/README.md).
