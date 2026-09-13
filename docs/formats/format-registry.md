# Format Registry

This is the canonical review policy for the nine roadmap formats, not a claim that the repository implements every parser or verifies every exchange. Purpose, unit/revision handling, workflow choices, and validation requirements below are repository policies. Preserved/lost semantics describe capabilities and risks, not guaranteed exporter/importer fidelity. The linked primary sources support the identified format facts; they do not award manufacturing approval.

Parseability is not semantic fidelity, and semantic fidelity is not manufacturing approval.

For every conversion, retain source and output hashes, declared design revision, application/exporter version, export options, unit interpretation, and comparison findings. A changed derivative or context invalidates dependent approval. Filenames, timestamps, rendered previews, and format extensions alone cannot establish authority. Missing or conflicting consequential evidence yields `MISSING_CONTEXT` or `SOURCE_VERIFICATION_REQUIRED`; all handoffs remain `REVIEW_REQUIRED`.

The source IDs below resolve to scoped claims and review metadata in the [source registry](../sources/source-registry.yaml). Run `python scripts/validate_format_registry.py` to check entry completeness and source cross-references. This offline check cannot establish source truth, currentness, or job applicability.

## Native CAD

- Intended purpose: Preserve the declared editable design master in its originating application.
- Semantics preserved: Application-defined features and parameters may survive; FreeCAD FCStd specifically separates parametric/geometric document data, display data, and stored B-rep shapes.
- Semantics lost or ambiguous: Do not assume another application's importer preserves dependencies, feature behavior, assembly intent, or PMI.
- Unit handling: Record document units and explicit units for scripts/parameters; reopen and compare a known dimension. An application display preference is insufficient evidence of export scale.
- Revision implications: Bind source revision to the document hash and referenced files; a rebuild or dependency change requires renewed comparison of derivatives.
- Suitable workflow: Editable-source review, design changes, and controlled exports to an agreed neutral format.
- Unsuitable workflow: Unverified cross-vendor editing or a self-contained manufacturing instruction based only on the native extension.
- Required validation: Opening/rebuild result, external dependencies, model bodies, critical dimensions, units, revision, and requested PMI against the authoritative drawing/design.
- Sources: [freecad-fcstd](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/File_Format_FCStd.md)

## STEP AP242

- Intended purpose: Neutral product-data handoff with an explicitly agreed AP242 export/import capability.
- Semantics preserved: STEP can carry parts, assemblies, and PMI. Semantic PMI is computer-interpretable; graphic PMI represents annotation appearance. Validate them separately.
- Semantics lost or ambiguous: Do not infer editable native feature history, complete PMI, or identical importer interpretation from a successful open.
- Unit handling: Inspect representation units and conversion settings; compare physical dimensions after import rather than relying on the application's display units.
- Revision implications: Record AP/schema and exporter version separately from design revision; bind exported bytes to the reviewed native source and any external assembly references.
- Suitable workflow: CAD/CAM/inspection exchange after geometric and semantic comparisons.
- Unsuitable workflow: Assuming all STEP files are AP242, treating displayed annotations as semantic PMI, or using syntax success as acceptance.
- Required validation: Schema/reference checks, bodies and bounds, source comparison, semantic/graphic PMI inventory, validation properties where provided, and importer loss report.
- Sources: [nist-step-analyzer](https://www.nist.gov/services-resources/software/step-file-analyzer-and-viewer)

## IGES

- Intended purpose: Agreed legacy geometry exchange when the receiving workflow requires IGES.
- Semantics preserved: Curves, surfaces, and supported B-rep entities can transfer. IGES is not exclusively a surface-only format; translator/version support matters.
- Semantics lost or ambiguous: Native features and administrative metadata are not guaranteed. OCCT documents that its translated shapes do not carry the file's Global-section administrative data.
- Unit handling: Inspect Global-section units and model scale; record importer conversion and compare physical dimensions. Do not confuse drawing units with model units.
- Revision implications: Preserve design revision and original file metadata outside the translated shape; record healing changes as a new derivative.
- Suitable workflow: Legacy curve/surface/solid exchange with receiver-agreed entities and repair review.
- Unsuitable workflow: Treating unsewn surfaces as an accepted solid or relying on imported geometry alone to preserve revision and PMI.
- Required validation: Entity support, conversion settings, closure/topology, healing differences, critical dimensions, and source comparison.
- Sources: [occt-iges](https://occt3d.com/dev/doc/overview/html/occt_user_guides__iges.html), [occt-iges-units](https://dev.opencascade.org/doc/occt-7.7.0/refman/html/class_i_g_e_s_data___global_section.html)

## DXF

- Intended purpose: Controlled 2D contour/drawing exchange for the initial laser workflow.
- Semantics preserved: Supported entities and layers may transfer; Autodesk's HEADER reference identifies drawing settings, including unit-related fields.
- Semantics lost or ambiguous: Entity appearance does not establish cut/engrave intent, material, or machine compatibility. Unsupported entities need explicit handling.
- Unit handling: Inspect `$INSUNITS`, including unitless cases, but do not treat an insertion-unit setting as physical-scale proof. Compare model-space geometry with a known dimension and the export/import contract.
- Revision implications: Carry the design revision and source hash in the handoff manifest; a header date or filename is not sufficient. Recheck after scaling or contour edits.
- Suitable workflow: Unit-verified 2D cutting geometry with explicit layer/path intent.
- Unsuitable workflow: Full 3D product definition or manufacturing approval from a drawing preview.
- Required validation: Version/entity support, units, scale, closed/open path intent, duplicates, transforms, and source dimensions; process/material/ventilation review remains separate.
- Sources: [autodesk-dxf-header](https://help.autodesk.com/cloudhelp/2021/ENU/AutoCAD-DXF/files/GUID-A85E8E67-27CD-4C59-BE61-4DC9FADBE74A.htm)

## SVG

- Intended purpose: Controlled vector exchange for reviewed 2D cutting paths.
- Semantics preserved: Vector coordinates are interpreted through viewport, `viewBox`, and element transforms; these are part of the geometry interpretation, not decoration.
- Semantics lost or ambiguous: Browser appearance does not establish CAD dimensions, material, tolerances, or manufacturing path intent.
- Unit handling: Resolve physical width/height, `viewBox`, and transforms together. Unitless values must not be assumed millimetres; unresolved pixel/percentage scale blocks handoff.
- Revision implications: Preserve source revision/hash outside presentation metadata and revalidate changes to paths, transforms, or viewport sizing.
- Suitable workflow: Supported, scale-verified vector paths with explicit cut/engrave intent.
- Unsuitable workflow: Treating arbitrary browser-renderable SVG as a ready laser job or a complete CAD master.
- Required validation: Physical dimensions, transformed bounds, supported geometry, closure, duplicates, and path intent. Flag scripts/external resources; do not execute or retrieve them during geometry review.
- Sources: [w3c-svg-coordinates](https://www.w3.org/TR/SVG2/coords.html)

## STL

- Intended purpose: Tessellated shape derivative for mesh review and slicer intake, with a separate provenance/unit contract.
- Semantics preserved: Surface geometry for the exported mesh; it does not carry the PrusaSlicer project configuration that a project 3MF can retain.
- Semantics lost or ambiguous: Do not infer native features, tolerances, materials, source authority, or print settings from STL geometry.
- Unit handling: Require an external declared length unit and compare a known dimension; do not silently assume millimetres from a slicer's default.
- Revision implications: Record source revision, tessellation/export settings, and mesh hash. Regenerate and re-review after a source or scale change.
- Suitable workflow: Mesh-integrity and build-volume checks before reviewed FDM preparation.
- Unsuitable workflow: Sole authoritative master for feature-based CAD editing or a substitute for a tolerance/PMI handoff.
- Required validation: Parsing, finite coordinates, manifoldness, normals, degenerate/self-intersecting geometry as supported, dimensions after unit conversion, and comparison with the source.
- Sources: [prusa-project-formats](https://blog.prusa3d.com/3mf-file-format-and-why-its-great_30986/)

## 3MF

- Intended purpose: Additive model/package handoff while preserving supported resource, build, and project metadata.
- Semantics preserved: Core model resources, build items/transforms, and declared units; PrusaSlicer projects can additionally retain slicer configuration.
- Semantics lost or ambiguous: Core conformance does not imply support for every vendor profile or extension, nor verified printer/material settings.
- Unit handling: Honor the model unit; the reviewed Core specification defines millimeter when omitted. Record explicit versus defaulted units and apply them to geometry and placements before physical-dimension comparison.
- Revision implications: Hash the whole package and track source/model/profile revisions; a settings-only change requires renewed review even if mesh coordinates are unchanged.
- Suitable workflow: Additive exchange between consumers whose required extensions and configuration behavior have been checked.
- Unsuitable workflow: Treating 3MF as an STL rename or importing bundled settings as job approval.
- Required validation: Bounded package/XML inspection, relationships/resources/build references, mesh validity, units/transforms, and required-extension support. Unsupported required extensions block processing; separately review printer/material/profile compatibility.
- Sources: [3mf-core](https://github.com/3MFConsortium/spec_core/blob/master/3MF%20Core%20Specification.md), [prusa-project-formats](https://blog.prusa3d.com/3mf-file-format-and-why-its-great_30986/)

## NC/G-code

- Intended purpose: Controller-specific artifact for static review and independent simulation, never automatic execution.
- Semantics preserved: Words, modal commands, coordinates, and tool references interpreted by the selected controller dialect. LinuxCNC documentation is one dialect reference, not a universal machine contract.
- Semantics lost or ambiguous: Source design intent, collision freedom, physical offsets, and machine suitability cannot be inferred from readable text.
- Unit handling: Establish explicit dialect-specific units and modal state; LinuxCNC uses G20 for inches and G21 for millimetres. Comments or filenames cannot establish active units.
- Revision implications: Bind program hash to source revision, CAM/post version, machine/controller, setup, tooling, and verification; any consequential change invalidates approval.
- Suitable workflow: Non-actuating CNC review with known context and qualified follow-up.
- Unsuitable workflow: Cross-controller reuse without verification or running a reviewed file from this repository.
- Required validation: Dialect/token support, comments, modal units/WCS, tool references, supported limits checks, provenance/post identity, simulation, and scoped human review. Document parser limitations; absence of a warning is not safety evidence.
- Sources: [linuxcnc-gcode-overview](https://www.linuxcnc.org/docs/html/gcode/overview.html), [linuxcnc-units](https://linuxcnc.org/docs/html/gcode/g-code.html)

## STEP-NC

- Intended purpose: Research-track review of structured manufacturing data; not a v0.x runtime path.
- Semantics preserved: AP238 combines machining-model information from ISO 14649 with STEP geometry, GD&T, and product-data management concepts.
- Semantics lost or ambiguous: Actual consumer support, edition compatibility, and machine mapping must be demonstrated, not inferred from the STEP-NC label.
- Unit handling: Inspect declared geometry/process units and transformations using the selected schema; compare physical dimensions and reject unresolved mappings.
- Revision implications: Record standard/schema edition separately from job revision; preserve source, process-plan, and translated-output hashes.
- Suitable workflow: Isolated interoperability research and documented comparison of supported representations.
- Unsuitable workflow: Assuming controller support or replacing the established review/approval chain with a STEP-NC file.
- Required validation: Explicit research status, schema/entity coverage, units, geometry/process mapping, and independent review. No machine connection or production approval.
- Sources: [stepnc-ap238-model](https://www.steptools.com/stds/stepnc/tech_resources/howtoread.html)
