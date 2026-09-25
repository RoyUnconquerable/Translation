# Translation workflow

This file is the order of work for one chapter. Stage 1 settles what the
chapter says. Stage 2 makes the English read well without changing what it
says. The detail lives in three specs: `translation-spec.md` for Stage 1,
`editing-spec.md` for Stage 2 and `maintenance.md` for everything after
delivery.

The owner wants routine chapters quickly. Speed never justifies an omission,
and no step exists only for process.

## Session start

1. Read `chatgpt/PROJECT_INSTRUCTIONS.md`, `chatgpt/chapters/state.json` and
   this file once per session. Verify the checkout against the canonical
   branch tip named in state once per session, and preserve any unrelated
   local changes.
2. Load `chatgpt/reference/style-guide.md`, `chatgpt/reference/craft-examples.md`,
   `chatgpt/reference/known-errors.md` and
   `chatgpt/reference/Reference_Formatting_Rules.md`. Keep them for the
   session. Reload a file only after it changes.
3. Use every other authority in the state manifest by lookup. Search the
   glossary, phrase memory, decision log, world reference and continuity
   archive for the chapter's names and terms. Read the matching entries with
   enough context to resolve them, never a whole archive. Search outside the
   repository only for a material question the records do not answer.
4. A waiting chapter always comes first. Maintenance never runs ahead of it.

## Stage 1: translation (what is said)

1.1 Prepare. Save the exact supplied Chinese to a file outside Git and run:

```text
python3 chatgpt/scripts/prepare.py <source-file>
```

Keep the file intact. `translation-spec.md` explains the paragraph numbering
and how to repair a paste that lost its boundaries. If `prepare.py` reports
that repository state trails the conversation, rerun it with
`--observed-through N`, where N is the last source chapter you have verified
in this session (`chatgpt/README.md`); this changes no state and proves no
delivery.

1.2 Terminology gate. Send the owner one batch with every new or changed term
and wait for the answer before drafting. If there is nothing new, go straight
on. The batch format is in `translation-spec.md`.

1.3 Continuity and identity. Check each reference fact against the chapter's
identity, life and timeline before using it (`translation-spec.md`).

1.4 Draft for meaning and for English agency, under the explicitation licence
and the paragraph mapping rules in `translation-spec.md`.

1.5 Verify every paragraph against the source, repair the findings, and build
the connector ledger and the motif ledger for Stage 2 (`translation-spec.md`).

## Stage 2: editing and formatting (how it reads)

2.1 Cold read the English alone and mark each stumble with the principle it
breaks.

2.2 Rebuild the sentences the cold read marked or a check caught, each for a
named principle, inside the fixed limits.

2.3 Run the formatting and conventions pass.

2.4 Send every span whose meaning, degree, actor or order could have moved back
through the Stage 1 bilingual check.

2.5 Run the mechanical check on the exact text you will deliver:

```text
python3 chatgpt/scripts/chat_check.py <source-file> <target-file> --scene-break-before <indices>
```

- Always pass `--scene-break-before`. With no reviewed breaks, pass the flag
  with no indices. If you omit the flag and the source has no `---`, the
  checker skips the reviewed-position check.
- Indices are source content indices: the title is 1, and a standalone `---`
  is not counted.
- For a display-only split, add `--display-splits SOURCE:COUNT` (for example
  `8:3`). COUNT is the total number of target paragraphs for that source
  paragraph, and SOURCE is 2 or higher.
- Fix real failures in the affected spans and rerun. Adjudicate a lexical false
  positive against the source, record it for maintenance, and never call it a
  clean PASS. Resolve digit warnings against the source quantities.
- The checker proves mechanics only, not meaning. If a tool cannot run, do its
  checks by hand and say so.

2.6 Confirm the definition of done in `editing-spec.md`.

`editing-spec.md` holds the checks for steps 2.1 to 2.6.

## Deliver

Send the complete checked text in chat, with the title, paragraph boundaries,
thought spans and scene breaks exactly as checked. If the text changes after
the check, re-verify the changed spans and rerun the check.

After the chapter, add a FLAGS block. List:

- provisional or unapproved terms, with paragraph index;
- relations you could only infer, and so left unstated;
- puns or wordplay that did not survive;
- repairs to the supplied paste, such as recovered paragraph boundaries;
- unresolved findings and material ambiguities kept open;
- adjudicated checker exceptions and any tool that did not run.

Write "FLAGS: none" when the list is empty.

Delivery rules:

- Deliver the complete chapter in chat before any maintenance.
- A saved draft is not delivery. If the output was cut off, resend the whole
  chapter before doing anything else.
- An explicit owner correction applies to the current chapter now. It becomes
  durable only when the maintenance update is committed and pushed
  (`maintenance.md`).
- Never commit chapter prose, source text, full comparisons or provisional
  handoffs.
- Be honest about what is durable. A chapter in chat or an uncommitted edit is
  not a published record.

## After delivery

Feedback, durable updates, validation and publication follow `maintenance.md`.
