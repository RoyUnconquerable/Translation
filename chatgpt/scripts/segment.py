"""Stage 1: ingest a raw chapter and write chapters/work/<chapter>.segments.jsonl.

Usage: python3 segment.py <source-file> [--chapter NAME]

Normalizes the raw text (BOM, NFC, newlines), splits it into paragraphs
(blank-line separated when the file has blank lines, otherwise one
paragraph per line, which is how web-novel raws usually arrive), assigns
chapter-scoped zero-padded ids, and prints ingest stats.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common


def normalize(text: str) -> str:
    text = text.lstrip("\ufeff")
    text = unicodedata.normalize("NFC", text)
    return text.replace("\r\n", "\n").replace("\r", "\n")


def split_paragraphs(text: str) -> list[str]:
    if re.search(r"\n[ \t　]*\n", text):
        blocks = re.split(r"\n[ \t　]*\n+", text)
    else:
        blocks = text.split("\n")
    paragraphs = []
    for block in blocks:
        # a blank-line-separated paragraph may still wrap over several lines
        para = " ".join(part.strip() for part in block.split("\n") if part.strip())
        if para:
            paragraphs.append(para)
    return paragraphs


def estimate_tokens(text: str) -> int:
    """Rough token estimate: one per Han character, one per ~4 other chars."""
    cjk = sum(1 for ch in text if common.is_cjk(ch))
    return cjk + round((len(text) - cjk) / 4)


def main() -> None:
    common.configure_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="raw source file, e.g. chapters/source/ch012.txt")
    parser.add_argument("--chapter", help="chapter name (default: the source file's stem)")
    args = parser.parse_args()

    root = common.find_root()
    src_path = Path(args.source)
    if not src_path.is_file():
        src_path = root / args.source
    if not src_path.is_file():
        raise SystemExit(f"error: source file not found: {args.source}")

    chapter = args.chapter or src_path.stem
    paragraphs = split_paragraphs(normalize(src_path.read_text(encoding="utf-8-sig")))
    if not paragraphs:
        raise SystemExit(f"error: no paragraphs found in {src_path}")

    width = max(4, len(str(len(paragraphs))))
    rows = [
        {"id": f"{chapter}-{i:0{width}d}", "src": para}
        for i, para in enumerate(paragraphs, 1)
    ]
    out_path = root / "chapters" / "work" / f"{chapter}.segments.jsonl"
    common.write_jsonl(out_path, rows)

    chars = sum(len(p) for p in paragraphs)
    tokens = sum(estimate_tokens(p) for p in paragraphs)
    print(f"chapter:  {chapter}")
    print(f"segments: {len(rows)}")
    print(f"chars:    {chars}")
    print(f"~tokens:  {tokens}")
    print(f"wrote:    {out_path.relative_to(root)}")


if __name__ == "__main__":
    main()
