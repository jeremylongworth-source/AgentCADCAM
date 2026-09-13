# Context fingerprint version 2

The Phase 6 conformance audit found that the runtime omitted the declared root workholding field, while the YAML rule register omitted WCS and post version. Job identity, verification/simulation evidence, CAM system, and authorization context were also absent from the fingerprint despite their effect on the review's applicability.

Version 2 synchronizes the rule register and runtime dependencies and hashes a canonical JSON envelope containing `version: 2` and the relevant context. Strict JSON serialization rejects unsupported Python objects, non-string object keys, and non-finite numbers. Boolean/number changes are distinct even though Python considers `True == 1`. All SHA-256 strings remain 64 hexadecimal characters; the hash content changes for existing records.

## Existing approval records

Treat all version-1 fingerprints as stale. Preserve the old approval, reviewed fingerprint, reviewer, timestamp, and evidence. Do not overwrite an old fingerprint with a version-2 value while leaving the record approved: that would imply a review that did not happen.

Revalidate the job context, carry out the required review, and create a new approval scoped to the appropriate review token and new fingerprint. The integrated router defaults to the scope token `manufacturing_handoff`; narrower callers can set `required_scope` explicitly. A record for another scope remains retained but does not satisfy the current request.

The router computes effective approval from the supplied record, not from the request's `approval_state` or the job's `approval_status`. Stale records yield an invalidated copy and require human review. Malformed records yield explicit validation blockers. No repository files are rewritten by routing; the caller owns audit persistence and record identity/authentication.

## Verification

Regression tests cover the original field omissions, type-sensitive changes, source-of-truth conflicts, missing profiles, stale records without a previous snapshot, correctly renewed records, wrong scope, absent timestamps, and independent simulation/verification blocks. `route(request)` remains available for triage compatibility; use `route_job` for bounded state and approval consistency checks.
