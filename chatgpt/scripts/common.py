"""Shared helpers for the ChatGPT translation pipeline.

Every stage script imports this module. It is standard-library-only and safe
to run from the repository root or anywhere inside ``chatgpt/``.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DEFAULT_CONFIG = {
    "source_lang": "zh",
    "target_lang": "en",
    "source_script": "cjk",      # "cjk" or "latin"
    "strict_numbers": False,     # number preservation: warn (False) or fail (True)
    "ratio_bounds": [0.6, 4.5],  # sane window for len(tgt)/len(src) per segment
    "allowed_source_chars": "",  # source-script chars permitted in the target
    "term_min_count": 3,         # minimum frequency for a glossary candidate
}

# Main Han ranges: URO, Extension A, compatibility ideographs, and the
# SIP/TIP extension blocks. Kana and Hangul are deliberately out of scope.
CJK_RANGES = (
    (0x4E00, 0x9FFF),    # CJK Unified Ideographs
    (0x3400, 0x4DBF),    # Extension A
    (0xF900, 0xFAFF),    # Compatibility Ideographs
    (0x20000, 0x2A6DF),  # Extension B
    (0x2A700, 0x2EBEF),  # Extensions C-F
    (0x30000, 0x3134F),  # Extension G
)

# Fullwidth / CJK punctuation that should not survive into a Latin-script
# target. Curly quotes, the single-glyph ellipsis, and both long dashes are
# included because the style guide bans them in English output.
CJK_PUNCT = set(
    "、。，；：？！"
    "「」『』〈〉《》"
    "【】〔〕（）"
    "・·…—–～"
    "“”‘’"
    "＂＇｀＝＋－＊／＼｜＜＞＃＄％＆＠＾＿｛｝￥"
    "　"
)


def configure_stdio() -> None:
    """Use UTF-8 for Chinese terms on Windows and other legacy consoles."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def find_root(start: Path | None = None) -> Path:
    """Return the ``chatgpt`` pipeline directory from any repository subdirectory."""
    here = (Path(start) if start else Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "config.json").is_file() \
                and (candidate / "chapters").is_dir():
            return candidate
        nested = candidate / "chatgpt"
        if (nested / "config.json").is_file() \
                and (nested / "chapters").is_dir():
            return nested
    raise SystemExit(
        "error: could not find chatgpt/config.json in this directory or any parent; "
        "run from inside the repository"
    )


def load_config(root: Path | None = None) -> dict:
    """Project config merged over the built-in defaults."""
    root = root or find_root()
    cfg = dict(DEFAULT_CONFIG)
    with open(root / "config.json", encoding="utf-8") as fh:
        cfg.update(json.load(fh))
    return cfg


def read_jsonl(path: Path) -> list[dict]:
    """Read a JSONL file; raise ValueError naming the offending line on bad input."""
    rows = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name} line {lineno}: invalid JSON ({exc})") from None
            if not isinstance(row, dict):
                raise ValueError(f"{path.name} line {lineno}: expected a JSON object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def is_cjk(ch: str) -> bool:
    """True for Han ideographs in the ranges above."""
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in CJK_RANGES)


def glossary_paths(root: Path) -> list[Path]:
    """Return canonical glossary files in override order.

    ``terminology.tsv`` is the base glossary. State-backed owner ruling files
    under ``glossary/owner-rulings-*.tsv`` are loaded afterward in lexical
    order, so the latest chapter-range supplement overrides earlier rows. This
    makes owner corrections enforceable by every script rather than leaving
    them as documentation only.
    """
    glossary_dir = root / "glossary"
    primary = glossary_dir / "terminology.tsv"
    supplements = sorted(glossary_dir.glob("owner-rulings-*.tsv"))
    return [primary, *supplements]


def load_glossary(root: Path | None = None) -> dict[str, dict]:
    """Parse the base terminology TSV and owner ruling supplements.

    Columns are source / target / notes, tab-separated, with a header row. The
    target field may hold pipe-separated variants, for example
    ``qi|spiritual qi``. A later row for the same source overrides an earlier
    one, matching the owner's final-ruling policy.
    """
    root = root or find_root()
    entries: dict[str, dict] = {}

    for path in glossary_paths(root):
        if not path.is_file():
            continue
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                cols = line.split("\t")
                if cols[0].strip().lower() == "source" and len(cols) > 1 \
                        and cols[1].strip().lower() == "target":
                    continue
                if len(cols) < 2 or not cols[0].strip() or not cols[1].strip():
                    continue
                source = cols[0].strip()
                target = cols[1].strip()
                notes = cols[2].strip() if len(cols) > 2 else ""
                exceptions = [
                    item.strip()
                    for group in re.findall(r"\[except:\s*([^\]]+)\]", notes)
                    for item in group.split("|")
                    if item.strip()
                ]
                entries[source] = {
                    "source": source,
                    "target": target,
                    "variants": [v.strip() for v in target.split("|") if v.strip()],
                    "notes": notes,
                    "exceptions": exceptions,
                    "file": path.name,
                }

    return entries
