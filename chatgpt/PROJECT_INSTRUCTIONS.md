# Project instructions

Continue the Chinese-to-English xianxia translation in
`RoyUnconquerable/Translation`. The active pipeline is `chatgpt/`; legacy
Claude paths are read-only.

Start with `chapters/state.json`, then follow `instructions/workflow.md`. Load
only the canonical files named by state. The latest pushed tip of the GitHub
canonical branch recorded there is the persistent project authority across
sessions and context compactions. A new live instruction applies provisionally
to the current task and becomes durable only after verification, classification,
commit, and push. Repository authorities outrank chat memory, summaries,
rejected drafts, and model preference.

The target is accurate, natural, published-quality modern English that retains
the Chinese cultivation setting, rhetoric, hierarchy, imagery, humor, and
philosophy. Preserve every source paragraph in the same order. Do not omit,
invent, summarize, Westernize, or explain material inside the translation.
Use the glossary exactly, resolve identities before assigning pronouns, and
keep divine capitalization tied to the real referent.

The exact Chinese source governs chapter content. Owner intent, explicit
terminology choices, and approved editorial decisions are authoritative, but
owner-supplied English still receives source, grammar, continuity, terminology,
tense, and allusion checks. Repair clear mechanical errors. If wording changes
the source meaning or conflicts with established authority, flag it and present
a source-grounded alternative before canonizing it. Classify each verified
change as macro style, terminology, phrase or allusion, world fact, continuity,
local preference, or mechanical repair. Promote only reusable decisions. Do
not create a new per-chapter rule file.

For chat-first work, deliver the chapter after one complete draft and two
focused source-grounded checks. Repository maintenance follows owner approval.
Chapter prose stays out of Git unless the owner explicitly requests durable
storage.
