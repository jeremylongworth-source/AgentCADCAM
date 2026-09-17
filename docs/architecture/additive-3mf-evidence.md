# Additive 3MF evidence contract

Status: implemented bounded review subset; `REVIEW_REQUIRED`. Phase 4 remains open.
Audience: maintainers and reviewers of additive preflight results.

## Decision and source basis

Inspect package bytes directly rather than treat a 3MF label as proof or convert
the package to STL and discard units, instances and exact coordinates. No new
runtime dependency, extraction, repair, settings import or machine connection is
introduced. `scripts/three_mf_review.py` uses the standard library and the shared
partial-topology kernel in `scripts/stl_mesh_review.py`.

The primary reference is the [3MF Consortium Core specification 1.4.0](https://github.com/3MFConsortium/spec_core/blob/997b385e06f3181cf9aae0c578e0b45ccd48ccb2/3MF%20Core%20Specification.md),
revision `997b385e06f3181cf9aae0c578e0b45ccd48ccb2`, accessed 2026-09-17.
Relevant sections: 1.1 and 2.1 (package/relationships), 2.3 (XML/extensions),
3.1–3.4 (coordinate system, transforms, units, resources/build), 4.1–4.2
(mesh and components), and Appendix C (namespaces/content types).
Core defines a millimeter default, six length units, row-major affine transforms
and references from build items to resources. Unsupported required extensions
cannot be silently ignored. These are format semantics, not printer approval.

This implementation is **not a conformant general 3MF consumer or XSD validator**.
Some valid packages deliberately return `SOURCE_VERIFICATION_REQUIRED` because
their semantics are outside this review subset. Such a result does not claim
the package is corrupt.

## Current implementation

1. Hash the supplied whole package, bounded to 16 MiB. No hash is reported for an
   over-limit input, including a CLI read that may be only a prefix.
2. Inspect the ZIP directory and read bounded members with CRC checks. Only
   stored/deflated parts are inspected. Reject encryption, symlinks, duplicate
   or case-ambiguous names, unsafe paths and excessive expansion. Resolve package
   relationships in memory, never on the filesystem or network.
3. Require content types, root relationships, one selected model part and
   existing internal relationship targets. Additional model parts need review.
4. Decode UTF-8 XML, reject DTD/entity declarations, and bound XML size, nodes
   and nesting. Enforce the supported element/attribute structure and namespaces.
5. Inspect model-type object meshes and earlier-object component references.
   Validate resource IDs, triangle indices and transform values. Mesh checks
   share the existing STL topology kernel without converting coordinates to STL
   floats. Even unused mesh resources are inspected, but only build-referenced
   instances contribute to the reported build envelope.
6. Apply component transforms before parent/build transforms using exact rational
   arithmetic. Report transformed bounds and extents as rational strings in the
   model unit. Track explicit versus Core-default units. Singular transforms
   block; reflections affect bounds without being mistaken for reversed source
   winding. No transformed or repaired mesh is emitted.
7. Compare embedded units against job declarations. Embedded semantics drive
   size/placement checks even when external metadata conflicts. Check extents
   and transformed bounds against a declared zero-origin rectangular envelope
   after explicit unit conversion. Never silently recenter a build.

Input identities remain external: the job must declare `mesh_sha256`, source
revision and units. Adding or changing a settings-only part changes package
identity; the utility never renews the declared hash itself. Existing synthetic
printer/material lifecycle records are not promoted by these checks.

## Supported bounds and limitations

Limits are implementation safeguards, not 3MF or printer constraints: 256 ZIP
members, 32 MiB total declared expansion, 16 MiB per part/XML, compression ratio
at most 1000, 400,000 XML nodes and depth 64; 1,024 objects/build items/expanded
instances, 100,000 source or expanded triangles, component depth 24. Numeric
tokens are at most 64 characters, with decimal exponent/magnitude bounded to
100 and transformed numerator/denominator bit lengths bounded to 4,096.

Names use a restricted unescaped ASCII subset. All nonempty required/recommended
extension declarations, unsupported attributes/children, multiple model parts,
non-model object types, material/property assignments, triangle sets and other
unsupported constructs require further review. Auxiliary parts, including
thumbnails or vendor settings, are inventoried and conservatively block pending
separate review. They are not authenticated, interpreted or executed. Inert
supported model metadata cannot authorize a job.

The geometry checks are partial: no self-intersection, tolerance welding,
positive-fill Boolean union, material suitability, support adequacy, bed-shape,
support/brim clearance or slicer validation. Overlapping instance envelopes
require review; an envelope overlap does not prove a geometric intersection.
Disjoint envelopes do not establish printability. Multiple shells also need
review. The topology kernel groups exactly equal coordinates, which may flag
distinct-index touching geometry; it never merges or rewrites input vertices.

Preflight still checks several context **declarations**, not their authenticity.
It is not the composed approval workflow. Every output remains review-required
and non-executable, including a result with no detected software blockers.

## Acceptance criteria and evidence

All cases below use actual package bytes created by the repository's synthetic
tetrahedron builder in `tests/safety/test_three_mf_review.py`.

| Given / when | Required observation |
| --- | --- |
| Complete minimal package and matching context | Exact identity, 1/1/1 extents, default-unit provenance; preflight still requires human approval |
| Model located through a non-default relationship target | Inspect that model, not a guessed filename |
| Explicit Core unit or omitted unit | Preserve explicit/default origin and exact physical scale |
| Nested component, rotated/scaled/translated build, or repeated item | Measure the referenced transformed instances in correct order |
| Tiny decimal change or just-outside translated item | No float rounding or extent-only comparison hides the difference |
| Missing facet with a fresh test hash and valid metadata label | Geometry-derived `MISSING_CONTEXT` |
| Invalid/duplicate IDs, indices, references or numbers | Block, with JSON-safe diagnostics |
| DTD, malformed ZIP/XML, CRC failure, external target or expansion abuse | Block without extraction, repair, external access or execution |
| Unknown extensions, materials, support types or auxiliary settings | Explicit further-review blocker, never silent acceptance |
| Settings-only change with an old job hash | Whole-package identity mismatch remains blocking |

The [retained observations](../../fixtures/additive/fdm-bracket/expected/3mf-observations.json)
record a positive package, removed facet, out-of-envelope translation and
conflicting inch unit. A fixed stored-ZIP envelope makes hashes replayable without
depending on a compressor version. The test reconstructs and compares the actual
reports; it does not derive expected outcomes dynamically. No third-party model
is redistributed. CLI tests use temporary files and both script/module forms.

## Remaining work and review triggers

The [evaluation record](../evaluation/additive-fdm-evaluation.md) tracks executed
validation. This change does not close gate 05. The specified PrusaSlicer/open-model
experiment, retained skill-assisted additive handoffs, unresolved geometry and
usable-bed boundaries, and the complete gate audit remain required. General
material/extension/vendor-project support is unproven. Revisit the supported
subset using independent reference evidence, not by weakening blockers to accept
a fixture. Any new extension, tolerance rule, approval integration or false-ready
case requires renewed negative tests and architectural review.
