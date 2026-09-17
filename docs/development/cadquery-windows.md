# Windows native fixture environment

For the synthetic bracket generator, the tested environment is Windows x64 with CPython 3.12.14, CadQuery 2.8.0, OCP 7.9.3.1.1, VTK 9.6.2, CasADi 3.6.7, and NLopt 2.11.0. The native probe checks four hole locations, analytical volume, solid validity, dimensions, STEP round-trip geometry, STL envelope, and interpreter exit status.

## Setup

Use a separate Python 3.12 environment. With the Windows Python launcher and Python 3.12 installed, run from the repository root:

```powershell
py -3.12 -m venv venv/cad312
.\venv\cad312\Scripts\python.exe -m pip install -r requirements-dev.txt -c constraints/cadquery-win312.txt
.\venv\cad312\Scripts\python.exe -m pip check
.\venv\cad312\Scripts\python.exe -m tests.native.check_cadquery_runtime
```

If using another Python 3.12 installation, replace `py -3.12` with its executable path for environment creation. The repository does not depend on Codex's bundled interpreter. The constraints are an explicitly selected, tested Windows/Python 3.12 combination, not a universal compatibility claim or complete hash-locked dependency set. Review and retest before updating them. Other platforms can use the generic development requirements and the same native probe.

To regenerate the tracked derivatives after a successful native check:

```powershell
.\venv\cad312\Scripts\python.exe scripts/generate_cad_fixture_step.py
if ($LASTEXITCODE -ne 0) { throw 'CAD generation failed' }
```

The native check starts only the fixed local probe with the selected interpreter. It generates files in a repository-local temporary directory, checks geometry, waits for shutdown, and removes its temporary output. It does not load user manufacturing jobs or operate machines. It is opt-in and does not import CadQuery into the portable unit-test process.

The CAD file-review CLI now also checks a [declared source/derivative byte binding](../architecture/derivation-binding.md). Regeneration does not update that record automatically. Resolve source intent and inspect regenerated derivatives before recording any new hashes; an export command's success alone is not approval of a new association.

## Reproduced failure and comparison

Both the original system Python 3.14 environment and a fresh Python 3.12.14 environment crashed after importing CadQuery 2.8.0 with CasADi 3.8.0 / NLopt 2.11.0. The system failure reduces to `python -c "import casadi, nlopt"`; each library alone exits normally. Failures included Windows codes `0xC0000005` and `0xC0000374`, after output had already printed.

An [upstream investigation](https://github.com/CadQuery/cadquery/issues/1911#issuecomment-5564602712) attributes the same pair failure to SWIG runtime cleanup across differing C runtimes. Our import comparison reproduces the symptom; it does not independently prove the allocator mechanism. The related [CadQuery fix proposal](https://github.com/CadQuery/cadquery/pull/2092) was open and unmerged when checked during this work.

Changing only CasADi to 3.6.7 in the isolated Python 3.12 environment made the paired import and CadQuery import exit 0; `pip check` passed. The native bracket probe then passed with a clean child process exit. The original system installation was left unchanged. We did not patch interpreter destructors or modify installed library source.

## Geometry correction

The stronger native check found that the old STEP/STL derivatives contained only the two base holes. The face-local coordinates used for the upright cutters placed them outside the solid. The generator now uses explicit cylinder positions and directions from the authoritative OpenSCAD source.

The corrected ideal solid has four 6 mm diameter through holes and volume approximately `22361.4159868246 mm³`, versus `22700.7079934123 mm³` for the old two-hole derivative. The source design remains revision A; the fixture bundle version is 2 because the derivatives were corrected. Consumers must replace the old derivative files and invalidate approvals tied to their previous hashes. The additive fixture references the corrected STL automatically.

The STEP envelope check now uses topological vertex coordinates instead of every Cartesian point. Untrimmed surface definitions can legitimately place construction points outside the physical solid. This envelope check remains narrower than the opt-in native geometry test.

## Verification evidence

- 78 portable tests passed in both the Python 3.14 test environment and the isolated Python 3.12 environment.
- Foundation and schema validation passed (ten schemas and thirteen instances).
- The constrained Python 3.12 native probe passed with process exit 0; tracked STEP/STL regeneration also exited 0.
- The same native runner against the unchanged system environment detected the post-output access violation and returned failure. Printed geometry results cannot mask a failed child process.

These results cover the synthetic bracket and the tested dependency combination. They do not close the real-input practitioner pilot gate.
