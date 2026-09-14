"""Offline link checks against small, disposable documentation trees."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.markdown_references import validate_documents


class MarkdownReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def check(self, documents, assets=()):
        contents = {}
        for name, content in documents.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            contents[path] = content
        for name in assets:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        return validate_documents(self.root, contents)

    def test_inline_reference_collapsed_shortcut_and_image_links(self):
        errors = self.check({"README.md": '''[inline](guide.md "Title")
[full][Guide]
[guide][]
[guide]
![figure][image]

[guide]: guide.md
[image]: figure.svg
''', "guide.md": "# Guide"}, ["figure.svg"])
        self.assertEqual(errors, [])

    def test_missing_reference_targets_and_images_fail(self):
        for content in ("[x][ref]\n\n[ref]: missing.md", "![x](missing.svg)",
                        "[unused]: missing.md"):
            with self.subTest(content=content):
                self.assertTrue(self.check({"README.md": content}))

    def test_code_examples_and_comments_are_not_links(self):
        content = '''`[inline](missing.md)`

```markdown
[fenced][ref]
[ref]: missing.md
# Not a heading
```

    [indented](missing.md)

<!-- <a href="missing.md">comment</a> -->
'''
        self.assertEqual(self.check({"README.md": content}), [])

    def test_same_and_cross_file_heading_anchors(self):
        self.assertEqual(self.check({
            "README.md": "# Home\n[here](#home) [there](guide.md#setup)",
            "guide.md": "Setup\n=====\n[home](README.md#home)",
        }), [])

    def test_duplicate_formatted_unicode_and_code_headings(self):
        content = '''# Hello *world* `code`!
# Hello world code!
# Hello world code-1
# Café 你好
[first](#hello-world-code)
[second](#hello-world-code-1)
[collision](#hello-world-code-1-1)
[unicode](#caf%C3%A9-%E4%BD%A0%E5%A5%BD)
'''
        self.assertEqual(self.check({"README.md": content}), [])

    def test_missing_anchors_and_headings_only_in_code_fail(self):
        for target in ("#missing", "guide.md#missing", "guide.md#fake"):
            with self.subTest(target=target):
                errors = self.check({"README.md": f"[x]({target})",
                                     "guide.md": "# Real\n\n```\n# Fake\n```"})
                self.assertTrue(any("anchor" in error for error in errors), errors)

    def test_github_documented_greek_heading_and_custom_anchor_numbering(self):
        content = """# This'll be a _Helpful_ Section About the Greek Letter Θ!
[example](#thisll-be-a-helpful-section-about-the-greek-letter-Θ)
<a name="guide"></a>

# Guide
# Guide
[duplicate](#guide-1)
"""
        self.assertEqual(self.check({"README.md": content}), [])

    def test_table_links_and_strikethrough_headings_are_parsed(self):
        content = """# ~~Old~~ Setup

| Link |
| --- |
| [valid](#old-setup) |
"""
        self.assertEqual(self.check({"README.md": content}), [])
        self.assertTrue(self.check({"README.md": content.replace("#old-setup", "#missing")}))

    def test_image_alt_text_does_not_create_nested_links(self):
        content = "![[not a hyperlink](missing.md)](figure.svg)"
        self.assertEqual(self.check({"README.md": content}, ["figure.svg"]), [])

    def test_html_anchors_in_code_do_not_exist(self):
        content = '`<a name="fake"></a>`\n\n[missing](#fake)'
        self.assertTrue(self.check({"README.md": content}))

    def test_duplicate_counters_reset_per_document(self):
        self.assertEqual(self.check({"README.md": "# Guide\n[x](guide.md#guide)",
                                     "guide.md": "# Guide\n[x](README.md#guide)"}), [])

    def test_frontmatter_does_not_create_headings(self):
        content = "---\nname: sample\n---\n# Real\n[x](#name-sample)"
        self.assertTrue(self.check({"README.md": content}))

    def test_html_links_images_and_custom_anchors(self):
        content = '''<a id="custom"></a>
<a name="legacy"></a>
[id](#custom) [name](#legacy)
<a href="guide.md#guide">Guide</a> <img src="figure.svg">
'''
        self.assertEqual(self.check({"README.md": content, "guide.md": "# Guide"}, ["figure.svg"]), [])
        self.assertTrue(self.check({"README.md": '<a href="missing.md">Missing</a>'}))

    def test_parentheses_spaces_entities_and_query(self):
        content = r'''[parentheses](guide(v1).md#guide)
[spaces](<my guide.md#guide> "title")
[escaped](guide\(v1\).md#guide)
[encoded](my%20guide.md?plain=1#guide)
[entity](a&amp;b.md)
'''
        self.assertEqual(self.check({"README.md": content, "guide(v1).md": "# Guide",
                                     "my guide.md": "# Guide", "a&b.md": "# Guide"}), [])

    def test_external_urls_are_not_fetched_and_empty_fragments_pass(self):
        content = "[web](https://example.invalid/missing#anchor) [mail](mailto:x@example.invalid) [top](#) [self]()"
        self.assertEqual(self.check({"README.md": content}), [])

    def test_directory_and_shared_relative_links(self):
        self.assertEqual(self.check({"README.md": "[dir](docs/) [heading](docs/#guide)",
                                     "docs/README.md": "# Guide\n[root](../README.md)"}), [])

    def test_unsafe_paths_rejected_before_target_probe(self):
        for target in ("../private.md", "%2e%2e/private.md", "%2Fprivate.md",
                       "C:/private.md", "C%3A/private.md", "//server/private.md",
                       "file:///private.md", "javascript:alert(1)", "private%5Cfile.md"):
            with self.subTest(target=target), patch.object(Path, "is_file", side_effect=AssertionError("outside probe")):
                errors = validate_documents(self.root, {self.root / "README.md": f"[x]({target})"})
                self.assertTrue(errors)

    def test_resolved_symlink_escape_is_rejected_before_probe(self):
        alias = self.root / "alias.md"
        resolve = Path.resolve
        with patch.object(Path, "resolve", lambda path, *a, **kw: self.root.parent / "outside.md" if path == alias else resolve(path, *a, **kw)), \
             patch.object(Path, "is_file", side_effect=AssertionError("outside probe")):
            errors = validate_documents(self.root, {self.root / "README.md": "[x](alias.md#secret)"})
        self.assertTrue(any("outside" in error for error in errors), errors)

    def test_non_markdown_fragments_only_check_file_existence(self):
        self.assertEqual(self.check({"README.md": "[pdf](drawing.pdf#page=2)"}, ["drawing.pdf"]), [])

    def test_unresolved_reference_syntax_is_commonmark_plain_text(self):
        self.assertEqual(self.check({"README.md": "[text][undefined] [literal]"}), [])

    def test_unscanned_markdown_anchor_does_not_trigger_read(self):
        errors = self.check({"README.md": "[x](excluded.md#heading)"}, ["excluded.md"])
        self.assertTrue(any("not scanned" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
