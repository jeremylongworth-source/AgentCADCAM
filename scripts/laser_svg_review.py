"""Bounded SVG contour evidence in millimetres; never render, repair or lase."""

from collections import Counter
from decimal import Decimal
from fractions import Fraction
import hashlib
from io import BytesIO
from math import isqrt
import re
import xml.etree.ElementTree as ET


SVG = "http://www.w3.org/2000/svg"
MAX_BYTES = 2 * 1024 * 1024
MAX_NODES = 4096
MAX_SEGMENTS = 1024
NUMBER = r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?"
TOKEN = re.compile(NUMBER + r"|[A-Za-z]")
IDENTITY = tuple(Fraction(v) for v in (1, 0, 0, 1, 0, 0))
LENGTHS = {"mm": Fraction(1), "cm": Fraction(10), "in": Fraction(127, 5)}


class ReviewRequired(ValueError):
    """Unsupported semantics/resource bounds, not necessarily invalid SVG."""


def number(value):
    if not isinstance(value, str) or len(value) > 64 or not re.fullmatch(NUMBER, value.strip()):
        raise ValueError("invalid numeric value")
    exponent = re.search(r"[eE]([+-]?[0-9]+)$", value.strip())
    if exponent and abs(int(exponent[1])) > 40:
        raise ReviewRequired("SVG numeric range requires further review")
    value = Decimal(value.strip())
    if abs(value.as_tuple().exponent) > 40 or abs(value.adjusted()) > 40:
        raise ReviewRequired("SVG numeric range requires further review")
    return Fraction(value)


def numbers(value):
    if not isinstance(value, str):
        raise ValueError("missing numeric list")
    # Deliberately strict separator subset; never scrape numbers out of text.
    if not re.fullmatch(rf"\s*{NUMBER}(?:(?:\s*,\s*|\s+){NUMBER})*\s*", value):
        raise ValueError("invalid numeric list")
    matches = list(re.finditer(NUMBER, value))
    if len(matches) > 2*MAX_SEGMENTS:
        raise ReviewRequired("SVG numeric list exceeds review limit")
    return [number(match[0]) for match in matches]


def length(value):
    match = re.fullmatch(rf"\s*({NUMBER})(mm|cm|in)\s*", value or "")
    if not match:
        raise ReviewRequired("SVG viewport requires explicit mm, cm or in lengths")
    result = number(match[1]) * LENGTHS[match[2]]
    if result <= 0:
        raise ValueError("nonpositive viewport")
    return result, match[2]


def compose(parent, child):
    a, b, c, d, e, f = parent
    g, h, i, j, k, l = child
    result = (a*g+c*h, b*g+d*h, a*i+c*j, b*i+d*j, a*k+c*l+e, b*k+d*l+f)
    if any(max(v.numerator.bit_length(), v.denominator.bit_length()) > 1024 for v in result):
        raise ReviewRequired("SVG transform arithmetic exceeds review limit")
    return result


def point(p, matrix):
    a, b, c, d, e, f = matrix
    return (a*p[0] + c*p[1] + e, b*p[0] + d*p[1] + f)


def transform(value):
    result, offset = IDENTITY, 0
    if value is None:
        return result
    for index, match in enumerate(re.finditer(r"([A-Za-z]+)\s*\(([^()]*)\)", value)):
        if index >= 64:
            raise ReviewRequired("SVG transform list exceeds review limit")
        gap = value[offset:match.start()]
        if not re.fullmatch(r"\s*" if index == 0 else r"\s*,?\s*", gap):
            raise ValueError("invalid transform list")
        kind, v = match[1], numbers(match[2])
        if kind == "matrix" and len(v) == 6:
            matrix = tuple(v)
        elif kind == "translate" and len(v) in (1, 2):
            matrix = (1, 0, 0, 1, v[0], v[1] if len(v) == 2 else 0)
        elif kind == "scale" and len(v) in (1, 2):
            matrix = (v[0], 0, 0, v[-1], 0, 0)
        elif kind == "rotate" and len(v) in (1, 3) and v[0] % 90 == 0:
            cosine, sine = ((1, 0), (0, 1), (-1, 0), (0, -1))[int(v[0] / 90) % 4]
            matrix = (cosine, sine, -sine, cosine, 0, 0)
            if len(v) == 3:
                matrix = compose((1, 0, 0, 1, v[1], v[2]), compose(matrix, (1, 0, 0, 1, -v[1], -v[2])))
        else:
            raise ReviewRequired("unsupported SVG transform; no approximate conversion applied")
        if matrix[0]*matrix[3] - matrix[1]*matrix[2] == 0:
            raise ValueError("singular transform")
        result = compose(result, matrix)
        offset = match.end()
    if not offset or value[offset:].strip():
        raise ValueError("invalid transform list")
    return result


def viewport(root):
    width, wu = length(root.get("width"))
    height, hu = length(root.get("height"))
    box = numbers(root.get("viewBox"))
    if len(box) != 4 or box[2] <= 0 or box[3] <= 0:
        raise ValueError("invalid viewBox")
    x, y, w, h = box
    sx, sy = width/w, height/h
    aspect = root.get("preserveAspectRatio", "xMidYMid meet").split()
    if aspect == ["none"]:
        tx, ty = -x*sx, -y*sy
    else:
        if not aspect or not re.fullmatch(r"x(Min|Mid|Max)Y(Min|Mid|Max)", aspect[0]):
            raise ReviewRequired("unsupported SVG aspect ratio")
        if len(aspect) > 2 or len(aspect) == 2 and aspect[1] != "meet":
            raise ReviewRequired("SVG slice/clipping requires further review")
        sx = sy = min(sx, sy)
        align = re.fullmatch(r"x(Min|Mid|Max)Y(Min|Mid|Max)", aspect[0])
        fraction = {"Min": 0, "Mid": Fraction(1, 2), "Max": 1}
        tx = -x*sx + (width-w*sx)*fraction[align[1]]
        ty = -y*sy + (height-h*sy)*fraction[align[2]]
    return (sx, 0, 0, sy, tx, ty), {"width_mm": str(width), "height_mm": str(height),
        "declared_width_unit": wu, "declared_height_unit": hu,
        "view_box": list(map(str, box)), "scale_mm_per_user_unit": [str(sx), str(sy)]}


def path_contours(value):
    tokens, offset = [], 0
    for match in TOKEN.finditer(value or ""):
        gap = (value or "")[offset:match.start()]
        between_numbers = tokens and not tokens[-1].isalpha() and not match[0].isalpha()
        if not re.fullmatch(r"\s*,?\s*" if between_numbers else r"\s*", gap):
            raise ValueError("invalid path token")
        tokens.append(match[0])
        if len(tokens) > 4*MAX_SEGMENTS:
            raise ReviewRequired("SVG path exceeds token review limit")
        offset = match.end()
    if not tokens or value[offset:].strip():
        raise ValueError("empty or malformed path")
    if any(t.isalpha() and t not in "MmLlHhVvZz" for t in tokens):
        raise ReviewRequired("SVG curved/unsupported path commands require further review")
    contours, points, current, command, i = [], [], (Fraction(0), Fraction(0)), None, 0
    while i < len(tokens):
        if tokens[i].isalpha():
            command, i = tokens[i], i + 1
            if command in "Zz":
                if not points:
                    raise ValueError("close without subpath")
                contours.append((points, True))
                current, points, command = points[0], [], None
                continue
            if i == len(tokens) or tokens[i].isalpha():
                raise ValueError("path command lacks arguments")
        if command is None:
            raise ValueError("path command missing")
        count = 2 if command in "MmLl" else 1
        if i + count > len(tokens) or any(t.isalpha() for t in tokens[i:i+count]):
            raise ValueError("path command lacks arguments")
        values = list(map(number, tokens[i:i+count]))
        i += count
        if command in "MmLl":
            target = tuple(values)
            if command.islower():
                target = tuple(a+b for a, b in zip(current, target))
        elif command in "Hh":
            target = (values[0] + (current[0] if command == "h" else 0), current[1])
        else:
            target = (current[0], values[0] + (current[1] if command == "v" else 0))
        if command in "Mm":
            if points:
                contours.append((points, False))
            points = [target]
            command = "l" if command == "m" else "L"
        else:
            if not points:
                raise ValueError("path must begin each subpath with moveto in supported subset")
            points.append(target)
        current = target
        if sum(len(p) for p, _ in contours) + len(points) > MAX_SEGMENTS:
            raise ReviewRequired("SVG path exceeds segment review limit")
    if points:
        contours.append((points, False))
    return contours


def cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def on_segment(a, b, p):
    return cross(a, b, p) == 0 and all(min(a[i], b[i]) <= p[i] <= max(a[i], b[i]) for i in (0, 1))


def intersects(a, b, c, d):
    u, v, w, x = cross(a, b, c), cross(a, b, d), cross(c, d, a), cross(c, d, b)
    return (u*v < 0 and w*x < 0) or any((on_segment(a, b, c), on_segment(a, b, d), on_segment(c, d, a), on_segment(c, d, b)))


def contour_review(polygons, circles):
    segments, bounds, opens, degenerates = [], [], 0, 0
    for index, (points, closed) in enumerate(polygons):
        if len(points) > 1 and points[-1] == points[0]:
            points, closed = points[:-1], True
        opens += not closed
        pairs = list(zip(points, points[1:] + points[:1] if closed else points[1:]))
        if len(points) < 3 or closed and sum(a[0]*b[1]-a[1]*b[0] for a, b in pairs) == 0:
            degenerates += 1
        degenerates += sum(a == b for a, b in pairs)
        segments.extend((a, b, index, edge, len(pairs), closed) for edge, (a, b) in enumerate(pairs))
        bounds.extend(points)
    if len(segments) + len(circles) > MAX_SEGMENTS:
        raise ReviewRequired("SVG exceeds combined contour review limit")
    duplicate_segments = sum(n-1 for n in Counter(tuple(sorted((s[0], s[1]))) for s in segments).values())
    duplicate_circles = sum(n-1 for n in Counter(circles).values())
    intersections = 0
    for i, (a, b, group, edge, count, closed) in enumerate(segments):
        for c, d, other, other_edge, _, _ in segments[i+1:]:
            if tuple(sorted((a, b))) == tuple(sorted((c, d))):
                continue  # Already reported as duplicate geometry.
            adjacent = group == other and (other_edge == edge+1 or closed and edge == 0 and other_edge == count-1)
            if adjacent and cross(a, b, c) == 0 and cross(a, b, d) == 0:
                shared = set((a, b)) & set((c, d))
                if shared and not any(on_segment(a, b, p) for p in (c, d) if p not in shared) and not any(on_segment(c, d, p) for p in (a, b) if p not in shared):
                    continue
            elif adjacent:
                continue
            if intersects(a, b, c, d):
                intersections += 1
        for center, radius in circles:
            delta = (b[0]-a[0], b[1]-a[1])
            square = sum(v*v for v in delta)
            t = max(0, min(1, sum((center[j]-a[j])*delta[j] for j in (0, 1))/square)) if square else 0
            distance = sum((a[j]+t*delta[j]-center[j])**2 for j in (0, 1))
            farthest = max(sum((p[j]-center[j])**2 for j in (0, 1)) for p in (a, b))
            intersections += distance <= radius**2 <= farthest
    for i, (center, radius) in enumerate(circles):
        bounds.extend([(center[0]-radius, center[1]-radius), (center[0]+radius, center[1]+radius)])
        for other, r in circles[i+1:]:
            if (center, radius) == (other, r):
                continue
            distance = sum((center[j]-other[j])**2 for j in (0, 1))
            intersections += (radius-r)**2 <= distance <= (radius+r)**2
    if not bounds:
        raise ValueError("no geometry")
    low = [min(p[i] for p in bounds) for i in (0, 1)]
    high = [max(p[i] for p in bounds) for i in (0, 1)]
    return {"contours": len(polygons)+len(circles), "segments": len(segments), "circles": len(circles),
            "open_contours": opens, "degenerate_contours_or_edges": degenerates,
            "duplicate_segments": duplicate_segments, "duplicate_circles": duplicate_circles,
            "intersections_or_touches": intersections}, {"min": list(map(str, low)), "max": list(map(str, high))}


def inspect_svg(data):
    result = {"status": "blocked", "sha256": None, "viewport": None, "bounds_mm": None, "contours_mm": None,
              "dimensions_mm": None, "geometry": None, "blockers": [], "findings": [],
              "review_required": True, "execution_allowed": False,
              "limitations": ["restricted SVG contour subset, not rendering or full SVG conformance",
                              "stroke/kerf, path intent, material, machine and process are unverified",
                              "no source equivalence or manufacturing approval"]}
    if type(data) is not bytes or not data:
        result["blockers"], result["findings"] = ["MISSING_CONTEXT"], ["actual nonempty SVG bytes are required"]
        return result
    if len(data) > MAX_BYTES:
        result["blockers"], result["findings"] = ["SOURCE_VERIFICATION_REQUIRED"], ["SVG exceeds byte review limit"]
        return result
    result["sha256"] = hashlib.sha256(data).hexdigest()
    try:
        text = data.decode("utf-8-sig")
        if "\x00" in text or re.search(r"<!\s*(?:DOCTYPE|ENTITY)|<\?(?!xml\s)", text, re.I):
            raise ReviewRequired("SVG declarations/entities/processing instructions are unsupported")
        declaration = re.match(r"<\?xml\s+.*?\?>", text, re.S)
        if declaration and re.search(r"encoding\s*=\s*['\"](?!UTF-8['\"])", declaration[0], re.I):
            raise ReviewRequired("SVG XML must use UTF-8")
        root, depth, count = None, 0, 0
        for event, node in ET.iterparse(BytesIO(text.encode("utf-8")), events=("start", "end")):
            if event == "start":
                root = node if root is None else root
                count, depth = count+1, depth+1
                if count > MAX_NODES or depth > 32:
                    raise ReviewRequired("SVG exceeds node/depth review limit")
            else:
                depth -= 1
        if root.tag != f"{{{SVG}}}svg":
            raise ValueError("wrong root namespace")
        matrix, result["viewport"] = viewport(root)
        polygons, circles = [], []
        attrs = {"svg": {"width", "height", "viewBox", "preserveAspectRatio", "version"}, "g": set(),
                 "rect": {"x", "y", "width", "height"}, "circle": {"cx", "cy", "r"},
                 "polygon": {"points"}, "polyline": {"points"}, "line": {"x1", "y1", "x2", "y2"},
                 "path": {"d"}, "title": set(), "desc": set()}

        def visit(node, parent, fill="black", stroke="none"):
            kind = node.tag.removeprefix(f"{{{SVG}}}")
            if kind not in attrs or node.tag != f"{{{SVG}}}{kind}" or kind == "svg" and node is not root:
                raise ReviewRequired("SVG contains unsupported elements or nested viewports")
            allowed = attrs[kind] | {"id", "fill", "stroke", "stroke-width", "transform"}
            if set(node.attrib) - allowed:
                raise ReviewRequired("SVG contains unsupported attributes, styling or external references")
            if node is root and "transform" in node.attrib:
                raise ReviewRequired("SVG root transform requires outer-viewport review")
            if kind in ("title", "desc"):
                if len(node) or set(node.attrib) - {"id"}:
                    raise ReviewRequired("unsupported SVG description structure")
                return
            if (node.text and node.text.strip()) or any(child.tail and child.tail.strip() for child in node):
                raise ValueError("unexpected SVG text")
            matrix = compose(parent, transform(node.get("transform")))
            fill, stroke = node.get("fill", fill), node.get("stroke", stroke)
            if fill != "none" or not re.fullmatch(r"none|black|white|red|green|blue|yellow|cyan|magenta|gray|grey|orange|#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?", stroke):
                # A group's fill may be overridden by children; geometry cannot.
                if kind not in ("svg", "g"):
                    raise ReviewRequired("SVG fill/paint semantics require path-intent review")
            if "stroke-width" in node.attrib and number(node.get("stroke-width")) <= 0:
                raise ReviewRequired("SVG nonpositive stroke visibility requires review")
            if kind in ("svg", "g"):
                for child in node:
                    visit(child, matrix, fill, stroke)
                return
            if len(node) or stroke == "none":
                raise ReviewRequired("SVG hidden/child-bearing geometry requires review")
            get = lambda key, default="0": number(node.get(key, default))
            if kind == "circle":
                radius = get("r")
                a, b, c, d, _, _ = matrix
                scale2 = a*a+b*b
                if scale2 != c*c+d*d or a*c+b*d != 0:
                    raise ReviewRequired("SVG circle becomes ellipse under transform")
                n, den = isqrt(scale2.numerator), isqrt(scale2.denominator)
                if n*n != scale2.numerator or den*den != scale2.denominator:
                    raise ReviewRequired("SVG circle scale requires irrational arithmetic review")
                if radius <= 0:
                    raise ValueError("nonpositive circle")
                circles.append((point((get("cx"), get("cy")), matrix), radius*Fraction(n, den)))
            else:
                if kind == "rect":
                    x, y, w, h = get("x"), get("y"), get("width"), get("height")
                    if w <= 0 or h <= 0:
                        raise ValueError("nonpositive rectangle")
                    shapes = [([(x, y), (x+w, y), (x+w, y+h), (x, y+h)], True)]
                elif kind == "line":
                    shapes = [([(get("x1"), get("y1")), (get("x2"), get("y2"))], False)]
                elif kind in ("polyline", "polygon"):
                    v = numbers(node.get("points"))
                    if len(v) % 2 or len(v) < 4:
                        raise ValueError("invalid point pairs")
                    shapes = [(list(zip(v[::2], v[1::2])), kind == "polygon")]
                else:
                    shapes = path_contours(node.get("d"))
                for pts, closed in shapes:
                    measured = [point(p, matrix) for p in pts]
                    if len(measured) > 1 and measured[-1] == measured[0]:
                        measured, closed = measured[:-1], True
                    polygons.append((measured, closed))
            if sum(len(pts) for pts, _ in polygons) + len(circles) > MAX_SEGMENTS:
                raise ReviewRequired("SVG exceeds combined contour review limit")

        visit(root, matrix)
        geometry, bounds = contour_review(polygons, circles)
        result.update(geometry=geometry, bounds_mm=bounds,
                      contours_mm=[{"kind": "polyline", "closed": closed, "points": [list(map(str, p)) for p in pts]}
                                   for pts, closed in polygons] +
                                  [{"kind": "circle", "center": list(map(str, center)), "radius": str(radius)} for center, radius in circles],
                      dimensions_mm={axis: str(Fraction(bounds["max"][i])-Fraction(bounds["min"][i])) for i, axis in enumerate("xy")})
        for key, value in geometry.items():
            if key not in ("contours", "segments", "circles") and value:
                result["blockers"].append("MISSING_CONTEXT")
                result["findings"].append(f"{key}: {value}")
        width, height = (Fraction(result["viewport"][key]) for key in ("width_mm", "height_mm"))
        if any(Fraction(bounds["min"][i]) < 0 or Fraction(bounds["max"][i]) > limit for i, limit in enumerate((width, height))):
            result["blockers"].append("SOURCE_VERIFICATION_REQUIRED")
            result["findings"].append("geometry extends outside SVG viewport; clipping/placement review required")
    except ReviewRequired as error:
        result["blockers"].append("SOURCE_VERIFICATION_REQUIRED")
        result["findings"].append(str(error))
    except (ValueError, UnicodeError, ET.ParseError, OverflowError):
        result["blockers"].append("MISSING_CONTEXT")
        result["findings"].append("SVG is malformed, empty or has invalid geometry/numbers")
    result["blockers"] = sorted(set(result["blockers"]))
    result["status"] = "blocked" if result["blockers"] else "checked_partial_geometry"
    return result
