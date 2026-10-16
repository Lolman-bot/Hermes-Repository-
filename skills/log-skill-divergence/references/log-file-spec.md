# The log file spec

This is a contract with a reader you will never meet: an agent or a person, months from now, holding
this file and nothing else. It cannot ask what you meant, cannot see the chat, and cannot re-run the
tool call. Everything it needs is in the file or it is lost.

## Redaction: apply before writing anything

The shared log lives in a Team-wide SharePoint library. **Everyone at Bitpool can read it, and it is
the only copy.** Treat a local-fallback log the same way; it is meant to be moved there later.

- No credentials, tokens, keys, or connection strings, not even expired ones.
- No customer or personnel names, email addresses, or account identifiers. Say "a customer record"
  or "a person's record", never which one.
- No raw tool payloads. Describe the shape of the result ("returned 24 records"), not the records.
- No file paths containing anyone's data, and no absolute paths from another machine.
- Nothing from `$HERMES_HOME/.env`, `auth.json` or credential files, ever.

If the divergence cannot be described without one of these, **do not write the log**. Say what you
found in the conversation, explain why it can't be written down as-is, and offer a redacted version.

## Filename

```
YYYY-MM-DD_HHmm_<session-title-slug>.md
```

Slug = session title lowercased, non-alphanumerics collapsed to single hyphens, trimmed to 60
characters at a word boundary (`divergence_log.py slug` / `free-name` do this). If the session has
no title yet, slug the divergence itself and note it in `Confidence and caveats`. On a clash,
`-2`, `-3`, ...; never overwrite.

## Frontmatter

Every field, every time. An honest `unknown` beats an absent field, because the reader cannot tell
absence from oversight. Start from `assets/divergence-log.md.template`.

```yaml
---
type: skill-divergence
agent: hermes
logged: 2026-10-16T10:51+10:00
logged_by: Eric Sharp
session_id: 20261016_105102_a1b2c3
session_title: unknown
surface: cli
hermes_version: Hermes Agent v0.x.y
hermes_profile: default
cwd: C:\Users\<user>\Projects
skill: create-new-skill
skill_version: 1.0.0
skill_source: Lolman-bot/Hermes-Repository-
skill_path: skills/create-new-skill/references/publishing.md:42
divergence_type: workflow-gap
severity: medium
status: unresolved
resolved_at:
resolved_by:
resolution:
resolution_pr:
duplicate_of:
archived_at:
---
```

| Field | Notes |
|---|---|
| `agent` | Always `hermes`. Tells a reader this isn't a Claude-era log. |
| `logged` | ISO 8601 with the local offset. Absolute, never relative. |
| `logged_by` | Display name from `user-config-store` (`display_name`). **Required**; never blank or `unknown`. |
| `session_id` | Lets the reader pull the full transcript (`hermes sessions export`) if the excerpt is not enough. |
| `skill`, `skill_version` | Frontmatter `name` and `version` of the skill as loaded, so the reader knows which version was wrong. |
| `skill_source` | Where the installed copy came from. Only `Lolman-bot/Hermes-Repository-` skills get fixed in that repo. |
| `skill_path` | **Repo-relative**, most specific file: the reference file, not `SKILL.md`, when the wrong line is in a reference. Add `:<line>` when known. Don't guess: a wrong path costs more than `unknown`. |
| `divergence_type` | Exactly one of `fact-contradicted`, `workflow-gap`, `trigger-miss`. |
| `status` | Always `unresolved` on write. This skill never changes it. |
| `resolved_*`, `duplicate_of`, `archived_at` | Present but **empty** on write. Empty means "not yet triaged". |

## The status lifecycle

| `status` | Means |
|---|---|
| `unresolved` | Written, not yet triaged. The only value this skill writes. |
| `resolved` | Acted on: the skill was changed (PR merged; `resolution_pr` links it), or was already correct. |
| `wont-fix` | Deliberately rejected: by design, or the fix costs more than the harm. |
| `duplicate` | Same finding as an earlier log; `duplicate_of` names its filename. |

`/skill-health` surfaces `unresolved` logs; fixing one is `/edit-skill`. Whoever resolves a log sets
the status in the file and the index row together, moves the file to `Archive/YY-MM/` (the month in
`resolved_at`), sets `archived_at`, and repoints the index link. The row never moves and **no log is
ever deleted**.

## Body: six sections, in this order

1. **What the skill claims.** The verbatim quote in a blockquote, path and line beneath it.
2. **What was actually observed.** Evidence, redacted. Concrete about the shape of the result.
3. **Conversation excerpt.** The moment itself, verbatim and redacted, two or three turns. The
   section most often written too short.
4. **Why it matters.** One paragraph of consequence. No consequence, probably no divergence.
5. **Suggested fix.** The section that earns the file. Name the file, propose the wording, show the
   replacement. Not "the skill should be updated", but: in
   `skills/<name>/references/<file>.md`, the line "X" should read "Y". If the fix isn't obvious,
   say what must be established first, and by whom.
6. **Confidence and caveats.** One-off or reproducible? Specific to this machine, OS, profile,
   surface, account, or moment? Verified or inferred? Could the skill be right? A log that
   overstates its certainty is worse than none, because it gets acted on.

### When the wrong thing is a path or a per-person setting

Many divergences are one value that's right for the skill's author and wrong for everyone else: a
clone location, a browser profile, an install directory. **Don't propose a second hardcoded value**;
it fixes this machine and breaks on the third person.

Propose the `user-config-store` pattern, naming the key:

> In `skills/<name>/SKILL.md`, replace the hardcoded path with a `user-config-store` lookup for
> `clone_path`: if absent, ask once and store it; if present, use it without asking. See
> `skills/user-config-store/references/config-file-pattern.md`.

Limits, stated in `Confidence and caveats` when they apply:

- **Not for secrets.** A wrong credential is fixed via `required_environment_variables` /
  `$HERMES_HOME/.env`, not that store.
- **A setting the author can declare** may be better as `metadata.hermes.config`.
- **Check `user-config-store` still ships** in the repo before proposing it. Recommending a skill
  that no longer exists is itself a divergence.

## The index row

Inserted into `index.md` **directly under the table header** (`divergence_log.py index-add`), never
at the bottom, never by rewriting existing rows.

```
| 2026-10-16 10:51 | Eric Sharp | create-new-skill | 1.0.0 | workflow-gap | medium | unresolved | Clone path hardcoded; differs per person | [log](2026-10-16_1051_publishing-a-new-skill.md) |
```

Columns: date and time · who · skill · version · type · severity · status · one-line summary
(under ~90 characters, what was found, not what was done) · link. Escape any `|` in the summary as
`\|`. The `status` cell must always match the file's frontmatter.
