"""Apply already-decided exact texts to draft lines, deterministically.

Usage:
  python3 patch.py <chapter> --set <id> <tgt> [--set <id> <tgt> ...]

This is NOT a translation tool. It exists for edits whose exact final text
is already decided - the owner's own wording, or conductor-specified
mechanical fixes (casing, punctuation, quote marks, banned glyphs). Anything
requiring translation judgment still needs a source-grounded translation pass.

Validates the file contract (same ids, same order, same count), writes the
draft, then re-lints the chapter and prints the result. Exit 0 only if the
patched chapter lints clean.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import lint


def main() -> None:
    common.configure_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chapter")
    parser.add_argument("--set", dest="edits", nargs=2, action="append",
                        metavar=("ID", "TGT"), required=True,
                        help="segment id and its exact replacement tgt")
    args = parser.parse_args()

    root = common.find_root()
    work_dir = root / "chapters" / "work"
    draft_path = work_dir / f"{args.chapter}.draft.jsonl"
    segments_path = work_dir / f"{args.chapter}.segments.jsonl"
    if not draft_path.is_file():
        raise SystemExit(f"error: no draft for '{args.chapter}'")
    rows = common.read_jsonl(draft_path)
    if not segments_path.is_file():
        raise SystemExit(f"error: no segments for '{args.chapter}'")
    segments = common.read_jsonl(segments_path)
    expected_ids = [row.get("id") for row in segments]
    actual_ids = [row.get("id") for row in rows]
    if actual_ids != expected_ids or len(set(actual_ids)) != len(actual_ids):
        raise SystemExit(
            "error: draft contract mismatch (ids/order/count); nothing written"
        )
    by_id = {row.get("id"): row for row in rows}

    for seg_id, tgt in args.edits:
        if seg_id not in by_id:
            raise SystemExit(f"error: id '{seg_id}' not in the draft; nothing written")
        if not tgt.strip():
            raise SystemExit(f"error: empty tgt for '{seg_id}'; nothing written")

    for seg_id, tgt in args.edits:
        by_id[seg_id]["tgt"] = tgt
        print(f"patched {seg_id}")

    common.write_jsonl(draft_path, rows)

    report = lint.lint_chapter(root, common.load_config(root),
                               common.load_glossary(root), args.chapter)
    lint.print_report(report)
    sys.exit(0 if report["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
