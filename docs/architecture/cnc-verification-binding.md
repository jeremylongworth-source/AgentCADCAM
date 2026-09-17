# CNC verification context binding — 2026-09-17

## Decision and scope

Implemented for maintainers and callers of `router.job_router.route_job`.
REVIEW_REQUIRED. This closes a demonstrated record-consistency gap, not CNC
gate 04, physical verification, or practitioner approval.

The gate audit reproduced four false-effective-approval cases: a bare passed
label, a simulation record naming another job/machine, changed NC bytes with
an updated descriptor, and changed machine evidence. A newly matching approval
fingerprint could previously retain these unrelated or stale verification claims.
The first regression run failed four of five tests.

The router now checks structured verification after the independent NC artifact
review. A failed verification record does not suppress an otherwise runnable
static check. Every execution-adjacent or live-execution CNC route must have:

- At least one current passed `kind: simulation` record and one current passed
  `kind: verification` record in `state.verification_results`.
- Each record conforming to `handoff.schema.json#/$defs/cnc_verification_check`,
  with unique `check_id`, nonblank summary, nonempty evidence locators, status,
  and `context_binding: {version: 1, fingerprint: <64 lowercase hex characters>}`.
- Every supplied record valid, passed and bound to the current inputs. Extra
  failed, malformed, duplicate-ID or stale records cannot be ignored by adding
  a passing record. Verification-kind and simulation-kind claims are distinct.
- The existing independent `simulation_status: verified` declaration, profile,
  artifact, static, coordinate, scope and approval checks still satisfied.

Approved execution-adjacent CNC handoffs require both bound record kinds in their
schema. Schema validation checks their representation, not checksum equality or
unique IDs across different record objects; current-state routing checks those.
Live-execution handoffs remain blocked, and routing never authorizes execution.

## Fingerprint basis and approval ordering

`state.state.verification_context_fingerprint` hashes the same finite canonical
JSON inputs as the version-2 approval fingerprint, except `simulation_status` and
`verification_results`. Those outcomes are excluded to avoid circular hashing.
The serialized wrapper is `{verification_context_version: 1, context: ...}`,
distinct from the approval fingerprint domain. Missing fields use null, as in
the existing fingerprint; this does not make missing required inputs acceptable.

All other `INVALIDATING_FIELDS` are included: job/source/revision/units/process,
material, machine/controller, setup/workholding/WCS, tools, CAM/post/version,
generated NC descriptor/hash, jurisdiction and IP/export context. Future changes
to this basis require a version/migration review. Input ordering is canonical;
nonfinite and non-JSON inputs are refused. Approval status itself is not an input.

The verifier declares the input basis alongside the applicable evidence. The
router recomputes that basis without repairing records. Then the full existing
version-2 approval fingerprint still covers *all* evidence records and outcomes.
Changing an evidence locator or outcome therefore invalidates an old approval
even when the verification input basis is unchanged. Updating an approval alone
does not renew verification; renewing verification alone does not renew approval.

`MISSING_CONTEXT` covers malformed, unresolved, failed or incomplete verification.
Stale bindings also produce `SOURCE_VERIFICATION_REQUIRED`. Missing current
simulation, a stale/failed simulation record, or the existing unverified
simulation status produces `SIMULATION_REQUIRED`. Consequential failures
invalidate a matching approved record copy and require human review; the original
record, reviewed fingerprint and caller inputs are preserved. Diagnostics do not
echo private record values.

## Migration and historical evidence

Draft bounded states remain persistable under the existing generic state schema.
Generic non-CNC handoffs need not add CNC-only fields. Lower-consequence CNC
planning without supplied NC/generated output does not require a simulated
program. Supplying an NC artifact still imposes the execution-adjacent floor.

Old passed labels cannot be upgraded by inserting today's hash. Obtain applicable
verification of the current declared inputs, retain the reports and their scope,
record the verification basis, and obtain a new scoped human review. Do not claim
that the hash computation itself performs any of that review. The only automatic
rebinding helper is explicitly test-only in `tests/routing/cnc_fixture.py`.

The nine retained CNC packets and CAMotics native report are unchanged historical
evidence. Their jobs remain blocked, with simulation not run and no approval.
Current replay adds exactly three missing-binding findings to each packet's
routing diagnostics. The replay regression compares everything else exactly,
including original findings/order, blockers, state fingerprints, artifact bytes,
raw and coordinate reports. It does not rewrite historical observations to match
new code or ignore arbitrary diagnostic changes.

## Limits, alternatives and review triggers

Rejected alternatives were accepting passed labels, relying only on the approval
fingerprint, or checking a few optional machine/revision fields. None establishes
that verification claims refer to all consequential inputs. Using the complete
approval fingerprint inside verification would be circular.

This is a **declared-context consistency check**, not authenticated verification.
Evidence locators are not fetched; report contents, reviewer identity, simulation
coverage, collisions, physical state and applicability are not independently
established. A caller can fabricate a checksum and a report claim. Existing human
review remains necessary. The separate CAMotics synthetic-prism experiment is
not verification of the actual bracket job and is not promoted by this change.

Tests cover positive/nonexecuting routing, the four original counterexamples,
every input-basis dependency, outcome/approval separation, malformed/failed/extra
records, duplicate identities, privacy/immutability, planning scope and fresh
static findings despite stale verification. Schema tests cover both required
kinds and preservation of blocked legacy drafts. Reopen for new process scope,
verification methods, basis changes, evidence authentication requirements or any
false-ready counterexample. Full Phase 3 acceptance remains a separate audit.
