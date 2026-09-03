# Owner revision and editing

The owner's intent, explicit terminology choices, and approved editorial
decisions are authoritative. Supplied English is not exempt from source,
grammar, continuity, terminology, tense, formatting, or allusion review.

Repair clear mechanical errors directly. If owner wording appears to change
meaning, weaken or substitute an idiom, contradict a hard term or identity, or
create unnatural English, do not canonize it silently and do not silently
override it. Present the issue and a source-grounded alternative for
confirmation.

## Compare once

Align the owner version with both the exact source and the prior draft,
paragraph by paragraph. First verify fidelity, grammar, terminology,
continuity, thought mode and tense, allusions, and formatting. Then record what
changed in word choice, tone, sentence structure, pacing, terminology, logic,
and formatting. Do not treat a typo or an unverified mistranslation as stylistic
evidence.

## Classify before promotion

Every difference receives one classification:

- `MACRO`: a reusable writing principle;
- `TERM`: a stable recurring name or concept;
- `PHRASE`: a contextual title, allusion, verse, image, or special line;
- `FACT`: a stable world mechanic or relationship;
- `CONTINUITY`: current plot state;
- `LOCAL`: a passage-specific preference;
- `MECHANICAL`: spelling, punctuation, agreement, duplicated text, or paste
  damage.

Promote each item only to its matching canonical file. One edit may support an
existing rule without creating a new one. Local and mechanical items do not
become global rules.

## Repository update

Update the chapter ledger and compact state. Do not create chapter-specific
style, glossary, continuity, world, or owner-edit files. Record concise
provenance in `reference/decision-log.tsv` only when useful.

A live decision is provisional cross-session memory until its repository update
has been committed and pushed to the canonical GitHub branch named in state.

In file-backed mode, apply wording to the aligned draft and reassemble rather
than hand-editing final output. In chat-first mode, chapter prose remains in
chat unless the owner explicitly authorizes durable storage.

Run every repository gate in `workflow.md`, review the diff, make one coherent
commit, and push it.
