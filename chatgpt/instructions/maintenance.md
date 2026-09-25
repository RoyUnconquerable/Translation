# Maintenance

Maintenance turns owner feedback into durable records and publishes them. It
runs only after delivery (`workflow.md`).

## When it runs

- It runs on an approval, a correction or an explicit maintenance turn.
- A turn that brings a correction and a new chapter applies the correction to
  that chapter, delivers it, and does the maintenance afterwards.
- An explicit owner correction authorizes its own verified update. Do not ask
  for whole-chapter approval, and do not wait for a feedback-only prompt.

## Compare once

Use the exact source, the delivered draft and the owner's version. Make one
indexed comparison, including punctuation, capitalization, merged paragraphs
and dropped framing. Align a body-only paste to the source body, not the title.

- For each changed sentence, ask why it changed: the problem, the intended
  improvement and the source support. Label inferred intent as inferred.
- Attribute each error to the draft, the revision or both.
- Check the changed spans and the causal and referent links next to them. Do
  not recheck unchanged text that already had a full review unless a new
  defect, term, identity or source finding reaches it. With no evidence of
  that review, do one complete bilingual pass.
- Keep the full comparison in chat, and give it when the owner asks. Do not
  log every wording substitution.

An owner-edited chapter is not automatically owner-final. Source seen, chat
delivery, correction recorded and owner-final approval stay separate states,
and historical gaps stay recorded. Owner-final stays at Ch. 1338 until the
owner says otherwise. Never infer approval from the next chapter arriving, or
delivery from a timestamp.

## Source-check owner revisions

Check every owner revision against the source. An explicit decision applies
exactly as given. Accidental damage, such as an omission, a new source
conflict or a mechanical slip, is shown to the owner with a located
alternative. Never silently replace owner wording, and never promote accidental
damage as a preference.

## Classify and promote

Classify each lesson before you edit a record:

- TERM: a stable recurring rendering or an explicit term correction;
- MACRO: a reusable writing principle, not a favored local synonym;
- PHRASE: fixed wording, a live image or a contextual sense, with its scope;
- FACT: a stable world mechanic, with its limits and who claims it;
- CONTINUITY: the current plot state, with earlier beliefs kept and dated;
- LOCAL: phrasing for one passage, kept as evidence only;
- MECHANICAL: a typo, agreement slip or paste repair, not a new preference.

Behind a wording edit, find the construction problem: subject and action,
clause relations, information order, imagery, rhythm or register. Search the
older records first. Amend the matching rule in place instead of adding a
second one. If the style guide already covers the lesson, add no rule.

An explicitly repeated correction is binding within its scope. Remove the
superseded alternatives from active entries; old wording stays as provenance.
A local variant stays local. Never write per-chapter supplements.

The four owner reference files (`Reference_Formatting_Rules.md`,
`Reference_Idioms.md`, `Reference_Italicized_Titles.md`,
`Reference_Talents_and_Hundred_Lives.md`) are book-wide authorities. Maintain
them in place and never copy their tables elsewhere. Editing one puts the
owner's library copy out of sync, so record the change in
`reference/project-source-registry.md`.

## Exemplar bank

`reference/craft-examples.md` holds at most 16 before/after triples. When a new
owner rewrite shows a principle clearly, it replaces the oldest triple that
shows the same principle. Keep each triple to three short lines. The file never
grows past the cap.

## Update and commit

Update every affected record together in one local patch: glossary (terms,
entities, phrase memory), style guide, craft examples, continuity, world
reference, known errors, decision log, ledger and state. Leave unaffected files
untouched.

Commit and push once after every chapter that ends in 0 (1410, 1420 and so
on), or earlier when the owner explicitly asks. Apply feedback locally at once
and keep it uncommitted until then. Editing feedback on an old chapter does not
count as a new chapter. An uncommitted edit is not published persistence.

## Validate

Run these once after the patch is complete, then review the diff:

```text
python3 -m unittest discover -s chatgpt/tests
python3 chatgpt/scripts/audit.py
python3 chatgpt/scripts/lint.py --all
python3 chatgpt/scripts/state.py
```

After fixing a real defect, rerun only the affected checks. A size warning
means consolidate. Never raise a limit, reclassify a real term, or split one
note into many rules to silence a warning.

Change scripts and instructions only in a maintenance run, with the tests, and
never inside a chapter turn.

## Publish

1. Fetch the remote first. If it moved, reconcile without force-pushing and
   without overwriting other work.
2. Push to the canonical branch named in state, and to the working branch
   when it differs.
3. Verify that the published tree matches the reviewed local tree.
4. If publication is blocked, report it plainly.
5. Claim persistence only after the push succeeds.

## Evidence limits

- The English-only upload guide is not a translation authority. Its paragraph
  restructuring, Word tracking and no-raws policy do not transfer. The
  display-only split rule in `translation-spec.md` still applies.
- Publisher research is craft evidence, not authority over this novel, and it
  never enters the chapter path.
- The manuscript the owner approved on 16 September 2026 carries English
  approval only. It is not a bilingual audit, and maintenance never edits it.
- Record research turns and instruction rewrites in
  `reference/consolidation-history.md`.
