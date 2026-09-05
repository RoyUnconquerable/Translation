# Translation workflow

This file is the workflow dispatcher. Chat-first work is the default. Use the
file-backed path only when the owner asks to store chapter prose or the source
already exists as a repository chapter artifact.

## Routine chapter performance target

A routine chat-first chapter should be delivered in roughly three to five
minutes when the source is complete and no material ambiguity or tool failure
intervenes. This is a performance budget, not permission to skip fidelity,
English, or mechanical checks. Treat each new chapter as an incremental turn,
not a full pipeline bootstrap.

Use this working budget:

- authority verification and chapter inventory: about 30 seconds;
- one translation draft: about two to three minutes;
- parallel detector reviews and one surgical correction pass: about one minute;
- final mechanical validation and delivery: under 30 seconds.

If a real blocker is likely to push the turn materially beyond that range,
send the owner a concise update identifying it instead of silently expanding
the process.

## 1. Load the compact authority set

Read `chapters/state.json`, then load the canonical paths it names. Do not load
historical Git versions, the full decision log, or all phrase memory by
default. Search the phrase memory, decision log, and registered project source
only for material that appears in the current Chinese chapter.

Within the same active conversation, first verify the repository tip. If the
tip and relevant authority files are unchanged and their contents remain in
active context, reuse that verified authority instead of rereading or dumping
the full files. Still read state, follow this workflow, run the chapter
inventory, and perform targeted searches for terms and issues in the new
source. After a new session, context compaction that removes the actual
authority contents, a changed repository tip, or an uncertain checkout, reload
the compact authority set from the repository. Never use a conversation
summary as a substitute for repository authority.

Do not dump the whole ledger, glossary, phrase memory, decision log, continuity
archive, or world reference into context for a routine chapter. Use
`prepare.py`, then query only the entries implicated by the current source.

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

Use external research only after the canonical authorities and registered
project source fail to resolve a material question of meaning, identity, or
allusion. Do not browse merely to choose between equally valid stylistic
alternatives in a chat draft.

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
   and translationese without changing source meaning. Explicitly review
   contractions, articles, prepositions, complements, collocations, and
   sentence linkage inside each source paragraph rather than relying on the
   mechanical checker to catch prose problems.

The owner's Chapter 1290 direction permits fuller, clearer phrasing when it
preserves source detail or makes a relationship explicit. Do not meet the
performance budget by compressing away grammatical structure. Complete the
article, preposition, complement, and contraction review before delivery.

When subagents are available, launch these as two independent detector tasks
at the same time after the lead translator has produced one draft. Give each
reviewer an isolated context with no inherited conversation history, or the
smallest possible recent context, plus the exact source, the same draft, the
short chapter authority sheet, and only the relevant canonical rulings. Do not
make each reviewer reread the full repository or conversation. A reviewer may
query one specific authority when a finding genuinely depends on it. They
return paragraph-indexed findings only, never replacement chapters, and they
do not edit shared authority files. If subagents are unavailable, perform the
same two passes sequentially.

Continue the lead translator's local review while both detector tasks run.
Avoid repeated short polling. Collect their findings once the local pass is
complete, then adjudicate them together.

The lead translator decides each finding and applies all accepted corrections
in one surgical patch whenever possible. Save the patched target to an
untracked temporary file outside the repository, then run the mechanical check
once before delivery:

```text
python chatgpt/scripts/chat_check.py <source-file> <target-file>
```

When the scripts are available, this check is mandatory for every chat-first
chapter. It is the enforcement path for hard terms such as `神念` to `divine
sense`, paragraph alignment, title presence, punctuation, and numbers.
If it reports a real hard failure, patch only the listed defect and rerun it.
Do not start another general prose-polishing cycle after the two reviews have
already passed.

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
