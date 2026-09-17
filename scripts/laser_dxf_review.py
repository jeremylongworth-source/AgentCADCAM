"""Bounded ASCII DXF planar contour evidence; no recovery, rendering or execution."""

from collections import defaultdict
from fractions import Fraction
import hashlib
import re

if __package__:
    from .laser_svg_review import MAX_BYTES, MAX_SEGMENTS, ReviewRequired, number, contour_review
else:
    from laser_svg_review import MAX_BYTES, MAX_SEGMENTS, ReviewRequired, number, contour_review


MAX_TAGS = 100_000
UNITS = {1: ("inch", Fraction(127, 5)), 4: ("mm", Fraction(1)), 5: ("cm", Fraction(10))}


def integer(value):
    if not isinstance(value, str) or not re.fullmatch(r"[+-]?[0-9]{1,10}", value):
        raise ValueError("invalid DXF integer")
    return int(value)


def one(tags, code, default=None):
    values = [value for key, value in tags if key == code]
    if len(values) > 1 or not values and default is None:
        raise ValueError("missing or duplicate singleton DXF tag")
    return values[0] if values else default


def records(tags):
    result = []
    for tag in tags:
        if tag[0] == 0:
            result.append([tag])
        elif not result:
            raise ValueError("DXF record lacks entity type")
        else:
            result[-1].append(tag)
    return result


def sections(data):
    text = data.decode("ascii")
    if "\x00" in text:
        raise ReviewRequired("binary/nontext DXF is unsupported")
    lines = text.splitlines()
    if len(lines) % 2:
        raise ValueError("DXF has an incomplete tag pair")
    if len(lines) > 2*MAX_TAGS:
        raise ReviewRequired("DXF exceeds tag limit")
    tags = []
    for i in range(0, len(lines), 2):
        code, value = integer(lines[i].strip()), lines[i+1].strip()
        if not 0 <= code <= 1071 or len(value) > 4096:
            raise ReviewRequired("DXF tag code/value is outside review limits")
        if code != 999:  # Comments are inert, not source/revision authority.
            tags.append((code, value))
    if not tags or tags[-1] != (0, "EOF"):
        raise ValueError("DXF requires terminal EOF")
    result, i = {}, 0
    while i < len(tags)-1:
        if tags[i] != (0, "SECTION") or i+1 >= len(tags) or tags[i+1][0] != 2:
            raise ValueError("invalid DXF section envelope")
        name, i = tags[i+1][1], i+2
        if name in result:
            raise ValueError("duplicate DXF section")
        if name not in ("HEADER", "CLASSES", "TABLES", "BLOCKS", "ENTITIES", "OBJECTS", "THUMBNAILIMAGE"):
            raise ReviewRequired("unsupported DXF section")
        content = []
        while i < len(tags) and tags[i] != (0, "ENDSEC"):
            if tags[i] in ((0, "SECTION"), (0, "EOF")):
                raise ValueError("unterminated DXF section")
            content.append(tags[i])
            i += 1
        if i >= len(tags):
            raise ValueError("unterminated DXF section")
        result[name], i = content, i+1
    if not {"HEADER", "ENTITIES", "TABLES"} <= result.keys():
        raise ValueError("DXF requires explicit header, layer table and entities")
    return result


def header_values(tags):
    header, current = {}, None
    for code, value in tags:
        if code == 9:
            if value in header:
                raise ValueError("duplicate DXF header variable")
            current = value
            header[current] = []
        elif current is None:
            raise ValueError("DXF header variable is missing")
        else:
            header[current].append((code, value))
    return header


def layer_table(tags):
    layers, table = {}, None
    for record in records(tags):
        kind = record[0][1]
        if kind == "TABLE":
            if table is not None:
                raise ValueError("nested DXF table")
            table = one(record, 2)
        elif kind == "ENDTAB":
            if table is None:
                raise ValueError("unexpected table end")
            table = None
        elif table is None:
            raise ValueError("record outside DXF table")
        elif table == "LAYER":
            if kind != "LAYER":
                raise ValueError("non-layer record in layer table")
            name = one(record, 2)
            if name.casefold() in layers:
                raise ValueError("duplicate DXF layer")
            layers[name.casefold()] = record
    if table is not None:
        raise ValueError("unterminated table")
    return layers


def check_layer(record):
    if {code for code, _ in record} - {0, 2, 5, 330, 100, 70, 62, 6, 290, 370, 390, 347, 420}:
        raise ReviewRequired("DXF used layer has unsupported attributes/extensions")
    flags = integer(one(record, 70, "0"))
    if flags & ~68 or flags < 0 or integer(one(record, 62, "7")) <= 0 or integer(one(record, 290, "1")) != 1:
        raise ReviewRequired("DXF layer is off, frozen, nonplotting or externally dependent")
    if one(record, 6, "CONTINUOUS").upper() != "CONTINUOUS":
        raise ReviewRequired("DXF layer linetype requires path-intent review")


def line_chains(lines):
    """Join exact LINE endpoints within each layer; no tolerance or invented edge."""
    groups = defaultdict(list)
    for a, b, layer in lines:
        groups[layer].append((a, b))
    chains = []
    for edges in groups.values():
        graph = defaultdict(list)
        for index, (a, b) in enumerate(edges):
            graph[a].append(index)
            graph[b].append(index)
        remaining = set(range(len(edges)))
        while remaining:
            index = min(remaining)
            a, b = edges[index]
            start = a if len(graph[a]) != 2 else b if len(graph[b]) != 2 else a
            points, current = [start], start
            while index in remaining:
                remaining.remove(index)
                a, b = edges[index]
                current = b if current == a else a
                points.append(current)
                if current == start or len(graph[current]) != 2:
                    break
                available = [edge for edge in graph[current] if edge in remaining]
                if not available:
                    break
                index = available[0]
            closed = points[-1] == points[0]
            chains.append((points[:-1] if closed else points, closed))
    return chains


def inspect_dxf(data):
    result = {"status": "blocked", "sha256": None, "declared_unit": None, "unit_scale_mm": None,
              "geometry": None, "contours_mm": None, "bounds_mm": None, "dimensions_mm": None,
              "layers": [], "uninterpreted_sections": [], "blockers": [], "findings": [],
              "review_required": True, "execution_allowed": False,
              "limitations": ["restricted planar ASCII DXF subset, not full DXF conformance or rendering",
                              "INSUNITS is a declaration, not authenticated design scale",
                              "layer/path intent, kerf, source equivalence and manufacturing context unverified"]}
    if type(data) is not bytes or not data:
        result["blockers"], result["findings"] = ["MISSING_CONTEXT"], ["actual nonempty DXF bytes are required"]
        return result
    if len(data) > MAX_BYTES:
        result["blockers"], result["findings"] = ["SOURCE_VERIFICATION_REQUIRED"], ["DXF exceeds byte review limit"]
        return result
    result["sha256"] = hashlib.sha256(data).hexdigest()
    try:
        parts = sections(data)
        result["uninterpreted_sections"] = sorted(set(parts) - {"HEADER", "TABLES", "ENTITIES"})
        header = header_values(parts["HEADER"])
        unit = integer(one(header.get("$INSUNITS", []), 70))
        if unit not in UNITS:
            raise ReviewRequired("DXF INSUNITS is unspecified or outside supported mm/cm/inch units")
        result["declared_unit"], scale = UNITS[unit]
        result["unit_scale_mm"] = str(scale)
        layers = layer_table(parts["TABLES"])
        polygons, circles, lines, used = [], [], [], set()
        entities = records(parts["ENTITIES"])
        if not entities or len(entities) > MAX_SEGMENTS:
            raise ReviewRequired("DXF entity count is empty or exceeds review limit")
        common = {0, 5, 330, 100, 8, 6, 62, 60, 67, 410, 39, 210, 220, 230}
        allowed = {"LWPOLYLINE": {90, 70, 43, 38, 10, 20, 40, 41, 42, 91},
                   "CIRCLE": {10, 20, 30, 40}, "LINE": {10, 20, 30, 11, 21, 31}}
        for record in entities:
            kind = record[0][1]
            if kind not in allowed or {code for code, _ in record} - common - allowed[kind]:
                raise ReviewRequired("DXF contains unsupported entity or attribute semantics")
            subclasses = [value for code, value in record if code == 100]
            expected_class = {"LWPOLYLINE": "AcDbPolyline", "LINE": "AcDbLine", "CIRCLE": "AcDbCircle"}[kind]
            if subclasses and subclasses != ["AcDbEntity", expected_class]:
                raise ReviewRequired("DXF entity subclass semantics are unsupported")
            layer = one(record, 8).casefold()
            if layer not in layers:
                raise ValueError("entity refers to missing layer")
            check_layer(layers[layer])
            used.add(layer)
            if integer(one(record, 60, "0")) != 0 or integer(one(record, 67, "0")) != 0 or one(record, 410, "Model") != "Model":
                raise ReviewRequired("DXF hidden or paper-space geometry requires review")
            if one(record, 6, "BYLAYER").upper() not in ("BYLAYER", "CONTINUOUS") or not 1 <= integer(one(record, 62, "256")) <= 256:
                raise ReviewRequired("DXF entity appearance/path intent is unsupported")
            for code, expected in ((39, 0), (210, 0), (220, 0), (230, 1)):
                if number(one(record, code, str(expected))) != expected:
                    raise ReviewRequired("DXF nonplanar thickness/extrusion requires review")
            if kind == "LWPOLYLINE":
                if integer(one(record, 70, "0")) not in (0, 1):
                    raise ReviewRequired("unsupported polyline flags")
                if number(one(record, 38, "0")) != 0 or number(one(record, 43, "0")) != 0:
                    raise ReviewRequired("DXF polyline elevation/width requires review")
                points, vertex = [], None
                for code, value in record:
                    if code == 10:
                        if vertex is not None:
                            if 20 not in vertex:
                                raise ValueError("missing polyline y coordinate")
                            points.append((vertex[10]*scale, vertex[20]*scale))
                        vertex = {10: number(value)}
                    elif code in (20, 40, 41, 42, 91):
                        if vertex is None or code in vertex:
                            raise ValueError("misplaced or duplicate vertex tag")
                        vertex[code] = number(value) if code != 91 else integer(value)
                        if code in (40, 41, 42) and vertex[code] != 0:
                            raise ReviewRequired("DXF polyline bulge/variable width requires review")
                if vertex is None or 20 not in vertex:
                    raise ValueError("incomplete polyline")
                points.append((vertex[10]*scale, vertex[20]*scale))
                if len(points) != integer(one(record, 90)) or len(points) < 2:
                    raise ValueError("polyline vertex count mismatch")
                closed = integer(one(record, 70, "0")) == 1
                if points[-1] == points[0]:
                    points, closed = points[:-1], True
                polygons.append((points, closed))
            else:
                if number(one(record, 30, "0")) != 0 or kind == "LINE" and number(one(record, 31, "0")) != 0:
                    raise ReviewRequired("DXF nonzero Z requires planar review")
                a = (number(one(record, 10))*scale, number(one(record, 20))*scale)
                if kind == "CIRCLE":
                    radius = number(one(record, 40))*scale
                    if radius <= 0:
                        raise ValueError("nonpositive circle radius")
                    circles.append((a, radius))
                else:
                    b = (number(one(record, 11))*scale, number(one(record, 21))*scale)
                    lines.append((a, b, layer))
            if sum(len(p) for p, _ in polygons)+len(circles)+len(lines) > MAX_SEGMENTS:
                raise ReviewRequired("DXF geometry exceeds review limit")
        polygons.extend(line_chains(lines))
        geometry, bounds = contour_review(polygons, circles)
        result.update(geometry=geometry, bounds_mm=bounds, layers=sorted(used),
                      contours_mm=[{"kind": "polyline", "closed": closed, "points": [list(map(str, p)) for p in pts]} for pts, closed in polygons] +
                                  [{"kind": "circle", "center": list(map(str, center)), "radius": str(radius)} for center, radius in circles],
                      dimensions_mm={axis: str(Fraction(bounds["max"][i])-Fraction(bounds["min"][i])) for i, axis in enumerate("xy")})
        for key, value in geometry.items():
            if key not in ("contours", "segments", "circles") and value:
                result["blockers"].append("MISSING_CONTEXT")
                result["findings"].append(f"{key}: {value}")
    except ReviewRequired as error:
        result["blockers"].append("SOURCE_VERIFICATION_REQUIRED")
        result["findings"].append(str(error).replace("SVG", "DXF"))
    except (ValueError, UnicodeError, OverflowError):
        result["blockers"].append("MISSING_CONTEXT")
        result["findings"].append("DXF is malformed, incomplete or has invalid planar geometry/numbers")
    result["blockers"] = sorted(set(result["blockers"]))
    result["status"] = "blocked" if result["blockers"] else "checked_partial_geometry"
    return result
