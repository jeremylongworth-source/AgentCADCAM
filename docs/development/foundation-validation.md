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
| Parsed Markdown references | Missing inline/reference-link/image targets, missing Markdown heading/custom anchors, unsafe schemes, and decoded or resolved path escapes. Code examples and comments are not treated as links. See scope below. |
| Format/source policies | Nine-format completeness and scoped source-reference checks described in the [source process](../sources/source-freshness-process.md). |

The content walker excludes `.git`, local dependency environments, caches, and build output. It does not traverse symbolic-link directories. This keeps developer-installed third-party files outside the repository-content checks. Fixture paths are resolved and checked before referenced descriptor contents are opened.

## Markdown reference scope

The checker uses [markdown-it-py's parsed token stream](https://markdown-it-py.readthedocs.io/en/latest/using.html), with CommonMark, tables, and strikethrough enabled. It checks inline, full/collapsed/shortcut reference links, image destinations, and reference definitions (including unused definitions). Fenced/indented code, inline code, comments, and link-like image alt text do not introduce hyperlinks. YAML frontmatter is excluded from heading generation.

Same-file and cross-file Markdown fragments are checked against parsed headings and HTML `id`/anchor `name` attributes. Duplicate heading slugs receive numeric suffixes, independently per document; custom anchors do not affect that numbering. The convention follows the [GitHub section-link examples](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#section-links) and the [HTML Pipeline TOC word categories](https://github.com/jch/html-pipeline/blob/v2.14.3/lib/html/pipeline/toc_filter.rb): lowercase ASCII, preserve Unicode letters/marks/numbers and connector punctuation, remove other punctuation, and replace each space with a hyphen. This is a tested local convention, not a call to GitHub's renderer; uncommon Unicode and renderer-specific extensions still need rendered review.

HTML `a`/`img` destinations are inspected, never rendered or executed. Percent-encoded paths are decoded before confinement checks. Portable relative paths may reference files or directories inside the repository; directory fragments require a scanned `README.md`. Absolute, drive, UNC, backslash, and escaping symlink paths are rejected before target file checks. Unlike GitHub's root-relative URL behavior, this repository checker requires explicit relative filesystem paths.

Boundaries:

- HTTP(S) and mailto links are not fetched; this does not establish source availability, freshness, or truth.
- Non-Markdown targets must exist, but their fragments (such as PDF page numbers) are not verified. Local URL queries are ignored for filesystem lookup.
- Undefined reference labels remain plain text under CommonMark; this is not an authoring-intent or malformed-Markdown linter.
- HTML sanitization, footnotes, generated-site anchors, raw HTML heading slug generation, and exact hosted-renderer parity are outside this check. Explicit HTML IDs are supported.
- Fragment checks use only the scanned Markdown corpus; they cannot silently read excluded dependency documents.

## Regression evidence

`tests/foundation/test_manifest_validation.py` mutates in-memory copies of repository documents. The initial run reproduced accepted empty/duplicate entries and type errors in manifest validation. Tests now cover these failures, missing referenced skills, valid cross-fixture references, out-of-bound paths, resolved-link escapes, mutation syntax, schema roots, and frontmatter types. No real job data or machine access is used.

`tests/foundation/test_markdown_references.py` adds 21 checks using disposable documentation trees. Cases cover reference variants, images, code exclusion, duplicate/formatted/Unicode headings, custom anchors, table links, escaped/encoded filenames, directories, and path escapes. Boundary tests assert that forbidden targets are rejected before filesystem existence probes. These are parser/validator tests, not browser-rendering tests.

```text
python -m unittest tests.foundation.test_manifest_validation -v
python -m unittest tests.foundation.test_markdown_references -v
python scripts/validate_foundation.py
python scripts/validate_schema_instances.py
python -m unittest discover -s tests -v
```

## Unfinished acceptance work

- The 14 existing skills now declare version, maintenance owner, and supported review levels under string-valued AgentSkills metadata. Tests cover the schema-like contract and compatibility with routed default levels; this is not evidence of skill behavior in a practitioner job.
- Parsed Markdown link and anchor checks are implemented within the scope above. External source verification and renderer-specific behavior remain separate review responsibilities.
- Syntax and path checks do not prove that a fixture mutation represents the claimed physical/geometric defect, that a source claim is true, or that a skill behaves correctly in an agent run.
- Required document contents, schema semantics, source applicability, remaining safety cases, and real-input practitioner evidence remain subject to the [roadmap reconciliation](roadmap-reconciliation.md).
