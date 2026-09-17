# Laser SVG file-derived contour evidence — 2026-09-17

Status: implemented bounded SVG inspection; `REVIEW_REQUIRED`. Phase 5 remains
open. Audience: maintainers implementing laser file review and auditing fixture
evidence. This is neither a renderer nor manufacturing approval.

## Decision and components

`scripts/laser_svg_review.py` consumes actual nonempty bytes and reports SHA-256,
physical viewport mapping, measured contours, bounds/dimensions in millimetres,
geometry defects and explicit blockers. It uses only the Python standard library.
It never opens embedded paths, fetches resources, renders CSS, repairs geometry,
chooses settings or activates equipment.

`scripts/validate_laser_fixture_geometry.py` now calls this inspector for its SVG
half. It requires the measured contours to match the existing synthetic fixture's
rectangle and two hole positions/radii. Changing a hole without changing outer
bounds therefore fails. This fixture assertion is deliberately exact and ordered;
it is not a general source-equivalence algorithm. The subsequent
[DXF/file-preflight implementation](laser-file-evidence.md) now also measures the
DXF contours and applies the same fixed-fixture assertion.

The standalone `scripts/laser_preflight.py` now consumes actual SVG/DXF bytes and
explicit identity/revision/dimension context as documented in that follow-up.
It still does not authenticate profile/environment evidence or approvals.
Historical evaluation records and fixture drawing bytes have not been rewritten.

## Supported interpretation and source basis

The W3C SVG 2 [coordinate-system chapter](https://www.w3.org/TR/SVG2/coords.html)
defines viewBox-to-viewport mapping, including aspect-ratio alignment. The reader
requires physical `mm`, `cm` or `in` width/height plus a viewBox; it does not infer
manufacturing dimensions from browser pixels, percentages or host layout. The
default meet alignment, explicit meet alignments and `none` mapping are measured.
Slice/clipping and outer-root transforms require further review.

The [basic-shapes chapter](https://www.w3.org/TR/SVG2/shapes.html) and
[path chapter](https://www.w3.org/TR/SVG2/paths.html) supply the rectangle, circle,
polyline/polygon and linear path semantics. Supported paths use M/L/H/V/Z,
absolute or relative, including repeated arguments and multiple subpaths. Curved
commands, rounded rectangles, ellipses and other elements are not approximated.
Sources accessed 2026-09-17; no W3C implementation code was imported.

Nested groups and geometry support affine matrix, translate, scale and quarter-
turn rotate transforms, including rotation centers. Exact decimal rationals
preserve transform order and tiny physical differences without tolerance rounding.
Circle transforms must preserve a circle with an exactly rational radius;
elliptical or irrational-scale cases require further review. General rotations
and skew syntax are outside this reader's current subset.

Supported geometry must resolve to no fill and an explicit supported opaque
stroke. A small named/hex color subset is accepted, not interpreted as cut/score
intent. Stylesheets, style attributes, clipping, masking, visibility controls,
event handlers, references, nested SVG viewports and unsupported attributes block.
Title/description text is inert, not authority for scale, revision or approval.
No stroke-to-outline or kerf compensation is computed.

## Measured findings

After transforms and physical scaling, the inspector records exact rational
coordinates for each contour. An explicit repeated start/end coordinate records
geometric closure without a duplicated closing vertex; input bytes remain
unchanged. This does not imply identical stroke-join rendering.

The bounded contour checks identify:

- Open contours, zero-area closed polygons and zero-length edges.
- Duplicate undirected segments regardless of path direction/start, and duplicate
  circles after transforms. Equivalent collinear subdivisions are surfaced as
  overlaps rather than assumed distinct paths.
- Straight-segment crossings, nonadjacent touches and collinear overlaps;
  line/circle and circle/circle intersections or tangencies. Ordinary adjacent
  polygon joins are allowed; backtracking overlaps are not.
- Geometry outside the physical SVG viewport, which requires clipping/placement
  review rather than silently dropping the out-of-bounds portion.

Nested nonintersecting contours are allowed geometrically, but no hole/part,
cut-order or material intent is inferred. Path intent, source consistency, units
declared by a job, machine working area, kerf, material, ventilation and process
evidence require separate review. A large but consistent SVG can be measured
successfully; comparing it to the intended physical design remains necessary.

Detected geometry defects return `MISSING_CONTEXT`; unsupported semantics or
review limits return `SOURCE_VERIFICATION_REQUIRED`. A successful result is
`checked_partial_geometry`, always review-required and non-executable, never
ready, approved, safe or permission to cut. Whole-file identity is an observation,
not authenticated source truth or authorization.

## Input and resource boundaries

Inputs must be UTF-8 XML with the SVG namespace. DTD/entities and non-XML
processing instructions are rejected before parsing; XML encoding declarations
must agree with UTF-8. The parser does not resolve external content. Error reports
do not echo arbitrary parser exceptions or input text.

Implementation limits, not format/machine constraints: 2 MiB of input, 4,096 XML
nodes, depth 32, 1,024 combined polygon vertices/circles and at most 1,024 measured
segments/circles. Numeric tokens are at most 64 characters with decimal exponent
and magnitude bounded to 40; numeric lists and path tokens are bounded before
conversion, transform lists to 64 entries, and composed matrix rationals to
1,024 numerator/denominator bits. Pairwise contour comparisons are bounded by
the segment limit. An oversized input returns no digest, avoiding prefix identity.

Rejecting unsupported inputs is intentional, not a declaration that all such
SVG files are invalid. This is not a full SVG conformance/security guarantee.
The checker does not use the old CAD drawing text grammar as a contour validator,
and does not depend on a native renderer to decide manufacturing semantics.

## Validation and remaining work

`tests/safety/test_laser_svg_review.py` exercises actual fixture bytes and altered
geometry: holes/radii, duplicate and open contours, unsupported commands,
viewBox/unit scale, transforms, exact tiny differences, intersections, malformed
numbers/syntax, inert content and resource limits. Paired-validator regressions
modify temporary copies, not source fixtures or metadata labels.

```text
python -m unittest tests.safety.test_laser_svg_review tests.safety.test_laser_preflight -v
python scripts/validate_laser_fixture_geometry.py
```

Executed results are retained in the [laser evaluation follow-up](../evaluation/laser-cut-evaluation.md).
The subsequent file-preflight implementation supplies DXF geometry/unit evidence
and byte/context checks. Retained complete skill reviews and the Phase 5 gate
audit remain. Phase 6 integration and real-input practitioner acceptance
remain separate. No material-safety, machine-power or legal claim is introduced.

Revisit for new supported elements, transforms, styles or units, source-
equivalence requirements, tolerance changes, larger inputs or a false-ready
counterexample. Preserve old evidence; do not relax a blocker to make a file pass.
