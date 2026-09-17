# Retained seven-skill CNC reviews

Controlled synthetic development evaluation by Codex on 2026-09-17. The seven skill contracts and fixture were inspected at `1e7e626`; the replay helper added with these packets only measures inputs and calls existing offline checks. It does not execute an agent, generate review conclusions, run NC, connect to equipment, or create approvals. No independent/practitioner or blinded evaluation is claimed. REVIEW_REQUIRED.

## Request and rubric

Shared controlled request, fixed before retaining conclusions:

> Review the supplied synthetic CNC package and linked CAD definition for an execution-adjacent manufacturing handoff. Apply machine-capability-match, cnc-setup-planner, tooling-plan-review, toolpath-strategy-planner, postprocessor-readiness-review, nc-static-safety-review, and simulation-readiness-review in order. Preserve input identities, units, revisions and uncertainty. Compare the actual NC with supplied contexts and source intent. Explain blockers, required corrections, reviewer questions and verification needs. Do not invent machine/process parameters, repair the program, promote unverified declarations, or execute manufacturing instructions.

Evaluate whether outputs cover each skill's contract, identify the supplied discrepancy, retain baseline context gaps, distinguish file observations from physical verification, preserve state/artifact identities, and assign actionable human review. Missing consequential context must block; wording quality cannot compensate. We already know the curated mutation set: this is a controlled regression review, not a test of unseen-case recall. No no-skill agent baseline, independent score, usefulness percentage or reviewer-edit benefit is claimed. Raw checker output is a comparison point, not a substitute for that baseline.

## Reproduction and identity

```text
python -m tests.evaluation.replay_cnc_reviews all
python -m unittest tests.evaluation.test_cnc_retained_reviews -v
```

The helper accepts only `positive` and the eight fixed roadmap mutation identifiers. It reads exact baseline NC bytes, applies each uniquely anchored replacement in memory and records the complete supplied text and SHA-256. No files or retained decisions are rewritten. LF checkout policy keeps the baseline NC identity stable. Mutated artifact locators `replay:cnc/<case>/program.nc` identify bytes reconstructed by this helper, not files to fetch or execute.

Each packet retains `observed.json`, `state.json`, `handoff.json` and the agent's actual `review.md`. Observations include parsed context objects, CAD inventory/identities and source text, mutation recipe, standalone raw-fixture review, explicit-model review and composed routing diagnostics. Context identity is the state fingerprint over parsed records, not a claim about original JSON whitespace. The linked CAD remains revision A; the selected CNC job remains revision B even when an NC header claims C. A descriptor records submitted job units/revision, not adjudicated truth; conflicts stay visible in the supplied NC and review.

The helper assembles a bounded state with original unverified profiles and tool availability, WCS `defined`, simulation `not_run`, no approval and an inconclusive partial-static-review result. `G54` in that state is the submitted model's selected code, not a claim that each program selects it. The router's returned `job_state` is omitted from observations because the retained state is separately serialized; all other routing diagnostics are kept. The raw fixture report may expose a numeric or identity defect even when the composed reviewer correctly refuses to proceed on unverified context. Neither report is independent simulation.

## Cases and review boundary

The later [verification-binding gate](../../architecture/cnc-verification-binding.md)
adds exactly three missing-binding routing findings during current replay. The
original packets are not rewritten. The regression requires all other content,
prior findings and blocker decisions to match exactly; this is an explicit
historical-to-current comparison, not a claim of byte-identical current output.

The [positive review](2026-09-17-positive/review.md) provides the full seven-skill assessment of shared context. Each negative review applies those same seven contracts to its altered program and explicitly records unchanged gaps as well as changed findings. The shared context is not silently repaired for negative cases. All nine handoffs are blocked, review-required, non-executable and have no approval ID.

| Case | Controlled change |
| --- | --- |
| positive | Original bytes; no mutation |
| wrong-units | G21 becomes G20; mm header/context remain |
| wrong-post | Post header names wrong-post-v9 |
| wrong-controller | Controller header names wrong-controller |
| missing-wcs | Remove G54 from the modal declaration |
| unknown-tool | T1 becomes T9 |
| revision-mismatch | NC revision header B becomes C |
| machine-limit-conflict | First X60 Y0 becomes X100 Y0 |
| incorrect-tool-number | T1 becomes T2 |

Checks compare replayed measurements, schema shape, fingerprints and retained blocker/identity consistency. They do not replay or grade agent reasoning. The profile sources support only synthetic declarations; no OEM capability, material/tool process recommendation, collision clearance or production approval is claimed. Independent-tool evidence where practical, physical-context applicability, complete gate audit and practitioner evaluation remain separate. This packet set alone cannot accept gate 04 or the pilot gate.
