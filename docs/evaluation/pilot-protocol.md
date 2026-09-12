# Real-Input Pilot Protocol

## Decision to inform

Determine whether CAD/CAM Skills improves the completeness and safety of real manufacturing handoffs for qualified practitioners without increasing unsupported assumptions or false-ready decisions.

## Participants

Recruit reviewers representing several of: CAD designers, mechanical designers, CAM programmers, machinists, manufacturing engineers, additive users, laser operators, makers, and DFM reviewers. Record role and relevant experience, not unnecessary personal information.

Exclude any input that the participant is not authorized to share, contains credentials or machine-network details, or cannot be sanitized for the evaluation environment.

## Method

Use a moderated, task-based review of a real or sanitized manufacturing packet. Ask the participant to provide a baseline workflow result and then review the skill output. Do not execute NC, G-code, slicer output, laser settings, or machine actions. Scenario tests can supplement the pilot but cannot satisfy the gate alone.

## Neutral task prompts

1. Walk through a recent CAD/CAM or manufacturing handoff you were responsible for.
2. What information did you need to establish source authority, revision, units, material, process, machine, setup, tooling, or approval?
3. Which defects or missing-context cases have caused rework, scrap, delay, or safety concern?
4. What did you do when a neutral export, mesh, drawing, postprocessor, or process profile was ambiguous?
5. Review the baseline and skill outputs. What is missing, incorrect, unsupported, or unusually useful?
6. Which findings would you act on, escalate, or ignore, and why?
7. What edits would be required before you would hand the package to the next qualified reviewer?

Ask for recent behavior and concrete examples before opinions about future adoption. Probe frequency, impact, workaround, reviewer burden, and disconfirming cases. Do not pitch the solution during evidence capture.

## Consent and data handling

- Obtain consent for the evaluation and any recording before capture.
- Prefer sanitized or synthetic copies; retain the participant’s original outside the repository.
- Keep raw evidence separate from interpretation.
- Redact names, customer identifiers, proprietary geometry, credentials, endpoints, and export-sensitive details.
- Store only the minimum packet required to reproduce the finding and obtain permission before public release.

## Measures

Capture the roadmap measures: schema validity, routing accuracy, revision/provenance detection, interoperability recommendation accuracy, handoff completeness, unsupported assumptions, reviewer edit burden, usefulness, safety findings, and false-ready decisions.

Use the roadmap targets as decision thresholds: 100% schema validity and critical safety detection, zero critical false-ready states, router accuracy at least 97%, handoff completeness at least 98%, revision/provenance detection at least 98%, interoperability accuracy at least 95%, unsupported assumptions below 2%, and at least 90% usable with minor/no edits. Report sample size and confidence; do not generalize a small directional sample.

## Verdict

Each packet records `proceed`, `revise`, or `stop`, with evidence, required edits, safety findings, and unresolved risks. `CADCAM_09_PILOT_VALIDATED` is not valid until real practitioners or suitably qualified reviewers evaluate real-input packets across the intended workflow scope.
