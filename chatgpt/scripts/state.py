"""Validate durable chapter state, review evidence, output, and telemetry.

Usage: python chatgpt/scripts/state.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import lint


def chapter_number(name: str) -> int:
    match = re.fullmatch(r"ch(\d+)", name)
    if not match:
        raise ValueError(f"invalid chapter name: {name}")
    return int(match.group(1))


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing file: {path}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from None


def main() -> None:
    common.configure_stdio()
    root = common.find_root()
    state_path = root / "chapters" / "state.json"
    state = load_json(state_path)
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    chapters = state.get("chapters")
    if not isinstance(chapters, dict) or not chapters:
        raise SystemExit("state: FAIL\n  chapters must be a nonempty object")

    telemetry_path = root / "chapters" / "work" / "telemetry.csv"
    telemetry_rows: list[dict[str, str]] = []
    if telemetry_path.is_file():
        with open(telemetry_path, newline="", encoding="utf-8") as fh:
            telemetry_rows = list(csv.DictReader(fh))
    telemetry_by_chapter: dict[str, dict[str, str]] = {}
    for row in telemetry_rows:
        chapter = row.get("chapter", "")
        if chapter in telemetry_by_chapter:
            errors.append(f"telemetry has duplicate row for {chapter}")
        telemetry_by_chapter[chapter] = row

    cfg = common.load_config(root)
    glossary = common.load_glossary(root)
    final_chapters: list[str] = []

    for chapter, expected in sorted(chapters.items(), key=lambda item: chapter_number(item[0])):
        work_dir = root / "chapters" / "work"
        source_path = root / "chapters" / "source" / f"{chapter}.txt"
        segments_path = work_dir / f"{chapter}.segments.jsonl"
        draft_path = work_dir / f"{chapter}.draft.jsonl"
        issues_path = work_dir / f"{chapter}.issues.json"
        final_path = root / "chapters" / "final" / f"{chapter}.{cfg['target_lang']}.txt"

        for path in (source_path, segments_path, draft_path, issues_path):
            check(path.is_file(), f"{chapter}: missing {path.relative_to(root)}")
        if not all(path.is_file() for path in (segments_path, draft_path, issues_path)):
            continue

        try:
            segments = common.read_jsonl(segments_path)
            draft = common.read_jsonl(draft_path)
        except ValueError as exc:
            errors.append(f"{chapter}: {exc}")
            continue

        segment_ids = [row.get("id") for row in segments]
        draft_ids = [row.get("id") for row in draft]
        check(segment_ids == draft_ids,
              f"{chapter}: draft ids/order/count do not match segments")
        check(len(segment_ids) == len(set(segment_ids)),
              f"{chapter}: duplicate segment ids")
        check(expected.get("segments") == len(segments),
              f"{chapter}: state segments={expected.get('segments')}, actual={len(segments)}")

        report = lint.lint_chapter(root, cfg, glossary, chapter)
        check(report["status"] == "pass", f"{chapter}: recomputed lint failed")
        check(expected.get("lint_status") == report["status"],
              f"{chapter}: state lint status is stale")
        check(expected.get("lint_warnings") == len(report["warns"]),
              f"{chapter}: state lint_warnings={expected.get('lint_warnings')}, "
              f"actual={len(report['warns'])}")

        issues = load_json(issues_path)
        if not isinstance(issues, list):
            errors.append(f"{chapter}: issues file must contain a JSON array")
            continue
        valid_ids = set(segment_ids)
        flagged = {issue.get("id") for issue in issues if issue.get("id") in valid_ids}
        patched = {issue.get("id") for issue in issues
                   if issue.get("id") in valid_ids and issue.get("patched") is True}
        unknown = sorted({str(issue.get("id")) for issue in issues
                          if issue.get("id") not in valid_ids})
        check(not unknown, f"{chapter}: issues name unknown ids: {', '.join(unknown)}")
        check(expected.get("issues") == len(issues),
              f"{chapter}: state issues={expected.get('issues')}, actual={len(issues)}")
        check(expected.get("flagged_segments") == len(flagged),
              f"{chapter}: state flagged_segments is stale")
        check(expected.get("patched_segments") == len(patched),
              f"{chapter}: state patched_segments is stale")

        if expected.get("status") == "final":
            final_chapters.append(chapter)
            check(all(issue.get("patched") is True for issue in issues),
                  f"{chapter}: finalized chapter has unpatched issues")
            check(final_path.is_file(), f"{chapter}: final output is missing")
            if final_path.is_file() and segment_ids == draft_ids:
                tgt_by_id = {row["id"]: row.get("tgt", "") for row in draft}
                assembled = "\n\n".join(
                    tgt_by_id[row["id"]].strip() for row in segments
                ) + "\n"
                check(final_path.read_text(encoding="utf-8") == assembled,
                      f"{chapter}: final output is stale or hand-edited")

            telemetry = telemetry_by_chapter.get(chapter)
            check(telemetry is not None, f"{chapter}: telemetry row is missing")
            if telemetry:
                rate = round(len(flagged) / len(segments), 4) if segments else 0.0
                check(telemetry.get("segments") == str(len(segments)),
                      f"{chapter}: telemetry segment count is stale")
                check(telemetry.get("flagged") == str(len(flagged)),
                      f"{chapter}: telemetry flagged count is stale")
                check(telemetry.get("patched") == str(len(patched)),
                      f"{chapter}: telemetry patched count is stale")
                try:
                    telemetry_rate = float(telemetry.get("flag_rate", "nan"))
                except ValueError:
                    telemetry_rate = float("nan")
                check(telemetry_rate == rate,
                      f"{chapter}: telemetry flag rate is stale")

    if final_chapters:
        latest = max(final_chapters, key=chapter_number)
        check(state.get("latest_finalized") == latest,
              f"state latest_finalized should be {latest}")
        expected_next = f"ch{chapter_number(latest) + 1:04d}"
        check(state.get("next_expected") == expected_next,
              f"state next_expected should be {expected_next}")

    extra_telemetry = sorted(set(telemetry_by_chapter) - set(chapters))
    check(not extra_telemetry,
          "telemetry has chapters absent from state: " + ", ".join(extra_telemetry))

    if errors:
        print(f"state: FAIL ({len(errors)} error(s))")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print(f"state: PASS ({len(chapters)} chapter(s), "
          f"latest {state['latest_finalized']}, next {state['next_expected']})")


if __name__ == "__main__":
    main()
