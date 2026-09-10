# Translation project entry point

`chatgpt/` is the only active pipeline. Legacy Claude files are read-only.

Read `chatgpt/chapters/state.json`, then follow the single execution policy in
`chatgpt/instructions/workflow.md`. The state manifest is a lookup map, not an
instruction to read every authority on every turn. Reuse unchanged references;
retrieve relevant history across all chapters, not only the recent window.

The exact Chinese governs content. Verified owner decisions govern editorial
choices; the canonical GitHub branch named in state is the durable authority,
above conversation memory. The workflow defines review and feedback handling.

Deliver complete chapters in chat before maintenance. Never commit chapter
text or provisional handoffs. Preserve unrelated changes and every valid
historical ruling. Claim persistence only after the atomic update is pushed.
