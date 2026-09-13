"""Generate and inspect the synthetic bracket; parent checks the process exit."""

from __future__ import annotations

import json
import math
import sys
from importlib.metadata import version
from pathlib import Path

from scripts.generate_cad_fixture_step import build_bracket, main as generate
from scripts.validate_cad_fixture_step import validate as validate_step
from scripts.validate_cad_fixture_mesh import validate as validate_mesh


def main() -> int:
    folder = Path(sys.argv[1])
    step = folder / "bracket.step"
    mesh = folder / "bracket.stl"
    sys.argv = ["generate", str(step), "--stl-output", str(mesh)]
    if generate() != 0:
        raise RuntimeError("generation failed")
    errors = validate_step(step) + validate_mesh(mesh)
    if errors:
        raise RuntimeError("; ".join(errors))

    import cadquery as cq

    original = build_bracket().val()
    imported = cq.importers.importStep(str(step)).val()
    # Ideal circular holes from the fixture dimensions, not a general DFM test.
    expected_volume = 60 * 40 * 6 + 60 * 6 * 24 - 4 * math.pi * 3**2 * 6
    for label, shape in (("original", original), ("STEP round trip", imported)):
        if not shape.isValid() or len(shape.Solids()) != 1:
            raise RuntimeError(f"{label}: expected one valid solid")
        if not math.isclose(shape.Volume(), expected_volume, rel_tol=1e-8):
            raise RuntimeError(f"{label}: volume does not match the bracket definition")
        cylinders = [face for face in shape.Faces() if face.geomType() == "CYLINDER"]
        expected_centres = [(12, 3, 18), (12, 20, 3), (48, 3, 18), (48, 20, 3)]
        centres = sorted(tuple(round(v, 6) for v in face.Center().toTuple()) for face in cylinders)
        if centres != expected_centres:
            raise RuntimeError(f"{label}: four cylindrical holes are not at the source coordinates")
        if any(not math.isclose(face.Area(), 2 * math.pi * 3 * 6, rel_tol=1e-8) for face in cylinders):
            raise RuntimeError(f"{label}: incorrect cylindrical hole area")
        bounds = shape.BoundingBox()
        for actual, expected in zip((bounds.xlen, bounds.ylen, bounds.zlen), (60, 40, 30)):
            if not math.isclose(actual, expected, abs_tol=1e-6):
                raise RuntimeError(f"{label}: incorrect bracket dimensions")

    print(json.dumps({
        "checks_finished": True,
        "versions": {name: version(name) for name in ("cadquery", "cadquery-ocp", "vtk", "casadi", "nlopt")},
        "step_bytes": step.stat().st_size, "stl_bytes": mesh.stat().st_size,
        "volume_mm3": imported.Volume(),
    }, sort_keys=True))
    # This message is not success evidence until the interpreter exits cleanly.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
