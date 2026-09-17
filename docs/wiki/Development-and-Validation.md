# Development and validation

Work from the current checkout, follow [AGENTS.md](../../AGENTS.md), and stay within the governing [roadmap](../../ROADMAP.md). The project has no required sibling-repository dependency.

## Portable checks

After [environment setup](Getting-Started.md), run from the repository root:

```sh
python scripts/validate_foundation.py
python scripts/validate_schema_instances.py
python -m unittest discover -s tests -p "test_*.py"
git diff --check
```

| Check | Evidence provided |
| --- | --- |
| Foundation validator | Required files, metadata, manifests, source-registry structure and local documentation references |
| Schema-instance validator | Schema definitions and declared checked-in instances; not every external user file |
| Unit suite | Curated positive/negative fixtures, routing, parsers, invalidation, governance and evaluation-tool regressions |
| Diff check | Whitespace errors; not semantic or safety review |

Use focused tests while iterating and expand validation with risk. Record actual outcomes. Never treat skipped native checks as passed or silence blockers to obtain a green suite.

## Optional native tools

The portable suite includes `ezdxf`; it does not require CadQuery. `requirements-dev.txt` includes CAD-generation dependencies. Optional native probes have separate setup and evidence boundaries:

- [CadQuery on Windows](../development/cadquery-windows.md)
- [CAMotics evidence boundary](../architecture/camotics-evidence-boundary.md)
- [PrusaSlicer on Windows](../development/prusaslicer-windows.md)

These are offline experiments, not machine control or blanket validation of a simulator, slicer or installation.

## Contribution checklist

1. Explain the problem, affected contracts and scope.
2. Preserve provenance, units, revisions and human-approval boundaries.
3. Cite applicable primary evidence for consequential factual claims.
4. Add positive and negative regressions for changed decisions.
5. Document migration and invalidation implications for breaking changes.
6. Report validation and unresolved limitations.

Follow [CONTRIBUTING.md](../../CONTRIBUTING.md), [testing standards](../standards/testing-standard.md) and [fixture licensing](../standards/fixture-licensing-standard.md). Safety reports follow [SECURITY.md](../../SECURITY.md), not ordinary public disclosure.

## Documentation contributions

Edit wiki source in `docs/wiki/` alongside affected code and contracts. Keep links relative so repository readers and local checks work. Use the [publishing workflow](../development/wiki-publishing.md) to export hosted links; avoid independent edits that make the hosted wiki diverge from reviewed source.
