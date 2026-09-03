# Optional file-backed chapter workflow

Use this path only when the owner requests durable chapter prose or explicitly
chooses the repository artifact workflow.

1. Save the untouched source to `chapters/source/<chapter>.txt`.
2. Run `python chatgpt/scripts/segment.py <source-path>` and verify the segment
   count against the source paragraphs.
3. Run `python chatgpt/scripts/glossary.py candidates <chapter>`, curate only
   meaningful unknown terms, and obtain owner approval where required.
4. Draft one JSONL target row per source row under `translation-spec.md`.
5. Run `python chatgpt/scripts/lint.py <chapter>`.
6. Perform the two reviews in `qa-rules.md`, record findings in the issues
   file, and patch only cited segment IDs.
7. Re-run lint and run `python chatgpt/scripts/assemble.py <chapter>`.
8. Update the ledger, continuity, state, and any genuinely reusable authority.
9. Run all repository gates in `workflow.md` before committing.

`lint.py` is read-only unless `--write-report` is supplied. Final output must be
assembled from the reviewed draft, never hand-edited.
