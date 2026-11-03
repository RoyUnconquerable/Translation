# Agent entry point: next novel branch

This branch is the setup area for a new Chinese-to-English translation. The prior novel remains intact on its existing canonical branch.

1. Begin at `chatgpt/novels/next-novel/README.md`, then read `chatgpt/novels/next-novel/state.json`.
2. Reuse the general fidelity, English craft, paragraph alignment, review, and delivery methods recorded in `chatgpt/instructions/`. Adapt voice to the new novel.
3. Treat `chatgpt/novels/next-novel/` as the only authority for the new novel's characters, names, glossary, decisions, continuity and footnotes. Do not import any terminology, setting facts or book-specific decisions from the earlier novel.
4. Before each chapter, inspect all idioms, slang, quotations, puns and allusions for the new novel's footnote candidate log, even when the English requires no note.
5. The original `chatgpt/chapters/state.json`, original glossary, original `chatgpt/reference/Reference_*.md` tables and old-script lookup configuration are for the previous novel. They are not active new-novel authorities. Do not claim the original mechanical checker validated a new-novel chapter until the scripts are reconfigured.
6. Deliver complete chapter prose in chat, not Git. Report unresolved terms and footnote candidates separately. Only claim persisted changes after the branch commit is verified.

The setup currently awaits the new novel's title/source and a tool routing/validation migration; see the pack README.
