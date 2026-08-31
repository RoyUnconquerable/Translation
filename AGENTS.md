# ChatGPT Translation Pipeline

For translation work, `chatgpt/` is the only writable pipeline. The legacy
Claude files (`.claude/`, `CLAUDE.md`, `project/`, `source/`, `work/`, and
`output/`) are frozen migration evidence; do not change them unless the owner
explicitly requests legacy maintenance.

Before working on a chapter, read:

1. `chatgpt/chapters/state.json`
2. `chatgpt/config.json`
3. `chatgpt/glossary/terminology.tsv`
4. `chatgpt/reference/style-guide.md`
5. `chatgpt/reference/continuity.md`
6. `chatgpt/reference/known-errors.md`
7. the relevant source, segments, draft, issues, and final chapter files

Follow `chatgpt/instructions/workflow.md`. The glossary is authoritative and
new or changed renderings require owner approval before drafting. Translate
every segment faithfully; never merge, split, reorder, omit, or invent content.
QA must compare target text directly with source segments. Do not edit
`chatgpt/chapters/final/` by hand; assemble it from the reviewed draft.

Conversation summaries and prior model drafts are never substitutes for the
current Chinese source or repository authorities. When a source exists only in
chat under the chat-only fast path, audit that exact pasted source paragraph by
paragraph and establish the identity and pronoun of every recurring referent.

After any translation change, run:

```text
python chatgpt/scripts/lint.py --all
python chatgpt/scripts/state.py
```

Do not finish with failures, unpatched review issues, stale final output, or a
stale chapter state. Owner edits are final: adopt them exactly, then record any
durable terminology, continuity, or style ruling in the repository.
