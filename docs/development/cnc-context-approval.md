# CNC context and effective approval

`router.job_router.route_job` applies the roadmap's CNC hard manufacturing rule to execution-adjacent and live-execution requests. Matching an approval fingerprint is necessary but insufficient: required declared context must also be complete and consistent.

## Accepted declared context

| State field | Required check |
| --- | --- |
| `machine_profile`, `controller_profile`, `material` | Present, schema-valid profiles with the corresponding request `*_known` flag true. Existing process-family checks still apply. |
| `units` | Explicit `mm`, `in`, or `inch`; supported by the controller. |
| `setup` | Schema-valid setup; positive stock dimensions `x/y/z` with matching units; nonempty orientation; `wcs_status: verified`. |
| `setup.coordinate_model` | Execution-adjacent CNC requires a current reviewed fixed Cartesian translation and initial machine position, matching machine/controller/setup/tool/WCS identities and units. Explicit three-axis machine bounds are required. See the [coordinate contract](../architecture/nc-coordinate-model.md); no zero offsets or physical verification are inferred. |
| Workholding | Nonempty `type` and `clamps_clear: true`. Root `workholding`, when non-null, is checked instead of silently falling back to setup workholding; shared declarations must not conflict. |
| `work_coordinate_system` | Explicit `code` and `status: verified`; code must appear in controller `modes_and_offsets.wcs`. |
| `tool_library.tools` | Nonempty list of schema-valid tools, unique IDs and nonnegative integer tool numbers, nonempty geometry type, positive diameter, holder and reach, and `availability: available`. |
| `postprocessor` | Schema-valid profile with `validation_state: verified`; machine, controller, CAM system, and post version must match selected state. |
| `simulation_status` | `verified`. |
| `verification_results` | Separate passed simulation and verification records with unique check IDs, nonempty evidence and current versioned input-context bindings; every supplied record must satisfy the [verification-binding contract](../architecture/cnc-verification-binding.md). Bare passed labels are insufficient. |
| `generated_manufacturing_output` and `nc_program` argument | Execution-adjacent CNC requires an artifact-schema descriptor, derived NC role, matching revision/units and exact SHA-256 of supplied bytes. Fresh static checks must not produce blockers. See the [binding contract](../architecture/nc-artifact-approval-binding.md). |

The schema permits incomplete draft context. This stricter review gate does not prevent storing drafts; it prevents treating an incomplete CNC context as effectively approved. Stock units must match rather than being silently converted. Tool geometry checks are basic completeness checks for the initial milling scope; they do not prove cutting suitability or dimensional compatibility.

## Result and migration

Missing or conflicting information adds explicit `MISSING_CONTEXT`, `MACHINE_CONTEXT_REQUIRED`, `SOURCE_VERIFICATION_REQUIRED`, or `SIMULATION_REQUIRED` blockers. If a matching approved record was provisionally recognized, required CNC context failures return an `invalidated` copy, update effective job approval, and add `HUMAN_APPROVAL_REQUIRED`.

The original inputs and reviewed fingerprint are retained unchanged. Callers must preserve the returned diagnostics in their own audit storage; the utility persists nothing. Existing records that previously passed on incomplete context now require complete evidence and renewed review. Do not simply replace a fingerprint or mark missing context verified to retain approval.

The test fixture marks its declarations verified only to exercise this contract. The function does not authenticate a reviewer, inspect a machine, establish clamp clearance, prove tool reach, or validate a simulator's physical fidelity. Every result remains non-executing and review-required, including a result with no blockers. The router now invokes static NC review when execution-adjacent CNC prerequisites allow it; callers can inspect `nc_review` to distinguish a performed check from blocked prerequisites. The current static reviewer supports one tool only, so otherwise-valid multi-tool context cannot retain effective approval through this path.

Regression coverage is in `tests/routing/test_job_router.py`; broader unresolved requirements remain in the [roadmap reconciliation](roadmap-reconciliation.md).
