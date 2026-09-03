"""Audit the canonical authority architecture for drift and bloat."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

OBSOLETE_PATTERNS = (
    "glossary/owner-rulings-*.tsv",
    "reference/owner-edits-*.md",
    "reference/style-owner-rulings-*.md",
    "reference/continuity-ch*.md",
    "reference/world-reference-supplement-*.md",
    "reference/world-reference-correction-*.md",
)

SIZE_LIMITS = {
    "chapters/state.json": 6000,
    "reference/style-guide.md": 18000,
    "reference/known-errors.md": 10000,
    "reference/continuity.md": 18000,
    "reference/world-reference.md": 22000,
}

EXPECTED_AUTHORITIES = {
    "chapter_ledger": "chatgpt/chapters/ledger.tsv",
    "terminology": "chatgpt/glossary/terminology.tsv",
    "entities": "chatgpt/glossary/entities.tsv",
    "phrase_memory": "chatgpt/glossary/phrase-memory.tsv",
    "style": "chatgpt/reference/style-guide.md",
    "continuity": "chatgpt/reference/continuity.md",
    "continuity_archive": "chatgpt/reference/continuity-archive.md",
    "world_reference": "chatgpt/reference/world-reference.md",
    "active_errors": "chatgpt/reference/known-errors.md",
    "owner_decisions": "chatgpt/reference/decision-log.tsv",
    "project_sources": "chatgpt/reference/project-source-registry.md",
    "workflow": "chatgpt/instructions/workflow.md",
}

EXPECTED_REPOSITORY_AUTHORITY = {
    "remote": "origin",
    "canonical_branch": "claude/translation-pipeline-build-3gdy6r",
    "durable_record": "latest_committed_and_pushed_tip",
}

REPOSITORY_POINTERS = {
    "README.md": "Current progress is recorded only in `chatgpt/chapters/state.json`",
    "CLAUDE.md": "This repository has one active translation pipeline: `chatgpt/`",
    ".claude/README.md": "No executable Claude automation is active",
    "project/README.md": "legacy migration evidence only",
    "project/style-guide.md": "not an active translation authority",
}

FORBIDDEN_LEGACY_TRIGGERS = (
    ".claude/settings.json",
    ".claude/agents",
    ".claude/skills",
)


def main() -> None:
    common.configure_stdio()
    root = common.find_root()
    errors: list[str] = []

    state_path = root / "chapters" / "state.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"authority audit: FAIL\n  state unreadable: {exc}") from None

    authorities = state.get("authorities", {})
    if authorities != EXPECTED_AUTHORITIES:
        errors.append("state authority manifest differs from the canonical manifest")
    if state.get("repository_authority") != EXPECTED_REPOSITORY_AUTHORITY:
        errors.append("state repository authority differs from the canonical GitHub ref")
    for key, value in authorities.items():
        if isinstance(value, str) and len(value) > 180:
            errors.append(f"authority path {key!r} contains prose or is too long")

    for pattern in OBSOLETE_PATTERNS:
        matches = sorted(root.glob(pattern))
        if matches:
            errors.append(
                f"obsolete active supplements match {pattern}: "
                + ", ".join(path.name for path in matches)
            )

    repo_root = root.parent
    for relative, marker in REPOSITORY_POINTERS.items():
        path = repo_root / relative
        if not path.is_file():
            errors.append(f"missing repository authority pointer {relative}")
            continue
        if marker not in path.read_text(encoding="utf-8"):
            errors.append(f"repository authority pointer is stale: {relative}")

    for relative in FORBIDDEN_LEGACY_TRIGGERS:
        if (repo_root / relative).exists():
            errors.append(f"retired legacy trigger remains auto-discoverable: {relative}")

    for relative, limit in SIZE_LIMITS.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing canonical file {relative}")
            continue
        size = path.stat().st_size
        if size > limit:
            errors.append(f"{relative} is {size} bytes; limit is {limit}")

    try:
        glossary = common.load_glossary(root)
        phrases = common.load_phrase_memory(root)
        entities = common.load_entities(root)
    except ValueError as exc:
        errors.append(str(exc))
        glossary, phrases, entities = {}, [], []

    if len(glossary) > 375:
        errors.append(
            f"hard glossary has {len(glossary)} rows; review phrase-level leakage"
        )
    if len(phrases) > 250:
        errors.append(
            f"phrase memory has {len(phrases)} rows; archive or consolidate it"
        )
    if len(entities) > 75:
        errors.append(f"entity registry has {len(entities)} rows; review scope")

    decision_path = root / "reference" / "decision-log.tsv"
    try:
        decisions = common.read_tsv(
            decision_path,
            ("date", "chapter", "category", "decision", "promoted_to", "status"),
        )
    except ValueError as exc:
        errors.append(str(exc))
        decisions = []
    for row in decisions:
        if row["status"] not in {"active", "consolidated", "pending", "superseded"}:
            errors.append(f"invalid decision status {row['status']!r}")
        if len(row["decision"]) > 240:
            errors.append(f"decision log row for {row['chapter']} is too detailed")

    exception_path = root / "chapters" / "legacy-lint-exceptions.tsv"
    try:
        exceptions = common.read_tsv(
            exception_path, ("chapter", "segment", "source", "reason")
        )
    except ValueError as exc:
        errors.append(str(exc))
        exceptions = []
    keys = [(row["chapter"], row["segment"], row["source"]) for row in exceptions]
    if len(keys) != len(set(keys)):
        errors.append("legacy lint exceptions contain duplicate keys")

    if errors:
        print(f"authority audit: FAIL ({len(errors)} error(s))")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)
    print(
        f"authority audit: PASS ({len(glossary)} hard terms, "
        f"{len(phrases)} phrase memories, {len(entities)} entities, "
        f"{len(decisions)} decisions)"
    )


if __name__ == "__main__":
    main()
