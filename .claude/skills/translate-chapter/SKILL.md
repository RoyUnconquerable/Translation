---
name: translate-chapter
description: The ONLY sanctioned way to do translation work in this project.
  Use for ANY request that touches translation - translate, draft, redraft,
  revise, review, finalize, polish, assemble, or segment a chapter; anything
  touching source/, work/, or output/; glossary or terminology work, adding
  or changing a term; rolling-summary or style questions. Trigger phrases
  include "translate", "draft", "revise", "finalize", "polish", "chapter",
  "glossary", "term". Ad hoc translation - translating in the main context
  without this workflow - is never acceptable in this project.
---

# translate-chapter: the conductor script

You are the conductor, not the translator. You run scripts, curate terms with
the user, spawn the drafter and reviewer subagents, loop on lint, and commit
at the three fixed points. Translation prose is produced by subagents only.

All commands run from the project root. `<chapter>` is the work-file basename:
`ch012` for `source/ch012.txt`. Scripts live at
`.claude/skills/translate-chapter/scripts/`.

## Stage order

### 1. Segment

    python3 .claude/skills/translate-chapter/scripts/segment.py source/<file> [--chapter <chapter>]

Sanity-check the printed stats; a web-novel chapter is usually 30-120 segments.

### 2. Term pass (the one interactive stage)

    python3 .claude/skills/translate-chapter/scripts/glossary.py candidates <chapter>

Etiquette:
- Curate the raw list yourself: drop grammar fragments and empty function
  words, keep real names, techniques, realms, artifacts, recurring set
  phrases - AND recurring ordinary vocabulary that could drift between fair
  alternatives (异常 anomaly/aberration, 气息 aura/breath). The glossary is
  the pipeline's memory, and it is not just for proper nouns.
- Candidates count cumulatively across all chapters and carry precedent
  lines showing how earlier chapters rendered the term. Consistency
  outranks novelty: where a precedent exists, propose the established
  rendering unless the user overrules it.
- Propose a rendering for each keeper, then present the batch to the user and
  WAIT for approval. The script proposes strings and counts; the model
  curates; the human approves.
- Batch ALL questions for the user here - term renderings, source
  ambiguities, style calls. The later stages run unattended.
- After changing an existing rendering with `--force`, run
  `lint.py --all`: it re-checks every earlier draft against the new rule
  and lists exactly which old segments now need repair.
- Record each approved term:

      python3 .claude/skills/translate-chapter/scripts/glossary.py add <source> <target> [--note "..."]

  Renderings in dispute get resolved here, in the glossary, never later in
  the text. Use `--force` only for a deliberate override, and re-check
  earlier chapters when you do.

### 3. Draft (subagent only)

Spawn the `chapter-drafter` agent in MODE A, telling it the chapter name.
Drafting never happens in the main context. Relay any glossary concerns from
its closing report to the user at the next natural pause.

### 4. Lint, and the failure loop

    python3 .claude/skills/translate-chapter/scripts/lint.py <chapter>

If there are failures: re-invoke `chapter-drafter` in MODE B with ONLY the
failing ids and their lint details (from `work/<chapter>.lint.json`), then
re-run lint. Repeat until zero failures. Warnings are for your judgment:
scan them, note real risks (a ratio outlier is how omissions and padding
show up), ignore the benign ones.

### 5. Commit point 1

    git add -A && git commit -m "draft: <chapter>"

### 6. Review (subagent only)

Spawn the `chapter-reviewer` agent with the chapter name. It writes
`work/<chapter>.issues.json`, then patches only the flagged segments in the
draft. The reviewer must always have the segments file available: it judges
the draft against the source, never on its own.

Re-run lint afterward. If a patch broke a check, run the stage-4 failure
loop again until clean.

### 7. Commit point 2

    git add -A && git commit -m "review: <chapter>"

The user's human review is now one command: `git diff` between the draft and
review commits shows exactly what the reviewer changed and nothing else.

### 8. Assemble

    python3 .claude/skills/translate-chapter/scripts/assemble.py <chapter>

It re-lints, refuses on failures, writes `output/<chapter>.en.txt`, and
appends the telemetry row.

### 9. Rolling summary

Append a short capsule for this chapter to `project/rolling-summary.md`
(newest chapter last) and trim the whole file to stay near 250 words.

### 10. Commit point 3

    git add -A && git commit -m "assemble: <chapter>"

Report the flag rate and any open glossary discussion items to the user.

## Telemetry rule

After assembling, check `work/telemetry.csv`. If flag_rate exceeded 0.40 for
THREE consecutive chapters, edit `.claude/agents/chapter-drafter.md` to
`model: sonnet` and tell the user: at that rate the review cascade is a
disguised rewrite, and the cheap draft is costing more than it saves.

## Hard rules

- Never finish with lint failures. The Stop gate enforces this; fix the
  draft instead of fighting the gate. `SKIP_LINT_GATE=1` exists only for the
  day the gate itself is wrong, and only with the user's consent.
- The reviewer always sees the source.
- Patch, don't rewrite. Repairs go through Mode B with specific ids; review
  edits touch only flagged segments.
- One rendering per term. Disputes are resolved in the glossary with the
  user, never by improvising in the text.
- Never hand-edit output/. It is assembled from work/ or it is wrong.
