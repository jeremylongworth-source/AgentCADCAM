# CAMotics synthetic experiment

This is an explicit simulator calibration configuration, **not** an inferred physical setup for `mill-bracket`. The project is copied into a private temporary directory by the opt-in native probe together with one exact fixture NC variant. Do not execute the NC on equipment or promote the project's settings into job context. REVIEW_REQUIRED.

The 60 × 40 × 6 prism at origin zero, 6-diameter / 12-length cylindrical cutting shape, and 1-mm sampling resolution are arbitrary synthetic experiment settings. The cutting length is not derived from the job's reach field; actual cutter length, stock position, fixture/holder geometry and offsets remain unknown. A coarse exported surface cannot establish a real workpiece, feature tolerance, collision clearance or physical suitability.

Only tool 1 is explicitly supplied. Unknown-tool cases deliberately expose the simulator's handling of missing entries; defaults are observations to flag, not accepted tooling data. Fixed workpiece bounds prevent automatic stock resizing from hiding a changed program extent. No machine, fixture, holder, controller limit or reviewed coordinate model is supplied to CAMotics.

The [probe and trust boundary](../../../docs/architecture/camotics-evidence-boundary.md) explain the observed results and how they differ from job verification. The project was authored for repository testing, uses synthetic CC0 fixture inputs, and is not a manufacturing parameter recommendation.
