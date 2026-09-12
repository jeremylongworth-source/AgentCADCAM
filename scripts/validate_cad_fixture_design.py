"""Cross-check declared source, drawing, and exchange-fixture dimensions."""

from __future__ import annotations

import re
import sys
from pathlib import Path


DIMENSIONS = {
    "plate_width": 60.0,
    "plate_depth": 40.0,
    "plate_thickness": 6.0,
    "back_height": 30.0,
}


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    source = (root / "source/bracket.scad").read_text(encoding="utf-8")
    drawing = (root / "source/bracket.svg").read_text(encoding="utf-8")
    metadata = (root / "metadata/revision.json").read_text(encoding="utf-8")
    for name, expected in DIMENSIONS.items():
        match = re.search(rf"\b{name}\s*=\s*([-+0-9.eE]+)\s*;", source)
        if not match or float(match.group(1)) != expected:
            errors.append(f"source dimension {name} does not equal {expected}")
    for phrase in ("60 mm wide", "40 mm deep", "6 mm thick", "REV A", "UNITS: mm"):
        if phrase.lower() not in drawing.lower():
            errors.append(f"drawing is missing declaration: {phrase}")
    for phrase in ('"revision": "A"', '"units": "mm"'):
        if phrase not in metadata:
            errors.append(f"metadata is missing declaration: {phrase}")
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("fixtures/cad/bracket")
    errors = validate(root)
    if errors:
        print("CAD FIXTURE DESIGN VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CAD FIXTURE DESIGN VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
