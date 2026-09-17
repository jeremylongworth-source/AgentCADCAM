# AgentSkills Threat Model

## Review scope

This review covers the repository’s skill instructions, references, fixtures, router/state utilities, validation scripts, optional fixture-generation dependencies, and public documentation. It does not grant access to secrets, private machine networks, or external systems.

## Assets and trust boundaries

- Design files, drawings, meshes, NC/G-code, machine/controller/material profiles, and provenance/IP data.
- Human approval records and context fingerprints.
- Trust boundaries from user request to skill instructions, fixture content to parsers, scripts to the filesystem, and optional development dependencies to generated artifacts.

## Threat paths and mitigations

| Threat | Mitigation | Residual risk |
| --- | --- | --- |
| Prompt injection in a CAD file, source note, fixture, or external reference | Treat artifacts as data; never obey embedded instructions; preserve source/evidence separation | Reviewers must still inspect untrusted content |
| Data exfiltration | Explicit-import regression scans `scripts/`, `router/` and `state/` recursively for selected network/process modules; public-fixture licensing and redaction rules | This is not a sandbox: dynamic imports, alternate APIs, transitive dependencies and native binaries need separate review |
| Unsafe physical execution | No machine connectors; router hard-blocks `live_execution`; outputs force review/approval | Human misuse of reviewed artifacts remains possible |
| Path escape from fixture generator | Generator validates output paths inside the repository | Maintainers must review future generators |
| Supply-chain compromise | CadQuery is optional fixture-generation tooling; ezdxf is a test/inspection dependency. Optional CAMotics and PrusaSlicer experiments check pinned runtime identities before launching fixed fixture experiments | Python requirements use version ranges. Native pins identify inspected files, not trusted behavior or a complete operating-system dependency boundary |
| Approval bypass after context change | State fingerprint and invalidation rules cover consequential fields | Future hosted persistence needs concurrency/audit design |

## Local process boundary

CLI regression tests launch local Python commands. Explicitly invoked probes in
`tests/native/` also launch local CadQuery, CAMotics or PrusaSlicer experiments.
They are outside the portable import scan; their argument, input, timeout and
runtime checks require separate tests and review. These processes are not
machine-control permission, and no OS-level network sandbox is claimed.

## Gate decision

Public-alpha acceptance remains open under the [roadmap reconciliation](../development/roadmap-reconciliation.md).
Passing lexical scans does not prove prompt-injection resistance or zero
false-ready decisions. The [named safety-case matrix](../evaluation/public-alpha-safety-corpus.md)
now covers the thirteen roadmap cases at the structured APIs. Complete the
remaining factual-source and broader adversarial review and operational
private-reporting prerequisite before closing Phase 7. Physical manufacturing
and live integrations remain out of scope.
