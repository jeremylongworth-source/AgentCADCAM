"""Validate the synthetic DXF/SVG laser fixture geometry and units."""

from __future__ import annotations

import re
import sys
from pathlib import Path

if __package__:
    from .laser_svg_review import inspect_svg
    from .laser_dxf_review import inspect_dxf
else:
    from laser_svg_review import inspect_svg
    from laser_dxf_review import inspect_dxf


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    dxf_path = root / "source/bracket.dxf"
    svg_path = root / "source/bracket.svg"
    dxf_report = inspect_dxf(dxf_path.read_bytes())
    if dxf_report["blockers"]:
        errors.extend(f"DXF: {finding}" for finding in dxf_report["findings"])
    if dxf_report["declared_unit"] != "mm":
        errors.append("DXF declared units are not millimetres")
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
        if dxf_report["contours_mm"] != expected:
            errors.append("DXF measured contours differ from the declared synthetic fixture in mm")
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
