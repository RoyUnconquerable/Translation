# ChatGPT translation pipeline

This directory contains the active translation authorities and optional
file-backed tooling for the novel continuation.

## Authority hierarchy

The latest pushed tip of the GitHub canonical branch named in
`chapters/state.json` is the persistent project record. Within a live task, the
exact Chinese source governs chapter content. The owner controls editorial
intent and explicit terminology approvals, but supplied English is verified
before it is promoted into that persistent record.

1. The exact current Chinese source for chapter content.
2. `glossary/terminology.tsv` for hard recurring terminology.
3. `glossary/entities.tsv` for identity and pronoun facts.
4. `reference/style-guide.md` for macro prose policy.
5. `reference/world-reference.md` and `reference/continuity.md` for mechanics
   and current story state.
6. `reference/known-errors.md` for active traps.
7. `glossary/phrase-memory.tsv` and `reference/decision-log.tsv`, searched only
   when the current source makes them relevant.
8. Earlier final prose as precedent where the authorities are silent.

No file may silently override another file at the same level. Conflicts are
errors and must be resolved in the canonical source. A new live owner decision
temporarily supersedes stored policy for the current task, but it becomes
cross-session authority only after it has been source-checked, classified,
committed, and pushed.

## Active structure

```text
chatgpt/
|-- chapters/state.json          compact routing state
|-- chapters/ledger.tsv          chapter-by-chapter status evidence
|-- glossary/terminology.tsv     unique hard term mappings
|-- glossary/entities.tsv        names, aliases, identity, pronouns
|-- glossary/phrase-memory.tsv   fixed lines and adaptive allusion guidance
|-- reference/style-guide.md     sole macro style authority
|-- reference/world-reference.md stable mechanics and relationships
|-- reference/continuity.md      rolling current story state
|-- reference/known-errors.md    active recurring traps only
|-- reference/decision-log.tsv   concise owner-decision provenance
|-- instructions/                workflow, translation, editing, and QA rules
`-- scripts/                     read-only checks and optional file pipeline
```

The default is chat-first translation. The JSONL chapter pipeline remains
available when the owner asks to persist chapter prose or requests file-backed
work. See `instructions/workflow.md`.

Phrase memory uses three scopes: `fixed` for exact titles, quotations, verses,
panels, and formulas; `image` for imagery that must survive while syntax and
tense are rebuilt; and `sense` for contextual meaning that must be composed
afresh. Only `fixed` targets may be copied as complete wording.

## Validation

Run from the repository root:

```text
python -m unittest discover -s chatgpt/tests
python chatgpt/scripts/audit.py
python chatgpt/scripts/lint.py --all
python chatgpt/scripts/state.py
```

These commands do not rewrite tracked files. `lint.py --write-report` is an
explicit opt-in for refreshing a stored legacy lint report.

For chat-first work, `scripts/prepare.py` builds the pre-draft authority sheet
from a temporary source file, and `scripts/chat_check.py` checks a temporary
source and target pair without storing chapter prose.
