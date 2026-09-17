"""Check the bounded revision-A bracket's source and SVG declarations.

This is a restricted fixture grammar, not an OpenSCAD interpreter, SVG renderer,
or general drawing/PMI parser. Unsupported constructs require separate review.
"""

from __future__ import annotations

import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


DIMENSIONS = {
    "plate_width": 60.0,
    "plate_depth": 40.0,
    "plate_thickness": 6.0,
    "back_height": 30.0,
    "hole_diameter": 6.0,
    "hole_offset": 12.0,
}
NUMBER = r"[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?"
SVG = "{http://www.w3.org/2000/svg}"
ATTRIBUTES = {
    "svg": {"width", "height", "viewBox"},
    "title": set(), "desc": set(), "g": set(), "tspan": set(),
    "rect": {"x", "y", "width", "height", "fill", "stroke"},
    "circle": {"cx", "cy", "r", "fill", "stroke"},
    "text": {"x", "y", "font-size"},
}


def _source_parameters(source: str, errors: list[str]) -> dict[str, float]:
    code = re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"', "", source, flags=re.DOTALL)
    values = {}
    for name, expected in DIMENSIONS.items():
        assignments = re.findall(rf"\b{name}\s*=\s*([^;]*)\s*;", code)
        if len(assignments) != 1 or not re.fullmatch(NUMBER, assignments[0].strip()):
            errors.append(f"source parameter {name} requires one literal numeric assignment")
            continue
        value = float(assignments[0])
        if not math.isfinite(value) or value != expected:
            errors.append(f"source dimension {name} does not equal revision-A value {expected}")
        values[name] = value
    declarations = re.findall(r"//\s*Units:\s*([^.]+)\.\s*Revision:\s*([^.]+)\.", source)
    if [(units.strip(), revision.strip()) for units, revision in declarations] != [("millimetres", "A")]:
        errors.append("source revision-A millimetre declaration is missing or unsupported")
    return values


def _numbers(element, names):
    literals = [element.attrib[name].strip() for name in names]
    if not all(re.fullmatch(NUMBER, value) for value in literals):
        raise ValueError("unsupported drawing numeric syntax")
    values = tuple(float(value) for value in literals)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("non-finite drawing coordinate")
    return values


def _drawing_checks(drawing: str, values: dict[str, float]) -> list[str]:
    errors = []
    if re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", drawing, re.IGNORECASE):
        return ["drawing DTD/entity declarations are unsupported"]
    if re.search(r"<\?(?!xml\s)", drawing, re.IGNORECASE):
        return ["drawing processing instructions are unsupported"]
    try:
        root = ET.fromstring(drawing)
    except ET.ParseError:
        return ["drawing is not well-formed XML"]
    if root.tag != SVG + "svg":
        return ["drawing root must be an SVG element in the SVG namespace"]
    nodes = {name: [] for name in ATTRIBUTES}
    for node in root.iter():
        name = node.tag.removeprefix(SVG)
        if node.tag != SVG + name or name not in ATTRIBUTES or set(node.attrib) - ATTRIBUTES.get(name, set()):
            return ["drawing contains unsupported elements or attributes; rendering/interpretation needs review"]
        if name == "svg" and node is not root:
            return ["nested SVG viewports require separate interpretation"]
        if name not in {"svg", "g", "text"} and list(node):
            return ["drawing contains unsupported nested content"]
        if name == "text" and any(child.tag != SVG + "tspan" for child in node):
            return ["drawing text supports only unstyled tspan fragments"]
        if name == "tspan" and not any(node in list(parent) for parent in root.iter(SVG + "text")):
            return ["drawing tspan must belong to a text annotation"]
        nodes[name].append(node)
    if root.attrib != {"width": "80mm", "height": "55mm", "viewBox": "0 0 80 55"}:
        errors.append("drawing viewport must preserve the declared 80 by 55 millimetre fixture scale")
    if len(nodes["title"]) != 1 or "".join(nodes["title"][0].itertext()).strip() != "CADCAM fixture bracket revision A":
        errors.append("drawing title must identify fixture revision A")
    width, depth, thickness = (values.get(name) for name in ("plate_width", "plate_depth", "plate_thickness"))
    description = re.compile(rf"Reference drawing:\s*({NUMBER}) mm wide by ({NUMBER}) mm deep,\s*({NUMBER}) mm thick base plate\.", re.IGNORECASE)
    if len(nodes["desc"]) != 1:
        errors.append("drawing requires one dimensional description")
    else:
        match = description.fullmatch("".join(nodes["desc"][0].itertext()).strip())
        if not match or tuple(float(item) for item in match.groups()) != (width, depth, thickness):
            errors.append("drawing description dimensions are missing, unsupported, or conflict with source")
    annotation = re.compile(rf"REV\s+(\S+)\s*\|\s*UNITS:\s*(\S+)\s*\|\s*BASE:\s*({NUMBER})\s*[x×]\s*({NUMBER})\s*[x×]\s*({NUMBER})", re.IGNORECASE)
    headers = 0
    notices = 0
    for node in nodes["text"]:
        text = "".join(node.itertext()).strip()
        match = annotation.fullmatch(text)
        if match:
            headers += 1
            revision, units, *dimensions = match.groups()
            if revision != "A" or units != "mm":
                errors.append("drawing annotation revision or units conflict with revision A in mm")
            if tuple(float(item) for item in dimensions) != (width, depth, thickness):
                errors.append("drawing annotation dimensions conflict with source")
        elif text == "REFERENCE ONLY - REVIEW_REQUIRED":
            notices += 1
        else:
            errors.append("drawing contains an unsupported text annotation; no dimensional interpretation inferred")
        try:
            x, y, size = _numbers(node, ("x", "y", "font-size"))
            if not (0 <= x <= 80 and 0 <= y <= 55 and size > 0):
                raise ValueError("annotation placement")
        except (KeyError, ValueError):
            errors.append("drawing annotation placement or font size is missing or unsupported")
    if not headers or not notices:
        errors.append("drawing requires an explicit revision/units/base annotation and review-only notice")
    try:
        if len(nodes["rect"]) != 1 or _numbers(nodes["rect"][0], ("x", "y", "width", "height")) != (10, 10, width, depth):
            errors.append("drawing base rectangle conflicts with the source projection")
        circles = sorted(_numbers(node, ("cx", "cy", "r")) for node in nodes["circle"])
        offset, diameter = values.get("hole_offset"), values.get("hole_diameter")
        if None in (width, depth, offset, diameter):
            errors.append("drawing hole projection cannot be compared without source parameters")
        elif circles != sorted(((10 + offset, 10 + depth / 2, diameter / 2), (10 + width - offset, 10 + depth / 2, diameter / 2))):
            errors.append("drawing base-hole positions or radii conflict with source")
        if any(node.attrib.get("fill") != "none" or node.attrib.get("stroke") != "black" for node in nodes["rect"] + nodes["circle"]):
            errors.append("drawing projected geometry must retain the supported outline presentation")
    except (KeyError, ValueError):
        errors.append("drawing projected geometry has missing or invalid numeric attributes")
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        source = (root / "source/bracket.scad").read_text(encoding="utf-8")
        drawing = (root / "source/bracket.svg").read_text(encoding="utf-8")
        metadata = json.loads((root / "metadata/revision.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return ["source, drawing, or revision metadata could not be read or parsed"]
    values = _source_parameters(source, errors)
    errors.extend(_drawing_checks(drawing, values))
    if not isinstance(metadata, dict) or metadata.get("revision") != "A" or metadata.get("units") != "mm":
        errors.append("revision metadata must declare revision A and units mm")
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
