# Next novel translation pack

**Status:** Prepared for a new novel, title not yet assigned. This pack is the independent book-specific authority on branch `chatgpt/next-novel`.

The previous novel's glossary, characters, cultivation rules, idioms, lore, chronology, chapter state, and approved expressions belong to the previous novel only. Do not treat them as defaults here. Common Chinese language knowledge is not the same as importing an approved English rendering.

## Reusable translation workflow

- The exact supplied Chinese controls what happens, including omissions, numbers, conditionals, uncertainty, imagery, punctuation force, reveals, viewpoint and order.
- Translate into fluent, publication-quality American English. Match this novel's genre, author and character voices rather than copying the old novel's sardonic xianxia voice.
- Prepare and index source paragraphs. Preserve one English paragraph per Chinese paragraph, including title and ending, except genuine multiline display content. Retain genuine scene breaks.
- Identify new names, titles, places, artifacts, methods and recurring expressions before drafting. Ask one consolidated question only for material new ambiguities; reuse confirmed decisions silently.
- Draft once; check the entire chapter bilingually; cold-read the English; repair demonstrated defects; verify neighboring text. Run the correctly configured mechanical checker on the exact deliverable when available.
- Italicize true direct thoughts, distinguish ordinary narration and dialogue, and format actual panels or inscriptions only where the source and this novel's own conventions warrant it.
- Use straight quotation marks, three-dot ellipses and no em or en dashes; use natural contractions without endings in 'd unless this novel's approved style changes the rule.
- Deliver full chapter prose in chat before maintenance. Keep Chinese source, English chapter text, comparisons and unapproved drafts out of Git. Update only supported book-specific records after feedback or approved decisions.

## Book-specific authorities

1. `state.json`: chapter progress and branch.
2. `glossary/terminology.tsv`, `glossary/entities.tsv`, `glossary/phrase-memory.tsv`: approved and provisional mappings, characters and recurring expressions.
3. `reference/decisions.tsv`: owner rulings with scope and evidence.
4. `reference/continuity.md`, `reference/world.md`: spoiler-safe story and setting facts with chapter citations.
5. `reference/style.md`: the new author's voice and actual novel-specific display conventions.
6. `reference/footnote-candidates.tsv` and `instructions/footnotes.md`: exhaustive cultural-language flagging and selective reader-facing footnotes.
7. `chapters/ledger.tsv`: source, delivery and approval evidence.

Only promote an editorial preference when the owner approves it or a verified repeated pattern supports a scoped decision. Mark proposals as provisional.

## Activation safety

This is a **book pack scaffold**, not yet a fully switched translation pipeline. The existing scripts and `chatgpt/chapters/state.json` on this branch still reference the original novel and its canonical Git branch. They must be updated, isolated and validated against this pack before claiming mechanical checks or using the automatic terminology inventory for the new novel. Until then, use source-grounded manual checks and say when an automatic check was unavailable.

Fill in the actual novel title and chapter frontier only from supplied evidence. Do not assume that the different novel is a previously discussed excerpt.
