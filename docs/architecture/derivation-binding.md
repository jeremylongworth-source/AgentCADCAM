# Declared CAD derivation binding

## Decision and scope

Accepted for the synthetic CAD fixture's evidence architecture on 2026-09-17. This is not gate 03 acceptance or manufacturing approval. Maintainers need to detect changed source/derivative content even when revision labels and bounding dimensions remain unchanged.

Use a separate [schema-validated binding record](../../contexts/schemas/derivation.schema.json) containing one authoritative source and its declared derivative identities. The checked-in [bracket record](../../fixtures/cad/bracket/metadata/derivation.json) associates the revision-A OpenSCAD file with the STEP/STL reconstructions and SVG reference drawing already present at `050ff24`. No direct OpenSCAD export, new native geometry verification, or authenticated reviewer is asserted.

## Current data flow

1. The schema-instance validator checks binding structure and shared artifact fields through the local schema registry. It does not read artifact bytes.
2. `review_fixture` reads the manifest and revision metadata, then runs the existing declaration/envelope checks and `validate_cad_derivation.validate`.
3. The binding checker requires the fixed bracket inventory, unique artifact identifiers, and agreement on kind, authority, revision, and units. It verifies raw SHA-256 file identities against the stored declaration. File paths come from a fixed allowlist and must resolve inside the supplied bundle.
4. Missing/invalid records, context conflicts, unreadable files, or hash mismatches add `SOURCE_VERIFICATION_REQUIRED`. The CLI returns a blocked report and exit 1. Reports always require review and prohibit execution; matching hashes do not clear other blockers.

`review_bundle` remains metadata-only. Generic job fingerprints and approval records are not automatically updated by this checker. A composed job handoff must carry current artifact identities and re-evaluate its approval separately.

## Alternatives and consequences

- Revision-label-only and envelope-only checks were insufficient: tests changed the source hole diameter with unchanged derivatives, and separately moved one STL vertex without changing its envelope; both previously passed.
- Raw-byte hashes make all content changes visible, including whitespace and line endings. No semantic normalization is performed. Narrow `.gitattributes` rules keep these fixture text files at LF and the STL binary on checkout; manual byte changes still require review.
- A signature or authenticated evidence service is not implemented. Replacing both files and the binding with a self-consistent declaration can pass identity checks. That is not proof of correct derivation or approval. The declared source-to-output relationships, source authority, and geometry still require review.
- This checker reads stable local fixture files; it does not provide an atomic snapshot against concurrent writers. Treat input bundles as immutable during review and invalidate dependent approval after changes.

## Updating the fixture

Preserve the old binding in version history. Resolve why any source or derivative changed; inspect source intent and derivative geometry, regenerate where appropriate, and run the relevant portable/native checks. Only then record the intended new identities and scoped relationship in a reviewed change. The validator never writes or automatically re-signs the record, and the generator does not automatically update it. Do not copy current hashes into an old record merely to clear a blocker.

Bundles copied before this contract lack `metadata/derivation.json` and now block in the file-review CLI. Keep their original data; establish the actual association through review before adding a record. Removing the new checker or downgrading to metadata-only review is not evidence of freshness.

## Evidence and open questions

`tests/interoperability/test_cad_derivation.py` covers required fields, authority/units, record coverage and identity, missing/malformed records, revision/units conflicts, all four hashes, read-only behavior, and raw line-ending changes. `test_cad_fixture_review.py` exercises the two unchanged-envelope file mutations through the composed report. The positive tool report remains under `fixtures/cad/bracket/expected/file-review.json`.

General multi-source dependencies, generator/version provenance, authenticated review, semantic PMI, and byte-bound final job handoffs remain downstream work. Revisit this fixed-inventory checker when adding another fixture family or importing external bundles; do not infer generic file-format support from this implementation.
