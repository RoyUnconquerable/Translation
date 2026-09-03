# Translation specification

## Source contract

Translate from the exact Chinese source supplied for the current chapter. Keep
the chapter title and preserve one target paragraph for every source paragraph,
in the same order. Do not merge, split, omit, reorder, summarize, or invent.

In file-backed mode, each source and target is a JSON Lines object:

```json
{"id": "ch1282-0001", "src": "Chinese source paragraph."}
{"id": "ch1282-0001", "tgt": "English target paragraph."}
```

IDs, order, and row count must match exactly. A target row contains chapter
prose only, with no notes, alternatives, or commentary.

## Translation priorities

1. Transfer complete meaning, logic, chronology, and rhetorical force.
2. Apply canonical terms and identity facts.
3. Write natural modern English under the macro style guide.
4. Preserve the source's rhythm and each character's voice.

Keep all numbers, comparisons, uncertainty, negation, relationships,
cultivation distinctions, imagery, jokes, and wordplay. Refine Chinese syntax
into grammatical English without adding explanation.

## Chapter authority sheet

Before drafting, identify the paragraph count, scene breaks, recurring
referents and pronouns, hard terms, numbers, time relationships, and allusions.
Search phrase memory only for Chinese text or concepts present in the chapter.
Raise unresolved material choices together in one question batch.

## Drafting standard

- Compose English sentences directly instead of mapping Chinese clauses word
  by word.
- Keep action in clear causal order.
- Use modern, readable narration. Reserve classical elevation for classical
  source material.
- Choose direct thought or free indirect narration before formatting. Direct
  thought is anchored to the character's mental "now" in the story and is not
  mechanically backshifted with past-tense narration; remembered, future, and
  hypothetical content still takes its natural tense.
- Preserve Chinese cultural texture without Westernizing or over-literalizing.
- Preserve a live idiom or allusion inside normal contemporary English syntax.
  Verify recognized quotations instead of reconstructing them from memory.
- Check the actual identity behind every avatar, consciousness, divided self,
  quotation, and disguised speaker.

The complete macro policy is in `reference/style-guide.md`.
