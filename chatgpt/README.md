# ChatGPT Translation Pipeline

This directory is the complete ChatGPT/Codex continuation of the earlier
Claude pipeline. It preserves every source chapter, segment, draft, review
issue, lint report, final translation, glossary entry, continuity note, and
owner style ruling present at migration.

## Structure

```text
chatgpt/
|-- PROJECT_INSTRUCTIONS.md    concise text for ChatGPT Project settings
|-- config.json                language pair and deterministic QA settings
|-- instructions/              detailed translation, editing, QA, and workflow rules
|-- glossary/                  canonical terminology plus browsable reference views
|-- chapters/
|   |-- state.json             authoritative handoff and next-chapter pointer
|   |-- source/                Chinese source chapters
|   |-- work/                  segments, drafts, reviews, lint reports, telemetry
|   `-- final/                 assembled English chapters; never hand-edit
|-- reference/                 style, continuity, known errors, migration provenance
`-- scripts/                   standard-library, cross-platform pipeline tools
```

## Authority order

When sources disagree, use this order:

1. the owner's latest explicit ruling;
2. `glossary/terminology.tsv` for terms;
3. `reference/style-guide.md` for prose and formatting;
4. `reference/continuity.md` and `chapters/state.json` for story state;
5. earlier finalized chapters as precedent;
6. model preference only where the repository is silent.

Never silently resolve a real conflict. Surface it to the owner during the
terminology stage and record the approved result before drafting.

## Start the next chapter

Read `chapters/state.json`, place the raw text at
`chapters/source/ch1211.txt`, and follow `instructions/workflow.md`. All
commands are run from the repository root.
