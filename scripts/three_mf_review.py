"""Bounded, read-only 3MF Core geometry evidence, not conformance or print approval."""

from decimal import Decimal
from fractions import Fraction
import hashlib
from io import BytesIO
import posixpath
import re
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZIP_DEFLATED, ZIP_STORED, ZipFile
import zlib

if __package__:
    from .stl_mesh_review import MAX_BYTES, MAX_TRIANGLES, mesh_topology
else:
    from stl_mesh_review import MAX_BYTES, MAX_TRIANGLES, mesh_topology


CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
RELS = "http://schemas.openxmlformats.org/package/2006/relationships"
TYPES = "http://schemas.openxmlformats.org/package/2006/content-types"
START = "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"
MODEL_TYPE = "application/vnd.ms-package.3dmanufacturing-3dmodel+xml"
REL_TYPE = "application/vnd.openxmlformats-package.relationships+xml"
UNITS = {"micron": Fraction(1, 1000), "millimeter": Fraction(1), "centimeter": Fraction(10),
         "inch": Fraction(127, 5), "foot": Fraction(1524, 5), "meter": Fraction(1000)}
IDENTITY = tuple(Fraction(v) for v in (1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0))
MAX_MEMBERS = 256
MAX_EXPANDED_BYTES = 32 * 1024 * 1024
MAX_XML_BYTES = 16 * 1024 * 1024
MAX_NODES = 400_000
MAX_OBJECTS = 1024
MAX_INSTANCES = 1024
MAX_DEPTH = 24
NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")


class ReviewRequired(ValueError):
    """Supported review scope/resource limit exceeded, not necessarily invalid 3MF."""


def _number(value):
    if not isinstance(value, str) or len(value) > 64 or not NUMBER.fullmatch(value.strip()):
        raise ValueError("invalid or over-precision 3MF numeric value")
    decimal = Decimal(value.strip())
    if abs(decimal.as_tuple().exponent) > 100 or abs(decimal.adjusted()) > 100:
        raise ReviewRequired("3MF number exceeds the exact arithmetic review range")
    return Fraction(decimal)


def _index(value, minimum=0):
    if not isinstance(value, str) or not re.fullmatch(r"\+?[0-9]{1,10}", value.strip()):
        raise ValueError("3MF resource identity/index is missing or invalid")
    result = int(value)
    if not minimum <= result < 2**31:
        raise ValueError("3MF resource identity/index is out of range")
    return result


def _xml(data):
    if len(data) > MAX_XML_BYTES:
        raise ReviewRequired("3MF XML exceeds the byte review limit")
    text = data.decode("utf-8-sig")
    # Decode first: UTF-16 and NUL-interleaved declaration tricks cannot bypass this.
    if "\x00" in text or re.search(r"<!\s*(?:DOCTYPE|ENTITY)", text, re.I):
        raise ValueError("3MF XML DTD/entity declarations are prohibited")
    declaration = re.match(r"<\?xml\s+.*?\?>", text, re.S)
    if declaration:
        encoding = re.search(r"encoding\s*=\s*['\"]([^'\"]+)", declaration[0])
        if encoding and encoding[1].lower() != "utf-8":
            raise ValueError("3MF XML must declare UTF-8")
    depth = count = 0
    root = None
    for event, node in ET.iterparse(BytesIO(text.encode("utf-8")), events=("start", "end")):
        if event == "start":
            root = node if root is None else root
            depth += 1
            count += 1
            if depth > 64 or count > MAX_NODES:
                raise ReviewRequired("3MF XML exceeds node/depth review limits")
        else:
            depth -= 1
    return root


def _shape(node, tag, attributes=(), children=(), required=(), namespace=CORE, text=False):
    if node.tag != f"{{{namespace}}}{tag}":
        raise ValueError("3MF XML root or element namespace is unexpected")
    if set(node.attrib) - set(attributes):
        raise ReviewRequired("3MF element contains unsupported attributes/extensions")
    if not set(required) <= set(node.attrib):
        raise ValueError("3MF element lacks required attributes")
    if any(child.tag not in {f"{{{namespace}}}{name}" for name in children} for child in node):
        raise ReviewRequired("3MF element contains unsupported children/extensions")
    if (not text and node.text and node.text.strip()) or any(child.tail and child.tail.strip() for child in node):
        raise ValueError("3MF element contains unexpected text")


def _part_name(name):
    # Deliberately restricted unescaped ASCII subset, never a filesystem path.
    if (not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_./\[\]-]+", name)
            or name.startswith("/") or any(p in ("", ".", "..") for p in name.split("/"))):
        raise ReviewRequired("3MF package has an unsupported or unsafe part name")
    return name


def _target(source, target):
    if not target or not re.fullmatch(r"/?[A-Za-z0-9_./\[\]-]+", target):
        raise ReviewRequired("3MF relationship target is external, escaped or unsupported")
    name = posixpath.normpath(target.lstrip("/") if target.startswith("/") else
                             posixpath.join(posixpath.dirname(source), target))
    return _part_name(name)


def _package(data):
    parts = {}
    with ZipFile(BytesIO(data)) as archive:
        members = archive.infolist()
        if len(members) > MAX_MEMBERS or sum(m.file_size for m in members) > MAX_EXPANDED_BYTES:
            raise ReviewRequired("3MF archive exceeds member/expanded-byte review limits")
        seen = set()
        for member in members:
            name = _part_name(member.orig_filename.rstrip("/") if member.is_dir() else member.orig_filename)
            if name.casefold() in seen:
                raise ValueError("3MF archive has duplicate or case-ambiguous parts")
            seen.add(name.casefold())
            if (member.flag_bits & 1 or member.compress_type not in (ZIP_STORED, ZIP_DEFLATED)
                    or (member.external_attr >> 16) & 0o170000 == 0o120000):
                raise ReviewRequired("3MF archive encryption, compression or link entry is unsupported")
            if member.file_size > MAX_XML_BYTES or member.file_size > max(1, member.compress_size) * 1000:
                raise ReviewRequired("3MF archive part exceeds size/compression-ratio review limits")
            if not member.is_dir():
                # Bounded read also verifies CRC. Nothing is extracted or executed.
                with archive.open(member) as stream:
                    content = stream.read(MAX_XML_BYTES + 1)
                if len(content) != member.file_size:
                    raise ValueError("3MF archive part length does not match its directory")
                parts[name] = content
    if "[Content_Types].xml" not in parts or "_rels/.rels" not in parts:
        raise ValueError("3MF package requires content types and root relationships")
    types = _xml(parts["[Content_Types].xml"])
    _shape(types, "Types", children=("Default", "Override"), namespace=TYPES)
    defaults, overrides = {}, {}
    for node in types:
        override = node.tag == f"{{{TYPES}}}Override"
        key = "PartName" if override else "Extension"
        _shape(node, "Override" if override else "Default", (key, "ContentType"),
               required=(key, "ContentType"), namespace=TYPES)
        value = node.get(key)
        if override and not value.startswith("/"):
            raise ValueError("3MF content type override must use an absolute part name")
        value = _part_name(value[1:]) if override else value.lower()
        table = overrides if override else defaults
        if not value or value in table or not node.get("ContentType"):
            raise ValueError("3MF content type declaration is empty or duplicated")
        table[value] = node.get("ContentType")
    if any(name not in parts for name in overrides):
        raise ValueError("3MF content type override refers to a missing part")
    content_types = {name: overrides.get(name, defaults.get(name.rsplit(".", 1)[-1].lower()))
                     for name in parts if name != "[Content_Types].xml"}
    if any(value is None for value in content_types.values()):
        raise ValueError("3MF part lacks a content type")
    starts = []
    for name, content in parts.items():
        if not name.endswith(".rels"):
            continue
        if content_types[name] != REL_TYPE:
            raise ValueError("3MF relationship part has the wrong content type")
        if name == "_rels/.rels":
            source = ""
        else:
            directory, leaf = posixpath.split(name)
            if posixpath.basename(directory) != "_rels":
                raise ValueError("3MF relationship part is misplaced")
            source = posixpath.join(posixpath.dirname(directory), leaf[:-5])
            if source not in parts:
                raise ValueError("3MF relationship source part is missing")
        relationships = _xml(content)
        _shape(relationships, "Relationships", children=("Relationship",), namespace=RELS)
        ids, pairs = set(), set()
        for node in relationships:
            _shape(node, "Relationship", ("Id", "Type", "Target", "TargetMode"),
                   required=("Id", "Type", "Target"), namespace=RELS)
            if node.get("TargetMode", "Internal") != "Internal":
                raise ReviewRequired("3MF external relationships are not followed")
            target = _target(source, node.get("Target"))
            pair = (node.get("Type"), target)
            if not node.get("Id") or node.get("Id") in ids or pair in pairs or target not in parts:
                raise ValueError("3MF relationship is duplicated or its target is missing")
            ids.add(node.get("Id"))
            pairs.add(pair)
            if node.get("Type") == START:
                if source:
                    raise ReviewRequired("3MF multi-model relationships require extension review")
                starts.append(target)
    if len(starts) != 1 or content_types[starts[0]] != MODEL_TYPE:
        raise ValueError("3MF requires exactly one model start part with the model content type")
    models = [name for name, kind in content_types.items() if kind == MODEL_TYPE]
    if models != starts:
        raise ReviewRequired("3MF additional model parts require multi-part extension review")
    return parts, starts[0]


def _transform(value):
    if value is None:
        return IDENTITY
    fields = value.split()
    if len(fields) != 12:
        raise ValueError("3MF transform requires twelve row-major values")
    matrix = tuple(_number(field) for field in fields)
    a, b, c, d, e, f, g, h, i = matrix[:9]
    if a * (e*i - f*h) - b * (d*i - f*g) + c * (d*h - e*g) == 0:
        raise ValueError("3MF singular transform requires geometric review")
    return matrix


def _point(point, matrix):
    result = tuple(sum(point[row] * matrix[row * 3 + axis] for row in range(3)) + matrix[9 + axis]
                   for axis in range(3))
    if any(max(value.numerator.bit_length(), value.denominator.bit_length()) > 4096 for value in result):
        raise ReviewRequired("3MF transformed coordinates exceed the arithmetic review limit")
    return result


def _metadata(node):
    _shape(node, "metadata", ("name", "preserve", "type"), required=("name",), text=True)
    if node.get("preserve", "0") not in ("0", "1", "true", "false"):
        raise ValueError("3MF metadata preserve flag is invalid")


def _model(root, result):
    _shape(root, "model", ("unit", "requiredextensions", "recommendedextensions",
                           "{http://www.w3.org/XML/1998/namespace}lang"), ("metadata", "resources", "build"))
    if root.get("requiredextensions", "").strip() or root.get("recommendedextensions", "").strip():
        raise ReviewRequired("3MF required/recommended extensions need an explicit supported adapter")
    unit = root.get("unit", "millimeter")
    if unit not in UNITS:
        raise ValueError("3MF model declares an unknown length unit")
    result.update(unit=unit, unit_origin="explicit" if "unit" in root.attrib else "core_default",
                  unit_scale_mm=str(UNITS[unit]))
    children = list(root)
    while children and children[0].tag == f"{{{CORE}}}metadata":
        _metadata(children.pop(0))
    if [node.tag for node in children] != [f"{{{CORE}}}resources", f"{{{CORE}}}build"]:
        raise ValueError("3MF model requires ordered resources and build sections")
    resources, build = children
    _shape(resources, "resources", children=("object",))
    _shape(build, "build", children=("item",))
    if not 0 < len(resources) <= MAX_OBJECTS or not 0 < len(build) <= MAX_INSTANCES:
        raise ReviewRequired("3MF resource/build count is empty or exceeds review limits")
    objects = {}
    total_triangles = 0
    for obj in resources:
        _shape(obj, "object", ("id", "type", "name", "partnumber"), ("mesh", "components"), required=("id",))
        identity = _index(obj.get("id"), 1)
        if identity in objects:
            raise ValueError("3MF resource IDs must be unique")
        if obj.get("type", "model") != "model":
            raise ReviewRequired("3MF non-model object types require support/assembly review")
        if len(obj) != 1:
            raise ValueError("3MF object requires one mesh or components definition")
        geometry = obj[0]
        if geometry.tag == f"{{{CORE}}}components":
            _shape(geometry, "components", children=("component",))
            components = []
            if not 0 < len(geometry) <= MAX_INSTANCES:
                raise ReviewRequired("3MF component count is empty or exceeds review limits")
            for component in geometry:
                _shape(component, "component", ("objectid", "transform"), required=("objectid",))
                reference = _index(component.get("objectid"), 1)
                if reference not in objects:
                    raise ValueError("3MF component must reference an earlier object; dangling/cyclic reference")
                components.append((reference, _transform(component.get("transform"))))
            objects[identity] = {"components": components}
            continue
        _shape(geometry, "mesh", children=("vertices", "triangles"))
        if [node.tag for node in geometry] != [f"{{{CORE}}}vertices", f"{{{CORE}}}triangles"]:
            raise ValueError("3MF mesh requires ordered vertices and triangles")
        vertices_node, triangles_node = geometry
        _shape(vertices_node, "vertices", children=("vertex",))
        _shape(triangles_node, "triangles", children=("triangle",))
        total_triangles += len(triangles_node)
        if not 0 < len(vertices_node) <= MAX_TRIANGLES * 3 or not 0 < len(triangles_node) or total_triangles > MAX_TRIANGLES:
            raise ReviewRequired("3MF mesh is empty or exceeds vertex/triangle review limits")
        vertices = []
        for vertex in vertices_node:
            _shape(vertex, "vertex", ("x", "y", "z"), required=("x", "y", "z"))
            vertices.append(tuple(_number(vertex.get(axis)) for axis in "xyz"))
        triangles = []
        used = set()
        for triangle in triangles_node:
            _shape(triangle, "triangle", ("v1", "v2", "v3"), required=("v1", "v2", "v3"))
            indices = tuple(_index(triangle.get(key)) for key in ("v1", "v2", "v3"))
            if len(set(indices)) != 3 or max(indices) >= len(vertices):
                raise ValueError("3MF triangle indices are repeated or out of range")
            used.update(indices)
            triangles.append(tuple(vertices[index] for index in indices))
        topology = mesh_topology([((0, 0, 0), triangle) for triangle in triangles])
        result["objects"].append({"object_id": identity, "triangles": len(triangles), "topology": topology})
        if any(count for name, count in topology.items() if name not in ("shells", "signed_volume_positive")) or not topology["signed_volume_positive"]:
            result["blockers"].append("MISSING_CONTEXT")
            result["findings"].append(f"3MF object {identity} has partial-topology defects")
        if topology["shells"] != 1:
            result["blockers"].append("SOURCE_VERIFICATION_REQUIRED")
            result["findings"].append(f"3MF object {identity} requires multi-shell/fill-rule review")
        objects[identity] = {"vertices": [vertices[index] for index in sorted(used)], "triangles": len(triangles)}
    expanded_triangles = 0
    instances = []

    def expand(identity, transforms):
        nonlocal expanded_triangles
        if len(transforms) > MAX_DEPTH:
            raise ReviewRequired("3MF component expansion exceeds depth review limit")
        obj = objects[identity]
        if "components" in obj:
            for reference, matrix in obj["components"]:
                expand(reference, (matrix, *transforms))
            return
        expanded_triangles += obj["triangles"]
        if expanded_triangles > MAX_TRIANGLES or len(instances) >= MAX_INSTANCES:
            raise ReviewRequired("3MF expanded build exceeds triangle/instance review limits")
        points = []
        for point in obj["vertices"]:
            for matrix in transforms:
                point = _point(point, matrix)
            points.append(point)
        low = tuple(min(point[axis] for point in points) for axis in range(3))
        high = tuple(max(point[axis] for point in points) for axis in range(3))
        instances.append((low, high))

    for item in build:
        _shape(item, "item", ("objectid", "transform", "partnumber"), required=("objectid",))
        identity = _index(item.get("objectid"), 1)
        if identity not in objects:
            raise ValueError("3MF build refers to a missing object")
        expand(identity, (_transform(item.get("transform")),))
    low = tuple(min(bounds[0][axis] for bounds in instances) for axis in range(3))
    high = tuple(max(bounds[1][axis] for bounds in instances) for axis in range(3))
    result.update(triangles=expanded_triangles, build_items=len(build), instances=len(instances),
                  bounds_exact={"min": list(map(str, low)), "max": list(map(str, high))},
                  dimensions_exact={axis: str(high[i] - low[i]) for i, axis in enumerate("xyz")})
    # Overlapping envelopes are not proof of intersection, but cannot establish
    # assembly clearance or Core positive-fill union semantics either.
    if any(all(min(a[1][axis], b[1][axis]) > max(a[0][axis], b[0][axis]) for axis in range(3))
           for i, a in enumerate(instances) for b in instances[i + 1:]):
        result["blockers"].append("SOURCE_VERIFICATION_REQUIRED")
        result["findings"].append("3MF instance envelopes overlap; intersection/fill-rule review required")


def inspect_3mf(data):
    """Inspect supplied package bytes; never extract, repair, fetch or run settings."""
    result = {"status": "blocked", "sha256": None, "encoding": "3mf_zip", "model_part": None,
              "unit": None, "unit_origin": None, "unit_scale_mm": None,
              "triangles": 0, "objects": [], "build_items": 0, "instances": 0,
              "bounds_exact": None, "dimensions_exact": None, "unreviewed_parts": [],
              "blockers": [], "findings": [], "review_required": True, "execution_allowed": False,
              "limitations": ["self-intersections not checked", "not full OPC/XSD conformance validation",
                              "no manufacturing or design-equivalence verification",
                              "no vendor settings, materials, signatures or extensions authenticated",
                              "no tolerance-based vertex welding or geometric union"]}
    if type(data) is not bytes or not data:
        result["blockers"] = ["MISSING_CONTEXT"]
        result["findings"] = ["actual nonempty 3MF package bytes are required"]
        return result
    if len(data) > MAX_BYTES:
        result["blockers"] = ["SOURCE_VERIFICATION_REQUIRED"]
        result["findings"] = ["3MF exceeds the byte review limit"]
        return result
    result["sha256"] = hashlib.sha256(data).hexdigest()
    try:
        parts, model = _package(data)
        result["model_part"] = model
        result["unreviewed_parts"] = sorted(name for name in parts if name not in
                                            (model, "[Content_Types].xml") and not name.endswith(".rels"))
        if result["unreviewed_parts"]:
            result["blockers"].append("SOURCE_VERIFICATION_REQUIRED")
            result["findings"].append("3MF auxiliary parts/settings require separate review; not executed or trusted")
        _model(_xml(parts[model]), result)
    except ReviewRequired as error:
        result["blockers"].append("SOURCE_VERIFICATION_REQUIRED")
        result["findings"].append(str(error))
    except (ValueError, BadZipFile, UnicodeError, ET.ParseError, OSError, RuntimeError, zlib.error):
        result["blockers"].append("MISSING_CONTEXT")
        # Do not echo raw parser exceptions containing arbitrary embedded content.
        result["findings"].append("3MF package/model is malformed, incomplete or has invalid references/numbers")
    result["blockers"] = sorted(set(result["blockers"]))
    result["status"] = "blocked" if result["blockers"] else "checked_partial_geometry"
    return result
