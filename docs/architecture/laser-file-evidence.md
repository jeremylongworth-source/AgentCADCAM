# Laser DXF/SVG byte-aware preflight — 2026-09-17

Status: implemented partial file/context review; `REVIEW_REQUIRED`. The subsequent
[Phase 5 audit](../development/laser-gate-review.md) records development acceptance
without expanding this reader's scope. Audience: maintainers and reviewers.

## Decision and boundary

`laser_preflight.preflight` now requires actual drawing bytes, an explicit
source revision and matching `job.drawing_sha256`. It calls the bounded DXF or
[SVG reader](laser-svg-evidence.md), checks measured physical dimensions against
the declared design dimensions, compares the working-area envelope and preserves
geometry/context blockers. Labels such as valid, closed and verified no longer
replace actual file inspection. Neither reader repairs or renders geometry.

The DXF reader is a standard-library tag consumer, not an ezdxf recovery wrapper
or a conformant general DXF implementation. This preserves numeric literals as
exact decimal rationals without a float conversion or automatic recovery step.
It reuses the SVG module's bounded numeric and planar contour kernel; it does
not convert a DXF drawing into SVG. The existing optional ezdxf fixture generator
is unchanged and is not required by either reader or preflight.

Rejected alternatives: continue checking entity counts only; silently repair
malformed drawings; trust unit labels without physical dimensions; or infer
machine placement from drawing coordinates. No laser settings, kerf, offsets,
machine connection or manufacturing approval are introduced.

## DXF subset and authoritative format references

The reader consumes ASCII group-code/value pairs and explicit section envelopes.
It requires HEADER, TABLES and ENTITIES, no duplicate sections/header variables,
and a terminal EOF. The [Autodesk group-code description](https://help.autodesk.com/cloudhelp/2025/ENU/AutoCAD-DXF/files/GUID-89CB823D-614D-4D1E-8204-568EC72DF869.htm)
is the source for this tagged representation. Singleton values are selected by
code, not assumed table order. Vertex sequences retain their grouping.

Supported geometry is planar LINE, straight LWPOLYLINE and CIRCLE. Sources:
[LINE](https://help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF/files/GUID-FCEF5726-53AE-4C43-B4EA-C84EB8686A66.htm),
[LWPOLYLINE](https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-DXF/files/GUID-748FC305-F3F2-4F74-825A-61F04D757A50.htm),
and [CIRCLE](https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-DXF/files/GUID-8663262B-222C-414D-B133-4A8506A27C18.htm).
Vertex counts, closed flags, required coordinates and positive radii are checked.
Nonzero elevation, Z, thickness, width, bulge or nondefault extrusion block;
they are not flattened. Arcs, splines, inserts, images, text, hatches, old-style
polylines, custom subclasses and unknown entity attributes require review.
No inserts are expanded and no external reference is followed.

Exact LINE endpoints are assembled within each layer, without welding tolerance
or invented closing edges. Open/branched chains block through contour checks.
Duplicate edges/circles, degeneracy, crossings, overlaps and tangencies use the
same kernel as SVG. Layer names are preserved as an inventory, not interpreted
as cut/score/mark instructions. Per-entity manufacturing intent remains unverified.

Used layers must be explicitly present. Off/frozen/nonplotting/xref-dependent
layers, hidden/paper-space entities, unsupported appearance and linetypes block
rather than disappear from inspection. The source fields are documented in
[Autodesk LAYER](https://help.autodesk.com/cloudhelp/2018/ENU/AutoCAD-DXF/files/GUID-D94802B0-8BE8-4AC9-8054-17197688AFDB.htm)
and [common entity codes](https://help.autodesk.com/cloudhelp/2015/ENU/AutoCAD-DXF/files/GUID-3610039E-27D1-4E23-B6D3-7E60B22BB5BD.htm).

`$INSUNITS` must explicitly select millimetres, centimetres or inches in this
subset. It is an insertion-unit declaration, not proof of intended physical
dimensions; unspecified units never borrow host defaults. See
[Autodesk INSUNITS](https://help.autodesk.com/cloudhelp/2025/ENU/AutoCAD-Core/files/GUID-A58A87BB-482B-4042-A00A-EEF55A2B4FD8.htm).
All format references accessed 2026-09-17; no upstream source code was copied.

Other standard sections, unused block definitions and table content are not
rendered or treated as manufacturing evidence. The report inventories
uninterpreted sections and the whole-file hash covers them. Block inserts and
entity extensions cannot use this fact to bypass the supported geometry subset.
This is not full handle, table, layout or DXF schema/conformance validation.

Limits are implementation safeguards: 2 MiB input, 100,000 tag pairs, 4,096
characters per tag value, 1,024 entities and the shared 1,024 contour-segment
bound. Numeric literals reuse the SVG range/precision safeguards, including
lexical exponent checks. No oversized-file prefix receives a whole-file digest.

## Job context and migration

Callers must supply:

```text
preflight(job, machine, material, process,
          drawing_bytes=actual_bytes, source_revision=explicit_revision)
```

New fixture-version-2 job declarations are `drawing_sha256`, `model_dimensions`
in job units, `path_intent: cut`, `placement_frame: zero_origin_working_area`, and
the selected `process_profile_id`. Actual DXF units or SVG viewport physical
units must agree with job units. Measured extents are compared exactly after
conversion to millimetres; no manufacturing tolerance is invented.

Machine dimensions use `machine.lifecycle.units.length`. The declared placement
frame permits a bounds comparison with a zero-origin rectangle only. It is not
a calibrated origin, axis-direction mapping, reviewed nesting, kerf allowance,
usable-bed guarantee or physical-machine coordinate model. Translated geometry
can fail placement even when its extents fit. The paired fixture's symmetric
coordinates do not prove general SVG/DXF orientation equivalence.

Machine/material selection and the material's machine/process compatibility lists
are checked; the process profile must match the job's selected profile, machine
and material identities. Unknown job or material environmental declarations block. Beam and
process-emission findings remain independent. Missing/malformed contexts and
nonfinite, Boolean, string or nonpositive dimensions fail closed.

These checks still evaluate declarations, not evidence authenticity or applicable
process validation. Profiles remain unverified synthetic records and settings
remain empty. A complete skill review must request actual material, process,
ventilation, path-intent and reviewer evidence before any manufacturing-ready
conclusion. No-blocker utility output remains review-required/non-executable.
Full router/state approval composition is still Phase 6 work.

The CLI now reads the explicitly requested job and adjacent machine/material/
process JSON, plus only the explicitly requested drawing path:

```text
python scripts/laser_preflight.py --drawing fixtures/laser/cut-bracket/source/bracket.dxf --source-revision A
```

Reads are bounded to the byte limit plus one. It never follows a drawing path
inside untrusted metadata. Missing bytes/revision block; existing metadata-only
calls must migrate. Exit 1 means blockers, including missing human approval;
exit 0 means only no detected blocker in this limited review. JSON never grants
execution. Changing a real job's file requires renewed provenance and dependent
review, not automatically refreshing its hash to silence a mismatch.

## Evidence and remaining gate work

Both fixture files remain byte-for-byte unchanged; LF Git rules preserve their
identities. The paired validator now compares actual measured contours from both
readers against the fixed fixture, including hole positions/radii, not just
outer dimensions or counts. It remains an exact, ordered fixture assertion.

Tests exercise actual altered DXF/SVG bytes with valid labels and renewed
test-only hashes; explicit unit and expected-scale conflicts; partial contours;
unsupported semantics; malformed input; placement; target chains; environment;
source identity/revision and CLI behavior. Synthetic approved flags isolate these
failures from missing-human-approval; no approval record is created or promoted.
Executed results are in the [laser evaluation](../evaluation/laser-cut-evaluation.md).

The subsequent retained reviews and Phase 5 audit reconcile the format/intent/
evidence limits without approving any manufacturing handoff. Phase 6 composed
integration, public-alpha and practitioner validation remain open. Reopen these
boundaries for new entities/transforms, context schemas, tolerance/placement
rules or a consequential false-ready case.
