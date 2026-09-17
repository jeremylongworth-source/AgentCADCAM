# Initial skill-contract claim inventory

Reviewed: 2026-09-17 against all fourteen `skills/*/SKILL.md` files at `4591509`.
No skill, source assessment, fixture setting or retained approval is changed.
This is a bounded contract audit, not certification of every possible generated
response or every historical repository statement.

## Classification

Review duties, refusal rules, required fields and human-approval boundaries are
repository policy from the roadmap and domain contract. They are not claims that
a law mandates this particular software workflow. The contracts prescribe no
numeric machine, tooling, material, laser or exposure settings and make no final
legal classifications. Job-specific findings still require applicable evidence.

The [format registry](../formats/format-registry.md) records format facts and
primary references. The [non-format audit](nonformat-claim-audit.md) records the
four primary safety/context rationales and their inspected sections. This
inventory reuses those recorded reviews; it does not claim a new source fetch or
extend a citation to numerical process recommendations.

| Skill | Claim classification and evidence boundary |
| --- | --- |
| `cadcam-intake-and-scope` | Policy: inventory, classify, refuse physical control and unresolved authorization. No machine capability is inferred. |
| `design-file-provenance-review` | Policy: authority and permission must be established separately from possession. Format-loss rationale comes from the format registry; this is not a legal ownership determination. |
| `file-format-interoperability-plan` | Format facts route explicitly to the registry. Keeping parseability, fidelity and approval separate is policy; STL is not treated as complete product intent. |
| `cad-manufacturability-review` | Checklist of questions, not quantified process capability or a universal defect classifier. Molded-part/elastomer routing is conditional; no such implemented specialization is promised. |
| `drawing-pmi-handoff-review` | Policy: compare supplied intent and escalate ambiguity. No GD&T standard compliance, general PMI interpretation or dimensionally correct part is certified. |
| `machine-capability-match` | Requires actual sourced machine limits. Sandvik's selection considerations support the context rationale, not a machine-specific envelope result. |
| `cnc-setup-planner` | Policy: explicit stock, fixtures, WCS and verification. Haas's example-program limitations support requiring job context, not a generic safe setup procedure. |
| `tooling-plan-review` | Sandvik supports reviewing tool/machine/clamping context. Actual geometry, reach, clearance and availability require job evidence; tool presence is not clearance proof. |
| `toolpath-strategy-planner` | Planning checklist with explicit source requirements. No numerical strategy, feeds/speeds or toolpath performance claim is supplied. |
| `postprocessor-readiness-review` | Policy: match identity/applicability and obtain separate static/simulation review. Controller semantics require the actual dialect sources, not a post name. |
| `nc-static-safety-review` | Review obligations exceed the implemented parser subset. [Static NC scope](../architecture/nc-static-review-scope.md) and [coordinate model](../architecture/nc-coordinate-model.md) state the supported semantics, sources and refusals. No physical-motion guarantee. |
| `simulation-readiness-review` | Policy: simulation scope and input identity must match; success cannot authorize execution. Tool observations support only their retained experiments. |
| `additive-job-preflight` | Format facts come from the registry. NIOSH supports separate material/environment review; this does not establish safe exposure, ventilation design or printability. |
| `laser-job-preflight` | DXF/SVG facts come from scoped format/parser references. CCOHS supports separate beam/non-beam findings, not material approval or safe settings. |

## Software and retained-output boundaries

The architecture contracts for
[STL](../architecture/additive-stl-evidence.md),
[3MF](../architecture/additive-3mf-evidence.md),
[DXF](../architecture/laser-file-evidence.md),
[SVG](../architecture/laser-svg-evidence.md) and
[derivation binding](../architecture/derivation-binding.md)
distinguish externally sourced representation rules from implemented subsets.
Parser size limits are software guards, not machine capacities. Hash equality
establishes byte identity, not authenticated design intent or derivation truth.

Family and integration gate reviews retain exact observations and blocked
handoffs. Synthetic profile values, declared simulation status and test-only
source assessments are not OEM evidence. Positive controls recognize a scoped
review record while still forbidding execution. Do not transfer their parameters
or approvals to real jobs.

Jurisdiction specializations remain reserved; no Canadian legal module is
implemented. References from Canadian publishers do not select jurisdiction.
New legal, material-specific, numerical or compatibility claims require separate
applicable primary evidence and review under the
[freshness process](source-freshness-process.md).

No additional factual-source blocker was identified in these fourteen bounded
contracts. That finding does not close the public-alpha gate: see the
[release hold](../development/public-alpha-gate-review.md).
