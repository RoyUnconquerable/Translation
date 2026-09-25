# Stage 2: editing and formatting

Stage 1 settles what the chapter says. Stage 2 makes it read like an English
original without changing what it says. It starts from the verified Stage 1
draft and its two ledgers (`translation-spec.md`). The craft is in
`reference/style-guide.md`; the worked pairs are in `reference/craft-examples.md`.

## Mandate

- Inside the limits below, you may rebuild a whole sentence, reorder clauses
  inside it, and split or join sentences inside a paragraph, but only for a
  named reason: the style guide principle the sentence
  breaks, such as a buried agent, effect before cause, a demoted climax, a
  rotated refrain, an added hedge, thought turned into report, a lost connector
  or a monotone run. If you cannot name the principle, leave the sentence.
  There is no blanket smoothing.
- A correct sentence that breaks a named principle is a defect. "Equivalent
  wording is not a defect" protects only a single-word synonym swap.

## Limits

Stage 2 never changes:

- supported meaning, including premises, conditions and negation;
- degree and certainty, including every source hedge, and no new ones;
- terms, owner-fixed wording and identities;
- paragraph boundaries, paragraph order and revelation order in a paragraph;
- fixed displays, titles and recurring system text;
- deliberate one-line beats.

## 2.1 Cold read

Read the English alone, as a reader who never saw the Chinese. Keep the source
closed for this read. Go paragraph by paragraph, then read the whole chapter in
one pass for its rhythm and its motifs.

Mark every stumble: a reread, a wrong guess about who acts, a reason that
arrives late, a flat run, a beat that does not land. Write the principle next to
each mark (for example "P43: reversal demoted to participle, style guide 4").
The marks are the work list for 2.2.

## 2.2 Checks

Run each test, then take the smallest action that fixes what it finds.

1. Connector ledger. Test: for each marker in the ledger, point to its English
   carrier. Action: where a carrier is missing, add the smallest one (because,
   so, by contrast, the next instant, but). Remove a connector only when it is
   empty filler.
2. Last-clause test. Test: compare each paragraph's final English main verb
   with the source's final clause. Action: if the English ends on a participle,
   an adverbial or an explanation, promote the climax or move the explanation
   before its question.
3. Tail and attachment scan. Test: find sentences that end in ", -ing ...",
   "merely ...", "without the slightest ..." or two stacked prepositional
   phrases, and opening phrases whose implied subject is not the sentence's
   subject. Action: promote the tail to a finite verb, move it before the verb,
   or attach the phrase to its real subject. Exception (owner Ch.1411-1414): a
   participle tail that adds a secondary result or an accompanying state may
   stay ("deepening his sense of...", "intense emotion rising in their eyes");
   only a climactic action or a reversal must be promoted.
4. Pronoun walk. Test: name the referent of every he, she, it and they, and
   check number. Action: use the name where a nearby noun could claim the
   pronoun; fix agreement.
5. Motif ledger. Test: list every English rendering of each repeated key phrase
   and count each anaphora. Action: unify to the first rendering and restore
   the source count.
6. Hedge diff. Test: align seemed, apparently, could only, barely, little,
   merely and just with the source's hedges. Action: delete an unmatched hedge
   or intensifier; restore a missing hedge.
7. "And" audit. Test: find "X, and Y" where the source has 更, 因此, 却 or 反而,
   and sentences with two or more "and" joins. Action: replace one "and" with
   the real relation.
8. Question check. Test: every source question stays a question with its force,
   unless it is reported speech. Action: restore the question and its meaning.
9. Voice read. Test: read each deliberation paragraph as the character. Does it
   sound like a narrator summarizing? Action: restore interjections, litotes,
   rhetorical questions, 与其...不如 order and the thinker as he.
10. Padding strike. Test: find phrases with no source counterpart that grammar
    does not need, and doubled framing. Action: delete them.
11. Register pass. Test: check the uncontracted registers listed in style
    guide section 7 for contractions, and banter and Lü Yang's inner voice for
    formal labels. Action: expand the first; make the second colloquial.
12. Length spread. Test: in a paragraph of three or more sentences, are all
    lengths within about four words of each other? Do three consecutive
    sentences open with a prepositional or participial phrase? Action: join two
    sentences by their relation, split off the punch line, or move an opener.

## 2.3 Formatting and conventions pass (check 13)

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

## 2.4 Re-verify (check 14)

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
- No paragraph opens three consecutive sentences with a prepositional or
  participial phrase.
- Every source relation of cause, contrast and timing has a visible carrier.
- Each paragraph ends on the source's final clause, unless check 2 moved an
  explanation before its question.
- Refrains and motifs keep one wording and the source count.
- No hedge or intensifier lacks a source counterpart.
- Dialogue sounds spoken, and formal registers stay formal.
- Every moved span passed re-verification.
- The checker passes, or each exception is adjudicated and flagged.

## Owner edits

When the owner returns an edited chapter, the review scope, comparison,
classification and promotion rules are in `maintenance.md`.
