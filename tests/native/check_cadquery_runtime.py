"""Run a fixed offline native probe and require a clean interpreter shutdown."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    # The generator enforces repository-local output; cleanup affects only this directory.
    with tempfile.TemporaryDirectory(prefix="cad-native-check-", dir=ROOT) as directory:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "tests.native.cadquery_export_probe", directory],
                cwd=ROOT, capture_output=True, text=True, timeout=60,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except subprocess.TimeoutExpired:
            print("CADQUERY NATIVE CHECK FAILED: child exceeded 60 seconds")
            return 1
        print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        if result.returncode != 0:
            print(f"CADQUERY NATIVE CHECK FAILED: child exit={result.returncode} (0x{result.returncode & 0xffffffff:08X})")
            return 1
    print("CADQUERY NATIVE CHECK PASSED: geometry checks and process exit are clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
