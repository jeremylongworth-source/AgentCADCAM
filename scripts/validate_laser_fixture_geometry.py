"""Validate the synthetic DXF/SVG laser fixture geometry and units."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import ezdxf

if __package__:
    from .laser_svg_review import inspect_svg
else:
    from laser_svg_review import inspect_svg


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    dxf_path = root / "source/bracket.dxf"
    svg_path = root / "source/bracket.svg"
    document = ezdxf.readfile(dxf_path)
    if document.header.get("$INSUNITS") != 4:
        errors.append("DXF $INSUNITS is not millimetres")
    model = document.modelspace()
    polylines = list(model.query("LWPOLYLINE"))
    circles = list(model.query("CIRCLE"))
    if len(polylines) != 1 or not polylines[0].closed:
        errors.append("DXF must contain one closed outer polyline")
    if len(circles) != 2:
        errors.append("DXF must contain two hole circles")
    svg_bytes = svg_path.read_bytes()
    report = inspect_svg(svg_bytes)
    if report["blockers"]:
        errors.extend(f"SVG: {finding}" for finding in report["findings"])
    else:
        expected = [
            {"kind": "polyline", "closed": True, "points": [["5", "5"], ["65", "5"], ["65", "45"], ["5", "45"]]},
            {"kind": "circle", "center": ["17", "25"], "radius": "3"},
            {"kind": "circle", "center": ["53", "25"], "radius": "3"},
        ]
        if report["contours_mm"] != expected:
            errors.append("SVG measured contours differ from the declared synthetic fixture in mm")
    try:
        svg = svg_bytes.decode("utf-8-sig")
    except UnicodeError:
        svg = ""  # The byte inspector already reports the malformed input.
    if not re.search(r"REVISION A|revision A", svg, re.IGNORECASE):
        errors.append("SVG revision is missing")
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("fixtures/laser/cut-bracket")
    errors = validate(root)
    if errors:
        print("LASER FIXTURE GEOMETRY VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("LASER FIXTURE GEOMETRY VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
