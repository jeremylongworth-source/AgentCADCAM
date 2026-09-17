"""Synthetic, offline 3MF package mutations; no external model or slicer needed."""

import copy
from fractions import Fraction
import hashlib
from io import BytesIO
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings
from zipfile import ZIP_BZIP2, ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

from scripts.additive_preflight import load_contexts, preflight
from scripts.three_mf_review import CORE, MODEL_TYPE, RELS, REL_TYPE, START, TYPES, UNITS, inspect_3mf


ROOT = Path(__file__).resolve().parents[2]
MESH = ('<mesh><vertices><vertex x="0" y="0" z="0"/><vertex x="1" y="0" z="0"/>'
        '<vertex x="0" y="1" z="0"/><vertex x="0" y="0" z="1"/></vertices><triangles>'
        '<triangle v1="0" v2="2" v3="1"/><triangle v1="0" v2="1" v3="3"/>'
        '<triangle v1="0" v2="3" v3="2"/><triangle v1="1" v2="2" v3="3"/>'
        '</triangles></mesh>')


def model(resources=None, build='<item objectid="1"/>', attributes='', mesh=MESH):
    resources = f'<object id="1">{mesh}</object>' if resources is None else resources
    return (f'<model xmlns="{CORE}" {attributes}><resources>{resources}</resources>'
            f'<build>{build}</build></model>')


def package(xml=None, *, target="/3D/model.model", model_name="3D/model.model", extra=None,
            relationships=None, content_types=None, compression=ZIP_DEFLATED):
    parts = {
        "[Content_Types].xml": content_types or (
            f'<Types xmlns="{TYPES}"><Default Extension="rels" ContentType="{REL_TYPE}"/>'
            f'<Default Extension="model" ContentType="{MODEL_TYPE}"/>'
            '<Default Extension="txt" ContentType="text/plain"/></Types>'),
        "_rels/.rels": relationships or (
            f'<Relationships xmlns="{RELS}"><Relationship Id="r1" Type="{START}" Target="{target}"/>'
            '</Relationships>'),
        model_name: model() if xml is None else xml,
    }
    parts.update(extra or {})
    data = BytesIO()
    with ZipFile(data, "w", compression=compression) as archive:
        for name, content in parts.items():
            info = ZipInfo(name, (2026, 9, 17, 0, 0, 0))
            info.create_system = 0
            info.external_attr = 0o600 << 16
            info.compress_type = compression
            archive.writestr(info, content)
    return data.getvalue()


def retained_cases():
    """Stored ZIP avoids compressor-version drift in the retained byte identities."""
    return {
        "positive": package(compression=ZIP_STORED),
        "missing-face": package(model(mesh=MESH.replace('<triangle v1="1" v2="2" v3="3"/>', '')),
                                compression=ZIP_STORED),
        "translated-outside": package(model(build='<item objectid="1" transform="1 0 0 0 1 0 0 0 1 200 0 0"/>'),
                                      compression=ZIP_STORED),
        "conflicting-inch-unit": package(model(attributes='unit="inch"'), compression=ZIP_STORED),
    }


class ThreeMfReviewTests(unittest.TestCase):
    def test_exponents_beyond_decimal_implementation_range_are_structured_refusals(self):
        for number in ("1e999999999999999999999999", "1e-999999999999999999999999"):
            for xml in (model(mesh=MESH.replace('x="1"', f'x="{number}"', 1)),
                        model(build=f'<item objectid="1" transform="1 0 0 0 1 0 0 0 1 {number} 0 0"/>')):
                with self.subTest(number=number, transform="transform" in xml):
                    self.assert_blocked(package(xml), "SOURCE_VERIFICATION_REQUIRED")

    def assert_blocked(self, data, blocker=None):
        result = inspect_3mf(data)
        self.assertEqual(result["status"], "blocked", result)
        self.assertTrue(result["review_required"])
        self.assertFalse(result["execution_allowed"])
        if blocker:
            self.assertIn(blocker, result["blockers"], result)
        json.dumps(result, allow_nan=False)
        return result

    def test_basic_package_uses_root_relationship_not_assumed_filename(self):
        for name in ("3D/model.model", "Shapes/custom.model"):
            data = package(model_name=name, target="/" + name)
            result = inspect_3mf(data)
            self.assertEqual(result["blockers"], [])
            self.assertEqual(result["status"], "checked_partial_geometry")
            self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(result["model_part"], name)
            self.assertEqual(result["dimensions_exact"], dict(x="1", y="1", z="1"))
            self.assertEqual(result["triangles"], 4)
            self.assertEqual(result["objects"][0]["topology"]["boundary_edges"], 0)
            self.assertFalse(result["execution_allowed"])

    def test_all_core_units_and_default_origin_are_preserved(self):
        for unit, factor in UNITS.items():
            result = inspect_3mf(package(model(attributes=f'unit="{unit}"')))
            self.assertEqual(result["blockers"], [])
            self.assertEqual(result["unit_scale_mm"], str(factor))
            self.assertEqual(result["unit_origin"], "explicit")
        result = inspect_3mf(package())
        self.assertEqual((result["unit"], result["unit_origin"]), ("millimeter", "core_default"))
        self.assert_blocked(package(model(attributes='unit="parsec"')), "MISSING_CONTEXT")

    def test_build_translation_rotation_and_scaling_are_applied_in_row_order(self):
        result = inspect_3mf(package(model(build='<item objectid="1" transform="0 2 0 -3 0 0 0 0 4 10 20 30"/>')))
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["bounds_exact"], {"min": ["7", "20", "30"], "max": ["10", "22", "34"]})
        self.assertEqual(result["dimensions_exact"], dict(x="3", y="2", z="4"))

    def test_component_transform_precedes_parent_build_transform(self):
        resources = (f'<object id="1">{MESH}</object><object id="2"><components>'
                     '<component objectid="1" transform="1 0 0 0 1 0 0 0 1 2 0 0"/>'
                     '</components></object>')
        result = inspect_3mf(package(model(resources, '<item objectid="2" transform="2 0 0 0 3 0 0 0 4 10 0 0"/>')))
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["bounds_exact"], {"min": ["14", "0", "0"], "max": ["16", "3", "4"]})

    def test_reflection_preserves_partial_solid_evidence_without_repair(self):
        result = inspect_3mf(package(model(build='<item objectid="1" transform="-1 0 0 0 1 0 0 0 1 1 0 0"/>')))
        self.assertEqual(result["blockers"], [])
        self.assertTrue(result["objects"][0]["topology"]["signed_volume_positive"])
        self.assertEqual(result["bounds_exact"], {"min": ["0", "0", "0"], "max": ["1", "1", "1"]})

    def test_unreferenced_objects_do_not_enlarge_build_but_are_inspected(self):
        resources = f'<object id="1">{MESH}</object><object id="2">{MESH.replace("1\"", "90\"", 1)}</object>'
        result = inspect_3mf(package(model(resources)))
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["dimensions_exact"]["x"], "1")
        self.assertEqual(len(result["objects"]), 2)

    def test_repeated_instances_contribute_all_transformed_extents(self):
        build = '<item objectid="1"/><item objectid="1" transform="1 0 0 0 1 0 0 0 1 10 0 0"/>'
        result = inspect_3mf(package(model(build=build)))
        self.assertEqual(result["blockers"], [])
        self.assertEqual((result["instances"], result["triangles"]), (2, 8))
        self.assertEqual(result["dimensions_exact"]["x"], "11")
        overlap = inspect_3mf(package(model(build='<item objectid="1"/><item objectid="1"/>')))
        self.assertIn("SOURCE_VERIFICATION_REQUIRED", overlap["blockers"])

    def test_decimal_precision_survives_without_stl_float_conversion(self):
        xml = model(mesh=MESH.replace('x="1"', 'x="1.00000000000000000001"'))
        result = inspect_3mf(package(xml))
        self.assertEqual(result["blockers"], [])
        self.assertEqual(Fraction(result["dimensions_exact"]["x"]), Fraction("1.00000000000000000001"))

    def test_open_duplicate_reversed_and_degenerate_geometry_are_file_derived(self):
        mutations = [MESH.replace('<triangle v1="1" v2="2" v3="3"/>', ''),
                     MESH.replace('</triangles>', '<triangle v1="0" v2="2" v3="1"/></triangles>'),
                     MESH.replace('v1="0" v2="2" v3="1"', 'v1="0" v2="1" v3="2"'),
                     MESH.replace('x="1"', 'x="0"')]
        for mesh in mutations:
            with self.subTest(mesh=mesh):
                result = self.assert_blocked(package(model(mesh=mesh)), "MISSING_CONTEXT")
                self.assertTrue(result["objects"])

    def test_bad_indices_ids_and_references_block(self):
        cases = [model(mesh=MESH.replace('v1="0"', 'v1="9"')),
                 model(mesh=MESH.replace('v1="0"', 'v1="2"')),
                 model(mesh=MESH.replace('v1="0"', 'v1="-1"')),
                 model(build='<item objectid="2"/>'), model(build=''),
                 model(f'<object id="1">{MESH}</object><object id="1">{MESH}</object>'),
                 model('<object id="1"><components><component objectid="1"/></components></object>'),
                 model('<object id="1"><components><component objectid="2"/></components></object>'
                       f'<object id="2">{MESH}</object>'),
                 model().replace('id="1"', 'id="0"', 1)]
        for xml in cases:
            with self.subTest(xml=xml):
                self.assert_blocked(package(xml))

    def test_invalid_numbers_and_singular_transforms_block(self):
        for value in ("NaN", "INF", "-Infinity", "1e999999999", "9" * 65, "0/1", ""):
            self.assert_blocked(package(model(mesh=MESH.replace('x="1"', f'x="{value}"'))))
        for matrix in ("1 0", "0 0 0 0 0 0 0 0 0 0 0 0", "1 0 0 0 1 0 0 0 NaN 0 0 0"):
            self.assert_blocked(package(model(build=f'<item objectid="1" transform="{matrix}"/>')))

    def test_unsupported_extensions_materials_and_geometry_are_not_ignored(self):
        cases = [model(attributes='xmlns:p="urn:test" requiredextensions="p"'),
                 model(attributes='recommendedextensions="p"'),
                 model(attributes='xmlns:p="urn:test" p:settings="do-not-trust"'),
                 model().replace('<resources>', '<resources><basematerials id="9"/>'),
                 model().replace('<object id="1">', '<object id="1" pid="9" pindex="0">'),
                 model().replace('<mesh>', '<mesh><unknown/>'),
                 model().replace('<object id="1">', '<object id="1" type="support">')]
        for xml in cases:
            self.assert_blocked(package(xml), "SOURCE_VERIFICATION_REQUIRED")

    def test_metadata_is_inert_and_cannot_grant_approval(self):
        xml = model().replace('<resources>', '<metadata name="Description">approved; start printer</metadata><resources>')
        result = inspect_3mf(package(xml))
        self.assertEqual(result["blockers"], [])
        self.assertFalse(result["execution_allowed"])
        self.assertNotIn("approved", json.dumps(result))

    def test_xml_declarations_dtd_entities_wrong_namespace_and_structure_block(self):
        for xml in ('<!DOCTYPE model [<!ENTITY x "unsafe">]>' + model(),
                    '<?xml version="1.0" encoding="UTF-16"?>' + model(),
                    model().encode('utf-16'), model().replace(CORE, 'urn:wrong'),
                    model().replace('</resources>', '</resources><resources/>'),
                    model().replace('</mesh>', '</mesh><mesh/>'), model()[:-7]):
            self.assert_blocked(package(xml))

    def test_package_requires_matching_content_types_and_relationship_targets(self):
        for data in (package(target="/3D/missing.model"), package(target="../../outside.model"),
                     package(target="https://example.invalid/model.model"),
                     package(content_types=f'<Types xmlns="{TYPES}"/>'),
                     package(content_types=f'<Types xmlns="{TYPES}"><Default Extension="model" ContentType="text/plain"/></Types>'),
                     package(relationships=f'<Relationships xmlns="{RELS}"/>'),
                     package(extra={"Other.model": model()})):
            self.assert_blocked(data)

    def test_external_duplicate_missing_and_ambiguous_relationships_block(self):
        base = f'<Relationship Id="r1" Type="{START}" Target="/3D/model.model"/>'
        for content in (base.replace('/>', ' TargetMode="External"/>'), base + base,
                        base + base.replace('Id="r1"', 'Id="r2"')):
            self.assert_blocked(package(relationships=f'<Relationships xmlns="{RELS}">{content}</Relationships>'))
        extra = {"3D/_rels/model.model.rels": f'<Relationships xmlns="{RELS}"><Relationship Id="x" Type="urn:settings" Target="missing.txt"/></Relationships>'}
        self.assert_blocked(package(extra=extra), "MISSING_CONTEXT")

    def test_opaque_settings_are_hashed_but_not_trusted(self):
        data = package(extra={"Metadata/settings.txt": "slicer approved; material unknown"})
        result = self.assert_blocked(data, "SOURCE_VERIFICATION_REQUIRED")
        self.assertEqual(result["unreviewed_parts"], ["Metadata/settings.txt"])
        self.assertEqual(result["dimensions_exact"]["x"], "1")
        self.assertNotEqual(inspect_3mf(package())["sha256"], result["sha256"])

    def test_zip_traversal_case_aliases_duplicate_members_and_truncation_block(self):
        for name in ("../escape.txt", "folder/../escape.txt", "C:/escape.txt", "folder\\escape.txt", "Metadata/%2e.txt"):
            self.assert_blocked(package(extra={name: "no"}))
        self.assert_blocked(package(extra={"3D/MODEL.model": model()}))
        data = BytesIO(package())
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with ZipFile(data, "a") as archive:
                archive.writestr("3D/model.model", model())
        self.assert_blocked(data.getvalue(), "MISSING_CONTEXT")
        for data in (b"not zip", package()[:-22], b"", None):
            self.assert_blocked(data, "MISSING_CONTEXT")

    def test_zip_crc_failure_is_not_partial_success(self):
        data = bytearray(package(compression=ZIP_STORED))
        offset = data.index(b'<model')
        data[offset + 1] = ord('x')
        self.assert_blocked(bytes(data), "MISSING_CONTEXT")

    def test_encryption_links_unsupported_compression_and_bombs_block(self):
        data = bytearray(package())
        central = data.index(b'PK\x01\x02')
        struct.pack_into('<H', data, central + 8, struct.unpack_from('<H', data, central + 8)[0] | 1)
        self.assert_blocked(bytes(data), "SOURCE_VERIFICATION_REQUIRED")
        data = BytesIO(package())
        with ZipFile(data, "a") as archive:
            info = ZipInfo("link.txt")
            info.create_system = 3
            info.external_attr = 0o120777 << 16
            archive.writestr(info, "outside.txt")
        self.assert_blocked(data.getvalue(), "SOURCE_VERIFICATION_REQUIRED")
        self.assert_blocked(package(compression=ZIP_BZIP2), "SOURCE_VERIFICATION_REQUIRED")
        self.assert_blocked(package(extra={"bomb.txt": "0" * 2_000_000}), "SOURCE_VERIFICATION_REQUIRED")

    def test_xml_depth_and_transformed_numeric_growth_are_bounded(self):
        self.assert_blocked(package('<a>' * 65 + '</a>' * 65), "SOURCE_VERIFICATION_REQUIRED")
        resources = f'<object id="1">{MESH}</object>'
        for i in range(2, 16):
            resources += (f'<object id="{i}"><components><component objectid="{i-1}" '
                          'transform="1e100 0 0 0 1 0 0 0 1 0 0 0"/></components></object>')
        self.assert_blocked(package(model(resources, '<item objectid="15"/>')), "SOURCE_VERIFICATION_REQUIRED")

    def test_size_node_depth_and_expansion_limits_fail_closed(self):
        for constant, value in (("MAX_BYTES", 10), ("MAX_MEMBERS", 2), ("MAX_EXPANDED_BYTES", 10),
                                ("MAX_XML_BYTES", 10), ("MAX_NODES", 3), ("MAX_TRIANGLES", 3),
                                ("MAX_OBJECTS", 0), ("MAX_INSTANCES", 0)):
            with patch("scripts.three_mf_review." + constant, value):
                result = self.assert_blocked(package(), "SOURCE_VERIFICATION_REQUIRED")
                if constant == "MAX_BYTES":
                    self.assertIsNone(result["sha256"])
        resources = f'<object id="1">{MESH}</object>'
        for i in range(2, 28):
            resources += f'<object id="{i}"><components><component objectid="{i-1}"/></components></object>'
        self.assert_blocked(package(model(resources, '<item objectid="27"/>')), "SOURCE_VERIFICATION_REQUIRED")
        with patch("scripts.three_mf_review.MAX_TRIANGLES", 7):
            self.assert_blocked(package(model(build='<item objectid="1"/><item objectid="1"/>')), "SOURCE_VERIFICATION_REQUIRED")


class ThreeMfPreflightTests(unittest.TestCase):
    def setUp(self):
        self.contexts = load_contexts(ROOT / "fixtures/additive/fdm-bracket/contexts")
        self.contexts["job"].update(mesh_format="3MF", model_dimensions=dict(x=1, y=1, z=1))

    def review(self, data=None, identify=True):
        data = package() if data is None else data
        if identify:
            self.contexts["job"]["mesh_sha256"] = hashlib.sha256(data).hexdigest()
        return preflight(**self.contexts, mesh_bytes=data, source_revision="A")

    def test_positive_requires_human_review_and_never_mutates_context(self):
        self.contexts["job"]["mesh_sha256"] = hashlib.sha256(package()).hexdigest()
        before = copy.deepcopy(self.contexts)
        result = self.review(identify=False)
        self.assertEqual(result["blockers"], ["HUMAN_APPROVAL_REQUIRED"])
        self.assertEqual(self.contexts, before)
        self.assertFalse(result["execution_allowed"])
        self.assertTrue(result["review_required"])

    def test_retained_observations_replay_against_actual_package_bytes(self):
        report = json.loads((ROOT / "fixtures/additive/fdm-bracket/expected/3mf-observations.json").read_text(encoding="utf-8"))
        for name, data in retained_cases().items():
            with self.subTest(case=name):
                result = self.review(data)
                expected = report["cases"][name]
                self.assertEqual({key: result[key] for key in expected}, expected)

    def test_embedded_units_cannot_be_overridden_by_metadata(self):
        self.contexts["printer"]["capabilities"]["build_volume"] = dict(x=10, y=10, z=10)
        result = self.review(package(model(attributes='unit="inch"')))
        self.assertIn("MISSING_CONTEXT", result["blockers"])
        self.assertIn("MACHINE_CONTEXT_REQUIRED", result["blockers"])

    def test_exact_unit_conversion_and_boundary(self):
        self.contexts["job"]["mesh_units"] = "inch"
        self.contexts["printer"]["capabilities"]["build_volume"] = dict(x=25.4, y=25.4, z=25.4)
        self.assertEqual(self.review(package(model(attributes='unit="inch"')))["blockers"], ["HUMAN_APPROVAL_REQUIRED"])
        self.contexts["printer"]["capabilities"]["build_volume"]["x"] = 25.399999
        self.assertIn("MACHINE_CONTEXT_REQUIRED", self.review(package(model(attributes='unit="inch"')))["blockers"])

    def test_translated_small_model_outside_envelope_cannot_pass_extent_only_check(self):
        for offset in ("-1", "200", "199.00000000000000000001"):
            data = package(model(build=f'<item objectid="1" transform="1 0 0 0 1 0 0 0 1 {offset} 0 0"/>'))
            result = self.review(data)
            self.assertEqual(result["file_review"]["dimensions_exact"]["x"], "1")
            self.assertIn("MACHINE_CONTEXT_REQUIRED", result["blockers"])
        data = package(model(build='<item objectid="1" transform="1 0 0 0 1 0 0 0 1 199 0 0"/>'))
        self.assertEqual(self.review(data)["blockers"], ["HUMAN_APPROVAL_REQUIRED"])

    def test_changed_settings_identity_and_open_mesh_cannot_be_hidden_by_labels(self):
        self.review()
        result = self.review(package(extra={"settings.txt": "changed"}), identify=False)
        self.assertIn("SOURCE_VERIFICATION_REQUIRED", result["blockers"])
        self.assertTrue(any("mesh_sha256" in finding for finding in result["findings"]))
        data = package(model(mesh=MESH.replace('<triangle v1="1" v2="2" v3="3"/>', '')))
        self.assertIn("MISSING_CONTEXT", self.review(data)["blockers"])

    def test_cli_reads_package_bytes_with_explicit_context_and_never_executes(self):
        data = package()
        self.contexts["job"]["mesh_sha256"] = hashlib.sha256(data).hexdigest()
        with tempfile.TemporaryDirectory(prefix="3mf-review-test-") as temporary:
            root = Path(temporary)
            mesh = root / "model.3mf"
            mesh.write_bytes(data)
            for name, context in self.contexts.items():
                (root / f"{name}.json").write_text(json.dumps(context), encoding="utf-8")
            for entry in (["scripts/additive_preflight.py"], ["-m", "scripts.additive_preflight"]):
                run = subprocess.run([sys.executable, *entry, str(root / "job.json"), "--mesh", str(mesh),
                                      "--source-revision", "A"], cwd=ROOT, capture_output=True, text=True, timeout=30)
                self.assertEqual(run.returncode, 1, run.stderr)
                result = json.loads(run.stdout)
                self.assertEqual(result["blockers"], ["HUMAN_APPROVAL_REQUIRED"])
                self.assertEqual(result["file_review"]["sha256"], hashlib.sha256(data).hexdigest())
                self.assertFalse(result["execution_allowed"])


if __name__ == "__main__":
    unittest.main()
