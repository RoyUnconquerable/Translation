# QA rules

QA has two complementary layers. Neither substitutes for the other.

## Deterministic checks

`scripts/lint.py` verifies:

- every source ID appears exactly once and every target is nonempty;
- no source-script characters remain in English;
- glossary terms use an approved rendering, including recorded exceptions;
- source digit sequences survive in the target;
- target/source length ratios are plausible;
- banned CJK and typographic punctuation is reported.

Coverage, source-character, and glossary defects are hard failures. Number,
ratio, and punctuation findings are warnings unless configuration promotes
them, but each warning still needs human judgment.

## Human source review

Read every source row beside its target. Look for mistranslation, omission,
addition, term drift, wrong tone or pronoun, awkward English, lost logic,
changed certainty, incorrect speaker attribution, and punctuation that changes
meaning. Fluent prose is not evidence of accuracy.

Write issues before patches. Unflagged segments are untouchable. A correct
alternate phrasing is not an issue merely because a reviewer prefers another
word.

## Final-state gate

`scripts/state.py` verifies that:

- state counts match the actual chapter artifacts;
- segment and draft contracts match;
- lint passes when recomputed;
- every final chapter has review evidence with no unpatched issues;
- assembled output exactly matches the reviewed draft;
- telemetry has one accurate row per finalized chapter;
- the next-chapter pointer follows the latest finalized chapter.

The pipeline is not finished until both `lint.py --all` and `state.py` pass.
