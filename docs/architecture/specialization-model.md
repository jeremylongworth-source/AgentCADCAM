# Specialization Model

## Purpose

Specializations add explicit process, vendor, material, or jurisdiction knowledge without contaminating the portable core.

## Layers

1. **Core contracts** define shared vocabulary, schemas, safety behavior, and workflow-independent rules.
2. **Workflow specializations** define CNC milling, FDM additive, and laser-cutting checks.
3. **Vendor profiles/adapters** describe documented machine, controller, CAD/CAM, slicer, or simulation behavior.
4. **Jurisdiction profiles** provide research routing and source collections, never final legal determinations.

## Rules

- Specializations must declare scope and required source metadata.
- A specialization may tighten a rule but may not weaken a core safety block.
- Vendor or jurisdiction knowledge is opt-in and explicit in job context.
- No specialization becomes a required runtime dependency of the core.
- Conflicting profiles resolve to `SOURCE_VERIFICATION_REQUIRED` or `MACHINE_CONTEXT_REQUIRED`, not silent precedence.

## Planned initial locations

`specializations/cnc-milling/`, `specializations/additive-fdm/`, `specializations/laser-cutting/`, and `specializations/jurisdictions/canada/`.
