# Foundation validator coverage

`python scripts/validate_foundation.py` checks repository contracts. A passing run does not award a roadmap gate or approve manufacturing. Run the separate schema-instance validator and full test suite as well.

## Checks implemented

| Contract | Rejection cases covered |
| --- | --- |
| Repository YAML/JSON syntax | Invalid syntax, duplicate keys, and non-standard JSON constants such as NaN/Infinity. Scanning includes fixture mutations and examples, not just top-level manifests. |
| Skillset manifests | Invalid name/version/status shape; empty, malformed, duplicate, or unknown skill lists; references to missing SKILL.md files. |
| Router manifests | Invalid row types, duplicate IDs/families, incomplete family coverage, malformed skillset references, empty/duplicate artifact lists, and unknown default consequence values. The unknown-family route must explicitly select no skillset. |
| Fixture index | Empty/malformed entries, duplicate IDs or resolved descriptor paths, invalid family, missing status, and index/descriptor ID mismatch. |
| Fixture descriptors | Non-mapping descriptors, missing version/license/status/description, absent artifacts, malformed artifact/context references, and missing referenced files. |
| File references | Absolute, drive/UNC, backslash, and resolved out-of-bound paths are rejected. Fixture references may cross between fixture families but must remain under `fixtures/`; generator/constraint references are repository-relative. |
| Skill frontmatter | Invalid/duplicate YAML keys, malformed name/description, name/folder mismatch, unsupported top-level fields, non-string metadata, missing version/owner/consequence fields, invalid versions, and duplicate/unknown/live-execution scope. |
| Schema and safety documents | Non-mapping schema JSON and missing/unreadable required safety documents produce errors instead of unchecked exceptions. Full schema semantics are checked separately. |
| Inline Markdown file links | Missing local targets and paths outside the repository. External web links are not fetched. |
| Format/source policies | Nine-format completeness and scoped source-reference checks described in the [source process](../sources/source-freshness-process.md). |

The content walker excludes `.git`, local dependency environments, caches, and build output. It does not traverse symbolic-link directories. This keeps developer-installed third-party files outside the repository-content checks. Fixture paths are resolved and checked before referenced descriptor contents are opened.

## Regression evidence

`tests/foundation/test_manifest_validation.py` mutates in-memory copies of repository documents. The initial run reproduced accepted empty/duplicate entries and type errors in manifest validation. Tests now cover these failures, missing referenced skills, valid cross-fixture references, out-of-bound paths, resolved-link escapes, mutation syntax, schema roots, and frontmatter types. No real job data or machine access is used.

```text
python -m unittest tests.foundation.test_manifest_validation -v
python scripts/validate_foundation.py
python scripts/validate_schema_instances.py
python -m unittest discover -s tests -v
```

## Unfinished acceptance work

- The 14 existing skills now declare version, maintenance owner, and supported review levels under string-valued AgentSkills metadata. Tests cover the schema-like contract and compatibility with routed default levels; this is not evidence of skill behavior in a practitioner job.
- Markdown checks currently cover simple inline file links, not full CommonMark reference-link syntax or fragment-anchor existence. Code examples may require care to avoid being interpreted as links. This is not a complete broken-reference audit.
- Syntax and path checks do not prove that a fixture mutation represents the claimed physical/geometric defect, that a source claim is true, or that a skill behaves correctly in an agent run.
- Required document contents, schema semantics, source applicability, remaining safety cases, and real-input practitioner evidence remain subject to the [roadmap reconciliation](roadmap-reconciliation.md).
