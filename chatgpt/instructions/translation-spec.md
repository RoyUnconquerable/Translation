# Translation specification

## Input and output contract

Source segments are JSON Lines objects containing `id` and `src`. The draft
must contain exactly one JSON object per line:

```json
{"id": "ch1211-0001", "tgt": "English translation."}
```

IDs, order, and count must match the source segments exactly. Never merge,
split, reorder, skip, or invent segments. A target value contains prose only:
no notes, alternatives, brackets, or commentary.

## Translation priorities

1. Transfer the complete source meaning. Do not summarize, compress,
   embellish, or add causal links, images, motives, or facts.
2. Obey `glossary/terminology.tsv` exactly. A listed source term must use one
   of its listed variants, with the contextual exceptions recorded in notes.
3. Follow `reference/style-guide.md` for tense, register, dialogue,
   capitalization, titles, units, punctuation, and rhythm.
4. Use `reference/continuity.md` and the preceding chapter to resolve pronouns
   and scene continuity, but never import content absent from the source.
5. Preserve every number, date, sequence, measurement, contrast, negation,
   uncertainty marker, and speaker relationship.

Accuracy outranks elegance. Once meaning is secure, compose natural published
American English rather than mirroring Chinese syntax.

## Self-review before lint

- Check each target against its own source row.
- Confirm glossary forms and established divine-pronoun capitalization.
- Expand all contractions ending in `'d`.
- Remove banned glyphs and translationese listed in the style guide.
- Confirm dialogue versus inner-thought formatting.
- Check names where same-gender referents could make a pronoun ambiguous.
- Check that chapter-specific terms and unresolved ambiguities were surfaced
  during the approved terminology stage.
