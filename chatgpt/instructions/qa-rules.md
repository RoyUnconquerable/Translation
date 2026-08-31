# QA rules

QA has two complementary layers. Neither substitutes for the other.

## Deterministic checks

`scripts/lint.py` verifies:

- every source ID appears exactly once and every target is nonempty;
- no target row contains an embedded paragraph break;
- no source-script characters remain in English;
- glossary terms use an approved rendering, including recorded exceptions;
- source digit sequences survive in the target;
- target/source length ratios are plausible;
- banned punctuation and typography are absent;
- contractions ending in `'d` are absent.

Coverage, paragraph integrity, source-character, glossary, banned-style, and
forbidden-contraction defects are hard failures. Number and ratio findings are
warnings unless configuration promotes them, but each warning still requires
human judgment.

## Human source review

Read every source row beside its target. Record issues before patching. Review
for all of the following:

### Fidelity

- mistranslation, omission, addition, compressed meaning, invented causal links,
  changed certainty, changed negation, lost contrast, or altered chronology;
- every number, title, relationship, speaker intention, pronoun, and logical
  dependency;
- exact distinctions between cultivation, Dao Attainment, status, Mysteries,
  Fruition Attainments, Dao Fruits, divine abilities, techniques, and artifacts;
- combat geography and cause and effect: who acts, what is used, what it hits,
  and what changes.

### Alignment and formatting

- one target row and one target paragraph for every source row, in identical
  order;
- no source paragraph split for rhythm and no separate source paragraphs merged;
- spoken dialogue remains quoted and unitalicized;
- direct and unmistakable implicit internal thought is italicized, even when the
  Chinese does not explicitly mark it as thought;
- hard scene changes use a line containing only `---`.

### Terminology and continuity

- canonical glossary forms, articles, capitalization, and context exceptions;
- owner rulings such as `the Nether Whisper Ancestor`, bare
  `Demon-Purging True Person`, capitalized `True Self`, `Saint` rather than
  `Sage`, and singular or plural `Variable` according to meaning;
- established character identity, divine pronouns, Dao titles, and chapter
  continuity, without importing facts absent from the source.
- the actual referent behind every avatar, consciousness, divided self,
  quotation, or disguised speaker; divine capitalization follows that referent
  even when the surface form looks mortal.

### Xianxia prose quality

- fluent modern published English in the broad professional register associated
  with leading Wuxiaworld releases, without copying any published wording;
- dignified cultivation language, clear action, controlled grandeur, and the
  correct individual voice for Lü Yang, formal cultivators, and Dao Lords;
- no translationese, wooden syntax, excessive transition openers, clipped
  fragments, or needless formalization of jokes and profanity;
- no Westernization that erases Chinese cultivation concepts or sect culture.

### Idioms, allusions, and wordplay

- every chengyu, classical allusion, Buddhist or Daoist reference, couplet,
  proclamation, and scripture line preserves its defining image and rhetorical
  force;
- concrete images are not flattened into generic paraphrase. The donkey in
  `黔驴技穷`, the Heaven-and-Earth division in `绝地天通`, and the image
  sequence in `梦幻泡影` must survive;
- deliberate character substitutions, homophone jokes, corrupted idioms, and
  title wordplay preserve their contextual double meaning. In `人尽其材`, the
  English must retain both the familiar ideal of putting everyone to use and
  the darker joke that people have become usable material;
- established English allusion names may be used, but unrelated English idioms
  must not replace specifically Chinese imagery.

Fluent prose is not evidence of accuracy. A correct alternate phrasing is not
an issue merely because a reviewer prefers another word. Conversely, smooth
English that drops imagery, paragraph structure, wordplay, or source logic is an
issue.

Write every finding to the chapter issues file before patching. Patch only
flagged IDs and mark each issue patched after source-grounded verification.
Unflagged segments are untouchable.

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
