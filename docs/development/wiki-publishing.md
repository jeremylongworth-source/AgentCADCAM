# Wiki publication and maintenance

## Source and initial availability

Wiki content is maintained in `docs/wiki/`: seven guides plus `_Sidebar.md` and
`_Footer.md`. It is readable in the repository before the hosted wiki exists.
The roadmap, schemas and architecture contracts remain authoritative.

On 2026-09-17, both the CLI enable request and a direct repository update left
`has_wiki: false`; visibility remained private. The wiki Git remote returned
“Repository not found.” No hosted pages were published, no account plan was
changed, and no repository visibility change was made. The response alone does
not establish the exact eligibility or configuration cause.

Later on 2026-09-17, the API reported public visibility and `has_wiki: true`.
The wiki Git remote became available on `master`, with an initial Home page
containing only the default welcome message at `b68d2a3`. No visibility change
was made by this agent. The prepared source can now use the publishing workflow
below; confirm the hosted result before calling an export published.

[GitHub documents](https://docs.github.com/en/communities/documenting-your-project-with-wikis/about-wikis)
wiki availability for public repositories on Free plans and private repositories
on eligible paid plans. Do not change billing or visibility to unlock the feature
without explicit authorization.

## Review and export

Edit the source pages in the main repository. Use simple inline Markdown links,
relative paths, and ordinary fenced examples; the exporter handles these authored
pages, not arbitrary Markdown. Avoid reference-style links, raw HTML navigation,
link titles, and encoded/space-containing destinations in wiki source.

From the repository root, with test dependencies installed:

```sh
python scripts/validate_foundation.py
python -m unittest tests.foundation.test_wiki_export -v
python scripts/export_wiki.py
```

The exporter writes nine files to ignored `build/wiki/`, converts wiki navigation
to hosted page URLs, and converts repository references to `blob/main` URLs.
It preserves code examples, rejects missing/out-of-repository link targets,
refuses existing output directories, and does not use Git or the network.
For another export, choose a new directory with `--output build/wiki-next`.
Review the resulting Markdown before publication; automatic checks do not verify
GitHub's live rendering or remote links. The exported links track `main`, not a
versioned release. Keep release-specific documentation tied to its source commit.

## Publish when the wiki is available

1. Confirm repository visibility, disclosure authorization and wiki availability.
   Enabling a wiki is not permission to publish a private repository.
2. Create the initial Home page through GitHub's Wiki interface if needed. GitHub
   requires an initial page before the documented clone workflow; see
   [adding wiki pages](https://docs.github.com/en/communities/documenting-your-project-with-wikis/adding-or-editing-wiki-pages).
3. Clone `https://github.com/jeremylongworth-source/AgentCADCAM.wiki.git` into a
   separate working directory. Inspect its existing pages and default branch.
4. Copy the reviewed export into that checkout. Reconcile existing changes before
   overwriting; do not erase unrelated pages. Commit the intended files with the
   main-repository source commit ID, then push the wiki's observed default branch.
5. Inspect Home, navigation, tables, code blocks, repository links, and narrow and
   wide layouts in GitHub. Confirm sidebar/footer display and record both commit
   IDs. Do not describe the wiki as published before that succeeds.

GitHub recognizes the special sidebar/footer filenames; see
[its sidebar documentation](https://docs.github.com/en/communities/documenting-your-project-with-wikis/creating-a-footer-or-sidebar-for-your-wiki).

## Ongoing maintenance

Review source changes through the main repository, then regenerate and publish.
Bring intentional hosted edits back into `docs/wiki/` before the next export.
Never copy confidential pilot inputs or private reports into wiki pages. Wiki
publication does not close the public-alpha or practitioner gates.
