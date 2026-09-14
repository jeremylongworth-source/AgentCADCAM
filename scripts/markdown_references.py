"""Offline CommonMark/GFM-table links and GitHub-style Markdown anchors.

Parsing never renders HTML or fetches URLs. Callers provide the scanned text;
fragment checks do not open documents outside that corpus.
"""

from __future__ import annotations

import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

from markdown_it import MarkdownIt
from mdurl import decode


def _heading_slug(text, used):
    """Lowercase ASCII, retain Unicode words, and suffix collisions.

    Word categories follow the HTML Pipeline TOC convention (letters, marks,
    numbers, connector punctuation). Hyphens/spaces are retained; each space
    becomes a hyphen. This is a local convention, not a GitHub renderer API.
    """
    base = "".join(
        char.lower() if "A" <= char <= "Z" else char for char in text.strip()
        if char in {"-", " "} or unicodedata.category(char)[0] in {"L", "M", "N"}
        or unicodedata.category(char) == "Pc"
    ).replace(" ", "-")
    slug, count = base, 0
    while slug in used:
        count += 1
        slug = f"{base}-{count}"
    used.add(slug)
    return slug


class _HTMLReferences(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.anchors = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.anchors.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.anchors.add(attrs["name"])
        field = {"a": "href", "img": "src"}.get(tag)
        if field and attrs.get(field) is not None:
            self.links.append(attrs[field])


def _plain_text(tokens):
    parts = []
    for token in tokens:
        if token.type in {"text", "code_inline"}:
            parts.append(token.content)
        elif token.type in {"softbreak", "hardbreak"}:
            parts.append(" ")
        elif token.type == "image":
            parts.append(_plain_text(token.children or []))
    return "".join(parts)


def _parse(content):
    # YAML frontmatter is repository metadata, not a setext Markdown heading.
    content = re.sub(r"\A\ufeff?---[ \t]*\r?\n.*?\r?\n---[ \t]*(?:\r?\n|$)", "", content, count=1, flags=re.DOTALL)
    parser = MarkdownIt("commonmark").enable(["table", "strikethrough"])
    # Collect unsafe destinations too, so they are reported rather than silently
    # dropped by the renderer's URL filter. No rendering occurs in this module.
    parser.validateLink = lambda value: True
    env = {}
    tokens = parser.parse(content, env)
    links = []
    anchors = set()
    used_slugs = set()
    html = _HTMLReferences()

    def visit(items):
        for token in items:
            if token.type == "link_open":
                links.append(token.attrGet("href"))
            elif token.type == "image":
                links.append(token.attrGet("src"))
                # Children describe alt text, not rendered nested hyperlinks.
                continue
            elif token.type in {"html_inline", "html_block"}:
                html.feed(token.content)
            if token.children:
                visit(token.children)

    visit(tokens)
    html.close()
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            anchors.add(_heading_slug(_plain_text(tokens[index + 1].children or []), used_slugs))
    # Include unused definitions: stale destinations should not become hidden
    # defects merely because their current reference was removed.
    links.extend(ref["href"] for ref in env.get("references", {}).values())
    links.extend(html.links)
    anchors.update(html.anchors)
    return list(dict.fromkeys(links)), anchors


def validate_documents(root: Path, documents: dict[Path, str]) -> list[str]:
    """Check rendered local links, definitions, images and Markdown fragments.

    Absolute/UNC/drive paths and unrecognized URL schemes are rejected. HTTP(S)
    and mailto destinations are not fetched. Existing directories are valid;
    their fragments refer to README.md. Non-Markdown fragments are not checked.
    Undefined CommonMark reference labels are plain text, not parsed links.
    """
    errors = []
    root = root.resolve()
    parsed = {}
    for path, content in documents.items():
        try:
            resolved = path.resolve()
            if not resolved.is_relative_to(root):
                errors.append(f"Markdown source outside repository: {path.name}")
                continue
            parsed[resolved] = _parse(content)
        except (OSError, ValueError, RuntimeError, RecursionError) as exc:
            errors.append(f"cannot parse Markdown document {path}: {type(exc).__name__}")

    for path, (links, _) in parsed.items():
        for destination in links:
            label = f"broken Markdown reference in {path.relative_to(root)}: {destination!r}"
            if re.match(r"(?i)^(?:https?://|mailto:)", destination):
                continue
            raw_path, _, raw_fragment = destination.partition("#")
            local = decode(raw_path.partition("?")[0], exclude="")
            fragment = decode(raw_fragment, exclude="")
            if "\\" in local or ":" in local or local.startswith("/") or any(ord(char) < 32 for char in local):
                errors.append(f"{label}: requires a portable relative path or supported external URL")
                continue
            try:
                target = (path.parent / local).resolve() if local else path
                if not target.is_relative_to(root):
                    errors.append(f"{label}: target resolves outside repository")
                    continue
                if not target.is_file():
                    if not target.is_dir():
                        errors.append(f"{label}: referenced file or directory is missing")
                        continue
                    if not fragment:
                        continue
                    target = (target / "README.md").resolve()
                    if not target.is_relative_to(root):
                        errors.append(f"{label}: directory README resolves outside repository")
                        continue
                    if not target.is_file():
                        errors.append(f"{label}: directory anchor requires README.md")
                        continue
                if fragment and target.suffix.lower() == ".md":
                    if target not in parsed:
                        errors.append(f"{label}: Markdown anchor target was not scanned")
                    elif fragment not in parsed[target][1]:
                        errors.append(f"{label}: missing Markdown anchor {fragment!r}")
            except (OSError, ValueError, RuntimeError):
                errors.append(f"{label}: cannot resolve reference")
    return errors
