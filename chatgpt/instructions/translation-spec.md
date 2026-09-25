# Stage 1: translation spec

Stage 1 settles what the chapter says. Its output is a readable draft that
carries the whole meaning, a verification record, and two ledgers for Stage 2.
The exact supplied Chinese governs content.

## Source and paragraph numbering

- A paragraph is a unit separated by blank lines. Soft line wraps stay inside
  their paragraph. The title is paragraph 1. A standalone `---` is a separator
  and gets no number. `prepare.py` and `chat_check.py` use this numbering.
- If a paste lost its paragraph boundaries, recover them from the supplied
  source. Never guess a new layout. Report the repair in FLAGS.

## Terminology gate

Inspect the whole source for new names, titles, techniques, artifacts and
realms, and for known terms used in a new sense. Include unbracketed and
single-use terms. The `prepare.py` inventory is an aid; it does not find every
new term. Ordinary contextual word choice is not a term decision.

Send one batch, one line per item:

```text
P<index> | <source expression> | <proposed rendering> | <ambiguity, conflict or reason>
```

Put any material source ambiguity in the same batch. Reuse approved choices
without asking again. If a new blocker appears later, finish the independent
work and ask only that question. Never invent a ruling to keep moving. A term
the owner has not approved stays provisional and goes in FLAGS.

## Continuity and identity

Before you apply any reference fact, match the chapter, identity, incarnation,
True or False History, viewpoint and timeline.

- First attestation is not first life. The chapter where the records first
  mention a fact is not the moment it began or became known.
- An absent entry is not a contradiction.
- Do not import later revelations, and do not revive superseded terminology
  from older evidence.
- The Final Kalpa restart (Ch. 1340-1342) makes older chapter-number
  boundaries life-specific. A ruling tied to a chapter in the previous life
  does not carry into the restarted world by itself.
- A draft choice is not canon. Only an owner decision or the source settles a
  question.

## Drafting

Write for meaning and for English agency at once, under
`reference/style-guide.md` and its examples in `reference/craft-examples.md`.
The reader should see who acts, what they do, and why. Use the clearest
faithful expression in the first draft; Stage 2 catches what remains, it does
not supply the draft's natural syntax. Write one draft, not competing versions,
and never start a new translation from an owner edit.

Carry every source relation of cause, contrast or timing with an English word
or structure. Render each repeated key phrase once and reuse that wording.
Write thoughts as mental speech in the thinker's voice.

### Explicitation licence

Chinese often carries cause, contrast or sequence by juxtaposition, by a missing
subject or by aspect alone. When the relation is unambiguous, the English states
it; that is translation, not addition. The licence and the list of what counts
as invention are in style guide section 2. A relation that you can only infer
goes in FLAGS, not into the text.

## Paragraph mapping

- Write one target paragraph per source paragraph, in the same order. Never
  merge or split prose paragraphs.
- The one exception is a display-only split. Genuine panel lines or menu items
  and the narration that adjoins them may become separate paragraphs. Record
  each split as SOURCE:COUNT for the checker.
- Keep the title and the ending. A body-only paste from the owner never deletes
  them.
- A split or merge in the owner's own revision is a local approval, not a
  licence for later drafts. An English-only editing guide never overrides
  paragraph boundaries or source checks.
- Use `---` only for a genuine hard change of place, time or viewpoint, never
  for pacing. A cut to another place and viewpoint, such as 与此同时，…另一处 (owner Ch.1412), takes one. Place it before a time-jump sentence so that sentence opens the
  new scene. Keep every separator the source prints, and record the reviewed
  positions, or none, for the checker.

## Fidelity

Check these on every paragraph:

- numbers and units, including Chinese numerals, percentage points and spans
  of time;
- negation, comparison, certainty and degree; a condition stays a condition;
- the addressee, the speaker and each identity; a true body versus a projection;
- the prerequisites and limits of any power or rule;
- intent, timing, gestures, force and totality (all, every, none);
- revelation order inside the paragraph, and setup before payoff;
- interrupted speech stays unfinished, with no invented interruption action;
- deliberate ambiguity stays ambiguous;
- live idioms, allusions, altered quotations and puns keep their subject and
  logic;
- terms, names and pronouns as the glossary and entity records give them;
- fixed displays and recurring system text word for word.

## Bilingual verification

Read every paragraph against the source, in scene order, as part of its scene.
A term scan or a sample is not coverage. Report only two kinds of finding:

- Critical: meaning, scene logic, identity, number, certainty, omission or
  invention.
- Mechanical: grammar, a fixed display or terminology.

Record each finding in this form:

```text
P<index> | <span> | <source evidence> | <defect> | <Critical or Mechanical> | <smallest repair>
```

"Equivalent wording is not a defect" covers single-word synonym swaps only,
such as quickly for swiftly. It never protects a stiff sentence; Stage 2 owns
that. A current owner ruling outranks an earlier draft choice, so never revert
approved wording to match an older draft.

Record a disposition for every finding: applied, rejected with a reason, or
unresolved. After the repairs, read each changed paragraph with its neighbors.
Compare it with the source and the pre-repair draft for omissions, additions,
repeated transitions, broken references and lost setup or payoff. Account for
every paragraph, and never imply that a partial check covered the chapter.
Findings stay in chat or scratch, never in a repository report.

## Ledgers for Stage 2

Build both ledgers during verification and hand them to Stage 2.

- Connector ledger: each source marker of cause, contrast, concession, a
  fortiori reasoning or timing, with the English word or structure that
  carries it.
- Motif ledger: each repeated key phrase in the source, with its single English
  rendering and the number of times it appears.

Write each row as `P<index> | <source marker or phrase> | <English carrier>`.
