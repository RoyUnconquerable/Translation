# Consolidation history

On 2026-09-03, the active per-chapter terminology, style, owner-edit,
continuity, and world-reference supplements were consolidated into canonical
files. Their detailed provenance remains available in Git at commit
`7e62dbac3238c790d3932b5a7baae992ac502499` and earlier history.

The deleted files must not be restored to the default authority load path.
When a historical wording question arises, search Git history for that exact
chapter and promote only the relevant decision into the proper canonical file.

The follow-up audit on the same date classified phrase memory as `fixed`,
`image`, or `sense` and removed local sentence templates, locked tense, generic
word choices, duplicates, and unsafe owner slips. It also replaced the blanket
owner-final rule with source-checked promotion, made the chat preparation and
final mechanical checks mandatory when available, and redirected active-looking
legacy instruction files to the canonical pipeline. Executable legacy Claude
skills, agents, and hooks were removed from the active branch because automatic
discovery could bypass those pointers; the archive branch and Git history retain
their exact former contents.

## 2026-09-13 translation instruction audit

Baseline: 046d621a3e66e474d7741affaff252b4e3adc426 on the canonical branch
`claude/translation-pipeline-build-3gdy6r`. The older reference-import branch
still held the Chapter 1250-era workflow; the state manifest on the current
branch identified the actual authority. This audit changed instructions and
one preparation defect, not chapter text, terminology or chapter progress.
This section records evidence and scope, not another execution checklist.

Evidence inspected: current entry points, workflow/specifications, style,
error register, terminology, relevant Chapter 1332-1334 decision records,
preparation/checker code, validation scripts and existing tests; plus the
owner-supplied September 11 edition of `01_EDITING_GUIDE.md`, sections 1-8.
The guide supplies editorial evidence, not a new translation authority. Its
Chapter 1335 examples were not independently checked against Chinese in this
instruction-only audit. No claim is made to have reviewed a later Word sweep
or recovered its complete issue list. Existing pending findings remain pending.

| Finding | Repair and scope |
|---|---|
| The sole workflow mentioned batching questions but omitted the explicit pre-draft term approval gate. | Restored one batch for every new/changed term. Established decisions are reused; ordinary diction is not a new term. |
| Preparation's unknown-term section finds bracketed candidates only. | State its limits and require inspection of unbracketed and single-use terms; the legacy frequency option cannot waive approval. |
| `prepare.py` counted standalone source separators as paragraphs, while `chat_check.py` excluded them. | Share content parsing and print source separator positions. The title remains index 1. A CLI regression covers a term after a separator and omission of the required separator. |
| The style rule asking for one main beat could conflict with source paragraph preservation. | Follow the source paragraph's actual movement, including linked beats; retain isolated reactions. |
| Mandatory transition variation could encourage needless synonym changes. | Choose connectors by the actual relation and repair demonstrated awkwardness or repetition. |
| The existing review included English categories but did not explicitly require reading transitions as connected prose. | Clarify that its full source-aligned pass also reads the scene critically for reference, flow, logic and revelation order. No second English reviewer or new rewrite stage. |
| Repairs were followed by mechanical checking without an explicit contextual verification step. | Read each changed paragraph and immediate neighbors, grouping overlaps; compare actual repairs with source and pre-patch text. Reopen only demonstrated regressions. |
| Ch.1334 records document a duplicate transition and truncated paragraph; the supplied guide also warns about an unfinished thought before an action. | Protect paragraph content, setup/payoff and unfinished speech; do not equate paragraph totals or a newer revision with completeness. |
| Reference facts could be applied outside their chapter, incarnation or viewpoint. | Require matching identity/history and revelation timing; absence and first attestation do not prove a contradiction. |
| Mixed thought/narration spans and experienced-time comparisons need local judgment. | Clarify span-level italics, meaningful tense and the observer to whom elapsed time belongs. Preserve existing direct/free-indirect distinctions. |
| The workflow said the bilingual review proves properties that neither review nor lint can guarantee. | Separate mechanical results, full review coverage, unresolved findings and actual delivery; state tool limits and warning adjudication. |
| Chat delivery could introduce unverified last-minute wording. | Deliver the checked target unchanged; verify any subsequent change before sending it. |
| Editing and legacy file-backed instructions could be mistaken for mandatory translation stages. | Align the project bootstrap and README. Feedback maintenance stays after delivery; English-only paragraph restructuring and Word tracking do not transfer to translation. |
| Owner revisions may improve prose while introducing accidental damage. | Apply explicit decisions exactly, identify repairs/conflicts visibly, and keep inferred intent, local wording and pending meaning changes separate from approved reusable rules. |

The existing single-draft path remains in place: verified/cached authorities,
term approval when needed, one source-grounded bilingual and English review,
targeted repairs with context checks, mechanical verification, exact chat
delivery, then authorized atomic maintenance. Existing glossary, phrase memory,
entity, world, continuity, decision and progress records remain unchanged.
Repeated style clauses were consolidated in place, preserving their distinct
requirements and examples. The style guide remains below its existing size
review target; no audit threshold or lint exception was relaxed.

Validation: 40 unit tests passed, including the new CLI regression. The
authority audit, both retained file-backed chapter lints and state validation
passed. Existing size/concision advisory warnings and 31 historical lint
warnings remain; they are not new failures or evidence of semantic perfection.
The three-to-five-minute chapter target is preserved, not newly benchmarked.
No instruction audit can establish zero future errors or prove a globally
optimal model workflow without observing future chapter runs.

## 2026-09-10 healthy-path repair, following Chapter 1329

Baseline: c981f829a7625adb3e76c0bc2c46ecfd739b4ec4. The current workflow and
QA/editing specifications supersede older operational scheduling decisions.
The earlier instructions and settings remain exactly recoverable at that commit.
This section records evidence, not a new translation checklist.

Verified findings:

- Execution is manual: one draft, two detector assignments, lead adjudication
  and mechanical checking. There is no automated retranslating/rewrite engine.
- Turn-entry publication instructions conflicted with delivery-first wording.
  Recent metadata-only commits and the visible session confirm maintenance
  work between chapter deliveries; each publication also required remote calls.
- The root README also recommended separate project chats, duplicating context
  handoffs not required by the actual script path. It now points to one workflow.
- Both detectors reviewed all paragraphs, with overlapping English/source
  scopes plus a lead review. During the Chapter1329 owner review, detectors
  proposed reverting accepted capitalization/color and the fixed survival
  phrase. These were rejected. More reviews were not automatically safer.
- Repeated combined reference reads in the visible session were truncated.
  From the pre1326 tip 27d0b6d to this baseline, the decision log grew from
  214 to 260 lines; the latest feedback added 33 rows, many local sentence
  choices. Style and error files remained near their hard byte limits.
- A legitimate new term made the 375-term audit cap fail. Long decision rows
  also failed, leading to extra consolidation and validation cycles. Size is
  useful review guidance but does not establish a correctness defect.
- prepare.py printed target names but omitted hard-term/entity usage notes;
  its number inventory missed three-chi measurements and three-seven odds.
- In this checkout, prepare/check each took about 0.1 seconds and the whole
  six-command baseline took about 0.8 seconds. Script computation was not a
  demonstrated multi-minute bottleneck. Config controls language and legacy
  lint/candidate settings, not model speed, agents, polling or network latency.
- Existing telemetry records flag counts for two old file-backed chapters,
  not user-message-to-delivery times. Artifact timestamps are mutable and
  exclude earlier work. They cannot prove the end-to-end delay or its cause.

Likely but unmeasured: accumulated context and repeated adjudication can
increase generation latency. No evidence isolates model/server slowdown or
supports a guaranteed three-to-five-minute total on every chapter.

Repair: one bounded bilingual detector covers fidelity and English together;
source and mechanical safeguards remain. Chapter delivery has no publication
prerequisite. Approved feedback is consolidated once into the existing
canonical files and one atomic commit. Local comparisons remain historical,
not new global rules. Reference reuse is invalidated only by actual changes
or lost context. No agent, dashboard, automated pipeline or validation layer
was added. Legacy prose artifacts and tooling remain preserved but are outside
the active chapter path, which forbids committing chapter text.

### Historical error register before consolidation

The following is preserved verbatim for exact historical/source examples.
It is not a second active rule set; consult the canonical glossary, style,
current errors and the specific dated decision first.

# Active error register

Recurring traps beyond the style guide, glossary, entities, and checks.
Remove entries made redundant by stronger canonical controls.

## Source and alignment

- Alignment, framing, and scene boundaries follow the style guide and checker;
  fluent English or matching paragraph totals do not establish fidelity.
- Owner expansions can restore purpose, position, timing, sequence, and
  gesture. Ch.1303 also exposed shared omissions of plural address, immediate
  onset, boundlessness, and causal cues, plus weakened injury severity. Track
  explicit, conveyed, and missing details rather than treating fluency as proof.
- Matching paragraph totals is necessary but insufficient. Check every source
  paragraph against its corresponding target, especially around revisions
  that split sentences, combine questions, or change thought mode. Preserve
  the final causal verdict inside a paragraph: Ch.1306's explanation of why
  They are Dao Lords is source content, not a disposable repeated conclusion.
- Preserve degree and the dimension being described: difficulty is not
  impossibility; certainty is not magnitude; deadly is not unmistakable.
  Ch.1306 loses further repair, weakens actual success to achieving something,
  and substitutes unharmed for fine despite existing injuries. Restore the
  source distinction before promoting the edit. Refusing to tolerate recovery
  is not impatience; an inevitable outcome is not merely almost certain.
  Limited does not by itself preserve insufficient. Ch.1304's far beyond reach
  overstates 难度太高; 100,000 li of lofty mountains is about 31,000 miles,
  not 100,000 miles.
- Keep `几乎` in a near-absolute statement: almost no hesitation is not no
  hesitation at all. Preserve `试图` and the action attempted; trying to
  intercept a moving realm does not establish a sealing technique or success.
  Do not add an intensity such as crushing when the source only states a
  sense of oppression. These Ch.1295 issues arose in the owner revision,
  not the delivered draft, and were repaired during consolidation.
- Keep a conditional comparison conditional instead of turning it into an
  accomplished result. Distinguish a newly developed weakness from an old
  weakness that can no longer be concealed. Preserve entry when inside/outside
  changes the available Daos: Ch.1306 means attacking into the new world, not
  merely attacking it. Retain escalation when introducing a worse contingency.
- Triggering or stirring existing imagery is not creating it. In Chapter
  1293, 触动 points toward an already existing mark; gave rise to changes the
  causal relationship and must not become a reusable rendering.

## Identity and terminology

- A dated attachment is supporting evidence, not permission to reverse a later
  canonical owner ruling. `道音` remains `Dao resonance`, reaffirmed in Chapter
  1290; the older attachment's `Dao voice` is superseded.
- Resolve grammar before promoting an ordinary adjective into a cultivation
  term. The Chapter 1290 exception `步法玄妙` is `subtle footwork`; it does not
  remove capitalization from actual Mysteries elsewhere.
- Resolve the real referent before capitalizing pronouns. The Sword Sovereign
  is She/Her. Divine addressees also take You/Your, and groups of Dao Lords
  take Us/They/Them as applicable. A Dao's radiance instead takes its or their.
  The named Dao Variables takes singular agreement despite its spelling.
  The Ancestral Dragon is He/His/Him as the Dao Lord, but a detached guided
  consciousness may be it/its where continuity explicitly says so.
- Knowing a method in the sense of understanding or using it must not become
  merely knowing about its existence. Preserve the competence implied by
  懂得 when the scene depends on the character employing the technique.
- Check word boundaries in verb-plus-title constructions: 成道主 means become
  a Dao Lord, not the separate achievement 成道, prove the Dao. The glossary
  excludes this compound while retaining independent occurrences of 成道.
- Keep `Sword Edge Metal` unhyphenated, `两仪生灭玄光` as `Yin-Yang Creation
  and Destruction Profound Light`, and `光铸的双手` as `hands forged from light`.
- Resolve `现世` grammatically before enforcing terminology. As a noun it is
  `the mortal world`; as a verb, including `再度现世`, it means to manifest or
  appear.
- Count individual `箓文` as `seal-script characters`, not `seal scripts`,
  which incorrectly treats each glyph as an entire writing system.
- `天下` normally needs the established plural cosmological form, `under the
  heavens` or `beneath the heavens`, not bare `under heaven`.

## Prose regression traps

- Preserve concrete posture, timing, reasoning, reading, and minor problems
  even in unchanged prose (Ch.1309). Ch.1318 almost felt weakens actually felt;
  conception is not gestation, and the first Transcendence is an event, not a
  person. Do not move an expression into a voice or expand disbelief into never.
  A balance formed by a causal process need not be between two quantities.

- Default to modern direct English. Do not use archaic sentence inversions,
  ceremonial filler, or compressed bookish narration unless the Chinese is
  genuinely classical or ritualized.
- Preserve Chinese imagery selectively. A live image should survive; a dormant
  lexicalized idiom should not be forced into awkward literal English.
- Ch.1295's spent crossbow bolt was a delivered-draft over-literalism. Use
  spent force for that figurative dismissal; retaining the separate snake and
  brick/jade images does not justify literalizing every idiom nearby.
- Do not turn local owner synonyms into templates. Keep source relationships:
  overlap is not fusion; a domain is not the surrounding void.
- Do not overuse transition openers, intensifiers, `suddenly`, `simply`, or
  `couldn't help but`.
- Use natural contractions unless emphasis, contrast, formality, or clarity
  requires expansion; never use forms ending in 'd. Check this manually,
  rather than relying on the mechanical checker.
- A glossary PASS cannot certify prose. Repair complete clauses, articles,
  collocations and dialogue lists. Owner slips such as few talent, an Treading,
  or a missing conjunction before slammed are not preferences. Check merged
  reaction/punch-line paragraphs too. Conditional rapid repair remains an
  exception to ordinary repair, not a contradiction.
- Ch.1308's grade list is unresolved: 四等 may be a count or a fourth-class
  label. Neither the draft's four-grade reading nor the owner's six-item
  sequence has a verified mapping. Do not canonize either as a full ladder.
- Check what a possessive modifies: His teacher's ruler invents an owner when
  the source identifies His disciplinary implement. Separate a being's
  attainment from the action of using that being as material; compressed
  infinitives can attach to the wrong verb even when the meaning is recoverable.
- Link related premises and consequences within a source paragraph when this
  improves flow. Keep the necessary condition explicit: Only when the two
  were united could life arise is justified emphasis, not decorative inversion.
  Paragraph alignment remains unchanged.
- Preserve exact approved declarations and **【...】** formatting; the old
  blanket bracket-removal/punctuation rules conflicted with this requirement.
  Scene-break validation must compare reviewed positions, not merely check
  that any separators already present are well formed.
- Distinguish direct thought from free indirect narration before applying
  italics. Italics do not assign tense. Immediate mental speech normally uses
  present tense; memories and anterior events use past or perfect forms, plans
  use future forms, and hypotheticals use conditional forms.
- Do not backshift a current italicized judgment merely because the surrounding
  narration is past tense. Do not italicize a viewpoint-colored rhetorical
  paragraph when it remains free indirect narration.
- Preserve a live idiom or allusion, but keep ordinary surrounding syntax
  modern. Recheck the allusion's actual subject and wording before accepting a
  familiar-sounding English line.
- Preserve humor and profanity at source strength, then stop. Do not explain
  the joke or add another flourish. Contempt does not necessarily mean spoken
  cursing; use natural two-faced or double-dealing for treachery rather than
  the calque double-faced. Keep a live rat image when the source supplies it.
- Do not make a death-and-survival idiom imply literal rebirth or a metaphorical
  decisive act imply a particular weapon. Check what the image actually does
  in the scene before accepting either literal or naturalized wording.
- Attribute review findings accurately: distinguish errors in the delivered
  draft from changes introduced by a later revision. A previous reviewer PASS
  does not override a subsequently demonstrated source or prose error.

## Pending rejected draft: Chapter 1271

- Never reuse its rejected first draft or treat the later chat redraft as
  approved. For Chapter 1271 work, retrieve the complete source, pronoun,
  paragraph, and allusion checks in continuity-archive.md under this heading.

## Repository process

- Source seen, draft delivered, correction recorded and final approval differ.
  Later progress never establishes approval.
- Owner edits are source-checked before classification and promotion. Owner
  intent and approved terms are authoritative, but typos, grammar slips,
  mistranslated allusions, and source changes are not promoted as precedent.
  Local wording and mechanical fixes remain local.
- Validation must be read-only unless a write flag is explicit.
- Do not claim GitHub was updated until the commit is present on the remote.
- The canonical GitHub branch named in state, not conversation memory, is the
  persistent cross-session guide.
