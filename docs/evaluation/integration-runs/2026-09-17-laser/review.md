# Integrated laser preflight — 2026-09-17

REVIEW_REQUIRED. Block the manufacturing handoff. Apply `laser-job-preflight`
to the actual positive DXF, source inventory and unchanged fixture contexts
under the [protocol](../protocol.md).

## Source, units, scale and contours

The source manifest declares revision-A DXF authority for repository test
geometry only. Actual DXF hash
`200bb7af90248173158a9e9a84648a858ef244c6b61cea966e07a8832292761d`
matches it. Source and selected derivative remain separate descriptors; the
manifest remains reference evidence, not product-design authority. This does
not authenticate design intent or authorize a real manufacturing job.

The restricted byte reader found mm declarations, a closed four-segment
rectangle from (5,5) to (65,45), and two circles of radius 3 centred at (17,25)
and (53,25). Dimensions are 60 x 40. Supported open/duplicate/degenerate and
intersection/touch checks found none. All entities use layer 0. CLASSES, BLOCKS
and OBJECTS are listed as uninterpreted; this is not full DXF conformance or
rendering verification. Declared insertion units and fixture dimensions agree,
but authenticated physical scale/design comparison remains required.

## Path intent and process

The job says cut. Geometry/layer identity alone does not prove that every path
should be cut, nor establish sequencing, kerf compensation, focus or dimensional
acceptance. Ask the design owner to confirm path intent and required dimensions.
Do not translate the two-circle geometry into assumed drilling/marking intent.

Machine fixture-laser-40w, material fixture-plywood and process
fixture-plywood-profile agree by identifier. Placement lies within the declared
300 x 200 working-area tuple; machine and material lifecycles are unverified.
The process has `settings_status: verified` with **empty settings**. There is no
applicable numerical process evidence or supplied material thickness/composition.
Do not infer power from the machine name or guess power, speed, frequency, kerf
or focus. Require qualified material, machine and process review.

## Independent safety findings

| Review | Available declaration | Unresolved evidence and action |
| --- | --- | --- |
| Beam | Synthetic source-type/machine identity only | Applicable machine/site beam-safety review and qualified operator controls absent; no activation |
| Process emissions | Ventilation known; unsafe material not_indicated | Actual material composition/grade and site ventilation/emission evidence absent; obtain applicable source and site review |

Neither row satisfies the other. A plywood label is not a material-safety
determination, and a known-status label is not measured or qualified ventilation
evidence. No regulatory classification or numerical safety limit is asserted.

## Integrated handoff and reviewer action

The raw preflight retained partial geometry and the declarations, with missing
human approval. Integrated readiness rejects empty settings and unverified
profiles/current evidence. Because the nested process input is incomplete, the
integrated raw preflight does not run; the actual earlier byte check is retained
separately in [observed.json](observed.json).

Six review roles retain design/path uncertainty, missing process and output
checks, and distinct beam/emission findings. State-bound review details and
current-input bindings do not promote those findings to passed. The reviewer
must resolve source intent, material/thickness, applicable settings, both safety
reviews and final controller-output verification, then document the required
simulation/verification disposition and scoped human decision.

No final controller output, simulation, process settings or approval record was
produced. Both router and consumer return blockers and prohibit execution. This
same-agent synthetic review is development evidence, not a practitioner verdict
or a finding that this material/site/machine is safe to operate.
