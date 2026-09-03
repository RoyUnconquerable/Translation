"""Deterministic checks over file-backed chapter drafts.

Usage:
  python chatgpt/scripts/lint.py <chapter>
  python chatgpt/scripts/lint.py --all
  python chatgpt/scripts/lint.py <chapter> --write-report

Checks are read-only unless ``--write-report`` is explicit.
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
SCENE_BREAK_PREFIX = "---\n\n"
SCENE_BREAK_SUFFIX = "\n\n---"

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
    return [match.group(0).replace(",", "") for match in NUM_RE.finditer(text)]


def paragraph_payload(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if normalized.startswith(SCENE_BREAK_PREFIX):
        normalized = normalized[len(SCENE_BREAK_PREFIX):]
    if normalized.endswith(SCENE_BREAK_SUFFIX):
        normalized = normalized[:-len(SCENE_BREAK_SUFFIX)]
    return normalized


def source_occurrences(text: str, term: str):
    start = 0
    while True:
        index = text.find(term, start)
        if index < 0:
            return
        yield index, index + len(term)
        start = index + 1


def glossary_matches(source: str, glossary: dict[str, dict]) -> list[dict]:
    """Select non-overlapping source terms, longest first.

    This prevents a component key from firing inside a more specific key, such
    as Skyward inside Palace of Soaring Clouds or red dust inside Traversing
    the Mortal Dust.
    """
    occupied: set[int] = set()
    selected: list[dict] = []
    seen: set[str] = set()
    for entry in sorted(
        glossary.values(), key=lambda item: (-len(item["source"]), item["source"])
    ):
        for start, end in source_occurrences(source, entry["source"]):
            excepted = False
            for exception in entry.get("exceptions", []):
                for exception_start, exception_end in source_occurrences(source, exception):
                    if exception_start <= start and end <= exception_end:
                        excepted = True
                        break
                if excepted:
                    break
            if excepted:
                continue
            if any(position in occupied for position in range(start, end)):
                continue
            occupied.update(range(start, end))
            if entry["source"] not in seen:
                selected.append(entry)
                seen.add(entry["source"])
    return selected


def target_has_variant(target: str, variants: list[str]) -> bool:
    """Match lexical targets with boundaries and meaningful case control."""
    for variant in variants:
        forms = [variant, variant + "s", variant + "es", variant + "'s", variant + "s'"]
        for form in forms:
            pattern = r"(?<![A-Za-z0-9_])" + re.escape(form) + r"(?![A-Za-z0-9_])"
            if re.search(pattern, target):
                return True
        if variant and variant[0].islower():
            sentence_form = variant[0].upper() + variant[1:]
            start_pattern = r"^\s*[\"'*]*(?:" + re.escape(sentence_form) + r")(?![A-Za-z0-9_])"
            if re.search(start_pattern, target):
                return True
    return False


def lint_chapter(
    root: Path,
    cfg: dict,
    glossary: dict,
    chapter: str,
    write_report: bool = False,
) -> dict:
    fails: list[dict] = []
    warns: list[dict] = []

    def fail(check: str, seg_id: str, detail: str) -> None:
        fails.append({"check": check, "id": seg_id, "detail": detail})

    def warn(check: str, seg_id: str, detail: str) -> None:
        warns.append({"check": check, "id": seg_id, "detail": detail})

    work_dir = root / "chapters" / "work"
    exception_path = root / "chapters" / "legacy-lint-exceptions.tsv"
    legacy_exceptions: set[tuple[str, str, str]] = set()
    if exception_path.is_file():
        for row in common.read_tsv(
            exception_path, ("chapter", "segment", "source", "reason")
        ):
            legacy_exceptions.add((row["chapter"], row["segment"], row["source"]))
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

    src_by_id = {segment.get("id"): segment.get("src", "") for segment in segments}
    counts: dict[str, int] = {}
    for row in draft:
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id:
            fail("coverage", "", "draft row without an id")
            continue
        counts[row_id] = counts.get(row_id, 0) + 1
        if row_id not in src_by_id:
            fail("coverage", row_id, "invented id")
            continue
        target = row.get("tgt")
        if not isinstance(target, str) or not target.strip():
            fail("coverage", row_id, "empty target")
            continue
        payload = paragraph_payload(target)
        if not payload.strip():
            fail("coverage", row_id, "target contains only a scene break")
        elif "\n" in payload:
            fail("paragraph", row_id, "embedded line break inside one target row")

    for row_id, count in counts.items():
        if count > 1:
            fail("coverage", row_id, f"id appears {count} times")
    for segment in segments:
        row_id = segment.get("id")
        if row_id not in counts:
            fail("coverage", row_id or "", "missing from draft")

    pairs = [
        (row["id"], src_by_id[row["id"]], paragraph_payload(row["tgt"]))
        for row in draft
        if isinstance(row.get("id"), str)
        and row.get("id") in src_by_id
        and counts.get(row.get("id")) == 1
        and isinstance(row.get("tgt"), str)
        and paragraph_payload(row["tgt"]).strip()
    ]

    allowed = set(cfg.get("allowed_source_chars") or "")
    source_is_cjk = cfg.get("source_script", "cjk") == "cjk"
    for row_id, source, target in pairs:
        if source_is_cjk:
            leftover = sorted(
                {char for char in target if common.is_cjk(char) and char not in allowed}
            )
            if leftover:
                fail("source-chars", row_id, "source characters: " + "".join(leftover))

        banned = [
            f"{name} ({char})"
            for char, name in BANNED_STYLE_CHARS.items()
            if char in target and char not in allowed
        ]
        if banned:
            fail("banned-style", row_id, "banned typography: " + ", ".join(banned))

        contractions = list(
            dict.fromkeys(match.group(0) for match in D_CONTRACTION_RE.finditer(target))
        )
        if contractions:
            fail("d-contraction", row_id, "forbidden form: " + ", ".join(contractions))

        if source_is_cjk:
            punctuation = sorted(
                char
                for char in set(target)
                if char in common.CJK_PUNCT
                and char not in allowed
                and char not in BANNED_STYLE_CHARS
            )
            if punctuation:
                fail("cjk-punct", row_id, "CJK punctuation: " + "".join(punctuation))

        for entry in glossary_matches(source, glossary):
            if (chapter, row_id, entry["source"]) in legacy_exceptions:
                continue
            if not target_has_variant(target, entry["variants"]):
                fail(
                    "glossary",
                    row_id,
                    f"{entry['source']!r} requires one of: {entry['target']}",
                )

        target_numbers = set(digit_seqs(target))
        missing_numbers = [
            number
            for number in dict.fromkeys(digit_seqs(source))
            if number not in target_numbers
        ]
        if missing_numbers:
            report = fail if cfg.get("strict_numbers") else warn
            report("numbers", row_id, "missing digits: " + ", ".join(missing_numbers))

    low, high = cfg.get("ratio_bounds", common.DEFAULT_CONFIG["ratio_bounds"])
    ratios = {row_id: len(target) / len(source) for row_id, source, target in pairs if source}
    if ratios:
        median = statistics.median(ratios.values())
        for row_id, ratio in ratios.items():
            if ratio < low or ratio > high:
                warn("ratio", row_id, f"length ratio {ratio:.2f} outside [{low}, {high}]")
            elif ratio < median / MEDIAN_DEVIATION_FACTOR or ratio > median * MEDIAN_DEVIATION_FACTOR:
                warn("ratio", row_id, f"length ratio {ratio:.2f}, median {median:.2f}")

    report = {
        "chapter": chapter,
        "status": "pass" if not fails else "fail",
        "fails": fails,
        "warns": warns,
    }
    if write_report:
        path = work_dir / f"{chapter}.lint.json"
        path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report


def all_chapters(root: Path) -> list[str]:
    suffix = ".draft.jsonl"
    return sorted(
        path.name[:-len(suffix)]
        for path in (root / "chapters" / "work").glob(f"*{suffix}")
    )


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chapter", nargs="?")
    parser.add_argument("--all", action="store_true", help="check every draft")
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="write chapters/work/<chapter>.lint.json",
    )
    args = parser.parse_args()

    root = common.find_root()
    try:
        glossary = common.load_glossary(root)
    except ValueError as exc:
        raise SystemExit(f"glossary: FAIL\n  {exc}") from None
    cfg = common.load_config(root)
    if args.all:
        chapters = all_chapters(root)
    elif args.chapter:
        chapters = [args.chapter]
    else:
        parser.error("give a chapter name or --all")
    if not chapters:
        print("no file-backed drafts")
        return

    failed = False
    for chapter in chapters:
        report = lint_chapter(root, cfg, glossary, chapter, args.write_report)
        print_report(report)
        failed = failed or report["status"] == "fail"
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
