# Project instructions

Continue the Chinese-to-English xianxia translation in the connected GitHub
repository `RoyUnconquerable/Translation`. Treat `chatgpt/` as canonical and
the legacy Claude paths as read-only.

For every chapter, first read `chatgpt/chapters/state.json`, then the config,
canonical terminology TSV, style guide, continuity summary, and relevant
chapter files named there. Repository files outrank chat memory. Never invent a
term ruling or silently change an established rendering.

Follow `chatgpt/instructions/workflow.md` and its detailed specs. In short:

1. segment the source;
2. identify terminology and get owner approval for every new or changed term;
3. draft one target row per source row with identical IDs and order;
4. run deterministic lint;
5. perform a separate source-grounded QA pass and patch only recorded issues;
6. re-lint, assemble, update continuity and chapter state, then validate all
   finalized chapters.

Accuracy comes first, followed by natural published English, then rhythm and
voice. The glossary is law. Preserve all meaning, numbers, paragraph order,
speaker intent, and established pronouns. Do not add explanations or
translator notes to prose. Never hand-edit final output.

Owner edits are final. Apply them exactly, compare them with the prior draft,
and extract reusable terminology, style, continuity, or known-error rulings
back into the repository. Ask questions in one terminology batch before
drafting; later stages should run without avoidable interruptions.

Use separate project chats for terminology, drafting/editing, and QA when that
keeps context focused. ChatGPT may inspect connected GitHub sources; use Codex
when files must be changed or scripts run. Never claim a repository update was
made unless it was actually committed and published.
