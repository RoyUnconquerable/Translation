"""Shared helpers for the translation pipeline."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

DEFAULT_CONFIG = {
    "source_lang": "zh",
    "target_lang": "en",
    "source_script": "cjk",
    "strict_numbers": False,
    "ratio_bounds": [0.6, 4.5],
    "allowed_source_chars": "",
    "term_min_count": 3,
}

CJK_RANGES = (
    (0x4E00, 0x9FFF),
    (0x3400, 0x4DBF),
    (0xF900, 0xFAFF),
    (0x20000, 0x2A6DF),
    (0x2A700, 0x2EBEF),
    (0x30000, 0x3134F),
)

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
    """Use UTF-8 for Chinese terms on legacy consoles."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def find_root(start: Path | None = None) -> Path:
    """Return the chatgpt pipeline directory."""
    here = (Path(start) if start else Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "config.json").is_file() and (candidate / "chapters").is_dir():
            return candidate
        nested = candidate / "chatgpt"
        if (nested / "config.json").is_file() and (nested / "chapters").is_dir():
            return nested
    raise SystemExit(
        "error: could not find chatgpt/config.json in this directory or any parent"
    )


def load_config(root: Path | None = None) -> dict:
    root = root or find_root()
    cfg = dict(DEFAULT_CONFIG)
    with open(root / "config.json", encoding="utf-8") as fh:
        cfg.update(json.load(fh))
    return cfg


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{path.name} line {lineno}: invalid JSON ({exc})"
                ) from None
            if not isinstance(row, dict):
                raise ValueError(f"{path.name} line {lineno}: expected an object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_tsv(path: Path, required: tuple[str, ...]) -> list[dict[str, str]]:
    """Read a strict UTF-8 TSV and reject malformed or duplicate headers."""
    try:
        fh = open(path, newline="", encoding="utf-8")
    except FileNotFoundError:
        raise ValueError(f"missing file: {path}") from None
    with fh:
        reader = csv.DictReader(fh, delimiter="\t")
        fields = tuple(reader.fieldnames or ())
        missing = [name for name in required if name not in fields]
        if missing:
            raise ValueError(f"{path.name}: missing columns: {', '.join(missing)}")
        if len(fields) != len(set(fields)):
            raise ValueError(f"{path.name}: duplicate column names")
        rows = []
        for lineno, row in enumerate(reader, 2):
            if None in row:
                raise ValueError(f"{path.name} line {lineno}: too many columns")
            clean = {key: (value or "").strip() for key, value in row.items()}
            if not any(clean.values()):
                continue
            rows.append(clean)
    return rows


def is_cjk(ch: str) -> bool:
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in CJK_RANGES)


def glossary_paths(root: Path) -> list[Path]:
    """Return the single hard glossary path.

    Per-chapter override files are intentionally excluded. Conflicting rows
    must be resolved in the canonical table instead of by filename order.
    """
    return [root / "glossary" / "terminology.tsv"]


def load_glossary(root: Path | None = None) -> dict[str, dict]:
    root = root or find_root()
    path = glossary_paths(root)[0]
    entries: dict[str, dict] = {}
    for lineno, row in enumerate(read_tsv(path, ("source", "target", "notes")), 2):
        source = row["source"]
        target = row["target"]
        if not source or not target:
            raise ValueError(f"{path.name} line {lineno}: source and target are required")
        if source in entries:
            raise ValueError(f"{path.name} line {lineno}: duplicate source key {source!r}")
        variants = [value.strip() for value in target.split("|") if value.strip()]
        if not variants:
            raise ValueError(f"{path.name} line {lineno}: no target variants")
        exceptions = [
            value.strip()
            for group in re.findall(r"\[except:\s*([^\]]+)\]", row["notes"])
            for value in group.split("|")
            if value.strip()
        ]
        entries[source] = {
            "source": source,
            "target": target,
            "variants": variants,
            "notes": row["notes"],
            "exceptions": exceptions,
            "file": path.name,
        }
    return entries


def load_entities(root: Path | None = None) -> list[dict[str, str]]:
    root = root or find_root()
    return read_tsv(
        root / "glossary" / "entities.tsv",
        ("entity_id", "source_aliases", "english_names", "pronouns", "notes"),
    )


PHRASE_SCOPES = {"fixed", "image", "sense"}


def load_phrase_memory(root: Path | None = None) -> list[dict[str, str]]:
    root = root or find_root()
    path = root / "glossary" / "phrase-memory.tsv"
    rows = read_tsv(
        path,
        ("source", "target", "scope", "notes"),
    )
    for lineno, row in enumerate(rows, 2):
        if row["scope"] not in PHRASE_SCOPES:
            raise ValueError(
                f"{path.name} line {lineno}: invalid phrase scope {row['scope']!r}"
            )
        if not row["notes"]:
            raise ValueError(f"{path.name} line {lineno}: notes are required")
        if row["scope"] != "fixed" and row["target"].endswith((".", "!", "?")):
            raise ValueError(
                f"{path.name} line {lineno}: adaptive phrase target is a sentence template"
            )
    return rows
