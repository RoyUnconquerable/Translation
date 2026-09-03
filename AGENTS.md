# Translation project bootstrap

`chatgpt/` is the only active translation pipeline. Legacy Claude paths are
read-only migration evidence unless the owner explicitly requests otherwise.

For every translation or owner-revision task:

1. Read `chatgpt/chapters/state.json`.
2. Follow `chatgpt/instructions/workflow.md`.
3. Load only the canonical authorities named by state.
4. Use the exact Chinese source, preserve one target paragraph per source
   paragraph in the same order, and verify every recurring referent.
5. Treat the source as the authority for chapter content. The owner's
   editorial intent and explicit terminology decisions are authoritative, but
   supplied English still receives source, grammar, continuity, terminology,
   tense, and allusion checks.
6. Repair clear mechanical errors. If wording materially changes the source or
   conflicts with established authority, present the issue and a
   source-grounded alternative before promoting it.
7. Promote only verified, durable lessons to the appropriate canonical file.

The latest pushed tip of the GitHub canonical branch named in
`chatgpt/chapters/state.json` is the persistent authority across sessions and
context compactions. A new instruction in the live conversation applies to the
current task, but becomes durable only after it is verified, classified,
committed, and pushed. Repository authority outranks conversation memory,
summaries, rejected drafts, and model preference. The canonical glossary is the
only hard terminology source. Historical per-chapter supplements were removed
from the active tree because they created contradictory precedence; their
evidence remains recoverable in Git history.

Validation is read-only by default:

```text
python chatgpt/scripts/audit.py
python chatgpt/scripts/lint.py --all
python chatgpt/scripts/state.py
```

Do not stage or overwrite unrelated user changes. Never claim a repository
update exists until it has been committed and pushed.
