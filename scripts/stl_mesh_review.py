"""Bounded, read-only STL topology evidence; not proof of printability."""

from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import math
import re
import struct


MAX_BYTES = 16 * 1024 * 1024
MAX_TRIANGLES = 100_000
NUMBER = r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?"
VECTOR = rf"({NUMBER})\s+({NUMBER})\s+({NUMBER})"
FACET = re.compile(rf"facet\s+normal\s+{VECTOR}\s+outer\s+loop\s+"
                   rf"vertex\s+{VECTOR}\s+vertex\s+{VECTOR}\s+vertex\s+{VECTOR}"
                   r"\s+endloop\s+endfacet\s*", re.ASCII)


def _facets(data):
    if len(data) >= 84:
        count = struct.unpack_from("<I", data, 80)[0]
        if 84 + count * 50 == len(data):
            if not 0 < count <= MAX_TRIANGLES:
                raise ValueError("binary STL facet count is empty or exceeds the review limit")
            facets = []
            for offset in range(84, len(data), 50):
                row = struct.unpack_from("<12fH", data, offset)
                if row[-1] != 0:
                    raise ValueError("binary STL attribute/color extension is unsupported")
                facets.append((row[:3], (row[3:6], row[6:9], row[9:12])))
            return "binary", facets
    try:
        text = data.decode("ascii")
    except UnicodeError as error:
        raise ValueError("STL is neither an exact binary envelope nor supported ASCII") from error
    lines = text.strip().splitlines()
    if len(lines) < 2 or not re.fullmatch(r"solid(?:[ \t]+[^\r\n]*)?", lines[0]):
        raise ValueError("ASCII STL requires a solid header")
    if not re.fullmatch(r"endsolid(?:[ \t]+[^\r\n]*)?", lines[-1]):
        raise ValueError("ASCII STL requires an endsolid footer")
    if lines[0][5:].strip() != lines[-1][8:].strip():
        raise ValueError("ASCII STL solid names conflict")
    body, position, facets = "\n".join(lines[1:-1]).strip(), 0, []
    while position < len(body):
        match = FACET.match(body, position)
        if match is None:
            raise ValueError("ASCII STL contains malformed or unsupported facet structure")
        row = tuple(float(value) for value in match.groups())
        facets.append((row[:3], (row[3:6], row[6:9], row[9:12])))
        if len(facets) > MAX_TRIANGLES:
            raise ValueError("ASCII STL exceeds the facet review limit")
        position = match.end()
    if not facets:
        raise ValueError("ASCII STL contains no facets")
    return "ascii", facets


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _connected(graph):
    unseen, groups = set(graph), 0
    while unseen:
        groups += 1
        pending = [unseen.pop()]
        while pending:
            for neighbor in graph[pending.pop()]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    pending.append(neighbor)
    return groups


def inspect_stl(data):
    """Inspect supplied bytes without paths, repair, welding tolerance or execution.

    Vertex coordinates must match exactly. Rational arithmetic avoids floating
    underflow/overflow in degeneracy, orientation and signed-volume decisions.
    Self-intersections and nested/disjoint-shell semantics remain unverified.
    """
    result = {"status": "blocked", "sha256": None, "encoding": None,
              "triangles": 0, "bounds": None, "dimensions": None, "dimensions_exact": None, "topology": None,
              "blockers": [], "findings": [], "review_required": True, "execution_allowed": False,
              "limitations": ["self-intersections not checked", "no manufacturing or design-equivalence verification",
                              "STL has no authoritative unit or revision", "no tolerance-based vertex welding"]}
    if type(data) is not bytes or not data:
        result["blockers"] = ["MISSING_CONTEXT"]
        result["findings"] = ["actual nonempty STL bytes are required"]
        return result
    if len(data) > MAX_BYTES:
        result["blockers"] = ["SOURCE_VERIFICATION_REQUIRED"]
        result["findings"] = ["STL exceeds the byte review limit"]
        return result
    result["sha256"] = hashlib.sha256(data).hexdigest()
    try:
        encoding, facets = _facets(data)
        if any(not math.isfinite(value) for normal, triangle in facets for vector in (normal, *triangle) for value in vector):
            raise ValueError("STL contains nonfinite normals or vertices")
        vertices = {point for _, triangle in facets for point in triangle}
        low = [min(point[axis] for point in vertices) for axis in range(3)]
        high = [max(point[axis] for point in vertices) for axis in range(3)]
        dimensions = [high[axis] - low[axis] for axis in range(3)]
        if not all(math.isfinite(value) for value in dimensions):
            raise ValueError("STL dimensions exceed the numeric report range")
    except (ValueError, OverflowError) as error:
        result["blockers"] = ["MISSING_CONTEXT"]
        result["findings"] = [str(error)]
        return result
    result.update(encoding=encoding, triangles=len(facets), bounds={"min": low, "max": high},
                  dimensions=dict(zip("xyz", dimensions)),
                  dimensions_exact={axis: str(Fraction(high[i]) - Fraction(low[i])) for i, axis in enumerate("xyz")})
    exact = {point: tuple(Fraction(value) for value in point) for point in vertices}
    edges, faces, links = defaultdict(list), Counter(), defaultdict(list)
    degenerate = normal_conflicts = 0
    signed_six_volume = Fraction(0)
    for index, (normal, triangle) in enumerate(facets):
        faces[tuple(sorted(triangle))] += 1
        a, b, c = (exact[point] for point in triangle)
        cross = _cross(tuple(b[i] - a[i] for i in range(3)), tuple(c[i] - a[i] for i in range(3)))
        if not any(cross):
            degenerate += 1
        if sum(Fraction(normal[i]) * cross[i] for i in range(3)) < 0:
            normal_conflicts += 1
        origin_cross = _cross(b, c)
        signed_six_volume += sum(a[i] * origin_cross[i] for i in range(3))
        for start, end in ((0, 1), (1, 2), (2, 0)):
            u, v = triangle[start], triangle[end]
            edges[tuple(sorted((u, v)))].append((index, u, v))
        for center, left, right in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
            links[triangle[center]].append((triangle[left], triangle[right]))
    fan_defects = 0
    for pairs in links.values():
        graph = defaultdict(list)
        for u, v in pairs:
            graph[u].append(v)
            graph[v].append(u)
        if any(len(neighbors) != 2 for neighbors in graph.values()) or _connected(graph) != 1:
            fan_defects += 1
    face_graph = {index: set() for index in range(len(facets))}
    for uses in edges.values():
        # Star connectivity avoids quadratic work for a heavily reused edge.
        first = uses[0][0]
        for index, _, _ in uses[1:]:
            face_graph[first].add(index)
            face_graph[index].add(first)
    topology = {
        "boundary_edges": sum(len(uses) == 1 for uses in edges.values()),
        "nonmanifold_edges": sum(len(uses) > 2 for uses in edges.values()),
        "winding_conflicts": sum(len(uses) == 2 and uses[0][1:] == uses[1][1:] for uses in edges.values()),
        "nonmanifold_vertices": fan_defects, "duplicate_faces": sum(count - 1 for count in faces.values()),
        "degenerate_faces": degenerate, "normal_conflicts": normal_conflicts,
        "shells": _connected(face_graph), "signed_volume_positive": signed_six_volume > 0,
    }
    result["topology"] = topology
    for name, count in topology.items():
        if name not in ("shells", "signed_volume_positive") and count:
            result["findings"].append(f"{name}: {count}")
            result["blockers"].append("MISSING_CONTEXT")
    if not topology["signed_volume_positive"]:
        result["findings"].append("nonpositive signed volume requires orientation/solid review")
        result["blockers"].append("MISSING_CONTEXT")
    if topology["shells"] != 1:
        result["findings"].append("multiple shells require containment/intersection and assembly review")
        result["blockers"].append("SOURCE_VERIFICATION_REQUIRED")
    result["blockers"] = sorted(set(result["blockers"]))
    result["status"] = "blocked" if result["blockers"] else "checked_partial_geometry"
    return result
