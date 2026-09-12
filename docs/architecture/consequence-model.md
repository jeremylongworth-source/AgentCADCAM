# Consequence Model

## Purpose

Consequence classification determines how much context, verification, and human review a workflow requires. It is not a confidence score and cannot override a hard safety block.

## Levels

| Level | Meaning | Typical output |
| --- | --- | --- |
| `informational` | Explanatory or educational; no job-specific manufacturing decision | Definitions, questions, source map |
| `design_advisory` | Design or interoperability advice before process commitment | DFM findings, format plan |
| `manufacturing_planning` | Process, setup, tooling, profile, or handoff planning | Draft setup or print plan |
| `execution_adjacent` | Artifact is close to a machine or process and could be acted on | NC review, slicer readiness, laser preflight |
| `live_execution` | Request would control or start physical equipment | Always blocked in v0.x |

## Escalation rules

- A request to control physical equipment is `live_execution` and resolves to `BLOCK_EXECUTION`.
- A generated manufacturing artifact is at least `execution_adjacent`.
- Missing context raises review requirements; it never lowers consequence.
- Safety and authorization blocks are hard outcomes independent of completeness.
- A workflow may return multiple blockers and must preserve the most consequential unresolved conditions.

## Validation notes

The router owns classification. Skills may report findings and required context but must not downgrade a route to avoid a block.
