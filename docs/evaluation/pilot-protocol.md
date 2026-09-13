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
- Prefer sanitized copies of real inputs; retain the participant’s original outside the repository. Synthetic copies belong to supplemental tests and cannot count toward the pilot gate.
- Keep raw evidence separate from interpretation.
- Redact names, customer identifiers, proprietary geometry, credentials, endpoints, and export-sensitive details.
- Store only the minimum packet required to reproduce the finding and obtain permission before public release.

## Measures

Capture the roadmap measures: schema validity, routing accuracy, revision/provenance detection, interoperability recommendation accuracy, handoff completeness, unsupported assumptions, reviewer edit burden, usefulness, safety findings, and false-ready decisions.

For machine-readable aggregation, record the measures in `final-verdict/final-verdict.yaml`. Leave the template unset until a reviewer measures the outputs, then use `packet_status: completed`. Record a pseudonymous reviewer ID, role, relevant experience, qualification declaration, consent, sanitization, and `input_origin: real` or `sanitized_real`.

Each `evidence` entry lists packet-relative paths to nonempty files in its named directory. Preserve actual inputs, both outputs, reviewer findings, edits, and safety findings. A report explicitly recording no edits or no safety findings is acceptable; an empty directory is not evidence. The validator checks paths and declarations, not whether the documents substantiate the claims.

Use these measurement definitions consistently across baseline and skill output:

- Binary measures (`schema_valid`, `router_correct`, `revision_provenance_detected`, `interoperability_recommendation_accurate`, `handoff_complete`, `usable_with_minor_or_no_edits`) indicate whether the whole packet meets that criterion. Enumerate the inspected outputs, decisions, defects, and required handoff items in reviewer findings before scoring. These are packet pass rates, not item-level accuracy estimates. A criterion with no applicable opportunity is not a success: retain such an evaluation as draft or supplemental evidence until the packet covers the required criteria.
- `critical_safety_cases` and `critical_safety_cases_detected` count known critical cases and those correctly flagged. Declare the expected cases before assessing outputs. Zero known cases cannot demonstrate detection; the aggregate requires a positive total.
- `machine_post_mismatch_detected` records the known mismatch test result for CNC packets; null is allowed for other families. Preserve the machine/post mismatch findings even where a missed case is not critical.
- `false_ready_decision` is true if any critical false manufacturing-ready decision occurred; even one blocks readiness.
- `safety_regulatory_claims` counts all such claims in the assessed output, and `authoritatively_sourced_claims` counts those a qualified reviewer verified against authoritative references. Preserve a claim-to-source ledger with publisher, locator, revision/access date, supported claim, and reviewer determination in safety findings. Zero claims is permitted only with an explicit no-claims finding; it is reported as not applicable, not a 100% sourcing rate.
- `unsupported_assumption_count` counts unsupported factual assertions, and `unsupported_assumption_opportunities` counts all factual assertions reviewed. The reported rate is unsupported divided by reviewed assertions.
- `reviewer_edit_burden.baseline_count` and `.skill_count` count edits needed to bring comparable outputs to the same handoff standard. Define an edit consistently before review. Reduction is `1 - total_skill_edits / total_baseline_edits`; a zero baseline cannot demonstrate reduction.
- `usefulness_rating` is a reviewer score from 1 (unusable) to 5 (highly useful); report its mean without inventing a roadmap threshold.

Use the roadmap targets as decision thresholds: 100% schema validity, critical safety detection, and authoritative sourcing for safety/regulatory claims; zero critical false-ready states; router accuracy at least 97%; handoff completeness at least 98%; revision/provenance detection at least 98%; interoperability accuracy at least 95%; unsupported assumptions below 2%; at least 90% usable with minor/no edits; and edit burden reduced by at least 30%. Report sample size and confidence; do not generalize a small directional sample.

## Verdict

Each packet records `proceed`, `revise`, or `stop`, with evidence, required edits, safety findings, and unresolved risks. `CADCAM_09_PILOT_VALIDATED` is not valid until real practitioners or suitably qualified reviewers evaluate real-input packets across the intended workflow scope.

Run `python scripts/evaluate_pilot_gate.py <packet-root>` from the repository root. Every immediate subdirectory is treated as a submitted packet; missing or incomplete packets block the report. A complete submission covers all four initial workflow families. The report is `not_ready` (exit 1) or `thresholds_met` (exit 0), and always has `gate_awarded: false`. It does not establish source authority or input authenticity automatically. Qualified reviewers must inspect the referenced evidence and record the gate decision separately, including participant-role coverage, sampling limits, and unresolved risks.

Wilson intervals use a 95% nominal level and an independent-trials assumption. Repeated reviewers or related cases may be correlated; intervals describe submitted proportions, not a guarantee of future manufacturing performance. Threshold decisions use the roadmap's observed targets, not interval bounds. The roadmap specifies no minimum sample size, so a small passing submission still needs explicit scope and sampling review.
