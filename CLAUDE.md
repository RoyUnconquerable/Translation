# Translation Pipeline

This is a translation project (zh -> en xianxia web novel), driven end to end
by the `translate-chapter` skill.

- ALWAYS use the translate-chapter skill for anything translation-related:
  segmenting, drafting, revising, reviewing, assembling, glossary work.
  Never translate ad hoc in the main context.
- Run every script from the project root:
  `python3 .claude/skills/translate-chapter/scripts/<name>.py`
- Commit conventions: `draft: <chapter>`, `review: <chapter>`,
  `assemble: <chapter>` - one commit per stage so each stage's diff is one
  git command away.
- Respect the Stop-hook lint gate: never finish with lint failures, and use
  `SKIP_LINT_GATE=1` only deliberately, with the user's consent.
- Never hand-edit `output/`; it is assembled from `work/`.
