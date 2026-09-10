# Translation workflow

This is the sole execution policy. Source/style authorities govern content;
QA and editing specifications describe the relevant pass, not extra stages.
The target is complete, accurate modern xianxia English in chat in roughly
three to five minutes for an ordinary chapter. It is a budget, not a guarantee
or permission to cut content. Give a short update if a real blocker intervenes.

## 1. Verify once, then reuse

At session entry, verify the checkout and canonical remote tip named in
`chapters/state.json`, preserving unrelated changes. Read state and this
workflow once. State's authority manifest is a lookup map, not a reading list.
Load the style guide and current error guidance if not already in active
context. Do not use chat memory or a summary as a substitute for their contents.

During that session, reuse the verified tip and unchanged reference content.
Before each chapter, one local status/diff check is enough to detect local
changes. Do not fetch, reread the dispatcher, dump the full manifest, or run
repository-wide gates every chapter. Refresh the remote at a new session,
checkout uncertainty, an indicated external change, or before publishing.
After a local update, reload only affected authority entries. After compaction,
reload only the instructions and relevant source records no longer available.

Use the exact supplied Chinese, saved outside Git. Run once:

```text
python chatgpt/scripts/prepare.py <source-file>
```

Its inventory supplies matching terms, usage notes, entities, phrases, numbers
and potential scene changes. Reuse that output for drafting and review; do not
reproduce it in another full authority sheet. Add only relevant historical
facts, reviewed scene positions, thought speakers/time references and material
ambiguities. Search the glossary, phrase memory, decisions, world reference
and continuity archive across their full history by the current referents.
Read matching passages and enough context to resolve them, never whole archives.
Do not refetch an unchanged historical entry already in active context.

New owner corrections in the live turn must be included in the same compact
review input, clearly distinguished from draft wording and proposed alternatives.
A draft choice is not canon. Keep prerequisites, limits, identities, attribution
and earlier versus later revelations intact. A missing older attachment is not
evidence that it was checked. Search externally only for a material question
unresolved by the canonical records; batch necessary terminology questions.

### Progress between approved updates

Do not publish metadata just to start the next chapter. `prepare.py` already
checks the source frontier; do not also run `state.py --incoming-chapter`.
If approved-update state trails the visible conversation, verify the actual
intervening sources and deliveries, keeping source seen, delivered and approved
separate. Pass `--observed-through N` only for that verified in-session source
frontier. This read-only input does not mutate state, prove delivery or grant
approval. It cannot fill an unknown gap; retrieve specific missing evidence or
report the uncertainty. Reconcile verified progress in the next approved atomic
update, without provisional files, handoff commits or guessed approvals.

## 2. Draft once

Translate directly from the exact source. Preserve every source paragraph,
including title, isolated reaction and ending, in order. Sentence structure may
change inside paragraphs for clear English. Apply the style guide while writing.
Do not generate competing drafts or start a new translation from an owner edit.

## 3. One bounded bilingual review and targeted repair

Use the existing fidelity detector for one source-aligned review covering both
fidelity and English under `qa-rules.md`. There is no separate English detector
or additional lead reread of the whole chapter. The lead owns drafting and
adjudication, rather than duplicating the detector's review.

When delegation is available, use one reviewer with no inherited conversation
history. Supply the exact source, the one draft, its inventory plus relevant
historical rulings, explicit current owner corrections and the QA specification.
Do not give it full-history context or make it reload the repository. It returns
paragraph-indexed defects with source/authority evidence, never another draft,
optional synonym lists, or direct edits to shared authorities. It may resolve
one specifically necessary missing reference, not conduct broad research.
Without delegation, perform this same review locally once.

Allow roughly 60-90 seconds for review. Do not repeatedly poll or block a single
wait beyond 60 seconds. Read the completion when available. At the review budget,
ask the existing reviewer for its covered range and findings, stop it if needed,
and finish only the uncovered portion locally. Do not spawn replacements or
repeat completed work. State a fallback honestly; never pretend coverage passed.

Adjudicate findings against the exact source and current authority. Patch only
real defects, preferably in one pass. Reject unsupported preferences and stale
term reversions. Then run the existing mechanical check once:

```text
python chatgpt/scripts/chat_check.py <source-file> <target-file> --scene-break-before <indices>
```

Pass no indices after the flag if no breaks are required. It checks framing,
paragraph count, specified separators, terminology, fixed displays, typography,
source residue and digit warnings. It does not prove semantic completeness,
Chinese-number conversion or good English. The bilingual review does that.
For real failures, fix only the affected spans and rerun the check. A lexical
false positive gets a source-grounded adjudication, not invented wording or a
new exemption that hides real matches. Record it for the next feedback repair;
do not describe an unresolved exception as an unqualified PASS.

## 4. Deliver immediately

Return the complete reviewed chapter in chat as soon as required defects are
resolved. Do not begin repository maintenance, another polish pass, further
reference searching or CI waiting first. A saved draft is not delivery. If
interrupted, resume from the checked draft; if output was missing, resend it
in full before troubleshooting. Do not infer delivery from timestamps.

Ordinary chapters require preparation, one draft, one bilingual review, targeted
repair and the final mechanical check only. A reasonable allocation is about
30 seconds for preparation, two to three minutes for drafting, 60-90 seconds
for review/repair and under 30 seconds for the final check and delivery. The
three-to-five-minute goal depends on chapter complexity and service latency.
Never omit content to meet it; explain a concrete blocker instead.

## 5. Feedback after approval

Use `editing-spec.md` only on an approval, correction or maintenance turn.
Explicit owner corrections already authorize their verified update; do not
ask again for whole-chapter approval. Supplied edits receive one indexed
comparison and the same bounded bilingual check, not two additional reviews.
If feedback and a new chapter arrive together, apply the live correction to
that chapter and deliver it first. Publish the approved consolidated update
after delivery at the first available maintenance opportunity, in the same turn
if the interface allows it. If final chat delivery ends the turn, resume the
authorized update on the next available turn; no feedback-only prompt or renewed
approval is required. A waiting chapter still comes first. Do not claim
unpublished changes are saved.

Compare against the source and delivered draft, asking why each changed sentence
changed. Record inferred intent as inferred. Update the existing glossary,
style, continuity, world reference and state together where affected, in one
atomic commit. Preserve untouched valid records; changing every file is not a
goal. Never add chapter-specific supplements, commit chapter text, create
provisional handoffs or infer approval from the next chapter arriving.

## 6. One repository validation and publication

These are feedback/maintenance gates, never prerequisites to chapter delivery:

```text
python -m unittest discover -s chatgpt/tests
python chatgpt/scripts/audit.py
python chatgpt/scripts/lint.py --all
python chatgpt/scripts/state.py
```

Run them once after the complete patch and review the diff. If a gate reveals a
real defect, rerun only affected checks after fixing it. Size warnings prompt
focused consolidation on maintenance turns; preserve valid rules and do not
raise limits or reclassify a real term just to silence a warning.

Publish one coherent commit to the canonical branch and, when different, the
working branch without force-pushing. Fetch/check the current remote before
publication; if it moved, reconcile without overwriting external work. Use the
normal authenticated Git path when available; otherwise use the existing GitHub
connector once with bounded file reads. Verify the published tree against the
reviewed local tree and remote tip. Do not repeatedly try a known unavailable
credential path, resend truncated content, or claim persistence before success.
Report a real publication block plainly. No chapter-text storage mode is active;
legacy file-backed tools/artifacts remain for history and compatibility checks.
