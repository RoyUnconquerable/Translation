"""Stage 2: glossary tooling.

Usage:
  python3 glossary.py candidates <chapter>    propose new term candidates
  python3 glossary.py add <source> <target> [--note NOTE] [--force]
  python3 glossary.py list                    print the effective glossary

`candidates` proposes strings and counts only; it never invents renderings.
The model curates, the human approves. In CJK mode it counts every 2-4
character Han n-gram at or above term_min_count, prefers the longest match,
and drops anything already in the effective glossary. In Latin mode it counts
repeated capitalized token sequences instead.

`add` writes only to the canonical terminology table. Forced changes replace
the existing row in place so duplicate keys cannot become an override system.
"""

from __future__ import annotations

import argparse
import re
import signal
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

GLOSSARY_HEADER = "source\ttarget\tnotes"

LATIN_STOPWORDS = {
    "The", "A", "An", "And", "But", "Or", "Not", "No", "Yes", "If", "So",
    "He", "She", "It", "They", "We", "You", "I", "His", "Her", "Its",
    "Their", "Our", "Your", "My", "That", "This", "These", "Those", "There",
    "Here", "What", "Who", "Why", "How", "When", "Where", "Then", "Than",
    "As", "At", "In", "On", "Of", "To", "By", "For", "From", "With",
    "Now", "After", "Before", "Even", "Only", "Once", "While", "Yet",
}


def overlapping_count(text: str, term: str) -> int:
    if not term:
        return 0
    count = 0
    start = 0
    while True:
        idx = text.find(term, start)
        if idx == -1:
            return count
        count += 1
        start = idx + 1


def cjk_ngram_counts(texts: list[str], lo: int = 2, hi: int = 4) -> Counter:
    counts: Counter = Counter()
    for text in texts:
        for i, ch in enumerate(text):
            if not common.is_cjk(ch):
                continue
            for size in range(lo, hi + 1):
                gram = text[i:i + size]
                if len(gram) == size and all(common.is_cjk(c) for c in gram):
                    counts[gram] += 1
    return counts


def latin_seq_counts(texts: list[str]) -> Counter:
    seq_re = re.compile(r"\b[A-Z][\w'-]*(?:[ ]+[A-Z][\w'-]*)*")
    counts: Counter = Counter()
    for text in texts:
        for match in seq_re.finditer(text):
            seq = re.sub(r"\s+", " ", match.group(0))
            if " " not in seq and seq in LATIN_STOPWORDS:
                continue
            counts[seq] += 1
    return counts


def pick_candidates(counts: Counter, glossary_sources: list[str],
                    text: str, min_count: int) -> list[str]:
    """Apply frequency floor, longest-match preference, and known suppression."""
    occ_cache: dict[str, int] = {}

    def occ(term: str) -> int:
        if term not in occ_cache:
            occ_cache[term] = overlapping_count(text, term)
        return occ_cache[term]

    known = set(glossary_sources)
    longer_pool = [s for s in glossary_sources if len(s) >= 2]
    kept: list[str] = []
    eligible = sorted(
        (g for g, c in counts.items() if c >= min_count and g not in known),
        key=lambda g: (-len(g), -counts[g], g),
    )
    for gram in eligible:
        supers = [s for s in kept + longer_pool if len(s) > len(gram) and gram in s]
        covered = sum(occ(s) * s.count(gram) for s in supers)
        if counts[gram] - covered >= min_count:
            kept.append(gram)
    return sorted(kept, key=lambda g: (-counts[g], -len(g), g))


def sample_context(segments: list[dict], term: str, width: int = 18) -> tuple[str, str]:
    for seg in segments:
        src = seg.get("src", "")
        idx = src.find(term)
        if idx != -1:
            start = max(0, idx - width)
            end = min(len(src), idx + len(term) + width)
            snippet = ("..." if start > 0 else "") + src[start:end] \
                + ("..." if end < len(src) else "")
            return seg.get("id", ""), snippet
    return "", ""


def load_archive(root: Path, current_chapter: str) -> list[tuple[str, list[dict], dict]]:
    """Load earlier chapters' segments and drafted targets for precedent search."""
    archive = []
    suffix = ".segments.jsonl"
    work_dir = root / "chapters" / "work"
    for seg_path in sorted(work_dir.glob(f"*{suffix}")):
        chapter = seg_path.name[: -len(suffix)]
        if chapter == current_chapter:
            continue
        try:
            segments = common.read_jsonl(seg_path)
        except ValueError:
            continue
        tgt_by_id: dict = {}
        draft_path = work_dir / f"{chapter}.draft.jsonl"
        if draft_path.is_file():
            try:
                tgt_by_id = {
                    row.get("id"): row.get("tgt", "")
                    for row in common.read_jsonl(draft_path)
                }
            except ValueError:
                pass
        archive.append((chapter, segments, tgt_by_id))
    return archive


def find_precedent(archive: list, term: str, width: int = 90) -> tuple[str, str] | None:
    """Return the first earlier segment containing the term and its English."""
    for _chapter, segments, tgt_by_id in archive:
        for seg in segments:
            if term in seg.get("src", ""):
                tgt = (tgt_by_id.get(seg.get("id")) or "").strip()
                if tgt:
                    if len(tgt) > width:
                        tgt = tgt[:width] + "..."
                    return seg.get("id", ""), tgt
    return None


def active_write_path(root: Path) -> Path:
    """Return the sole hard terminology table."""
    return root / "glossary" / "terminology.tsv"


def cmd_candidates(args: argparse.Namespace) -> int:
    root = common.find_root()
    cfg = common.load_config(root)
    glossary = common.load_glossary(root)
    seg_path = root / "chapters" / "work" / f"{args.chapter}.segments.jsonl"
    if not seg_path.is_file():
        raise SystemExit(f"error: no segments file for '{args.chapter}'; run segment.py first")
    segments = common.read_jsonl(seg_path)
    texts = [seg.get("src", "") for seg in segments]
    min_count = int(cfg.get("term_min_count", 3))

    archive = load_archive(root, args.chapter)
    archive_texts = [seg.get("src", "") for _, asegs, _ in archive for seg in asegs]

    is_cjk_mode = cfg.get("source_script", "cjk") == "cjk"
    count_fn = cjk_ngram_counts if is_cjk_mode else latin_seq_counts
    counts = count_fn(texts)
    archive_counts = count_fn(archive_texts) if archive_texts else Counter()

    combined = Counter(counts)
    combined.update({g: c for g, c in archive_counts.items() if g in counts})
    text_all = "\n".join(texts + archive_texts)
    candidates = set(pick_candidates(combined, list(glossary), text_all, min_count))
    if is_cjk_mode:
        # Formal bracketed terms matter even when they occur only once.
        for text in texts:
            for term in re.findall(r"【([^】]+)】", text):
                if term and term not in glossary:
                    candidates.add(term)
    candidates = sorted(
        candidates,
        key=lambda term: (-counts.get(term, 1), -len(term), term),
    )

    if not candidates:
        print(f"no new candidates in {args.chapter} at term_min_count={min_count}")
        return 0
    print(
        f"{len(candidates)} candidate(s) in {args.chapter} "
        f"(cumulative frequency >= {min_count}, longest match preferred, "
        "effective glossary excluded):"
    )
    for term in candidates:
        seg_id, snippet = sample_context(segments, term)
        line = f"  {term}\tx{counts[term]}"
        if archive_counts.get(term):
            line += f" (+{archive_counts[term]} earlier)"
        print(f"{line}\t[{seg_id}] {snippet}")
        precedent = find_precedent(archive, term)
        if precedent:
            print(f"      precedent [{precedent[0]}] {precedent[1]}")
    print(
        "\nCurate this list, propose renderings, and get the owner's approval; "
        "then record each with: glossary.py add <source> <target> [--note ...]\n"
        "Consistency outranks novelty. Where a precedent line shows an earlier "
        "rendering, propose it unless the owner overrules it."
    )
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    root = common.find_root()
    source = args.source.strip()
    target = args.target.strip()
    note = (args.note or "").strip()
    for name, value in (("source", source), ("target", target), ("note", note)):
        if "\t" in value or "\n" in value:
            raise SystemExit(f"error: {name} must not contain tabs or newlines")
    if not source or not target:
        raise SystemExit("error: source and target must be non-empty")

    glossary = common.load_glossary(root)
    existing = glossary.get(source)
    if existing and not args.force:
        raise SystemExit(
            f"error: '{source}' is already in the glossary as '{existing['target']}'; "
            "use --force to override with a new authoritative row"
        )

    path = active_write_path(root)
    if not path.is_file():
        path.write_text(GLOSSARY_HEADER + "\n", encoding="utf-8")
    lines = path.read_text(encoding="utf-8").splitlines()
    replacement = f"{source}\t{target}\t{note}"
    if existing:
        replaced = False
        for index, line in enumerate(lines):
            if line.split("\t", 1)[0].strip() == source:
                lines[index] = replacement
                replaced = True
                break
        if not replaced:
            raise SystemExit(f"error: canonical row for {source!r} disappeared")
    else:
        lines.append(replacement)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        f"added to {path.name}: {source} -> {target}"
        + (f"  ({note})" if note else "")
    )
    if existing:
        print(
            f"replaced existing rendering '{existing['target']}'; "
            "earlier chapters may need re-checking against the new rendering"
        )
    return 0


def cmd_list(_args: argparse.Namespace) -> int:
    glossary = common.load_glossary(common.find_root())
    if not glossary:
        print("glossary is empty")
        return 0
    rows = [("source", "target", "notes", "file")] + [
        (
            entry["source"],
            entry["target"],
            entry["notes"],
            entry.get("file", ""),
        )
        for entry in glossary.values()
    ]
    widths = [max(len(row[i]) for row in rows) for i in range(4)]
    for row in rows:
        print(
            f"{row[0]:<{widths[0]}}  {row[1]:<{widths[1]}}  "
            f"{row[2]:<{widths[2]}}  {row[3]}".rstrip()
        )
    return 0


def main() -> None:
    common.configure_stdio()
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_cand = sub.add_parser("candidates", help="propose new term candidates for a chapter")
    p_cand.add_argument("chapter")
    p_cand.set_defaults(func=cmd_candidates)

    p_add = sub.add_parser("add", help="append an authoritative glossary entry")
    p_add.add_argument("source")
    p_add.add_argument("target", help="rendering; pipe-separate legitimate variants")
    p_add.add_argument("--note", default="")
    p_add.add_argument(
        "--force",
        action="store_true",
        help="override an existing source with a new authoritative row",
    )
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="print the effective glossary table")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
