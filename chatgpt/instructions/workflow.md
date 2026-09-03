# Translation workflow

This file is the workflow dispatcher. Chat-first work is the default. Use the
file-backed path only when the owner asks to store chapter prose or the source
already exists as a repository chapter artifact.

## 1. Load the compact authority set

Read `chapters/state.json`, then load the canonical paths it names. Do not load
historical Git versions, the full decision log, or all phrase memory by
default. Search the phrase memory, decision log, and registered project source
only for material that appears in the current Chinese chapter.

The latest pushed tip of the GitHub canonical branch recorded in state is the
persistent authority across sessions. If the checkout may be stale and remote
access is available, verify that it contains that tip before relying on it. A
new live instruction governs the current task provisionally and becomes durable
only after verification, classification, commit, and push.

The exact Chinese paste or source file is mandatory. A conversation summary,
continuity capsule, prior model draft, or English owner edit cannot substitute
for it.

Run `python chatgpt/scripts/state.py` before drafting if repository state may
have changed. A failure is a real blocker. The check must not mutate files.

## 2. Build a short chapter authority sheet

Before writing prose, record privately:

- chapter number, title, source paragraph count, and hard scene changes;
- every named or recurring referent, identity, and required pronoun;
- every glossary term that actually occurs;
- all numbers, dates, rankings, and causal dependencies;
- image-bearing idioms, allusions, poems, panels, jokes, and wordplay;
- each likely direct thought, its speaker, and its time reference;
- whether each idiom or allusion is fixed wording, a live image, or an adaptive
  contextual sense;
- unresolved terms or ambiguities that could materially change the chapter.

Save the exact chat paste to an untracked temporary file outside the repository
and generate this inventory with:

```text
python chatgpt/scripts/prepare.py <source-file>
```

When the scripts are available, this pre-draft check is mandatory. If execution
is unavailable, reproduce its terminology, identity, number, and phrase checks
manually and disclose the limitation.

Use one terminology question batch only when an unresolved choice matters.
Do not stop for terms already resolved by the canonical authorities.

## 3. Draft once

Translate from the Chinese, not from an earlier English attempt. Preserve one
target paragraph for each source paragraph, in identical order. Compose modern,
natural English while retaining every meaning-bearing detail and the source's
Chinese cultivation texture.

Do not generate multiple independent full drafts. They increase inconsistency
and encourage ungrounded stylistic blending.

## 4. Run two focused reviews

The reviews detect issues. They do not rewrite the chapter wholesale.

1. Fidelity review: compare every paragraph to the source for omissions,
   additions, logic, chronology, numbers, terms, identities, pronouns,
   allusions, their actual subjects and relationships, and alignment.
2. English review: check grammar, clarity, modern register, character voice,
   pacing, action geography, thought mode and tense, repetition, archaic drift,
   and translationese without changing source meaning.

When subagents are available, assign these as two independent detector tasks
after the lead translator has produced one draft. Give both reviewers the
exact source and the same draft. They return paragraph-indexed findings only,
never replacement chapters, and they do not edit shared authority files. If
subagents are unavailable, perform the same two passes sequentially.

The lead translator decides each finding and patches only affected paragraphs.
Save the patched target to an untracked temporary file outside the repository,
then run the mechanical check before delivery:

```text
python chatgpt/scripts/chat_check.py <source-file> <target-file>
```

When the scripts are available, this check is mandatory for every chat-first
chapter. It is the enforcement path for hard terms such as `神念` to `divine
sense`, paragraph alignment, title presence, punctuation, and numbers.

## 5. Chat-first delivery

For ordinary chat work, deliver the chapter before repository maintenance.
Do not create provisional per-chapter supplements or commits. After the owner
approves or supplies edited prose, compare it once against both the exact source
and the draft. Verify fidelity, grammar, terminology, continuity, thought mode
and tense, allusions, and formatting before classifying each change:

- `MACRO`: reusable prose policy, update the style guide;
- `TERM`: stable recurring rendering, update terminology or entities;
- `PHRASE`: contextual idiom, title, verse, or special wording, update phrase
  memory;
- `FACT`: stable world mechanic, update world reference;
- `CONTINUITY`: current plot state, update continuity;
- `LOCAL`: useful only in that passage, decision log or Git history only;
- `MECHANICAL`: typo or formatting repair, no stylistic promotion.

Update state and ledger in the same atomic commit. Never create a new
chapter-specific glossary, style, continuity, world, or edit-summary file.

## 6. File-backed path

When durable chapter prose is requested, follow
`instructions/file-backed-workflow.md`. The aligned JSONL files, issues,
assembly, and telemetry rules apply only to that mode.

## 7. Final repository gates

Before committing an authority update, run:

```text
python -m unittest discover -s chatgpt/tests
python chatgpt/scripts/audit.py
python chatgpt/scripts/lint.py --all
python chatgpt/scripts/state.py
```

Review `git diff` and `git status`. Preserve unrelated worktree changes. Make
one coherent forward commit for the owner-final update or maintenance task,
then push it to the working branch and ensure the canonical GitHub branch named
in state contains it. Do not claim cross-session persistence before both are
true. If work is committed on a noncanonical branch, verify that both remote
targets can be fast-forwarded, then push the same commit to the working branch
and the canonical branch. Prefer one atomic non-force push. If either branch
has diverged or branch protection rejects the update, stop and report the
conflict. Never force-push published history.
