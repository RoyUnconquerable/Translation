# Chapter workflow

All commands run from the repository root. Use `python` below; `python3` is an
equivalent choice where that is the installed command.

## 0. Resume from durable state

Read, in order:

1. `chatgpt/chapters/state.json`
2. `chatgpt/config.json`
3. `chatgpt/glossary/terminology.tsv`
4. `chatgpt/reference/style-guide.md`
5. `chatgpt/reference/continuity.md`
6. the immediately preceding chapter's source, work files, and final output

Run `python chatgpt/scripts/state.py` before beginning. Fix repository-state
errors before creating a new draft.

## 1. Ingest and segment

Save the untouched source as `chatgpt/chapters/source/<chapter>.txt`, then run:

```text
python chatgpt/scripts/segment.py chatgpt/chapters/source/<chapter>.txt
```

Inspect the printed count and token estimate. The produced JSONL is the stable
alignment contract for every later stage.

## 2. Terminology and questions

Run:

```text
python chatgpt/scripts/glossary.py candidates <chapter>
```

Curate real names, titles, places, techniques, realms, artifacts, cosmology,
and ordinary vocabulary liable to drift. Reuse precedent unless the owner
overrules it. Batch every term proposal, ambiguity, and necessary style choice
into one request and wait for approval.

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

Commit point: `draft: <chapter>`.

## 4. Deterministic QA

Run:

```text
python chatgpt/scripts/lint.py <chapter>
```

Repair failures by exact segment ID, then re-run lint until there are none.
Use `patch.py` only when the final replacement text is already decided:

```text
python chatgpt/scripts/patch.py <chapter> --set <segment-id> <exact-target>
```

Warnings require judgment. Ratio and number warnings often expose omissions;
punctuation warnings are mechanical but still must be resolved before final
delivery when the style guide bans the glyph.

## 5. Independent source-grounded review

Review every source segment against its target under `qa-rules.md`. Record all
findings in `chatgpt/chapters/work/<chapter>.issues.json` before patching. Patch
only flagged IDs and mark each issue `patched: true` after verification.

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
the next expected chapter. Add durable owner corrections to terminology, style,
or known errors.

Run the two final gates:

```text
python chatgpt/scripts/lint.py --all
python chatgpt/scripts/state.py
```

Commit point: `assemble: <chapter>`.

## 7. Owner revision

When the owner supplies edited final prose, adopt it exactly in the aligned
draft with `patch.py` where possible, reassemble, and record reusable rulings.
Never patch only the final file. Commit as `revise: <chapter> owner final`.
