# CADCAM-01 Domain Contract and Foundation Handoff

## Status

Foundation implementation in progress. The repository bootstrap and initial contract slice are present, but `CADCAM_02_FOUNDATION_READY` remains pending formal review and any required contract refinements.

## Delivered in this slice

- Standalone repository contract and public project documentation.
- Domain contract, taxonomy v1, consequence model, execution boundary, personas, and specialization model.
- Skill authoring, evidence, interoperability, safety, testing, evaluation, and context-profile standards.
- Format registry covering native CAD, STEP AP242, IGES, DXF, SVG, STL, 3MF, NC/G-code, and STEP-NC research status.
- Nine initial JSON Schema context contracts and representative job/handoff examples.
- Minimal deterministic router contract and four workflow route declarations plus `unknown`.
- Fixture/source registries and repository structure placeholders.
- Dependency-light foundation validator and six contract smoke tests.

## Validation evidence

```text
python scripts/validate_foundation.py
FOUNDATION VALIDATION PASSED

python -m unittest discover -s tests -p 'test_*.py' -v
Ran 6 tests ... OK
```

## Gate assessment

| Requirement | Current status |
| --- | --- |
| Standalone scope expressed | Drafted |
| Initial workflow families frozen | Drafted in domain contract and routes |
| Execution boundary explicit | Drafted and tested |
| Prohibited capabilities explicit | Drafted in AGENTS.md and SECURITY.md |
| Evidence hierarchy established | Standard documented; source registry is planned/empty |
| Context schemas parse | Passed |
| Validation scripts operational | Passed |
| Formal architecture review | Pending |
| Qualified safety/manufacturing review | Required before manufacturing use |

## Open questions for review

- Confirm repository license and maintainer attribution before the first public push.
- Confirm the desired AgentSkills metadata compatibility profile.
- Decide whether the integrated Phase 6 state schema should be added to the foundation or kept strictly behind the router integration gate.
- Add authoritative source records before making safety, machine, controller, material, or regulatory claims in workflow skills.

## Safety status

`REVIEW_REQUIRED`: This repository foundation is draft architecture and validation guidance. It does not authorize tooling, ordering, production, machine operation, or regulated use.
