"""Export the authored wiki pages with hosted links; never publish or overwrite."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/jeremylongworth-source/AgentCADCAM"
# Authored pages use simple inline links. Skip inline code and fenced/indented
# code blocks so example text is preserved. This is not a general Markdown editor.
INLINE = re.compile(r"`+[^`\n]*`+|\]\((?P<destination>[^\s)]+)\)")


def hosted_target(destination: str, page: Path, root: Path) -> str:
    if destination.startswith(("https://", "http://", "mailto:", "#")):
        return destination
    path, separator, fragment = destination.partition("#")
    if any(char in path for char in ("\\", ":", "?", "%", " ")) or path.startswith("/"):
        raise ValueError(f"unsupported wiki destination: {destination}")
    target = (page.parent / path).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError(f"missing or out-of-repository wiki target: {destination}")
    if target.parent == root / "docs" / "wiki" and target.suffix == ".md":
        url = f"{REPOSITORY}/wiki/{target.stem}"
    else:
        url = f"{REPOSITORY}/blob/main/{target.relative_to(root).as_posix()}"
    return url + (f"#{fragment}" if separator else "")


def render_page(content: str, page: Path, root: Path) -> str:
    lines = content.splitlines(keepends=True)
    protected = set()
    for token in MarkdownIt().parse(content):
        if token.type in {"fence", "code_block"} and token.map:
            protected.update(range(*token.map))

    def replace(match):
        destination = match.group("destination")
        if destination is None:
            return match.group(0)
        return "](" + hosted_target(destination, page, root) + ")"

    return "".join(line if index in protected else INLINE.sub(replace, line)
                   for index, line in enumerate(lines))


def export(root: Path, output: Path) -> int:
    root, output = root.resolve(), output.resolve()
    build = (root / "build").resolve()
    if not build.is_relative_to(root) or not output.is_relative_to(build) or output == build:
        raise ValueError("wiki output must be a new directory below repository build/")
    if output.exists():
        raise ValueError("wiki output already exists; choose a new build subdirectory")
    pages = sorted((root / "docs" / "wiki").glob("*.md"))
    if not pages or not any(page.name == "Home.md" for page in pages):
        raise ValueError("wiki source must include Home.md")
    rendered = {}
    for page in pages:
        if not page.resolve().is_relative_to(root):
            raise ValueError("wiki source resolves outside repository")
        rendered[page.name] = render_page(page.read_text(encoding="utf-8"), page, root)
    output.mkdir(parents=True, exist_ok=False)
    for name, content in rendered.items():
        (output / name).write_text(content, encoding="utf-8", newline="\n")
    return len(rendered)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "wiki")
    args = parser.parse_args()
    try:
        count = export(ROOT, args.output)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Wiki export failed: {exc}\n")
    print(f"Exported {count} wiki files to {args.output.resolve()}; nothing published.")
