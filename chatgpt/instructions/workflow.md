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
Read config, the canonical terminology table, the style guide, continuity
summary and current error guidance in that order when they are not already
available at the verified version. Use state to locate relevant chapter records.
Do not use chat memory or a summary as a substitute for their contents.

During that session, reuse the verified tip and unchanged reference content.
Before each chapter, consult the cached state first and check local status/diff
once for changed authorities. Do not fetch, reread the dispatcher, dump the full
manifest, or run repository-wide gates every chapter. Refresh the remote at a new session,
checkout uncertainty, an indicated external change, or before publishing.
After a local update, reload only affected authority entries. After compaction,
reload only the instructions and relevant source records no longer available.

Use the exact supplied Chinese, saved outside Git. Run once:

```text
python chatgpt/scripts/prepare.py <source-file>
```

Keep the source file intact. Both preparation and checking use blank-line
paragraphs, with the title as paragraph 1 and standalone `---` excluded from
content numbering. Soft line wraps stay inside their paragraph. If the paste
lost its boundaries, recover them from the supplied source before proceeding;
do not guess a new paragraph layout. No JSONL production stage is needed.

The inventory supplies matching terms, usage notes, entities, phrases, numbers
and potential scene changes. Reuse that output for drafting and review; do not
reproduce it in another full authority sheet. Add only relevant historical
facts, reviewed scene positions, thought speakers/time references and material
ambiguities. Search the glossary, phrase memory, decisions, world reference
and continuity archive across their full history by the current referents.
Read matching passages and enough context to resolve them, never whole archives.
The four owner reference files in state are targeted lookups for formatting,
idioms, titles and recurring system text. Use matching entries in the same draft
and review; they add no extra stage or mandatory full-file reload. Exact owner
decisions outrank inventory inference; local exceptions remain local.
Do not refetch an unchanged historical entry already in active context.
Match identity, incarnation, True/False History, viewpoint and chapter timeline
before applying a reference fact. First attestation is not a first life or the
date every fact became known; an absent entry is not a contradiction. Do not
import later revelations or revive superseded terminology from older evidence.

New owner corrections in the live turn must be included in the same compact
review input, clearly distinguished from draft wording and proposed alternatives.
A draft choice is not canon. Keep prerequisites, limits, identities, attribution
and earlier versus later revelations intact. A missing older attachment is not
evidence that it was checked. Search externally only for a material question
unresolved by the canonical records; batch necessary terminology questions.

### Terminology approval before drafting

Inspect the entire source for new names, titles, techniques, artifacts, realms
and changed senses or renderings, including unbracketed and single-use terms.
The inventory finds known matches and bracketed candidates; it is not a complete
new-term detector. `term_min_count` is a legacy candidate option, not an approval
threshold. Ordinary contextual diction does not create a new term ruling.

For every genuinely new or changed term, give one batch with source expression,
paragraph, proposed rendering and the material ambiguity or conflict. Wait for
owner approval before drafting. Reuse approved choices without asking again;
when there are no new decisions, proceed directly. An unresolved material
source ambiguity belongs in the same batch. Preserve intentional ambiguity.
If a new blocker is discovered later, finish independent checks and ask only
that question; never invent a ruling to keep the schedule. Apply live approvals
immediately and persist them with the next approved atomic update.

### Progress between approved updates

Do not publish metadata just to start the next chapter. `prepare.py` already
checks the source frontier; do not also run `state.py --incoming-chapter`.
If approved-update state trails the visible conversation, verify the actual
intervening sources and deliveries, keeping source seen, delivered and approved
separate. Pass `--observed-through N` only for that verified in-session source
frontier. This read-only input does not mutate state, prove delivery or grant
approval. It cannot fill an unknown gap; retrieve specific missing evidence or
report the uncertainty. An explicitly approved English manuscript can advance
the next-translation frontier while Chinese-source and chat-delivery evidence
stay separate. Its approval record does not prove a bilingual audit. Reconcile verified progress in the next approved atomic
update, without provisional files, handoff commits or guessed approvals.

## 2. Draft once

Translate directly from the exact source. Preserve every source paragraph,
including title, isolated reaction and ending, in order. For genuine display
lines/menu items only, separate panels and adjoining narration into paragraphs
without changing their content/order. Record each source index and resulting
target paragraph count for review and --display-splits; no prose splits or merges.
Sentence structure may change inside ordinary paragraphs. Apply the style guide:
resolve actors and ownership, use natural articles and collocations, connect
source-supported reasoning, and preserve deliberate beats and revelation order.
Construct natural English actions and claims during drafting, then retain their
source means, degree, choice and timing. Do not settle for individually correct
words in an awkward phrase or defer sentence construction to later editing.
Do not generate competing drafts or start a new translation from an owner edit.

## 3. One bounded bilingual review and targeted repair

Perform one source-aligned review covering fidelity and English under
`qa-rules.md`. Read every paragraph as part of the scene, including transitions
and connected reasoning; a term scan or a review of selected candidates is not
full coverage. There is no separate English detector, fresh rewrite, or duplicate
whole-chapter lead review. The lead owns drafting, adjudication and repair checks.

When delegation is available and permitted, use one reviewer with no inherited
conversation history. Supply the exact source, the one draft, its inventory plus relevant
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
term reversions. Record each finding's disposition: applied, rejected with a
reason, or unresolved. After applying repairs, read each changed paragraph with
its immediate neighbors, grouping overlapping spans. Compare changed content
with the source and pre-patch draft for omissions, additions, repeated transitions,
broken reference and lost setup/payoff. Verify the actual saved result. Reopen
only a demonstrated regression or its affected dependency, not the entire chapter.
Then run the existing mechanical check once:

```text
python chatgpt/scripts/chat_check.py <source-file> <target-file> --scene-break-before <indices>
```

Pass no indices after the flag if no additional breaks are required; explicit
source separators remain mandatory. Indices use the content numbering above.
For authorized display splits, append --display-splits SOURCE:COUNT entries
(for example 8:3). SOURCE is the original paragraph index; COUNT is its total
target paragraphs, including adjoining narration. Omit this option otherwise.
The checker accounts for the mapping, rejects undeclared/prose-only splits and
scene breaks inside a split, and checks framing, terminology, panel formatting,
fixed displays, typography, source residue and digits. Check panel classification,
title italics, pronoun referents and exact system-template values in the same review. It does not prove semantic completeness,
Chinese-number conversion or good English. Those require judgment in the
bilingual review; neither review nor lint guarantees that no error remains.
For real failures, fix only the affected spans and rerun the check. A lexical
false positive gets a source-grounded adjudication, not invented wording or a
new exemption that hides real matches. Record it for the next feedback repair;
do not describe an unresolved exception as an unqualified PASS.
Resolve digit warnings against source quantities and conversions. A checker
PASS is mechanical status only. If a tool cannot run, perform its checks locally
where feasible and disclose the unrun gate; never claim a successful tool run.

## 4. Deliver immediately

Return the complete reviewed chapter in chat as soon as required defects are
resolved and full review coverage is accounted for. Deliver the exact checked
target, retaining its title, paragraph boundaries, thought spans and separators;
do not regenerate or silently polish it while sending. If it changes, check the
affected content and rerun the mechanical check on that version. Do not begin
repository maintenance, another polish pass, further reference searching or
CI waiting first. A saved draft is not delivery. If
interrupted, resume from the checked draft; if output was missing, resend it
in full before troubleshooting. Do not infer delivery from timestamps.

Ordinary chapters require preparation, one draft, one bilingual review, targeted
repair with neighboring-context verification and the final mechanical check only.
A reasonable allocation is about 30 seconds for preparation, two to three
minutes for drafting, 60-90 seconds
for review/repair and under 30 seconds for the final check and delivery. The
three-to-five-minute goal depends on chapter complexity and service latency.
Never omit content to meet it; explain a concrete blocker instead.

## 5. Feedback after approval

Use `editing-spec.md` only on an approval, correction or maintenance turn. It
handles feedback and durable learning, not an obligatory prose-editing stage.
The separate English-only upload guide is evidence for relevant editorial
lessons, not an execution authority for translation: its general paragraph
restructuring, Word tracking and absence-of-raws policy do not transfer to this
path. The explicit display-only split ruling above does apply. Do not
import new formatting conventions or terms without a matching owner ruling.
Explicit owner corrections already authorize their verified update; do not
ask again for whole-chapter approval. Supplied edits receive one indexed
comparison and the same bounded bilingual check, not two additional reviews.
If feedback and a new chapter arrive together, apply the live correction to
that chapter and deliver it first. Publish the approved consolidated update
after delivery at the first available maintenance opportunity, subject to
the ten-chapter publication cadence below. Prepare verified local updates
without waiting for the push boundary. If final chat delivery ends the turn,
resume the authorized update on the next available turn; no feedback-only
prompt or renewed approval is required. A waiting chapter still comes first. Do not claim
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

The owner requested pushes every ten chapters starting with the Ch.1340
request. Apply feedback immediately and prepare coherent local commits on
maintenance turns; push the accumulated reviewed updates after each ten new
chapter deliveries (first batch Ch.1340-1349), or on an explicit earlier push
request. Editing feedback does not count as another delivered chapter. A
local commit is queued work, not published persistence.

At the batch boundary, publish the reviewed commits to the canonical branch
and, when different, the working branch without force-pushing. Fetch/check the
current remote before publication; if it moved, reconcile without overwriting external work. Use the
normal authenticated Git path when available; otherwise use the existing GitHub
connector once with bounded file reads. Verify the published tree against the
reviewed local tree and remote tip. Do not repeatedly try a known unavailable
credential path, resend truncated content, or claim persistence before success.
Report a real publication block plainly. No chapter-text storage mode is active;
legacy file-backed tools/artifacts remain for history and compatibility checks.
