# CNC Fixtures

The `mill-bracket` fixture supplies synthetic machine/controller/setup/tooling/post/job context and inert NC for planning and static-review tests. It is not a runnable manufacturing package.

Version 3 retains NC/job revision B with explicit feed-per-minute and RPM modes plus a declared initial spindle stop. Its source CAD fixture remains revision A. The machine profile is revision 3 with explicit machine-axis bounds; the controller remains revision 2. The new fixed coordinate model is revision 1. All three are unverified. The feed ceiling, RPM range, bounds, zero translation and initial position are synthetic test data, not manufacturing parameters, observed machine state or OEM specifications.

The unchanged standalone positive control remains blocked for missing simulation and human approval. Its CLI checks raw fixture bounds, not mapped coordinates. Composed routing requires the [reviewed coordinate model](../../docs/architecture/nc-coordinate-model.md) and other required profile evidence; checked-in unverified declarations cannot supply approval. Review limits and required numeric fields are documented in the [static-review boundary](../../docs/architecture/nc-static-review-scope.md). Program/profile changes require new review; passing a fixture test does not authorize execution.
