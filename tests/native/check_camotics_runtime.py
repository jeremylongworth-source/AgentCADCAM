"""Opt-in pinned Windows CAMotics experiment; never connects to machine hardware.

Accepts a runtime directory, not arbitrary programs, projects or command options.
Only fixed synthetic repository cases run, in private temporary directories.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import tempfile

from tests.evaluation.replay_cnc_reviews import CASES, ROOT, replay


PIN = ROOT / "constraints/camotics-win64.json"
PROJECT = ROOT / "fixtures/cnc/camotics-lab/project.camotics"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def verify_runtime(runtime):
    pin = json.loads(PIN.read_text(encoding="utf-8"))
    for name, expected in pin["files"].items():
        path = runtime / name
        if not path.is_file() or sha256(path.read_bytes()) != expected:
            raise ValueError(f"missing or changed pinned runtime file: {name}")
    return pin


def mesh_summary(data):
    if len(data) < 84:
        raise ValueError("missing binary STL header")
    count = struct.unpack_from("<I", data, 80)[0]
    if not count or len(data) != 84 + count * 50:
        raise ValueError("empty or inconsistent binary STL")
    low, high, volumes = [math.inf] * 3, [-math.inf] * 3, []
    for offset in range(84, len(data), 50):
        values = struct.unpack_from("<12fH", data, offset)
        if not all(math.isfinite(value) for value in values[:12]):
            raise ValueError("nonfinite STL normal or coordinate")
        a, b, c = (values[start:start + 3] for start in (3, 6, 9))
        for point in (a, b, c):
            for axis, value in enumerate(point):
                low[axis], high[axis] = min(low[axis], value), max(high[axis], value)
        volumes.append((a[0] * (b[1] * c[2] - b[2] * c[1])
                        + a[1] * (b[2] * c[0] - b[0] * c[2])
                        + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6)
    return {"sha256": sha256(data), "triangle_data_sha256": sha256(data[84:]), "bytes": len(data), "triangles": count,
            "bounds": {"min": low, "max": high},
            "absolute_signed_volume": abs(math.fsum(volumes)),
            "scope": "binary mesh measurements only; closedness, collision clearance and dimensional conformance not established"}


def invoke(executable, arguments, directory, program=None):
    result = subprocess.run([str(executable), *arguments], input=program, capture_output=True,
                            cwd=directory, timeout=45, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    def diagnostic(data):
        # Preserve messages but replace private temporary paths and CRLF spelling.
        return data.decode("utf-8", errors="replace").replace(str(directory), "<temporary>").replace("\r", "")
    return {"arguments": arguments, "exit_code": result.returncode,
            "stdout": diagnostic(result.stdout), "stderr": diagnostic(result.stderr)}


def run_probe(runtime):
    if os.name != "nt":
        raise ValueError("this pinned runtime probe targets Windows only")
    runtime = Path(runtime).resolve()
    pin = verify_runtime(runtime)  # Before launching anything or preparing inputs.
    project = PROJECT.read_bytes()
    report = {"runtime": pin, "project_sha256": sha256(project), "project": json.loads(project),
              "scope": "independent interpreter and synthetic prism-removal experiment, not job simulation verification",
              "review_required": True, "execution_allowed": False, "job_approval_promoted": False, "cases": []}
    with tempfile.TemporaryDirectory(prefix="agentcadcam-camotics-") as temporary:
        root = Path(temporary)
        report["versions"] = {tool: invoke(runtime / f"{tool}.exe", ["--version"], root) for tool in ("gcodetool", "camsim")}
        for case in CASES:
            observed = replay(case)
            program = observed["program"].encode("utf-8")
            if sha256(program) != observed["state"]["generated_manufacturing_output"]["sha256"]:
                raise ValueError("fixture NC identity mismatch")
            directory = root / case
            directory.mkdir()
            (directory / "program.nc").write_bytes(program)
            (directory / "project.camotics").write_bytes(project)
            interpreted = invoke(runtime / "gcodetool.exe", ["--metric", "--default-units", "0"], directory, program)
            simulated = invoke(runtime / "camsim.exe", ["--threads", "1", "--resolution", "1", "project.camotics", "surface.stl"], directory)
            mesh_path = directory / "surface.stl"
            mesh, mesh_error = None, None
            if mesh_path.is_file():
                try:
                    mesh = mesh_summary(mesh_path.read_bytes())
                except ValueError as error:
                    mesh_error = str(error)
            else:
                mesh_error = "simulator did not create a surface"
            report["cases"].append({"case": case, "nc_sha256": sha256(program),
                                    "interpreter": interpreted, "simulator": simulated,
                                    "surface": mesh, "surface_error": mesh_error,
                                    "router_blockers": observed["route_result"]["blockers"],
                                    "job_simulation_status": observed["state"]["simulation_status"],
                                    "job_approval_status": observed["state"]["approval_status"]})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = run_probe(args.runtime_dir)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"status": "probe_failed", "reason": str(error), "review_required": True, "execution_allowed": False}))
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    processes = list(report["versions"].values()) + [run[key] for run in report["cases"] for key in ("interpreter", "simulator")]
    return 0 if all(run["exit_code"] == 0 for run in processes) and all(run["surface"] is not None for run in report["cases"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
