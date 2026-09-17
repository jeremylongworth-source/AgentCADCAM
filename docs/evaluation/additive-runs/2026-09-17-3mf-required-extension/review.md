# Unsupported required 3MF extension

Decision: **blocked additive handoff; REVIEW_REQUIRED**. This is Codex's controlled application of `additive-job-preflight` under the [request and rubric](../README.md), not practitioner approval or a blinded evaluation. See [observed.json](observed.json), [state.json](state.json) and [handoff.json](handoff.json).

## Artifact and provenance

The packet retains the actual selected source and derivative hashes, submitted job fields, source revision and unit claims. Source authority is limited to repository-authored synthetic geometry; it is not a complete functional product specification. STL/3MF remains a print derivative. Revision and unit conflicts are preserved, not corrected in the replay. No external/customer files or printer credentials were used.

## Mesh, units and build volume

The package declares the synthetic p extension as required. Our Core-only checker stops before deriving units, topology or build bounds; the report does not claim those checks passed. Do not strip the declaration or borrow the geometry report from the otherwise similar simple tetrahedron.

## Printer, material and slicer

PrusaSlicer exported this synthetic case as the same STL as its basic tetrahedron without a diagnostic, but that observation does not demonstrate extension support or preserved intent. Our unsupported-extension blocker remains. Synthetic printer/material and missing slicer/environment evidence also remain unresolved.

The job's slicer_profile_status flag has no attached profile content/version or applicable sliced-output verification. PrusaSlicer 2.9.6 was used in a separately retained geometry experiment only. No actual job profile was validated, and no temperatures, cooling, layer settings, speeds or material process values are supplied by this review. Request applicable primary printer/material/profile evidence rather than populate missing properties.

## Orientation and supports

Orientation and support status labels are not the plans themselves. No orientation rationale, selected support strategy, removal/access assessment, placement clearance or acceptance criteria are supplied. The design/additive reviewer must relate these choices to the controlled geometry and intended features; this packet recommends no fabricated angle, support threshold or slicer setting. Self-intersection and other unsupported geometry semantics require qualified follow-up, not an implicit pass.

## Environment and operator context

The supplied material/profile source explicitly supports synthetic declarations only. No applicable job/site evidence establishes ventilation, thermal, material-handling or operator conditions. A known label is insufficient; an unknown label is an additional explicit blocker. Obtain applicable manufacturer documentation and qualified site/operator review before a manufacturing-ready conclusion. This packet makes no material-safety or legal determination.

## Blockers and reviewer action

Case-specific unresolved finding: A required extension has no supported, reviewed interpretation, so the package cannot be treated as a fully understood Core build.

Obtain the extension specification and a reviewed applicable adapter/consumer, or have the design authority supply a controlled alternative representation with explicit semantics-loss review. Do not bypass required-extension handling to get a passing geometry result.

All baseline evidence gaps also remain: source intent and dimensional acceptance, actual printer/material applicability, slicer profile/version, orientation/support plan, environment and applicable verification. Approval remains not_requested with no approval record or ID. The handoff keeps all raw-preflight and routing blockers plus the skill review's unresolved-context/source blockers; no averaging or successful-export exception is permitted. Do not print or start equipment from this output.

## Evidence and limits

The replay helper measures fixed files and calls existing checks; it does not generate this reasoning or authenticate a reviewer. Generic routing and additive byte inspection are retained separately, so a routing result cannot be substituted for package/model validity. State stores the full submitted additive job under an evaluation-only setup object, binding its material/profile/status/units claims without changing the production state schema. [Independent native observations](../../additive-independent/prusaslicer-2.9.6-windows.json) are reference evidence only and do not resolve missing job-specific slicing or physical context. No agent-baseline score, unseen-case reliability, production approval or practitioner verdict is claimed.
