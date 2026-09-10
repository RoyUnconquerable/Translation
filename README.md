# Translation

This repository contains a Chinese-to-English xianxia translation project with
one active pipeline and one preserved legacy implementation.

- `chatgpt/` is the active ChatGPT/Codex pipeline. It is self-contained and
  cross-platform. It was initialized from the complete Claude state through
  Chapter 1210 and has continued beyond that migration point.
- `source/`, `work/`, `output/`, and the legacy data under `project/` preserve
  migration evidence from the former Claude implementation. Its executable
  skill, agents, and stop hook are not present on the active branch.
- `CLAUDE.md`, `.claude/README.md`, and `project/style-guide.md` are
  compatibility pointers to the active pipeline, not alternate instructions.
- `archive/claude-pipeline-2026-08-19` preserves the exact pre-migration state
  at commit `405e61125ba6abc935cbc56eaf1ccbf57c3fb091`.

## Current state

Current progress is recorded only in `chatgpt/chapters/state.json`; this README
intentionally does not duplicate chapter numbers. The latest pushed tip of the
GitHub canonical branch named there is the persistent project authority across
sessions and context compactions. Exact Chinese source governs chapter content,
and verified owner decisions become durable when committed and pushed.

## Use this repository

Start with `AGENTS.md`, `chatgpt/chapters/state.json`, and the single execution
policy in `chatgpt/instructions/workflow.md`. `chatgpt/PROJECT_INSTRUCTIONS.md`
is the compact entry text; repository updates do not automatically update any
separately pasted platform instructions.

Keep the source, draft and review context together. Separate project chats or
parallel editorial pipelines are not required. Reuse unchanged references,
retrieve relevant historical entries and deliver the full chapter in chat
before maintenance. Verified feedback updates the affected canonical records
in one atomic commit. Never commit chapter prose or provisional handoffs.

## Validate approved authority updates

Run once after the maintenance patch, not before chapter delivery:

```text
python -m unittest discover -s chatgpt/tests
python chatgpt/scripts/audit.py
python chatgpt/scripts/lint.py --all
python chatgpt/scripts/state.py
```

See `chatgpt/README.md` and `chatgpt/instructions/workflow.md` for the full
workflow.
