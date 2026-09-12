"""Validate the generated STL fixture's binary/ASCII envelope and extents.

This is a lightweight mesh sanity check. It does not prove manifoldness,
surface orientation, tolerance fidelity, or manufacturing suitability.
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path


def _vertices(path: Path) -> list[tuple[float, float, float]]:
    data = path.read_bytes()
    if len(data) >= 84:
        triangle_count = struct.unpack_from("<I", data, 80)[0]
        if 84 + triangle_count * 50 == len(data):
            values: list[tuple[float, float, float]] = []
            for offset in range(84, len(data), 50):
                for vertex_offset in (12, 24, 36):
                    values.append(struct.unpack_from("<fff", data, offset + vertex_offset))
            return values
    text = data.decode("utf-8")
    return [tuple(float(value) for value in match) for match in re.findall(
        r"vertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)", text, re.IGNORECASE
    )]


def validate(path: Path) -> list[str]:
    if not path.is_file():
        return [f"missing STL fixture: {path}"]
    vertices = _vertices(path)
    if not vertices:
        return ["STL fixture contains no vertices"]
    extents = [(min(axis), max(axis)) for axis in zip(*vertices)]
    expected = [(0.0, 60.0), (0.0, 40.0), (0.0, 30.0)]
    errors = []
    for axis, (actual, target) in enumerate(zip(extents, expected)):
        if any(abs(a - b) > 1e-4 for a, b in zip(actual, target)):
            errors.append(f"axis {axis} extent {actual} does not match expected {target}")
    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("fixtures/cad/bracket/source/bracket.stl")
    errors = validate(path)
    if errors:
        print("STL FIXTURE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("STL FIXTURE VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
