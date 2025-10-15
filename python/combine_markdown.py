#!/usr/bin/env python3
"""Combine all Markdown files in the repository into result.md."""
from __future__ import annotations

from pathlib import Path


def find_markdown_files(root: Path, output_file: Path) -> list[Path]:
    """Return a sorted list of markdown files under root, skipping output_file."""
    markdown_files = []
    for path in root.rglob("*.md"):
        if path == output_file:
            continue
        markdown_files.append(path)
    # Sort by relative path to keep deterministic order regardless of platform.
    return sorted(markdown_files, key=lambda p: str(p.relative_to(root)))


def combine_markdown(root: Path) -> Path:
    """Write concatenated markdown content to result.md and return the path."""
    output_file = root / "result.md"
    markdown_files = find_markdown_files(root, output_file)

    with output_file.open("w", encoding="utf-8") as out:
        for md_path in markdown_files:
            rel_path = md_path.relative_to(root)
            # Add a heading so the source of each section is obvious in the result.
            out.write(f"# {rel_path.as_posix()}\n\n")
            out.write(md_path.read_text(encoding="utf-8"))
            out.write("\n\n")
    return output_file


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output_file = combine_markdown(root)
    print(f"Combined markdown written to {output_file}")


if __name__ == "__main__":
    main()
