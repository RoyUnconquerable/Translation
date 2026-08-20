# Translation

This repository contains a Chinese-to-English xianxia translation project and
two deliberately separate pipeline implementations.

- `chatgpt/` is the active ChatGPT/Codex pipeline. It is self-contained,
  cross-platform, and starts from the complete Claude state through Chapter
  1210.
- `.claude/`, `CLAUDE.md`, `project/`, `source/`, `work/`, and `output/` are the
  unchanged Claude implementation and migration source. Do not edit them on
  the ChatGPT branch.
- `archive/claude-pipeline-2026-08-19` preserves the exact pre-migration state
  at commit `405e61125ba6abc935cbc56eaf1ccbf57c3fb091`.

## Current state

Chapters 1209 and 1210 are finalized, owner-edited, lint-clean, and copied into
`chatgpt/` without content changes. The next expected chapter is 1211. The
authoritative handoff is `chatgpt/chapters/state.json`.

## Use with a ChatGPT Project

1. Connect `RoyUnconquerable/Translation` as a project source.
2. Copy `chatgpt/PROJECT_INSTRUCTIONS.md` into the project's instructions.
3. Keep terminology decisions, chapter drafting, and QA in separate project
   chats so each outcome stays focused.
4. Use ChatGPT to discuss and inspect connected repository context. Use Codex
   for repository edits and script execution.

This layout follows OpenAI's guidance that project instructions apply across
project chats while files and connected sources provide shared context:
https://learn.chatgpt.com/docs/projects

## Validate the handoff

From the repository root:

```text
python chatgpt/scripts/lint.py --all
python chatgpt/scripts/state.py
```

See `chatgpt/README.md` and `chatgpt/instructions/workflow.md` for the full
workflow.
