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
| Data exfiltration | No network or upload code in repository scripts; public-fixture licensing and redaction rules | Users may run unrelated local tools outside this repository |
| Unsafe physical execution | No machine connectors; router hard-blocks `live_execution`; outputs force review/approval | Human misuse of reviewed artifacts remains possible |
| Path escape from fixture generator | Generator validates output paths inside the repository | Maintainers must review future generators |
| Supply-chain compromise | CadQuery/ezdxf are optional development-only generators; generated artifacts are checked in and runtime skills do not import them | Dependency versions are range-pinned, not hash-locked |
| Approval bypass after context change | State fingerprint and invalidation rules cover consequential fields | Future hosted persistence needs concurrency/audit design |

## Recommendation

`approve with changes` for public alpha only after adversarial tests and source-freshness review remain green. Physical manufacturing and live integrations remain out of scope.
