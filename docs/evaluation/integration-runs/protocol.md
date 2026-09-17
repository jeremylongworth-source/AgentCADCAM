# Four-family integrated review protocol

## Scope and request

Protocol established before the reviews on 2026-09-17, at implementation baseline
`30eaeef`. This evaluates the four selected skillsets with the file-aware router
and serialized-handoff consumer. It does not replace the earlier family packets.

Apply this request to each case:

> Review the supplied source and manufacturing artifacts with their supplied
> context for a manufacturing handoff. Apply the selected skillset in manifest
> order. Preserve artifact authority, revision, units and unresolved context.
> Identify required reviewer actions, assemble bounded state and a handoff, and
> inspect both using the integrated router and handoff consumer. Do not operate
> equipment or supply missing process parameters.

Cases use the unchanged bracket CAD fixture, positive CNC program and contexts,
positive additive STL and contexts, and positive laser DXF and contexts. Here
`positive` names an input fixture, not an expected readiness verdict. Inspect
actual file bytes and declarations; do not substitute the reviewed synthetic
profiles or settings from routing test factories.

## Evidence layers

1. Raw fixture checks are tool-only observations, not a no-skill agent baseline.
2. `review.md` is the actual agent-authored application of the skill contract.
3. `decisions.json` records the review's unresolved assumptions, findings and
   required actions for deterministic serialization, not automated reasoning.
4. `state.json`, `handoff.json` and `observed.json` retain the integrated result.
   Replay reconstructs the supplied inputs and serialization; it does not
   regenerate or independently grade the authored review.
5. Isolated approval-lifecycle controls may use routing test factories, but must
   be labeled test-only and kept separate from these input packets. A synthetic
   approval record is not a qualified review or manufacturing authorization.

The author knows this corpus and implements the runtime. These are same-agent,
known-case development evaluations, not blinded comparisons, independent skill
usefulness measurements or Phase 8 practitioner packets. No no-skill agent
comparison or reviewer-edit-reduction claim is made.

## Rubric defined before judging

| Criterion | Evidence required |
| --- | --- |
| Routing and scope | Correct family/bundle; execution-adjacent handoff; no physical execution |
| Identity | Actual artifact hashes, declared authority, units and revisions preserved; conflicts not repaired |
| Skill output | Each selected skill's requested findings, missing inputs and reviewer actions addressed in authored prose |
| Evidence quality | Observed bytes separated from declarations, scoped parser results, unperformed checks and qualified review |
| Missing context | No invented settings, verified profiles, simulation result or approval; consequential gaps block |
| Integration | Current input-bound review findings, state-bound handoff, consumer result and preserved blockers |
| Review usefulness | Specific next reviewer decisions, not a generic request to be careful; same-agent judgment only |

Record observed gaps and remaining work. Do not average a consequential failure
into a quality score. Patch skills only for a concrete contract gap exposed by
the evaluation; formatting preferences alone do not warrant skill edits.

Schema validity checks record structure, not manufacturing suitability. A draft
state may preserve incomplete nested readiness inputs; its router must reject
those inputs. Retain raw checks separately if nested validation prevents a fresh
integrated parser run. Neither populated packets nor green regressions alone
close gate 07; a requirement-by-requirement audit remains necessary.
