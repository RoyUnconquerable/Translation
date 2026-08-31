# Chapter workflow

All commands run from the repository root. Use `python` below; `python3` is an
equivalent choice where that is the installed command.

## 0. Resume from durable state

Read, in order:

1. `chatgpt/chapters/state.json`;
2. `chatgpt/config.json`;
3. `chatgpt/glossary/terminology.tsv`;
4. `chatgpt/reference/style-guide.md`;
5. `chatgpt/reference/continuity.md`;
6. `chatgpt/reference/known-errors.md`;
7. every terminology, owner-style, world-reference, and continuity supplement
   named in the state handoff;
8. the immediately preceding chapter's source, work files, and final output.

Repository files outrank chat memory. The latest owner ruling wins. Run:

```text
python chatgpt/scripts/state.py
```

Fix repository-state errors before creating a new draft.

Conversation summaries and prior model drafts do not satisfy the source-read
requirement. Under the chat-only fast path, when the Chinese source exists only
in the owner's current message, treat that exact pasted text as the source and
audit it directly paragraph by paragraph.

## 1. Ingest and segment

Save the untouched source as `chatgpt/chapters/source/<chapter>.txt`, then run:

```text
python chatgpt/scripts/segment.py chatgpt/chapters/source/<chapter>.txt
```

Inspect the printed count and token estimate. The produced JSONL is the stable
alignment contract for every later stage. One source paragraph must remain one
target paragraph.

## 2. Terminology and questions

Run:

```text
python chatgpt/scripts/glossary.py candidates <chapter>
```

Curate real names, titles, places, techniques, realms, artifacts, cosmology,
idiom or allusion renderings liable to drift, and ordinary vocabulary liable to
drift. Reuse precedent unless the owner overrules it. Batch every term proposal,
ambiguity, and necessary style choice into one request and wait for approval.

Record approved terms only:

```text
python chatgpt/scripts/glossary.py add <source> <target> --note <reason>
```

Use `--force` only for an explicit change to an existing ruling, then run lint
over all chapters and repair every historical conflict.

## 3. Draft

Write `chatgpt/chapters/work/<chapter>.draft.jsonl` under
`translation-spec.md`. Drafting may happen in a focused ChatGPT Project chat or
a Codex task, but it must use repository sources rather than remembered text.

The draft must preserve source paragraph structure, italicize explicit and
unmistakable implicit internal thought, retain all source meaning and numbers,
and preserve Chinese idioms and classical allusions with their defining imagery
inside natural English. The target prose follows the professional xianxia house
style defined in `reference/style-guide.md`.

Commit point: `draft: <chapter>`.

## 4. Deterministic QA

Run:

```text
python chatgpt/scripts/lint.py <chapter>
```

Repair failures by exact segment ID, then re-run lint until there are none. Use
`patch.py` only when the final replacement text is already decided:

```text
python chatgpt/scripts/patch.py <chapter> --set <segment-id> <exact-target>
```

Warnings require judgment. Ratio and number warnings often expose omissions;
punctuation warnings are mechanical but still must be resolved before final
delivery when the style guide bans the glyph.

## 5. Independent source-grounded review

Review every source segment against its target under `qa-rules.md`. Record all
findings in `chatgpt/chapters/work/<chapter>.issues.json` before patching. The
review must separately check meaning, terminology, paragraph integrity, thought
formatting, Chinese idioms and allusions, combat causality, and professional
xianxia prose quality. Patch only flagged IDs and mark each issue `patched: true`
after verification.

Re-run lint. Commit point: `review: <chapter>`.

## 6. Assemble and update memory

Run:

```text
python chatgpt/scripts/assemble.py <chapter>
```

The command refuses to assemble lint failures, missing review evidence, unknown
issue IDs, or unpatched issues. It writes the final text and upserts telemetry.

Append a short continuity capsule to `chatgpt/reference/continuity.md`, keeping
the file compact. Update `chatgpt/chapters/state.json` with counts, status, and
the next expected chapter. Add durable owner corrections to the canonical
terminology TSV, style guide, world-reference supplement, continuity, or known
errors as appropriate. Do not leave a final owner ruling only in chat memory.

Run the two final gates:

```text
python chatgpt/scripts/lint.py --all
python chatgpt/scripts/state.py
```

Commit point: `assemble: <chapter>`.

## 7. Owner revision

When the owner supplies edited final prose, adopt it exactly in the aligned
draft with `patch.py` where possible, reassemble, and record every reusable
terminology, style, cultural, continuity, or known-error ruling. Never patch only
the final file. Commit as `revise: <chapter> owner final`.

## 8. Commit batching and CI hygiene

Treat the glossary, style, continuity, world-reference, known-error, and state
changes produced by one chapter as one coherent repository update. Publish them
in a single commit or tree update rather than one commit per file. Run the final
lint and state gates before moving the branch. Do not knowingly leave a failed
workflow run unresolved. The GitHub Actions workflow cancels superseded runs on
the same branch, but batching remains the primary safeguard against repeated
notifications.
