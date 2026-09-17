# NC artifact and approval binding — 2026-09-17

## Decision and scope

For maintainers and callers of `router.job_router.route_job`: execution-adjacent CNC review must inspect supplied NC bytes, not accept passing declarations alone. Before this change, a regression demonstrated a matching approval retaining effective `approved` status without any actual NC input. This document records the new software boundary; it does not accept CNC gate 04 or approve manufacturing.

Keeping artifact review as an optional wrapper would leave the original context-only approval path available. Instead, the existing router now calls [nc_evidence.py](../../router/nc_evidence.py) for every execution-adjacent or live-execution CNC route. Lower-consequence context-only planning without a manufacturing artifact remains available. Live execution is always prohibited.

## Inputs and data flow

1. The caller supplies `nc_program` as nonempty `bytes`. The router opens no artifact path, follows no URL and evaluates no NC instructions. Supplied bytes or a declared generated output impose the existing execution-adjacent consequence floor, even if the state is malformed or the request uses an informational label. NC bytes or an explicitly NC-kind descriptor conflict with a non-CNC bounded state; changing the family label cannot skip review.
2. `state.generated_manufacturing_output` must validate against `handoff.schema.json#/$defs/artifact`, with `kind: nc_program`, `authority: derived`, and revision/explicit units equal to the bounded job. The state's generic output object still permits storing drafts; the stricter runtime gate validates the artifact contract before recognizing approval.
3. Compute SHA-256 over exactly the supplied bytes. Compare with the declared hash without newline normalization, text re-encoding or automatic hash repair. The artifact locator is retained as metadata, not treated as authority to read a file. Byte identity does not authenticate provenance or applicability.
4. If artifact identity and required context are usable, require the [coordinate model](nc-coordinate-model.md), decode strict UTF-8 and run the [static reviewer](nc-static-review-scope.md) against the same state machine, controller, setup, post and tool profile. Pass the selected job WCS and coordinate model explicitly; neither the controller's first WCS nor zero offsets are inferred. The current one-tool reviewer rejects a library with multiple tools; it does not quietly select one.
5. Merge the fresh blockers into routing before final approval disposition. A previously recognized matching approval becomes an invalidated copy when required NC checks fail. Keep its old reviewed fingerprint and the supplied state/descriptor unchanged. Existing profile, simulation, verification, scope and human-review gates remain independent.

The static reviewer receives the router's effective scoped approval status, not the raw `state.approval_status`. This does not create an approval. It avoids allowing a stored flag to substitute for the actual record, timestamp, scope and context checks.

## Returned evidence

`nc_review` is null where the NC stage does not apply or state validation prevents it. Otherwise it includes `status`, computed `sha256` when bytes were supplied, the examined `context_fingerprint`, blockers/findings and `report` from the fresh static run. `report` is null if a prerequisite prevents the run. A `not_run` result with blockers must never be counted as a successful check.

The returned report is not inserted into `verification_results`, nor does the router manufacture a new review record or fingerprint. The existing version-2 fingerprint already includes the complete `generated_manufacturing_output` and all required context fields. Changing the declared hash invalidates an older record; retaining the old hash while changing bytes now fails independently. Re-signing a bad program in a synthetic test does not silence actual static findings.

Callers must retain the returned diagnostics, reviewed input identities and applicable software revision with their review package. The utility persists nothing. Reports and schema validation establish record consistency, not reviewer authentication or the truth of source, machine or simulation declarations.

## Breaking migration

For execution-adjacent CNC calls:

```python
result = route_job(request, state, approval, nc_program=nc_bytes)
```

Populate `generated_manufacturing_output` using the existing artifact schema: artifact ID, locator/path, kind, SHA-256, revision, authority and explicit units. Compute the hash from the exact bytes that will be reviewed; do not pass an encoded path or silently normalize text. The API deliberately does not fetch the locator for the caller.

Old context-only calls at this consequence level now return blockers and cannot retain effective approval. Resolve missing artifact/context evidence and obtain renewed scoped review where the fingerprint changes. Do not rewrite an old fingerprint or promote a failed static result to preserve approval. Unsupported representations, encodings and multi-tool workflows need additional review support, not a bypass switch.

The standalone `review_program` function remains an evidence utility, not an approval evaluator. Its optional `selected_wcs` and `coordinate_model` parameters let callers supply selected coordinate context; the original fixture-only fallback remains for standalone use. The composed router always supplies both or blocks. Existing execution-adjacent states without a reviewed model must follow the [coordinate migration](nc-coordinate-model.md#migration-and-standalone-boundary).

## Validation and remaining work

[Artifact-gate tests](../../tests/routing/test_nc_artifact_gate.py) exercise matching/missing/changed bytes, false passed declarations, updated bad-program hashes, malformed descriptors/encoding, line-ending identity, consequence floors, selected WCS, multi-tool refusal and live-action prohibition. [Existing context tests](../../tests/routing/test_job_router.py) now explicitly supply NC bytes through a shared synthetic test fixture, retaining profile and approval invalidation assertions. All test review declarations stay in memory; checked-in profiles remain unverified.

The program mutations cover all eight roadmap CNC negatives, plus overspeed. This is composed software regression evidence, not the retained seven-skill CNC evaluation or a practitioner verdict. The declared coordinate model adds initial-position and translated-target arithmetic, not observed physical coordinate state. Tool/fixture collision, actual simulation evidence, independent tools where practical and the complete gate audit remain open. No machine execution capability was added. REVIEW_REQUIRED.
