# CNC Fixtures

The `mill-bracket` fixture supplies synthetic machine/controller/setup/tooling/post/job context and inert NC for planning and static-review tests. It is not a runnable manufacturing package.

Version 2 uses NC/job revision B with explicit feed-per-minute and RPM modes plus a declared initial spindle stop. Its source CAD fixture remains revision A. Machine/controller profile revisions are 2 and unverified. The 1000 mm/min feed ceiling, existing RPM range and coordinate bounds are synthetic test data, not manufacturing parameters or OEM specifications.

The unchanged positive control remains blocked for missing simulation and human approval. Review limits and the required numeric fields are documented in the [static-review boundary](../../docs/architecture/nc-static-review-scope.md). Program/profile changes require new review; passing a fixture test does not authorize execution.
