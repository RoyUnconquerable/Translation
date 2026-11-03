# Chinese expressions and footnote review

**Owner requirement:** For each new-novel chapter, flag all Chinese idioms, slang and allusions, including ones that read naturally in English and do not ultimately need a footnote. Record them in `../reference/footnote-candidates.tsv` with the exact source and chapter plus source paragraph index. Do not confuse detection with publication.

## What to flag

- **idiom**: chengyu, proverbs, proverbial images, set sayings and xiehouyu.
- **slang**: colloquial, internet, gaming, meme, regional and period-specific wording.
- **allusion**: classical literature, history, folklore, religion, myth, poetry, pop culture and named quotations.
- **wordplay**: puns, homophones, character-name jokes, altered quotations, ironic reversals and idioms whose literal image matters.
- **cultural**: culture-dependent customs, titles, institutions, practices and social references when the story relies on outside knowledge.

A phrase may need more than one category; use a comma-separated category field if appropriate. Do not flag an everyday word solely for being Chinese.

## Record and verify

For each flag, capture: chapter, Chinese paragraph index, exact Chinese text, category, the specific English rendering, scene-specific meaning, a possible one- or two-sentence footnote, priority, approval status, recurrence link and verification/origin evidence. Do not guess the historical source of a quotation or assert a popular but unverified explanation. Distinguish what the novel says from outside cultural research. Do not copy a previous novel's approved translation without checking the sense here.

If an expression recurs, link later occurrences to the earlier candidate. Retain new entries only when sense, joke, or allusion changes. A category inventory may include multiple occurrences; the published footnote should not repeat needlessly.

## Footnote decision

- **high**: The reader misses the joke, plot logic, naming choice or essential reference without context.
- **medium**: A brief note adds important cultural or literary depth not evident from the translation.
- **low**: The reference is understandable from context or the English already preserves the effect.

Set status to `flagged` by default, then `proposed`, `approved`, `omit`, or `published` as decisions are made. Footnotes are candidates, not automatically part of translated prose. Do not add an intrusive explanatory clause where a discreet note would work better. Keep the literary effect, metaphor and ambiguity in the translation, and avoid footnotes that only restate the English.

## Chapter delivery

Deliver the full translated chapter first. Then give a short `Footnote candidates` section with indexed source references, proposed notes, priority and uncertainty, and keep the complete tracking record in this book's candidate log. Ask the owner about material attribution uncertainties without holding up unrelated translation work. Publish footnotes only once approved, using the requested manuscript format.
