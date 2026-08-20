# Editing and owner-revision specification

## Minimal, traceable edits

Every non-mechanical edit starts with a recorded issue tied to a segment ID.
Repair only the named segment and preserve as much correct wording as the fix
allows. Do not restyle unrelated sentences while reviewing.

Mechanical edits whose exact final text is already known may use `patch.py`.
Translation judgment still requires direct comparison with the source and a
recorded reason.

## Owner edits

The owner's supplied final wording outranks model preference. When owner prose
arrives:

1. align each change to its segment ID;
2. apply the exact wording to the draft, not only the assembled final;
3. re-run lint and assembly;
4. diff owner text against the prior reviewed draft;
5. extract reusable rulings into the glossary, style guide, continuity, or
   known-errors file;
6. run all-chapter lint after a changed term ruling.

Do not generalize a one-off phrasing unless the edit establishes a repeatable
rule. Record uncertain scope explicitly and ask the owner rather than silently
turning a local choice into global policy.

## Issue record

`<chapter>.issues.json` is a JSON array. Each object has:

```json
{
  "id": "ch1211-0001",
  "type": "mistranslation",
  "severity": "major",
  "note": "One source-grounded sentence explaining the defect.",
  "patched": false
}
```

Allowed types are `mistranslation`, `omission`, `addition`, `terminology`,
`tone`, and `awkward`. Major means meaning is wrong, missing, or invented;
minor means style or flow. Mark `patched` true only after the replacement has
been checked against both source and terminology.
