# Translation specification

## Input and output contract

Source segments are JSON Lines objects containing `id` and `src`. The draft
must contain exactly one JSON object per line:

```json
{"id": "ch1211-0001", "tgt": "English translation."}
```

IDs, order, and count must match the source segments exactly. Never merge,
split, reorder, skip, or invent segments. One source paragraph remains one
target paragraph. Do not insert an extra paragraph break inside a target row or
combine separate source rows into one paragraph. A target value contains prose
only, with no notes, alternatives, brackets, or commentary.

## Required repository context

Before drafting, read in order:

1. `chapters/state.json`;
2. `config.json`;
3. `glossary/terminology.tsv`;
4. `reference/style-guide.md`;
5. every terminology, style, world-reference, and continuity supplement named
   in the state handoff;
6. the immediately preceding relevant chapter material.

Repository files outrank chat memory. The latest owner ruling wins.

## Translation priorities

1. Transfer the complete source meaning. Do not summarize, compress,
   embellish, or add causal links, images, motives, or facts.
2. Obey `glossary/terminology.tsv` exactly. A listed source term must use one
   of its listed variants, with the contextual exceptions recorded in notes.
3. Follow `reference/style-guide.md` for xianxia register, tense, thought
   formatting, dialogue, capitalization, titles, units, punctuation, idioms,
   allusions, paragraph integrity, and rhythm.
4. Use continuity and the preceding chapter to resolve pronouns and scene
   logic, but never import content absent from the source.
5. Preserve every number, date, sequence, measurement, contrast, negation,
   uncertainty marker, speaker relationship, and cultivation distinction.

Accuracy outranks elegance. Once meaning is secure, compose fluent,
published-quality American English in the broad professional xianxia register
associated with leading Wuxiaworld releases. Preserve Chinese cultural texture
and cultivation logic without mirroring Chinese syntax or copying published
wording.

## Cultural and thought handling

- Preserve the defining imagery of chengyu, classical allusions, Daoist and
  Buddhist references, couplets, proclamations, and scripture lines inside
  natural English.
- Never flatten an image-bearing idiom into a generic conclusion. Retain the
  donkey in `黔驴技穷`, the Heaven-and-Earth division in `绝地天通`, and
  comparable load-bearing images.
- Italicize direct and unmistakable implicit internal thought, including silent
  questions, exclamations, reasoning, and conclusions. Do not italicize plain
  focalized narration.
- Refine unclear or literal source syntax into natural English while preserving
  every meaning-bearing detail and keeping it in the same source paragraph.

## Self-review before lint

- Compare every target row directly against its own source row.
- Confirm one target row and one target paragraph per source row, with identical
  IDs and order.
- Confirm glossary forms, articles, capitalization, and established divine
  pronouns.
- Expand every contraction ending in `'d` while retaining other natural
  contractions.
- Remove em dashes, en dashes, curly quotes, single-glyph ellipses, fullwidth
  punctuation, and other banned forms.
- Confirm spoken dialogue versus internal-thought formatting, including
  implicit thoughts not explicitly marked in Chinese.
- Check every idiom, allusion, verse, and religious reference for preserved
  imagery and rhetorical force.
- Check combat geography, cause and effect, technique ownership, and the exact
  distinction between cultivation, Dao Attainment, status, Mysteries, and
  Fruition Attainments.
- Check names where same-gender referents could make a pronoun ambiguous.
- Read the English alone for professional xianxia flow, then recheck it against
  the source so fluency has not hidden an omission or invention.
- Confirm all new or changed terms and unresolved ambiguities were surfaced in
  the approved terminology batch before drafting.
