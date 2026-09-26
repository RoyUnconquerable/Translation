# Stage 2: editing and formatting

Stage 1 settles what the chapter says. Stage 2 makes it read like an English
original without changing what it says. It starts from the verified Stage 1
draft and its two ledgers (`translation-spec.md`). The craft is in
`reference/style-guide.md`; the worked pairs are in `reference/craft-examples.md`.

## Mandate

- Inside the limits below, you may rebuild a whole sentence, reorder clauses
  inside it, and split or join sentences inside a paragraph, but only for a
  named reason: the style guide principle the sentence
  breaks, such as a buried agent, events out of order, an unstated causal
  step, a key action demoted to a tail, a sentence carrying two claims, a
  rotated fixed phrase, an added or lost hedge, thought turned into report, or
  a literal gloss. If you cannot name the principle, leave the sentence.
  There is no blanket smoothing.
- A correct sentence that breaks a named principle is a defect. "Equivalent
  wording is not a defect" protects only a single-word synonym swap.

## Limits

Stage 2 never changes:

- supported meaning, including premises, conditions and negation;
- degree and certainty, including every source hedge, and no new ones;
- terms, owner-fixed wording and identities;
- paragraph boundaries (except the lead-in merges in `translation-spec.md`),
  paragraph order and revelation order in a paragraph;
- fixed displays, titles and recurring system text;
- deliberate one-line beats.

## 2.1 Cold read

Read the English alone, as a reader who never saw the Chinese. Keep the source
closed for this read. Go paragraph by paragraph, then read the whole chapter in
one pass for its rhythm and its motifs.

Mark every stumble: a reread, a wrong guess about who acts, a reason that
arrives late, a flat run, a beat that does not land. Write the principle next to
each mark (for example "P43: reversal demoted to a tail, style guide 4").
The marks are the work list for 2.2.

## 2.2 Checks

Run each test, then take the smallest action that fixes what it finds. The
style guide's priority order (section 2) decides conflicts: clarity and
natural English outrank keeping the source's clause shape.

1. Agency. Test: for every sentence, name who acts. Action: make the doer the
   subject, lead with the agent instead of an "At the cost of..." or "With..."
   opener, unpack a noun that hides an action, and name the real subject of a
   claim.
2. Order and cause. Test: do events appear in the order they happened, and
   can the reader see why each step follows? Check the connector ledger:
   every marker has a carrier or an English order that already shows the
   relation. Action: reorder into time order; add the smallest carrier (so,
   because, that meant, because of that) where the reader would otherwise
   infer; drop a marker the order already shows and every stock signpost.
3. Clause weight. Test: does the key action, reversal or decision have its own
   finite verb? Action: promote it from a participle, adverbial or trailing
   explanation. A participle tail that carries a secondary result or an
   accompanying state may stay. Attach every opening phrase to its real
   subject.
4. One claim per sentence. Test: find sentences that carry two ideas, two
   actors, a nested clause chain, or a shift of focus, and descriptions made of
   stacked modifiers. Action: split them, untangle the nesting into plain
   order, or break the description into concrete beats.
5. Pronoun walk. Test: name the referent of every he, she, it and they, and
   check number. Action: use the name where a nearby noun could claim the
   pronoun; fix agreement.
6. Wording ledger. Test: list every English rendering of each repeated key
   phrase. Action: unify to the phrase-memory or first rendering. Keep a
   refrain's repetition; clause-level anaphora may merge.
7. Hedge diff. Test: align seemed, apparently, might, may not, barely, merely
   and just with the source's hedges (似乎, 好像, 几乎, 仿佛, 恐怕, 未必, 或许).
   Action: delete an unmatched hedge or intensifier; restore a missing one.
   "That could only mean" as an inference is not a hedge.
8. "And" audit. Test: find "X, and Y" where the real relation is cause,
   contrast or consequence, and sentences with two or more "and" joins.
   Action: replace one "and" with the relation or split the sentence.
9. Question check. Test: every source question stays a question with its force,
   unless it is reported speech. Action: restore the question and its meaning.
10. Thought and voice. Test: apply the style guide's one italics test to each
    thought span; read each deliberation as the character. Action: italicize
    first-person or addressed inner speech in the thinker's present, romanize
    third-person comments, and restore interjections, litotes and rhetorical
    questions a narrator summary lost.
11. Idiom and diction pass. Test: find literal glosses of set phrases, stock
    signposts, stacked intensifiers and the other tells in style guide
    section 12. Action: use a natural English translation of the idiom or the
    stock English idiom, keep a meaningful image,
    cut the tell.
12. Register pass. Test: check the uncontracted registers in style guide
    section 7 for contractions, narration and composed speech for loose
    diction, and Lü Yang's voice for formal labels. Action: fix each.
13. Padding strike. Test: find phrases with no source counterpart that grammar
    does not need, and doubled framing. Action: delete them.

## 2.3 Formatting and conventions pass (check 14)

Apply the style guide sections named here; do not restate them.

- Language: check articles, possessives, countability, prepositions,
  agreement, complements and collocations; keep paired actions and modals
  parallel; put only beside what it limits.
- Thought: italics only for direct inner speech, over the actual span; tense
  from the thinker's now; free indirect thought roman and past (section 8).
- Titles per `Reference_Italicized_Titles.md`; bold **【...】** displays exact per
  `Reference_Formatting_Rules.md`; system text per
  `Reference_Talents_and_Hundred_Lives.md`.
- Capitalization and pronoun rulings (section 10).
- Contractions (sections 7 and 11), with no quota.
- Scene breaks, typography, numbers and units (section 11).

## 2.4 Re-verify (check 15)

Any span whose meaning, degree, actor or order could have moved goes back
through the Stage 1 bilingual check in `translation-spec.md`. Check those spans
only, each against its source paragraph and neighbors. A rebuild that fails
goes back to the verified wording or is rebuilt again.

## 2.5 Mechanical check

Run `chat_check.py` on the exact text you will deliver, as `workflow.md` step
2.5 specifies. Fix real failures and rerun. Adjudicate a lexical false positive
against the source and record it for the FLAGS block.

## 2.6 Definition of done

- Every sentence has a clear actor, or a deliberate reason not to.
- Events read in the order they happened, and every causal step the reader
  needs is visible.
- Each key action, reversal or decision has its own finite verb.
- No sentence carries two claims or a tangle of nested clauses.
- Fixed phrases keep one wording; refrains keep their repetition.
- No hedge or intensifier lacks a source counterpart.
- Dialogue sounds spoken, and formal registers stay formal.
- Every moved span passed re-verification.
- The checker passes, or each exception is adjudicated and flagged.

## Owner edits

When the owner returns an edited chapter, the review scope, comparison,
classification and promotion rules are in `maintenance.md`.
