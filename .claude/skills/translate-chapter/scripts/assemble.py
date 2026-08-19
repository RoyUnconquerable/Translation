"""Stage 7: final assembly and telemetry.

Usage: python3 assemble.py <chapter>

Re-runs the lint checks programmatically and refuses on any failure, joins
the drafted targets in segment order with blank lines into
output/<chapter>.<target_lang>.txt, computes the flag rate from
work/<chapter>.issues.json, and appends a row to work/telemetry.csv:
chapter, segments, flagged, patched, flag_rate.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import lint

FLAG_RATE_ALARM = 0.40


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chapter", help="chapter name, e.g. ch012")
    args = parser.parse_args()
    chapter = args.chapter

    root = common.find_root()
    cfg = common.load_config(root)
    glossary = common.load_glossary(root)

    report = lint.lint_chapter(root, cfg, glossary, chapter)
    if report["fails"]:
        lint.print_report(report)
        raise SystemExit(
            f"refusing to assemble {chapter}: {len(report['fails'])} lint failure(s); "
            "fix the draft first"
        )

    segments = common.read_jsonl(root / "work" / f"{chapter}.segments.jsonl")
    draft = common.read_jsonl(root / "work" / f"{chapter}.draft.jsonl")
    tgt_by_id = {row["id"]: row["tgt"] for row in draft}
    body = "\n\n".join(tgt_by_id[seg["id"]].strip() for seg in segments) + "\n"
    out_path = root / "output" / f"{chapter}.{cfg['target_lang']}.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8")

    issues_path = root / "work" / f"{chapter}.issues.json"
    flagged_ids: set[str] = set()
    patched_ids: set[str] = set()
    if issues_path.is_file():
        issues = json.loads(issues_path.read_text(encoding="utf-8"))
        if not isinstance(issues, list):
            raise SystemExit(f"error: {issues_path.name} must be a JSON array")
        for issue in issues:
            seg_id = issue.get("id", "")
            flagged_ids.add(seg_id)
            if issue.get("patched"):
                patched_ids.add(seg_id)
    else:
        print(f"note: {issues_path.name} not found; recording zero flagged segments")

    seg_count = len(segments)
    flag_rate = round(len(flagged_ids) / seg_count, 4) if seg_count else 0.0

    telemetry_path = root / "work" / "telemetry.csv"
    is_new = not telemetry_path.is_file()
    with open(telemetry_path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if is_new:
            writer.writerow(["chapter", "segments", "flagged", "patched", "flag_rate"])
        writer.writerow([chapter, seg_count, len(flagged_ids), len(patched_ids), flag_rate])

    print(f"assembled: {out_path.relative_to(root)}")
    print(f"segments:  {seg_count}")
    print(f"flagged:   {len(flagged_ids)}   patched: {len(patched_ids)}   "
          f"flag_rate: {flag_rate:.2%}")
    if report["warns"]:
        print(f"lint warnings carried: {len(report['warns'])} "
              f"(see work/{chapter}.lint.json)")
    if seg_count and flag_rate > FLAG_RATE_ALARM:
        print(f"WARNING: flag rate {flag_rate:.2%} exceeds 40% - the review pass was "
              "close to a rewrite. Three consecutive chapters like this means the "
              "drafter model should be upgraded (see the skill's telemetry rule).")
    print("reminder: the reviewer's edits are visible as a git diff between the "
          "draft and review commits.")


if __name__ == "__main__":
    main()
