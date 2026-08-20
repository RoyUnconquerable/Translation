"""Final assembly and telemetry for the ChatGPT pipeline.

Usage: python chatgpt/scripts/assemble.py <chapter>

Re-runs the lint checks programmatically and refuses on any failure, joins
the drafted targets in segment order with blank lines into
chapters/final/<chapter>.<target_lang>.txt, computes the flag rate from
chapters/work/<chapter>.issues.json, and upserts chapters/work/telemetry.csv:
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
    common.configure_stdio()
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

    work_dir = root / "chapters" / "work"
    segments = common.read_jsonl(work_dir / f"{chapter}.segments.jsonl")
    draft = common.read_jsonl(work_dir / f"{chapter}.draft.jsonl")
    segment_ids = {row["id"] for row in segments}

    issues_path = work_dir / f"{chapter}.issues.json"
    flagged_ids: set[str] = set()
    patched_ids: set[str] = set()
    if not issues_path.is_file():
        raise SystemExit(
            f"refusing to assemble {chapter}: {issues_path.name} is missing; "
            "complete the source-grounded review first"
        )
    issues = json.loads(issues_path.read_text(encoding="utf-8"))
    if not isinstance(issues, list):
        raise SystemExit(f"error: {issues_path.name} must be a JSON array")
    for issue in issues:
        seg_id = issue.get("id", "")
        if seg_id not in segment_ids:
            raise SystemExit(
                f"refusing to assemble {chapter}: issue names unknown id '{seg_id}'"
            )
        if not issue.get("patched"):
            raise SystemExit(
                f"refusing to assemble {chapter}: issue for {seg_id} is not patched"
            )
        flagged_ids.add(seg_id)
        patched_ids.add(seg_id)

    tgt_by_id = {row["id"]: row["tgt"] for row in draft}
    body = "\n\n".join(tgt_by_id[seg["id"]].strip() for seg in segments) + "\n"
    out_path = root / "chapters" / "final" / f"{chapter}.{cfg['target_lang']}.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8")

    seg_count = len(segments)
    flag_rate = round(len(flagged_ids) / seg_count, 4) if seg_count else 0.0

    telemetry_path = work_dir / "telemetry.csv"
    fieldnames = ["chapter", "segments", "flagged", "patched", "flag_rate"]
    telemetry: list[dict[str, str]] = []
    if telemetry_path.is_file():
        with open(telemetry_path, newline="", encoding="utf-8") as fh:
            telemetry = [row for row in csv.DictReader(fh)
                         if row.get("chapter") != chapter]
    telemetry.append({
        "chapter": chapter,
        "segments": str(seg_count),
        "flagged": str(len(flagged_ids)),
        "patched": str(len(patched_ids)),
        "flag_rate": str(flag_rate),
    })
    telemetry.sort(key=lambda row: row["chapter"])
    with open(telemetry_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(telemetry)

    print(f"assembled: {out_path.relative_to(root)}")
    print(f"segments:  {seg_count}")
    print(f"flagged:   {len(flagged_ids)}   patched: {len(patched_ids)}   "
          f"flag_rate: {flag_rate:.2%}")
    if report["warns"]:
        print(f"lint warnings carried: {len(report['warns'])} "
              f"(see chatgpt/chapters/work/{chapter}.lint.json)")
    if seg_count and flag_rate > FLAG_RATE_ALARM:
        print(f"WARNING: flag rate {flag_rate:.2%} exceeds 40% - the review pass was "
              "close to a rewrite. Three consecutive chapters like this means the "
              "drafting method should be strengthened before the next chapter.")
    print("reminder: the reviewer's edits are visible as a git diff between the "
          "draft and review commits.")


if __name__ == "__main__":
    main()
