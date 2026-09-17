"""Documentation export preserves examples and refuses unsafe output paths."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.export_wiki import REPOSITORY, ROOT, export, render_page
from scripts.markdown_references import _parse


class WikiExportTests(unittest.TestCase):
    def test_all_authored_pages_have_resolved_hosted_links(self):
        pages = sorted((ROOT / "docs/wiki").glob("*.md"))
        self.assertEqual(len(pages), 9)
        for page in pages:
            rendered = render_page(page.read_text(encoding="utf-8"), page, ROOT)
            links, _ = _parse(rendered)
            self.assertTrue(links, page.name)
            self.assertTrue(all(link.startswith(("https://", "#")) for link in links), page.name)

    def test_navigation_and_repository_links_preserve_fragments(self):
        page = ROOT / "docs/wiki/Home.md"
        content = "[Start](Getting-Started.md#troubleshooting) [License](../../LICENSE)"
        self.assertEqual(render_page(content, page, ROOT),
                         f"[Start]({REPOSITORY}/wiki/Getting-Started#troubleshooting) "
                         f"[License]({REPOSITORY}/blob/main/LICENSE)")

    def test_code_examples_and_external_links_are_unchanged(self):
        content = "`[x](missing.md)`\n```text\n[x](missing.md)\n```\n\n    [x](missing.md)\n\n[x](https://example.com)\n"
        self.assertEqual(render_page(content, ROOT / "docs/wiki/Home.md", ROOT), content)

    def test_missing_and_escaping_links_are_rejected(self):
        for destination in ("missing.md", "../../../outside.md", "C:/private.md", "/private.md"):
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                render_page(f"[x]({destination})", ROOT / "docs/wiki/Home.md", ROOT)

    def test_export_requires_new_confined_output_and_preserves_source(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "docs/wiki"
            source.mkdir(parents=True)
            (source / "Home.md").write_text("# Home\n", encoding="utf-8")
            output = root / "build/wiki"
            self.assertEqual(export(root, output), 1)
            self.assertEqual((output / "Home.md").read_text(), "# Home\n")
            for invalid in (output, root / "build", root / "outside", root / "build/../../outside"):
                with self.subTest(output=invalid), self.assertRaises(ValueError):
                    export(root, invalid)
            self.assertEqual((source / "Home.md").read_text(), "# Home\n")

    def test_broken_page_does_not_create_partial_export(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "docs/wiki"
            source.mkdir(parents=True)
            (source / "Home.md").write_text("[broken](missing.md)", encoding="utf-8")
            output = root / "build/wiki"
            with self.assertRaises(ValueError):
                export(root, output)
            self.assertFalse(output.exists())
