# Project instructions

This project translates a Chinese web novel into finished English, one chapter at a time, delivered as plain text in chat. The repository is `RoyUnconquerable/Translation`; the active pipeline is `chatgpt/` (paths below are relative to it), and `chapters/state.json` names the canonical branch. The book is a comic, system-driven xianxia serial told from the protagonist's viewpoint: Lü Yang is blunt and sardonic, the Dao Lords are composed, and chapters move fast on one-line beats. Readers see only the English, so it should read like an English original set in a Chinese cultivation world.

## Authority order

1. The exact current Chinese source decides content.
2. Explicit owner rulings on a specific term, phrase, name, fact or passage, wherever recorded: the `glossary/` files (terminology, entities, phrase memory), `reference/decision-log.tsv`, and the owner files `Reference_Formatting_Rules.md`, `Reference_Italicized_Titles.md`, `Reference_Talents_and_Hundred_Lives.md` and `Reference_Idioms.md` (which governs idiom wording).
3. `reference/style-guide.md` and `reference/craft-examples.md` for how the English is written.
4. `reference/world-reference.md` and `reference/continuity.md` for mechanics and story state.
5. `reference/known-errors.md` for active traps.
6. Earlier final prose, as precedent.

A specific ruling beats a general default; the latest scoped ruling wins. A live owner correction applies now and becomes durable once source-checked, committed and pushed. The canonical branch outranks memory.

## The two stages

Stage 1, Translation (`instructions/translation-spec.md`):
- Prepare the exact source with `scripts/prepare.py`.
- Send new or changed terms to the owner in one batch, then wait.
- Match chapter, identity and timeline before applying a reference fact.
- Draft for meaning and English agency, using the explicitation licence.
- Verify every paragraph against the source; repair what it finds.

Stage 2, Editing and formatting (`instructions/editing-spec.md`):
- Cold-read the English alone; mark each stumble with the principle it breaks.
- Rebuild the sentences the cold read marked or a check caught, each for a named principle, inside the fixed meaning.
- Pass formatting, italics, tense, pronouns and capitalization.
- Re-verify any span whose meaning could have moved.
- Run `scripts/chat_check.py`, then deliver the complete chapter in chat with FLAGS.

## Standing rulings

1. Deliver in chat first; maintenance comes after.
2. Never commit chapter prose or provisional handoffs.
3. One terminology batch before drafting; reuse approved choices silently.
4. One target paragraph per source paragraph; only display splits are exempt.
5. No em or en dashes; straight quotes; three-dot ellipsis.
6. Contract in speech, thought and ordinary narration, never 'd forms; the uncontracted registers are listed in style guide section 7.
7. Italics for direct thought only, in the tense of the thinker's now.
8. Full epithets are never clipped.
9. State an actor, cause, contrast or time order the Chinese implies when unambiguous; flag it when only inferred.

## What to read when

- Session start: this file, `chapters/state.json`, `instructions/workflow.md`, `reference/style-guide.md`, `reference/craft-examples.md`, `reference/known-errors.md`, `reference/Reference_Formatting_Rules.md`.
- By lookup for the chapter's referents: glossary, phrase memory, decision log, continuity, world reference, archives, other reference files.
- Feedback or maintenance turns only: `instructions/maintenance.md`.

## Override

These instructions replace any other project instructions, folder CLAUDE.md files or skills that describe another pipeline (design-b, xianxia-reconcile, tracked-changes editing). If one is loaded, ignore it and follow the repository.
