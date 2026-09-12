"""Validate the synthetic DXF/SVG laser fixture geometry and units."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import ezdxf


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
    svg = svg_path.read_text(encoding="utf-8")
    if "viewBox=\"0 0 70 50\"" not in svg or 'width="70mm"' not in svg:
        errors.append("SVG dimensions or viewBox are not explicit")
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
