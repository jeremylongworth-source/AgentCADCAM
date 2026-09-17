# Optional CAMotics evidence boundary — 2026-09-17

## Decision

For maintainers evaluating Phase 3, use an explicitly selected offline CAMotics runtime as independent interpreter/material-removal evidence, **not** an approval authority. The portable router and skills do not depend on it. The opt-in [native probe](../../tests/native/check_camotics_runtime.py) runs only the fixed synthetic baseline and eight roadmap mutations; it does not accept arbitrary customer programs, projects, machine addresses or command options. REVIEW_REQUIRED.

Interpreting the same files with another implementation provides evidence unavailable from our own parser tests. A simulator exit code alone is insufficient: this experiment actually completed for every negative case. Automatically importing successful native runs into `simulation_status: verified` would misrepresent both missing job context and what the simulator checks. No such adapter or promotion path is implemented.

## Runtime and install review

Selected package: CAMotics `1.2.0-release`, Windows AMD64, published 2019-02-09 by Cauldron Development LLC. The [pinned manifest](../../constraints/camotics-win64.json) records the official asset URL, measured SHA-256 and the observed valid Authenticode publisher signature. GitHub's release API supplied no asset digest; the hash is a local measurement, not an upstream checksum. Binary/source equivalence and the security of this older runtime were not independently audited.

Install disposition: use only for the controlled synthetic experiment with these safeguards. The release was downloaded into ignored `venv/camotics120/` and unpacked using the already-present 7-Zip 25.01. Its installer was **not** run. Only `gcodetool.exe`, `camsim.exe`, their bundled Qt/graphics DLLs and license/readme/changelog were extracted; the GUI, TPL executable and machine examples were not enabled. No administrator action, PATH/registry change, system-runtime installation, service start or machine connection was needed. GPL-2.0-or-later runtime binaries are not checked into this repository.

The first `camsim --help` attempt exited `-1073741515` before printing help. After extracting the additional DLLs from the same signed archive, it exited zero and printed help. No system dependency was replaced. `gcodetool --version` reports `1.2`; **camsim reports `0.0`** in this package. Preserve that actual output and use the pinned release/binary hashes for identity rather than silently correcting its version string.

For another development machine: obtain that exact asset from the manifest's official URL; verify its hash and publisher signature, inspect the pinned source entry points and license, and extract the listed files into an isolated folder with a reviewed archive tool. Do not auto-update, install globally or bypass a signature/hash mismatch. The runner checks every listed file before launching anything. The checks do not authenticate OS DLLs, other inherited host state or every possible dynamic dependency. Re-review after runtime/source/platform/input-scope changes.

## Data flow and reproducibility

Run from the repository root after preparing the optional runtime:

```powershell
.\.venv\Scripts\python.exe -m tests.native.check_camotics_runtime --runtime-dir venv/camotics120/runtime
```

1. Check the selected runtime's pinned hashes and capture both version commands, including process exit and both output streams.
2. Replay each fixed case from the exact repository NC bytes. Bind the supplied program to its existing descriptor SHA-256; do not substitute the interpreter's normalized output.
3. Create a private temporary working directory with only `program.nc` and the fixed lab `project.camotics`. Invoke `gcodetool --metric --default-units 0` with exact bytes on stdin; capture its diagnostic trace. Invoke `camsim --threads 1 --resolution 1 project.camotics surface.stl` without a shell and wait for termination. Each child has a 45-second timeout and no visible console window.
4. Measure the exported binary STL's byte count, triangle count, bounds and absolute signed-volume sum. Retain whole-file and triangle-payload hashes separately. These are measurements of an export, not validation of mesh closedness or dimensional conformance. Logs preserve native messages/timing; private temporary paths and CR spelling are normalized explicitly.
5. Delete only the probe's own temporary directory and print the report. The probe cannot rewrite retained observations, profiles, hashes, approval records or job simulation state. It adds no network API, device access or controller interface. This is not an OS process sandbox; restrict use to the inspected synthetic corpus.

The lab [project and assumptions](../../fixtures/cnc/camotics-lab/README.md) deliberately separate the simulation from physical job evidence. It declares a fixed prism and synthetic cutter, with a newly specified test cutting length rather than falsely deriving that length from tool reach. It supplies no actual fixture/holder/machine model, measured WCS/offset or physical initial pose. Unknown-tool cases intentionally leave tools 2/9 undefined to expose simulator defaults. None of these test settings resolve the retained job's missing context.

Native binaries are opt-in and not invoked by portable test discovery. The [retained report](../evaluation/cnc-independent/camotics-1.2.0-windows.json) records a real run; portable tests inspect its identity/relationships and exercise the measurement/hash guards. Timing, temporary export headers and whole-STL hashes need not reproduce exactly; do not overwrite prior observations solely to make an equality test pass. The full STL files were temporary, not retained geometry deliverables. A new native run is needed to inspect those surfaces again.

## Observed results and limitations

All nine interpreter calls and all nine simulator calls exited zero and produced traces/surfaces. This means the controlled experiment completed, not that nine jobs passed review.

| Case group | Independent observation | Required interpretation |
| --- | --- | --- |
| Baseline | Normalized metric moves and a cut-prism surface | Does not establish the linked L-bracket or a reviewed physical setup |
| Wrong post/controller/revision | Same normalized trace as baseline; altered comments do not trigger a native rejection | Identity/provenance checks remain our review responsibility |
| Missing WCS | Same trace/surface geometry as baseline despite omitted G54 | Default interpreter state cannot supply the required job WCS evidence |
| Wrong units | Metric trace includes X1524, Y1016, Z635 and converted feeds, rather than baseline X60/Y40/Z25 | Simulator interpretation does not reconcile the conflicting mm job declaration |
| Tool 9 / tool 2 | Simulator warns `Auto-creating missing tool 9` / `2` and continues with a different surface | Invented defaults cannot supply tool-library identity, geometry or availability |
| X100 conflict | Interpreter retains X100; simulator completes within its fixed stock experiment | It did not check the job's declared machine-axis limits |

For the baseline, the STL contains 9432 triangles while the log also reports a reduction to 146. The report uses the actual exported triangle count, not the reduction message as a geometry assertion. Stock-removal measurements, default-state behavior and the absence of errors cannot establish fixture/holder collision, kinematic feasibility, post/OEM compatibility, real feed/spindle behavior, initial state, feature completeness or manufacturing approval.

The retained job simulation stays `not_run`, approval stays `not_requested`, and the composed router still blocks all cases on unresolved required context. Historical seven-skill packets are not rewritten to imply that this later calibration run verified their jobs. Gate 04 still requires a requirement-by-requirement audit; practitioner/public-alpha gates remain separate. LinuxCNC and FreeCAD were not run. The current machine had no discovered executables for them on PATH; Docker's Linux engine was unavailable and was not started. Those limited checks do not prove that no alternate installation exists.

## Primary sources

All accessed 2026-09-17. Scope is the pinned software/documentation, not physical manufacturing safety or applicability.

- [Official release](https://github.com/CauldronDevelopmentLLC/CAMotics/releases/tag/1.2.0-release), publisher Cauldron Development LLC, published 2019-02-09: selected distribution and release identity. [License at the pinned tag](https://github.com/CauldronDevelopmentLLC/CAMotics/blob/1.2.0-release/LICENSE): optional runtime licensing; no binary redistribution here.
- [GCodeTool entry point](https://github.com/CauldronDevelopmentLLC/CAMotics/blob/1.2.0-release/src/gcodetool.cpp) and [command-line pipeline](https://github.com/CauldronDevelopmentLLC/CAMotics/blob/1.2.0-release/src/camotics/CommandLineApp.cpp), revision `1.2.0-release`: parse/interpreter pipeline and normalized metric output, not a physical controller connection.
- [camsim entry point](https://github.com/CauldronDevelopmentLLC/CAMotics/blob/1.2.0-release/src/camsim.cpp), same revision: project input, surface computation and STL output options. [Workpiece implementation](https://github.com/CauldronDevelopmentLLC/CAMotics/blob/1.2.0-release/src/camotics/project/Workpiece.cpp), same revision: explicitly configured versus automatically inferred stock bounds. Our experiment disables automatic bounds.
- [CAMotics manual](https://camotics.org/manual.html), publisher CAMotics, publication/update date unavailable: describes default tools/workpieces and limits of the GUI's model. It explains why missing tools can be auto-created; the native warning above independently reproduces that behavior. Its older XML-project description is not used as the 1.2.0 JSON format contract; pinned source/examples and the actual native run establish the selected format.
