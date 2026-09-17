# Laser Cutting Mutations

Declarative mutations change a copy of the job or process context. They must produce the hard outcomes in `../expected/outcomes.yaml` without changing the positive fixture.

These YAML cases do not alone prove geometry detection. Actual file mutations in
`tests/safety/test_laser_dxf_review.py`, `test_laser_svg_review.py` and
`test_laser_file_preflight.py` retain valid labels while changing contours, units
and scale. Only controlled test derivatives receive a new declared test hash;
the original DXF/SVG sources and real approvals are never rewritten.
