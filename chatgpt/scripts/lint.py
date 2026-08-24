"""Deterministic checks over drafted chapters.

Usage:
  python chatgpt/scripts/lint.py <chapter>  lint one chapter
  python chatgpt/scripts/lint.py --all      lint every draft

Checks, per segment, source against target:
  coverage       every source id present exactly once, none empty, no invented
                 ids                                            HARD FAILURE
  paragraph      no target row contains an embedded paragraph break
                                                                HARD FAILURE
  source-chars   leftover source-script characters in the target
                                                                HARD FAILURE
  glossary       a glossary source term in a segment's source requires one of
                 its approved target variants                    HARD FAILURE
  banned-style   em/en dashes, curly quotes, single-glyph ellipsis, and other
                 banned typography                               HARD FAILURE
  d-contraction  contractions ending in 'd                       HARD FAILURE
  cjk-punct      other CJK punctuation in the target             warning
  numbers        Arabic digit sequences in the source, comma-normalized, must
                 appear in the target      warning (failure under strict_numbers)
  ratio          length ratio outside ratio_bounds or far from chapter median
                                                                warning

Always writes chapters/work/<chapter>.lint.json.
"""

from __future__ import annotations

import argparse
import json
import re
import signal
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

MEDIAN_DEVIATION_FACTOR = 2.0
NUM_RE = re.compile(r"\d[\d,]*")
D_CONTRACTION_RE = re.compile(r"\b[A-Za-z]+(?:['’])d\b", re.IGNORECASE)

BANNED_STYLE_CHARS = {
    "—": "em dash",
    "–": "en dash",
    "…": "single-glyph ellipsis",
    "“": "left curly double quote",
    "”": "right curly double quote",
    "‘": "left curly single quote",
    "’": "right curly single quote",
}


def digit_seqs(text: str) -> list[str]:
    """Arabic digit runs, comma-normalized, so 1,000 becomes 1000."""
    return [m.group(0).replace(",", "") for m in NUM_RE.finditer(text)]


def _all_occurrences_excepted(src: str, term: str, exceptions: list[str]) -> bool:
    """Return true when every occurrence of term sits inside an exception."""
    spans = []
    for exc in exceptions:
        start = 0
        while True:
            idx = src.find(exc, start)
            if idx == -1:
                break
            spans.append((idx, idx + len(exc)))
            start = idx + 1
    pos = 0
    while True:
        idx = src.find(term, pos)
        if idx == -1:
            return True
        if not any(lo <= idx and idx + len(term) <= hi for lo, hi in spans):
            return False
        pos = idx + 1


def lint_chapter(root: Path, cfg: dict, glossary: dict, chapter: str) -> dict:
    """Run every check for one chapter, write lint.json, and return the report."""
    fails: list[dict] = []
    warns: list[dict] = []

    def fail(check: str, seg_id: str, detail: str) -> None:
        fails.append({"check": check, "id": seg_id, "detail": detail})

    def warn(check: str, seg_id: str, detail: str) -> None:
        warns.append({"check": check, "id": seg_id, "detail": detail})

    work_dir = root / "chapters" / "work"
    seg_path = work_dir / f"{chapter}.segments.jsonl"
    draft_path = work_dir / f"{chapter}.draft.jsonl"
    segments: list[dict] = []
    draft: list[dict] = []

    if seg_path.is_file():
        try:
            segments = common.read_jsonl(seg_path)
        except ValueError as exc:
            fail("coverage", "", str(exc))
    else:
        fail("coverage", "", f"segments file missing: {seg_path.name}")

    if draft_path.is_file():
        try:
            draft = common.read_jsonl(draft_path)
        except ValueError as exc:
            fail("coverage", "", str(exc))
    else:
        fail("coverage", "", f"draft file missing: {draft_path.name}")

    src_by_id = {seg.get("id"): seg.get("src", "") for seg in segments}

    counts: dict[str, int] = {}
    for row in draft:
        rid = row.get("id")
        if not isinstance(rid, str) or not rid:
            fail("coverage", "", "draft row without an id")
            continue
        counts[rid] = counts.get(rid, 0) + 1
        if rid not in src_by_id:
            fail("coverage", rid, "invented id: not in the segments file")
            continue
        tgt = row.get("tgt")
        if not isinstance(tgt, str) or not tgt.strip():
            fail("coverage", rid, "empty tgt")
            continue
        if "\n" in tgt or "\r" in tgt:
            fail(
                "paragraph",
                rid,
                "embedded line or paragraph break in tgt; one source row must remain one target paragraph",
            )

    for rid, n in counts.items():
        if n > 1:
            fail("coverage", rid, f"id appears {n} times in the draft")

    for seg in segments:
        rid = seg.get("id")
        if rid not in counts:
            fail("coverage", rid or "", "missing from the draft")

    pairs = [
        (row["id"], src_by_id[row["id"]], row["tgt"])
        for row in draft
        if isinstance(row.get("id"), str)
        and row.get("id") in src_by_id
        and counts.get(row.get("id")) == 1
        and isinstance(row.get("tgt"), str)
        and row["tgt"].strip()
    ]

    allowed = set(cfg.get("allowed_source_chars") or "")
    source_is_cjk = cfg.get("source_script", "cjk") == "cjk"

    for rid, src, tgt in pairs:
        if source_is_cjk:
            leftover = sorted({ch for ch in tgt if common.is_cjk(ch) and ch not in allowed})
            if leftover:
                fail(
                    "source-chars",
                    rid,
                    "source-script characters in target: " + "".join(leftover),
                )

        banned_found = [
            f"{name} ({char})"
            for char, name in BANNED_STYLE_CHARS.items()
            if char in tgt and char not in allowed
        ]
        if banned_found:
            fail("banned-style", rid, "banned typography: " + ", ".join(banned_found))

        d_contractions = list(dict.fromkeys(match.group(0) for match in D_CONTRACTION_RE.finditer(tgt)))
        if d_contractions:
            fail(
                "d-contraction",
                rid,
                "forbidden contraction ending in 'd: " + ", ".join(d_contractions),
            )

        if source_is_cjk:
            punct = sorted(
                {
                    ch
                    for ch in tgt
                    if ch in common.CJK_PUNCT
                    and ch not in allowed
                    and ch not in BANNED_STYLE_CHARS
                }
            )
            if punct:
                warn("cjk-punct", rid, "CJK punctuation in target: " + "".join(punct))

        tgt_lower = tgt.lower()
        for entry in glossary.values():
            if entry["source"] not in src:
                continue
            if entry.get("exceptions") and _all_occurrences_excepted(
                src, entry["source"], entry["exceptions"]
            ):
                continue
            if not any(variant.lower() in tgt_lower for variant in entry["variants"]):
                source_file = entry.get("file", "terminology.tsv")
                fail(
                    "glossary",
                    rid,
                    f"source term '{entry['source']}' not rendered as any of: "
                    f"{entry['target']} ({source_file})",
                )

        tgt_nums = set(digit_seqs(tgt))
        missing = [n for n in dict.fromkeys(digit_seqs(src)) if n not in tgt_nums]
        if missing:
            report = fail if cfg.get("strict_numbers") else warn
            report(
                "numbers",
                rid,
                "digit sequences in source missing from target: " + ", ".join(missing),
            )

    lo, hi = cfg.get("ratio_bounds", common.DEFAULT_CONFIG["ratio_bounds"])
    ratios = {rid: len(tgt) / len(src) for rid, src, tgt in pairs if src}
    if ratios:
        median = statistics.median(ratios.values())
        for rid, ratio in ratios.items():
            if ratio < lo or ratio > hi:
                warn("ratio", rid, f"length ratio {ratio:.2f} outside bounds [{lo}, {hi}]")
            elif ratio < median / MEDIAN_DEVIATION_FACTOR \
                    or ratio > median * MEDIAN_DEVIATION_FACTOR:
                warn(
                    "ratio",
                    rid,
                    f"length ratio {ratio:.2f} far from chapter median {median:.2f}",
                )

    report = {
        "chapter": chapter,
        "status": "pass" if not fails else "fail",
        "fails": fails,
        "warns": warns,
    }
    lint_path = work_dir / f"{chapter}.lint.json"
    lint_path.parent.mkdir(parents=True, exist_ok=True)
    lint_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def all_chapters(root: Path) -> list[str]:
    suffix = ".draft.jsonl"
    work_dir = root / "chapters" / "work"
    return sorted(p.name[: -len(suffix)] for p in work_dir.glob(f"*{suffix}"))


def print_report(report: dict) -> None:
    print(
        f"{report['chapter']}: {report['status'].upper()} "
        f"({len(report['fails'])} fail, {len(report['warns'])} warn)"
    )
    for item in report["fails"]:
        print(f"  FAIL [{item['check']}] {item['id']}: {item['detail']}")
    for item in report["warns"]:
        print(f"  warn [{item['check']}] {item['id']}: {item['detail']}")


def main() -> None:
    common.configure_stdio()
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("chapter", nargs="?", help="chapter name, e.g. ch012")
    parser.add_argument("--all", action="store_true", help="lint every draft")
    args = parser.parse_args()

    root = common.find_root()
    cfg = common.load_config(root)
    glossary = common.load_glossary(root)

    if args.all:
        chapters = all_chapters(root)
        if not chapters:
            print("no drafts in chatgpt/chapters/work/")
            sys.exit(0)
    elif args.chapter:
        chapters = [args.chapter]
    else:
        parser.error("give a chapter name or --all")

    failed = False
    for chapter in chapters:
        report = lint_chapter(root, cfg, glossary, chapter)
        print_report(report)
        failed = failed or report["status"] == "fail"
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
