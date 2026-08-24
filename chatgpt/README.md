# ChatGPT Translation Pipeline

This directory is the complete ChatGPT/Codex continuation of the earlier
Claude pipeline. It preserves source chapters, aligned segments, drafts, review
issues, lint reports, final translations, glossary entries, continuity notes,
world-reference updates, and owner style rulings.

## Structure

```text
chatgpt/
|-- PROJECT_INSTRUCTIONS.md    concise text for ChatGPT Project settings
|-- config.json                language pair and deterministic QA settings
|-- instructions/              detailed translation, editing, QA, and workflow rules
|-- glossary/                  base terminology and enforceable owner-ruling TSVs
|-- chapters/
|   |-- state.json             authoritative handoff and next-chapter pointer
|   |-- source/                Chinese source chapters
|   |-- work/                  segments, drafts, reviews, lint reports, telemetry
|   `-- final/                 assembled English chapters; never hand-edit
|-- reference/                 style, continuity, world reference, known errors
`-- scripts/                   standard-library, cross-platform pipeline tools
```

## Authority order

When sources disagree, use this order:

1. the owner's latest explicit ruling;
2. `glossary/terminology.tsv` plus the state-named
   `glossary/owner-rulings-*.tsv` files, loaded afterward as overrides;
3. `reference/style-guide.md` plus the state-named owner style supplement;
4. the verified world reference and its state-named post-coverage supplement;
5. continuity files and `chapters/state.json` for story state;
6. earlier finalized chapters as precedent;
7. model preference only where the repository is silent.

Never silently resolve a real conflict. Surface it to the owner during the
terminology stage and record the approved result before drafting.

## Prose standard

The target is accurate, natural, published-quality xianxia English in the broad
professional register associated with leading Wuxiaworld releases. Preserve
source paragraph structure, unmistakable internal thought, cultivation logic,
Chinese idioms, classical allusions, and religious imagery. Do not copy wording
from published translations.

## Start the next chapter

Read `chapters/state.json` for the current next-chapter pointer and every
required context file, then follow `instructions/workflow.md`. All commands are
run from the repository root.
