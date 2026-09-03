"""Validate compact routing state, chapter evidence, and file-backed finals."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import lint

SOURCE_STATUSES = {"repo", "chat_only_observed", "unknown"}
TRANSLATION_STATUSES = {
    "repo_final",
    "chat_draft_delivered",
    "chat_redraft_delivered",
    "source_received",
    "unknown",
}
REVIEW_STATUSES = {
    "owner_final",
    "owner_reviewed",
    "owner_revision_recorded",
    "owner_corrections_recorded",
    "pending",
    "rejected_redraft_pending",
    "not_started",
    "unknown",
}
CONTINUITY_STATUSES = {"current", "archived", "missing"}
STORAGE_STATUSES = {"repo", "chat_only", "unavailable"}


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing file: {path}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from None


def validate_file_final(
    root: Path, chapter: int, cfg: dict, glossary: dict, errors: list[str]
) -> None:
    name = f"ch{chapter}"
    work = root / "chapters" / "work"
    paths = {
        "source": root / "chapters" / "source" / f"{name}.txt",
        "segments": work / f"{name}.segments.jsonl",
        "draft": work / f"{name}.draft.jsonl",
        "issues": work / f"{name}.issues.json",
        "final": root / "chapters" / "final" / f"{name}.{cfg['target_lang']}.txt",
    }
    for label, path in paths.items():
        if not path.is_file():
            errors.append(f"{name}: missing {label} file {path.relative_to(root)}")
    if any(not path.is_file() for path in paths.values()):
        return
    try:
        segments = common.read_jsonl(paths["segments"])
        draft = common.read_jsonl(paths["draft"])
        issues = load_json(paths["issues"])
    except ValueError as exc:
        errors.append(f"{name}: {exc}")
        return
    segment_ids = [row.get("id") for row in segments]
    draft_ids = [row.get("id") for row in draft]
    if segment_ids != draft_ids:
        errors.append(f"{name}: draft ids, order, or count do not match segments")
    if len(segment_ids) != len(set(segment_ids)):
        errors.append(f"{name}: duplicate segment ids")
    if not isinstance(issues, list):
        errors.append(f"{name}: issues file must contain an array")
    else:
        valid = set(segment_ids)
        for issue in issues:
            if issue.get("id") not in valid:
                errors.append(f"{name}: issue names unknown id {issue.get('id')!r}")
            if issue.get("patched") is not True:
                errors.append(f"{name}: final chapter has an unpatched issue")
    report = lint.lint_chapter(root, cfg, glossary, name, write_report=False)
    if report["status"] != "pass":
        errors.append(f"{name}: recomputed lint failed")
    if segment_ids == draft_ids:
        target_by_id = {row["id"]: row.get("tgt", "") for row in draft}
        assembled = "\n\n".join(
            target_by_id[row["id"]].strip() for row in segments
        ) + "\n"
        if paths["final"].read_text(encoding="utf-8") != assembled:
            errors.append(f"{name}: final output does not match reviewed draft")


def main() -> None:
    common.configure_stdio()
    root = common.find_root()
    errors: list[str] = []
    try:
        state = load_json(root / "chapters" / "state.json")
    except ValueError as exc:
        raise SystemExit(f"state: FAIL\n  {exc}") from None

    if state.get("schema_version") != 2:
        errors.append("state schema_version must be 2")
    if state.get("mode") not in {"chat_first", "file_backed"}:
        errors.append("state mode must be chat_first or file_backed")

    repository_authority = state.get("repository_authority")
    expected_repository_authority = {
        "remote": "origin",
        "canonical_branch": "claude/translation-pipeline-build-3gdy6r",
        "durable_record": "latest_committed_and_pushed_tip",
    }
    if repository_authority != expected_repository_authority:
        errors.append(
            "state repository_authority must name the canonical pushed GitHub tip"
        )

    storage = state.get("storage")
    if not isinstance(storage, dict):
        errors.append("state storage must be an object")
    else:
        if storage.get("chapter_prose") not in {
            "chat_only_by_default", "file_backed_by_default"
        }:
            errors.append("state storage has an invalid chapter_prose policy")
        recoverable = storage.get("exact_chat_finals_recoverable_from_repository")
        if not isinstance(recoverable, bool):
            errors.append("state storage recoverability flag must be boolean")
        elif storage.get("chapter_prose") == "chat_only_by_default" and recoverable:
            errors.append("chat-only storage cannot claim exact finals are in Git")

    authorities = state.get("authorities")
    if not isinstance(authorities, dict):
        errors.append("state authorities must be an object")
        authorities = {}
    repo_root = root.parent
    for name, relative in authorities.items():
        if not isinstance(relative, str) or not relative.startswith("chatgpt/"):
            errors.append(f"authority {name!r} must be a chatgpt path")
            continue
        if not (repo_root / relative).is_file():
            errors.append(f"authority {name!r} is missing: {relative}")

    try:
        glossary = common.load_glossary(root)
        phrases = common.load_phrase_memory(root)
        entities = common.load_entities(root)
    except ValueError as exc:
        errors.append(str(exc))
        glossary, phrases, entities = {}, [], []

    phrase_sources: set[str] = set()
    for row in phrases:
        source = row["source"]
        if not source or not row["target"]:
            errors.append("phrase memory has an empty source or target")
        if source in phrase_sources:
            errors.append(f"phrase memory has duplicate source {source!r}")
        phrase_sources.add(source)
        if source in glossary:
            errors.append(f"source {source!r} appears in both hard terms and phrase memory")

    entity_ids: set[str] = set()
    aliases: set[str] = set()
    for row in entities:
        entity_id = row["entity_id"]
        if not entity_id or entity_id in entity_ids:
            errors.append(f"duplicate or empty entity id {entity_id!r}")
        entity_ids.add(entity_id)
        english_names = set(row["english_names"].split("|"))
        for alias in row["source_aliases"].split("|"):
            if alias in aliases:
                errors.append(f"entity alias {alias!r} belongs to more than one entity")
            aliases.add(alias)
            entry = glossary.get(alias)
            if entry is None:
                errors.append(f"entity alias {alias!r} is absent from terminology")
            elif not english_names.intersection(entry["variants"]):
                errors.append(
                    f"entity alias {alias!r} maps to {entry['target']!r}, "
                    f"outside entity names {row['english_names']!r}"
                )

    ledger_path = root / "chapters" / "ledger.tsv"
    try:
        ledger = common.read_tsv(
            ledger_path,
            (
                "chapter",
                "source_status",
                "translation_status",
                "review_status",
                "continuity_status",
                "prose_storage",
                "evidence",
            ),
        )
    except ValueError as exc:
        errors.append(str(exc))
        ledger = []

    chapters: list[int] = []
    cfg = common.load_config(root)
    for row in ledger:
        try:
            chapter = int(row["chapter"])
        except ValueError:
            errors.append(f"invalid chapter number {row['chapter']!r}")
            continue
        chapters.append(chapter)
        if not row["evidence"]:
            errors.append(f"chapter {chapter}: evidence must not be empty")
        for field, allowed in (
            ("source_status", SOURCE_STATUSES),
            ("translation_status", TRANSLATION_STATUSES),
            ("review_status", REVIEW_STATUSES),
            ("continuity_status", CONTINUITY_STATUSES),
            ("prose_storage", STORAGE_STATUSES),
        ):
            if row[field] not in allowed:
                errors.append(f"chapter {chapter}: invalid {field} {row[field]!r}")
        if row["translation_status"] == "repo_final":
            if row["source_status"] != "repo" or row["prose_storage"] != "repo":
                errors.append(f"chapter {chapter}: repo final lacks repo source or storage")
            validate_file_final(root, chapter, cfg, glossary, errors)
        if row["review_status"] == "rejected_redraft_pending" \
                and row["translation_status"] != "chat_redraft_delivered":
            errors.append(f"chapter {chapter}: rejected redraft status is inconsistent")
        if row["translation_status"] == "source_received" \
                and row["source_status"] == "unknown":
            errors.append(f"chapter {chapter}: source_received lacks a known source")
        if row["translation_status"] == "source_received" \
                and row["review_status"] != "not_started":
            errors.append(
                f"chapter {chapter}: an undelivered translation cannot be under review"
            )

    if len(chapters) != len(set(chapters)):
        errors.append("chapter ledger contains duplicate chapters")
    if chapters and chapters != list(range(min(chapters), max(chapters) + 1)):
        errors.append("chapter ledger must be sorted and continuous")

    if ledger:
        source_seen = max(
            int(row["chapter"]) for row in ledger if row["source_status"] != "unknown"
        )
        delivered_statuses = {
            "repo_final", "chat_draft_delivered", "chat_redraft_delivered"
        }
        draft_delivered = max(
            int(row["chapter"])
            for row in ledger
            if row["translation_status"] in delivered_statuses
        )
        owner_final = max(
            int(row["chapter"])
            for row in ledger
            if row["review_status"] == "owner_final"
        )
        awaiting_translation = [
            int(row["chapter"])
            for row in ledger
            if row["source_status"] != "unknown"
            and row["translation_status"] == "source_received"
        ]
        derived = {
            "latest_source_seen": source_seen,
            "latest_draft_delivered": draft_delivered,
            "most_recent_owner_final": owner_final,
            "next_translation_chapter": (
                min(awaiting_translation) if awaiting_translation else source_seen + 1
            ),
            "next_new_chapter": source_seen + 1,
        }
        if state.get("progress") != derived:
            errors.append(f"state progress is stale; expected {derived}")

    if errors:
        print(f"state: FAIL ({len(errors)} error(s))")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)

    pending = [
        row["chapter"]
        for row in ledger
        if row["review_status"] in {"pending", "rejected_redraft_pending"}
    ]
    awaiting = [
        row["chapter"]
        for row in ledger
        if row["translation_status"] == "source_received"
    ]
    print(
        f"state: PASS ({len(ledger)} ledger rows, {len(glossary)} hard terms, "
        f"pending review {', '.join(pending)}; "
        f"awaiting translation {', '.join(awaiting) or 'none'})"
    )


if __name__ == "__main__":
    main()
