# Translation

This repository holds a Chinese-to-English translation project for a xianxia
web serial. It has one active pipeline and preserved legacy material.

- `chatgpt/` is the active pipeline. It holds the instructions, terminology,
  style and continuity records, and the tools. The directory name is
  historical; the instructions are platform-neutral.
- `source/`, `work/`, `output/` and the legacy data under `project/` are
  migration evidence from the former pipeline. They are read-only.
- `CLAUDE.md`, `.claude/README.md` and `project/style-guide.md` are pointers to
  the active pipeline, not alternate instructions.
- The branch `archive/claude-pipeline-2026-08-19` preserves the pre-migration
  state at commit `405e61125ba6abc935cbc56eaf1ccbf57c3fb091`.

## Current state

Current progress is recorded only in `chatgpt/chapters/state.json`; this README
does not repeat chapter numbers. The latest pushed tip of the canonical branch
named there is the durable project record.

## Use this repository

Start with `chatgpt/PROJECT_INSTRUCTIONS.md`, then follow
`chatgpt/instructions/workflow.md`. Chapters are delivered in chat. Chapter
prose is never committed.

`chatgpt/README.md` maps the directory and describes the tools;
`chatgpt/instructions/maintenance.md` holds the validation commands.
