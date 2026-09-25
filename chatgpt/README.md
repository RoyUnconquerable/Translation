# Translation pipeline

This directory holds the active translation authorities, the chapter tools and
the validation scripts. Start at `PROJECT_INSTRUCTIONS.md`.

## Directory map

```text
chatgpt/
|-- PROJECT_INSTRUCTIONS.md          entry text: book, authority order, stages
|-- chapters/state.json              progress and the authority manifest
|-- chapters/ledger.tsv              chapter-by-chapter status evidence
|-- glossary/terminology.tsv         hard recurring terms
|-- glossary/entities.tsv            names, aliases, identities, pronouns
|-- glossary/phrase-memory.tsv       fixed lines, images and idiom senses
|-- instructions/workflow.md         the order of work for one chapter
|-- instructions/translation-spec.md Stage 1: translation and verification
|-- instructions/editing-spec.md     Stage 2: editing and formatting
|-- instructions/maintenance.md      feedback, durable updates, publication
|-- instructions/qa-rules.md         pointer to the two stage specs
|-- reference/style-guide.md         house voice and craft
|-- reference/craft-examples.md      before/after exemplar bank
|-- reference/known-errors.md        meaning traps
|-- reference/Reference_*.md         four owner reference files
|-- reference/...                    continuity, world reference, decision log
|-- scripts/                         prepare, check and validation tools
`-- tests/                           unit tests for the tools and records
```

Run the scripts with Python 3: `python3` on Linux and macOS, `python` or `py`
on Windows.

## prepare.py

`python3 chatgpt/scripts/prepare.py <source-file>` reads a Chinese source and
prints the paragraph count and numbering, the source's own scene breaks, the
title, matching hard terms with their notes, entities with scoped pronouns,
phrase-memory hits with their scope, bracketed terms missing from the glossary,
numbers, short stage reminders, and scene-break candidates. It never writes.

When the title contains a chapter number, it also checks that the chapter
follows the recorded frontier in state. If state trails the conversation, pass
`--observed-through N` with the verified in-session frontier. N must be at
least the recorded frontier and below the incoming chapter. This option changes
no state and proves neither delivery nor approval.

## chat_check.py

`chat_check.py` compares a source file and a target file and never writes. It
checks the target title number, the paragraph mapping (including declared
display splits), reviewed scene-break positions, required terms and forbidden
expansions, fixed displays and panel format, banned typography, CJK residue and
contractions ending in 'd. Digit mismatches are warnings. It does not prove
meaning, completeness, Chinese-number conversion, the chapter ending or good
English. `instructions/workflow.md` gives the flags.

## Phrase memory scopes

Phrase memory has three scopes. `fixed` covers exact titles, quotations,
verses, panels and formulas. `image` covers imagery that must survive while the
syntax is rebuilt. `sense` covers a contextual meaning that is composed afresh.
Only `fixed` targets may be copied as complete wording.

## Validation

The four validation commands, and when to run them, are in
`instructions/maintenance.md`. They do not rewrite tracked files; CI runs the
same set on every push.

`config.json` holds language settings and legacy lint options only.

Legacy file-backed tools and JSONL artifacts remain for compatibility tests
only; no chapter is produced with them.
