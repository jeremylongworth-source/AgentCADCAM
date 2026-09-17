"""Perform a dependency-free sanity check on the generated STEP fixture.

This validates the Part 21 envelope and expected geometric extent markers. It
does not prove topology, manifoldness, tolerances, or manufacturing readiness.
"""

from __future__ import annotations

import re
import math
import sys
from pathlib import Path


POINT_RE = re.compile(
    r"#(\d+)\s*=\s*CARTESIAN_POINT\('',\(([-+0-9.eE]+),([-+0-9.eE]+),([-+0-9.eE]+)\)\)"
)
VERTEX_RE = re.compile(r"VERTEX_POINT\('',#(\d+)\)")


def validate(path: Path) -> list[str]:
    if not path.is_file():
        return [f"missing STEP fixture: {path}"]
    return validate_text(path.read_text(encoding="utf-8"))


def validate_text(text: str) -> list[str]:
    """Check supplied fixture text without reading paths."""
    errors: list[str] = []
    if not text.startswith("ISO-10303-21;"):
        errors.append("missing ISO-10303-21 header")
    if not text.rstrip().endswith("END-ISO-10303-21;"):
        errors.append("missing END-ISO-10303-21 trailer")
    if "MANIFOLD_SOLID_BREP(" not in text:
        errors.append("STEP fixture does not declare a manifold solid BREP")
    if text.count("CIRCLE(") < 8:
        errors.append("STEP fixture does not contain both circular boundaries of all four holes")
    coordinates = {identifier: tuple(float(value) for value in xyz) for identifier, *xyz in POINT_RE.findall(text)}
    if any(not math.isfinite(value) for point in coordinates.values() for value in point):
        errors.append("STEP fixture contains nonfinite coordinates")
    vertices = VERTEX_RE.findall(text)
    missing = set(vertices) - coordinates.keys()
    if missing:
        errors.append("STEP fixture has unresolved vertex coordinates")
    # Surface origins and construction points may lie outside trimmed material.
    # Only topological vertex points contribute to this fixture-envelope check.
    points = [coordinates[identifier] for identifier in vertices if identifier in coordinates]
    if not points:
        errors.append("STEP fixture contains no resolved vertex points")
    else:
        extents = [(min(axis), max(axis)) for axis in zip(*points)]
        expected = [(0.0, 60.0), (0.0, 40.0), (0.0, 30.0)]
        for axis, (actual, target) in enumerate(zip(extents, expected)):
            if actual != target:
                errors.append(f"axis {axis} extent {actual} does not match expected {target}")
    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("fixtures/cad/bracket/source/bracket.step")
    errors = validate(path)
    if errors:
        print("STEP FIXTURE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("STEP FIXTURE VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
