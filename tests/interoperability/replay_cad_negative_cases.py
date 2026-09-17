"""Reproduce fixed synthetic inputs for retained reviews; never run an agent.

Only private temporary copies are changed. CLI prints evidence, writes no retained
records, and never executes CAD source, external tools, or machine commands.
"""

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import yaml

from scripts.cad_handoff_checks import review_bundle, review_fixture
from scripts.validate_cad_fixture_mesh import validate as validate_mesh


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures/cad/bracket"
CASES = ("revision-mismatch", "missing-units", "stale-derived-file", "stl-treated-as-design-master", "conflicting-dimensions")


def replay(case):
    if case not in CASES:
        raise ValueError("unknown fixed CAD case")
    bundle = yaml.safe_load((FIXTURE / "fixture.yaml").read_text(encoding="utf-8"))
    metadata = json.loads((FIXTURE / "metadata/revision.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="cad-negative-review-") as directory:
        root = Path(directory) / "bracket"
        if case == "stl-treated-as-design-master":
            (root / "source").mkdir(parents=True)
            (root / "metadata").mkdir()
            shutil.copyfile(FIXTURE / "source/bracket.stl", root / "source/bracket.stl")
            mesh = next(item for item in bundle["artifacts"] if item["path"] == "source/bracket.stl")
            mesh["authority"] = "authoritative"  # Deliberately wrong submitted claim.
            bundle["artifacts"] = [mesh]
            bundle["authoritative_artifact"] = mesh["path"]
            bundle["step_artifact"] = {"status": "not_supplied"}
            metadata["authoritative_artifact"] = mesh["path"]
        else:
            shutil.copytree(FIXTURE, root)
        def replace(path, before, after):
            target = root / path
            text = target.read_text(encoding="utf-8")
            if text.count(before) != 1:
                raise ValueError("fixture mutation anchor changed")
            target.write_text(text.replace(before, after), encoding="utf-8", newline="\n")
        if case == "revision-mismatch":
            replace("source/bracket.svg", "revision A", "revision B")
            replace("source/bracket.svg", "REV A", "REV B")
            next(item for item in bundle["artifacts"] if item["path"] == "source/bracket.svg")["revision"] = "B"
        elif case == "missing-units":
            next(item for item in bundle["artifacts"] if item["path"] == "source/bracket.stl")["units"] = None
            metadata["units"] = None
            path = root / "metadata/derivation.json"
            binding = json.loads(path.read_text(encoding="utf-8"))
            next(item["artifact"] for item in binding["derivatives"] if item["artifact"]["path"] == "source/bracket.stl")["units"] = None
            path.write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8", newline="\n")
        elif case == "stale-derived-file":
            replace("source/bracket.scad", "hole_diameter = 6;", "hole_diameter = 8;")
        elif case == "conflicting-dimensions":
            replace("source/bracket.svg", "BASE: 60 x 40 x 6", "BASE: 61 x 40 x 6")
        (root / "fixture.yaml").write_text(yaml.safe_dump(bundle, sort_keys=False), encoding="utf-8", newline="\n")
        (root / "metadata/revision.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n")
        if case == "stl-treated-as-design-master":
            bundle["metadata"] = metadata
            report = review_bundle(bundle, root)
            mesh_errors = validate_mesh(root / "source/bracket.stl")
            report["file_checks"] = [{"check": "stl_envelope", "paths": ["source/bracket.stl"],
                                      "status": "failed" if mesh_errors else "passed", "findings": mesh_errors}]
        else:
            report = review_fixture(root)
        inventory = []
        for item in bundle["artifacts"]:
            if not item["path"].startswith("source/"):
                continue
            inventory.append({**item, "sha256": hashlib.sha256((root / item["path"]).read_bytes()).hexdigest(),
                              "locator": f"replay:{case}/{item['path']}"})
        text_inputs = {}
        for path in ("source/bracket.scad", "source/bracket.svg"):
            if (root / path).is_file():
                text_inputs[path] = (root / path).read_text(encoding="utf-8")
        return {"case": case, "inventory": inventory, "metadata": metadata,
                "submitted_bundle": bundle,
                "submitted_binding": json.loads((root / "metadata/derivation.json").read_text(encoding="utf-8")) if (root / "metadata/derivation.json").is_file() else None,
                "text_inputs": text_inputs, "tool_result": report}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=(*CASES, "all"))
    args = parser.parse_args()
    results = [replay(case) for case in CASES] if args.case == "all" else [replay(args.case)]
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
