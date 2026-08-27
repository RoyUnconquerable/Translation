# Chat-Only Translation Fast Path

This supplement applies when the owner asks for chapter prose directly in chat and does not want chapter files committed. It changes scheduling and repository I/O only. It does not relax accuracy, terminology, paragraph alignment, thought formatting, idiom handling, or source-grounded review.

## Goal

Deliver the translated chapter promptly, with the owner's target of roughly three minutes where chapter length and terminology permit, while retaining the same quality standard.

## 1. Cache stable repository authorities within one project chat

At the start of a translation session, read the canonical state, config, terminology, style, continuity, and every supplement named by state. Record the branch head and the relevant file SHAs.

For later chapters in the same uninterrupted project chat:

- fetch `state.json` first;
- if the branch head and authority paths are unchanged, reuse the already-read canonical files rather than downloading the same large references again;
- fetch only newly named supplements, changed files, and the immediately relevant chapter material;
- repository files still outrank chat memory, and any changed SHA requires a fresh read.

This is a cache, not permission to rely on stale memory.

## 2. Use targeted terminology review

Search the glossary for terms actually appearing in the new source. Reuse locked terms without reopening them. Present one terminology batch only for genuinely new, changed, or materially ambiguous renderings.

Do not perform broad repository searches for ordinary words already governed by the style guide.

## 3. Deliver prose before repository maintenance

For a new chat-only chapter:

1. perform the terminology check;
2. translate and source-check the chapter;
3. show the complete chapter in chat as soon as the prose is ready;
4. do not create a provisional continuity or state commit before the owner reviews it.

The owner must not wait through GitHub metadata writes or CI before seeing the chapter.

## 4. Treat owner approval or edited prose as the stabilization point

After the owner approves the chapter or supplies edited prose:

- compare the owner version against the draft once;
- extract reusable terminology, style, cultural, continuity, and known-error rulings;
- update the glossary, style supplement, continuity, world reference, and state in one atomic tree commit;
- keep chapter prose out of GitHub unless the owner explicitly requests otherwise;
- trigger CI only once for that stabilized repository update.

Do not commit a provisional handoff and then repeat the same work after the owner edit.

## 5. Keep QA focused but complete

The chat-only draft still receives a separate source-grounded pass checking:

- omitted or added meaning;
- numbers and logical relations;
- established terms and pronouns;
- paragraph structure;
- direct and implicit internal thought;
- idioms, allusions, jokes, and metaphor chains;
- combat causality and natural published English.

Run this review once after the complete draft rather than repeatedly rewriting the chapter in successive stylistic passes. Patch only identified problems.

## 6. Batch tools and verification

- Group independent repository reads into one batch where possible.
- Use one Git tree commit for all files produced by an owner-finalized chapter.
- Poll the resulting workflow run once after its jobs have had time to complete rather than issuing many rapid status requests.
- Never leave an actual failed run unresolved, but do not delay presentation of chapter prose while a documentation-only handoff commit is validating.

## 7. Response order

For new chapters, the visible order is:

1. complete translated chapter;
2. a brief repository status note only after the owner-finalized update exists.

Avoid long process commentary, repeated citations to the same files, and descriptions of every low-level repository operation.
