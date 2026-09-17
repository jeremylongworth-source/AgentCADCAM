# Optional Windows PrusaSlicer reference experiment

Status: executed geometry experiment; `REVIEW_REQUIRED`. Not a runtime dependency
of the portable skills or a manufacturing approval. Phase 4 remains open.

## Source, dependency review and boundary

The experiment used the official [PrusaSlicer 2.9.6 release](https://github.com/prusa3d/PrusaSlicer/releases/tag/version_2.9.6),
published 2026-06-25, source commit
`b028299c770b8380ee81c921a2867d522f288123`. Sources accessed 2026-09-17:

- [Release asset metadata](https://api.github.com/repos/prusa3d/PrusaSlicer/releases/tags/version_2.9.6)
  supplies the portable ZIP and its SHA-256 digest.
- [CLI action implementation](https://github.com/prusa3d/PrusaSlicer/blob/b028299c770b8380ee81c921a2867d522f288123/src/CLI/ProcessActions.cpp)
  distinguishes geometry inspection/export from slicing and post-processing.
- [CLI setup](https://github.com/prusa3d/PrusaSlicer/blob/b028299c770b8380ee81c921a2867d522f288123/src/CLI/Setup.cpp)
  and [input loading](https://github.com/prusa3d/PrusaSlicer/blob/b028299c770b8380ee81c921a2867d522f288123/src/CLI/LoadPrintData.cpp)
  inform explicit data-directory isolation and avoiding arbitrary project settings.
- [Upstream license](https://github.com/prusa3d/PrusaSlicer/blob/b028299c770b8380ee81c921a2867d522f288123/LICENSE)
  is AGPL-3.0. No native binary or upstream source code is redistributed here.

The downloaded ZIP matched the published digest:

```text
5aaf22e42f95accecfa122d23a835911f289ecc2ff606db3e83d637ddcc0a209
```

The launcher Authenticode signature was observed as Valid, publisher Prusa
Research a.s. These observations do not constitute a reproducible-build audit
or a guarantee about all native behavior. Dependency-review decision: use only
the pinned portable runtime and fixed synthetic geometry actions with the
isolation below; do not enable arbitrary project/configuration execution.

## Local setup and replay

Download the ZIP linked in `constraints/prusaslicer-win64.json`, verify its exact
SHA-256 before extraction, and validate archive entry destinations remain within
the chosen project-local runtime directory. Do not run the installer, add a
system PATH entry, associate files, auto-update, or connect a printer account.
The executed copy is under ignored `venv/prusaslicer296/extracted/PrusaSlicer-2.9.6`.
The optional runtime can be absent on other contributors' machines and in CI.

```text
python -m tests.native.check_prusaslicer_runtime --runtime-dir venv/prusaslicer296/extracted/PrusaSlicer-2.9.6
python -m unittest tests.evaluation.test_prusaslicer_evidence -v
```

The native command validates the complete runtime tree (1,119 files including
resources) and all fixed input hashes before invoking the launcher. The tree
digest hashes sorted UTF-8 `relative-posix-path + NUL + sha256 + newline` records;
the manifest also retains individual EXE/DLL hashes. Missing, changed, extra or
linked entries block. Re-review and deliberately repin any runtime/input change;
do not automatically refresh hashes when verification fails.

The probe permits only help, STL export and 3MF export. It sets an isolated data
directory, temporary user-profile/application-data paths, a minimal environment,
45-second child timeouts and hidden Windows console creation. It does not inherit
the parent environment's credentials, load personal profiles, delegate to an
existing GUI, or request network/upload/physical actions. It disables arrangement
and automatic bed lifting to expose source placement. No printer/material process
parameters are invented. This is process/configuration isolation, **not an OS
network or filesystem sandbox**; run on a suitably isolated host if that stronger
boundary is required.

Inputs and exports live in a private temporary directory removed after the run.
Original input bytes are checked unchanged. The JSON report retains commands,
exit codes, redacted diagnostics, hashes and inspector results. A native exit 0
only means an observation completed; inspect each case and its blockers. A probe
infrastructure failure exits 1. No result renews a job approval.

## Actual observations

The [retained report](../evaluation/additive-independent/prusaslicer-2.9.6-windows.json)
contains nine child-process results: one help, seven STL round-trips and one 3MF
export. All exited 0. The [open fixture lab](../../fixtures/additive/prusaslicer-lab/README.md)
defines each input and its provenance.

| Case | Observed result and boundary |
| --- | --- |
| Bracket STL | PrusaSlicer reports 2,052 facets and 60/40/30 dimensions; our exported-byte inspection agrees. Export hash differs from source. |
| Open bracket and open tetrahedron | Both report three open edges and export successfully. The exported meshes still have three boundary edges; original and derivative remain blocked. |
| Inch tetrahedron | CLI displays 25.400000 extents; binary STL stores 25.399999618530273. Retain the precision loss instead of calling the representations exactly identical. |
| Translated tetrahedron | CLI `--info` shows centered local bounds, while actual STL bytes retain X=200..201. Original preflight still blocks the declared 200-unit build envelope violation. |
| Required-extension tetrahedron | PrusaSlicer exports the same STL as the simple tetrahedron without a diagnostic. Our original-package unsupported-extension blocker remains. This observation is specific to this synthetic extension and pinned version. |
| Bracket 3MF export | Export succeeds, but the envelope references a missing thumbnail and lacks content-type declarations for its auxiliary XML/config parts. Our package inspector blocks; the reference-tool result is not an exception to package review. |

No repair was observed in the open-mesh exports. No slicing, G-code generation,
profile validation, printer action or independent manufacturing verification
occurred. Console geometry summaries do not replace transformed output-byte
inspection. Success in a third-party tool does not establish Core conformance,
required-extension support or printability.

Exported ZIP timestamps/metadata can change between runs: native output hashes
are recorded observations, not cross-run golden identities. Portable tests replay
fixed input hashes and preflight results, then assert the retained measurements,
diagnostics and safety boundaries. They do not pretend to rerun native software.

## Remaining acceptance work

This provides the roadmap's initial independent PrusaSlicer/open-model geometry
reference evidence. It does not close additive acceptance. Full skill-assisted
handoffs, review of self-intersection/usable-bed limits and unsupported package
semantics, and the complete gate-05 audit remain. Actual applicable slicing
evidence is still required before a real job could claim slicer readiness.
Integration/approval authenticity and practitioner evaluation remain later gates.

Revisit for any new runtime version, input model family, extension, profile
import, process-output action, unhandled native error or false-ready case. Do not
relax missing-context or human-review controls just to match the reference tool.
