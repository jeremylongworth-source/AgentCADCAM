"""Opt-in pinned Windows PrusaSlicer geometry experiment; no slicing or printing.

Only repository-authored open fixtures and fixed geometry actions are accepted.
Runtime, inputs, profiles and outputs never become manufacturing-approved.
"""

import argparse
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
from zipfile import BadZipFile, ZipFile

from scripts.additive_preflight import load_contexts, preflight
from scripts.stl_mesh_review import inspect_stl
from scripts.three_mf_review import inspect_3mf
from tests.safety.test_three_mf_review import MESH, model, package, ZIP_STORED


ROOT = Path(__file__).resolve().parents[2]
PIN = ROOT / "constraints/prusaslicer-win64.json"
SOURCE = ROOT / "fixtures/cad/bracket/source/bracket.stl"
CASES = ("bracket-stl", "bracket-open-stl", "tetra-3mf", "tetra-inch-3mf",
         "tetra-translated-3mf", "tetra-open-3mf", "tetra-required-extension-3mf")
MAX_OUTPUT = 16 * 1024 * 1024


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def runtime_identity(runtime):
    """Pin the complete extracted tree, including resources, not just the launcher."""
    entries, binaries = [], {}
    for path in sorted(runtime.rglob("*"), key=lambda item: item.relative_to(runtime).as_posix()):
        if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
            raise ValueError("linked runtime entries are not allowed")
        if not path.is_file():
            continue
        name = path.relative_to(runtime).as_posix()
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        entries.append(f"{name}\0{digest}\n")
        if path.suffix.lower() in (".exe", ".dll"):
            binaries[name] = digest
    return {"tree_sha256": sha256("".join(entries).encode("utf-8")), "file_count": len(entries), "binaries": binaries}


def verify_runtime(runtime):
    pin = json.loads(PIN.read_text(encoding="utf-8"))
    if runtime_identity(runtime) != pin["runtime_identity"]:
        raise ValueError("missing, changed or extra files in pinned PrusaSlicer runtime")
    return pin


def fixture_cases():
    source = SOURCE.read_bytes()
    count = struct.unpack_from("<I", source, 80)[0]
    data = {
        "bracket-stl": source,
        "bracket-open-stl": source[:80] + struct.pack("<I", count - 1) + source[84:-50],
        "tetra-3mf": package(compression=ZIP_STORED),
        "tetra-inch-3mf": package(model(attributes='unit="inch"'), compression=ZIP_STORED),
        "tetra-translated-3mf": package(model(build='<item objectid="1" transform="1 0 0 0 1 0 0 0 1 200 0 0"/>'), compression=ZIP_STORED),
        "tetra-open-3mf": package(model(mesh=MESH.replace('<triangle v1="1" v2="2" v3="3"/>', '')), compression=ZIP_STORED),
        "tetra-required-extension-3mf": package(model(attributes='xmlns:p="urn:agentcadcam:unsupported" requiredextensions="p"'), compression=ZIP_STORED),
    }
    return {case: data[case] for case in CASES}


def isolated_environment(root, runtime):
    env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR") if key in os.environ}
    env.update(PATH=str(runtime) + os.pathsep + str(Path(env.get("SYSTEMROOT", "C:/Windows")) / "System32"),
               APPDATA=str(root / "roaming"), LOCALAPPDATA=str(root / "local"),
               USERPROFILE=str(root / "profile"), TEMP=str(root / "temp"), TMP=str(root / "temp"))
    return env


def invoke(runtime, action, directory, input_name=None):
    # This allowlist is intentional: no arbitrary options, load, slice, G-code,
    # post-processing, uploads or delegation to an already running GUI instance.
    if action not in ("help", "stl", "3mf"):
        raise ValueError("unsupported probe action")
    if action != "help" and input_name not in ("input.stl", "input.3mf"):
        raise ValueError("unsupported probe input name")
    arguments = ["--datadir", "config", "--threads", "1", "--config-compatibility", "disable"]
    if action == "help":
        arguments += ["--help"]
    else:
        arguments += ["--dont-arrange", "--no-ensure-on-bed", "--info", f"--export-{action}",
                      "--output", f"roundtrip.{action}", input_name]
    for name in ("config", "roaming", "local", "profile", "temp"):
        (directory / name).mkdir(exist_ok=True)
    env = isolated_environment(directory, runtime)
    result = subprocess.run([str(runtime / "prusa-slicer-console.exe"), *arguments], cwd=directory,
                            env=env, capture_output=True, timeout=45,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

    def diagnostic(data):
        text = data[:MAX_OUTPUT].decode("utf-8", errors="replace").replace("\r", "")
        for path, replacement in ((directory, "<temporary>"), (runtime, "<runtime>"), (ROOT, "<repository>")):
            text = text.replace(str(path), replacement).replace(path.as_posix(), replacement)
        return text

    return {"arguments": arguments, "exit_code": result.returncode,
            "stdout": diagnostic(result.stdout), "stderr": diagnostic(result.stderr),
            "diagnostics_truncated": max(len(result.stdout), len(result.stderr)) > MAX_OUTPUT}


def input_review(case, data):
    contexts = load_contexts(ROOT / "fixtures/additive/fdm-bracket/contexts")
    if case.endswith("3mf"):
        contexts["job"].update(mesh_format="3MF", model_dimensions=dict(x=1, y=1, z=1))
        if case == "tetra-inch-3mf":
            contexts["job"]["mesh_units"] = "inch"
    contexts["job"]["mesh_sha256"] = sha256(data)  # Only these fixed synthetic test inputs.
    result = preflight(**contexts, mesh_bytes=data, source_revision="A")
    return {"blockers": result["blockers"], "file_review": result["file_review"],
            "job_approval_status": contexts["job"]["approval_status"],
            "review_required": result["review_required"], "execution_allowed": result["execution_allowed"]}


def read_export(path, inspector):
    if not path.is_file():
        return {"present": False, "review": None}
    with path.open("rb") as stream:
        data = stream.read(MAX_OUTPUT + 1)
    result = {"present": True, "bytes": len(data), "complete": len(data) <= MAX_OUTPUT,
              "review": inspector(data)}
    if inspector is inspect_3mf and len(data) <= MAX_OUTPUT:
        # Fixed native export only: retain its package envelope for independent
        # diagnosis without storing a vendor project or importing its settings.
        try:
            with ZipFile(BytesIO(data)) as archive:
                result["parts"] = [{"name": member.filename, "bytes": member.file_size} for member in archive.infolist()]
                result["package_xml"] = {name: archive.read(name).decode("utf-8") for name in
                                         ("[Content_Types].xml", "_rels/.rels") if name in archive.namelist()}
        except (BadZipFile, UnicodeError):
            result["package_envelope_error"] = "native export envelope could not be decoded"
    return result


def run_probe(runtime):
    if os.name != "nt":
        raise ValueError("this pinned native probe targets Windows only")
    runtime = Path(runtime).resolve()
    pin = verify_runtime(runtime)
    cases = fixture_cases()
    if {name: sha256(data) for name, data in cases.items()} != pin["input_sha256"]:
        raise ValueError("reference fixture bytes changed; review and repin before running")
    report = {"runtime": pin, "scope": "independent geometry import/export observations; no slicing or printer/material approval",
              "review_required": True, "execution_allowed": False, "job_approval_promoted": False, "cases": []}
    with tempfile.TemporaryDirectory(prefix="agentcadcam-prusa-") as temporary:
        root = Path(temporary)
        report["help"] = invoke(runtime, "help", root)
        if report["help"]["exit_code"] or "PrusaSlicer-2.9.6" not in report["help"]["stdout"]:
            raise ValueError("pinned CLI did not report the expected version/help")
        for case, data in cases.items():
            directory = root / case
            directory.mkdir()
            input_name = "input.3mf" if case.endswith("3mf") else "input.stl"
            path = directory / input_name
            path.write_bytes(data)
            original = input_review(case, data)
            process = invoke(runtime, "stl", directory, input_name)
            exported = read_export(directory / "roundtrip.stl", inspect_stl)
            result = {"case": case, "input_sha256": sha256(data), "original_review": original,
                      "process": process, "stl_export": exported}
            if case == "bracket-stl":
                result["package_process"] = invoke(runtime, "3mf", directory, input_name)
                result["package_export"] = read_export(directory / "roundtrip.3mf", inspect_3mf)
            if path.read_bytes() != data:
                raise ValueError("reference tool changed a supplied input")
            result["input_preserved"] = True
            report["cases"].append(result)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = run_probe(args.runtime_dir)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        print(json.dumps({"status": "probe_failed", "reason": "runtime/input validation or bounded native execution failed",
                          "review_required": True, "execution_allowed": False}))
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    # Rejected input is an observation, not an infrastructure error. The caller
    # must review per-case exits and exports; zero never means manufacturing-ready.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
