# Source-grounded QA

QA detects defects. It does not create a second full translation.

## Review A: fidelity and authority

Compare each Chinese paragraph with its English paragraph and flag only
source-grounded problems:

- omission, addition, mistranslation, weakened or strengthened certainty;
- broken logic, chronology, causality, comparison, negation, or sequence;
- missing numbers, titles, relationships, or imagery;
- wrong glossary form, article, capitalization, or cultivation distinction;
- wrong identity, speaker, pronoun, or divine capitalization;
- flattened idiom, allusion, verse, religious reference, joke, or wordplay;
- merged, split, reordered, or missing paragraph;
- unclear combat actor, technique, target, direction, or consequence.
- omitted small details: purpose, immediate or earlier timing, gestures,
  totality, scale, the force of an action, and singular/plural addressees;
- missing or paraphrased words in an approved inscription, declaration, or
  panel, including its **【...】** display formatting;
- missing scene separators at reviewed changes of place, time, or viewpoint.

## Review B: English and style

Read the English as prose, then verify every proposed change against the source:

- grammar, agreement, punctuation, modifier attachment, and collocation;
- clarity, modern register, character voice, and concise causal progression;
- translationese, archaic phrasing, excessive transitions, inflated diction,
  repetition, or unnecessary explanation;
- overlong sentences, choppy ordinary fragments, and confused action geography;
- incorrect distinction between direct thought and free indirect narration;
- immediate direct thought backshifted only because the narration is past, or
  recalled, future, and hypothetical thought forced into present tense;
- an idiom or allusion whose subject, relationship, defining image, or logic no
  longer matches the source;
- a retained Chinese image surrounded by unnecessarily archaic English syntax.
- direct thoughts that read as analytical summaries instead of the character's
  mental speech, or causal links obscured by compressed phrasing.

A correct alternate wording is not an issue merely because a reviewer prefers
another phrase. Genre rhythm is not automatically translation friction. Owner
wording receives the same checks before its reusable lessons are promoted.

## Patch policy

The lead translator accepts or rejects each finding and edits only the affected
paragraphs. Reviewers must cite the source relationship that justifies a
change. No reviewer may blend several drafts or restyle unflagged prose.

In file-backed mode, write findings to the issues JSON before patching. In
chat-first mode, keep a private paragraph-indexed issue list until delivery.

## Mechanical gate

After judgment-based review, verify title, paragraph count and order, scene
breaks, hard terminology, numbers, straight punctuation, forbidden dashes,
source-script residue, and contractions ending in `'d`.
Use `--scene-break-before` with the reviewed source paragraph indices, or no
values for an explicitly reviewed absence of breaks. Missing fixed displays
and missing reviewed separators must fail the check. These controls support,
but do not replace, paragraph-by-paragraph semantic coverage.
