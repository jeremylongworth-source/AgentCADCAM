# Skill Authoring Standard

Every skill must define a narrow purpose, intended users, supported inputs, outputs, assumptions, source requirements, stop conditions, review status, and test fixtures. Skill metadata must identify its name, version, owner, and supported consequence levels.

Skills must be composable and vendor-neutral by default. They may report `MISSING_CONTEXT`, `SOURCE_VERIFICATION_REQUIRED`, `SIMULATION_REQUIRED`, `HUMAN_APPROVAL_REQUIRED`, or `BLOCK_EXECUTION`. They must not invent consequential parameters or claim certification.
