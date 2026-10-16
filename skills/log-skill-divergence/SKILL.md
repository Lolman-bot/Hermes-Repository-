---
name: log-skill-divergence
description: "Use when a loaded skill proved wrong. Ask, then log it."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, skills, feedback, divergence, quality]
    category: bitpool
    related_skills: [skill-health, edit-skill, user-config-store, update-hermes-skill]
---

# Log Skill Divergence

Captures the moment a Bitpool skill turns out to be wrong, so the finding survives the session it
happened in. The result is one Markdown file plus an index row in the Team SharePoint
`Hermes Skill logging` folder (or, when that isn't synced, under `$HERMES_HOME/skill-divergence/`),
written for `/skill-health` to surface and `/edit-skill` to act on.

This skill **logs**. It never edits the skill it reports on and never closes a log: every log it
writes is `unresolved`. Hermes's `skill_manage` and background curator can patch an installed copy,
but that fixes one machine and is overwritten by `hermes skills update`. The log is the
human-reviewable record that gets the fix into `Lolman-bot/Hermes-Repository-` for everyone.

## When to Use

- The user runs `/log-skill-divergence`.
- Proactively, the moment a loaded skill is contradicted by what you just observed (a call it calls
  "blocked" works), has a step you had to work around, or failed to trigger when it should have.

Don't use for:
- Fixing or closing a logged divergence, or changing a skill: `/edit-skill`.
- Reviewing a run you just watched end to end: `/skill-health`.
- Repo housekeeping and house rules: `/update-hermes-skill`.
- Your own mistakes that no skill caused.

## Procedure

The prompt is cheap and lives here; the write is expensive and lives in `references/`. **Read
nothing from `references/` except the rubric until the user has said yes.**

1. **Classify.** Check what you noticed against `references/what-counts-as-divergence.md`:
   `fact-contradicted`, `workflow-gap` or `trigger-miss`. Done when it fits one type; if it fits
   none, stop silently without prompting.
2. **Prompt with `clarify`.** One question naming the skill, what it claims, and what you
   observed, with three choices: `Yes, log it` / `No, skip this one` / `Silence for this session`.
   Done when the user has picked one.
3. **Branch.** No: say nothing more and return to the task. Silence: remember it for the rest of
   this session and never invoke this skill again in it. Yes: continue. Done when you are on the
   Yes path or back on the task.
4. **Gather identity and evidence.** Read `references/write-locations.md` and
   `references/log-file-spec.md`. Collect: `logged_by` (via `user-config-store`), session id
   (`${HERMES_SESSION_ID}`), session title, Hermes version and profile, surface, and the offending
   skill's `name`, `version`, source and most specific `skill_path:line` (load it with
   `skill_view`). Done when every frontmatter field has a value or an honest `unknown`.
5. **Locate.** `python ${HERMES_SKILL_DIR}/scripts/divergence_log.py locate`. Done when you know
   the folder and whether it's `shared` or `local`.
6. **Write.** Fill `assets/divergence-log.md.template` in memory, redacted; get a path from
   `free-name`; write it once with `write_file`; add the index row with `index-add` (it creates
   `index.md` from `assets/index.md.template` if needed). `status` is always `unresolved`. Done
   when `read_file` shows the log and the row is in `index.md`.
7. **Report in one line** (say "local, not shared" plus the sync hint when `kind` is `local`), then
   return to the interrupted task. Done when you're back on the task.

## Load-bearing rules

1. **Never write without an explicit yes.** Silent logging into a Team-wide library is
   surveillance, not feedback.
2. **Prompt once per divergence.** Distinct divergences each get their own prompt and file, unless
   the user chose silence.
3. **Silence holds for the rest of the session.** Don't re-ask or re-offer because a new one "feels
   different".
4. **Log only.** Never edit the skill (no `skill_manage`, no `patch`), never set a status other
   than `unresolved`, never write into `Archive/`.
5. **Never write a secret, credential, customer or personnel name, or raw tool payload.** If it
   can't be described without one, don't write it; offer a redacted version.
6. **Shared first, local fallback says so.** Prefer the Team library. A local log must be reported
   as local and not shared, with the sync instructions; never imply it reached the team.
7. **Who logged it goes in `logged_by`, never in the path.** Paths are lost on archive.
8. **Identify the Hermes skill exactly:** `skill` + `skill_version` from its frontmatter, repo-relative
   `skill_path`, and the session id. A log for the wrong version sends the reader to a fixed bug.
9. **Resolve every path at run time.** No usernames, no hardcoded Hermes home; use the helper and
   `$HERMES_HOME`.
10. **The index is append-only, newest row at the top.**
11. **Report the divergence, not a verdict on the skill.**

## Pitfalls

- **Never round-trip Markdown through Windows PowerShell**: it mangles UTF-8 and adds a BOM. Use
  `write_file` and the helper.
- **New sessions often have no title**: use `unknown` and slug the summary instead.
- **`Claude Skill logging` is the Claude-era folder.** Don't write Hermes logs there; the skill
  names, paths and repo differ.
- **A locally patched skill** (by `skill_manage` or the curator) may differ from the repo: compare
  with the repo version before logging.
- **On a messaging gateway** `clarify` may render as plain text; accept "yes", "no" or "silence"
  as replies.

## Verification

- The log file exists at the reported path, every frontmatter field is present, `status:
  unresolved`, and `logged_by` is a real name.
- `index.md` has the new row directly under the header, linking to the file.
- No secret or personal data appears in either file.

## Reference files

| File | Covers |
|---|---|
| `references/what-counts-as-divergence.md` | The three types with examples, severity rubric, and what is **not** a divergence. Read before prompting. |
| `references/log-file-spec.md` | Redaction rules, filename, frontmatter schema, status lifecycle and archiving, the six body sections, the index row. Read only after a yes. |
| `references/write-locations.md` | Team library vs `$HERMES_HOME` fallback, `logged_by`, session and skill identity, collisions, sync instructions. Read only after a yes. |
| `assets/divergence-log.md.template` | Skeleton for one log file. |
| `assets/index.md.template` | Header for a fresh `index.md`. |
| `scripts/divergence_log.py` | `locate`, `slug`, `free-name`, `index-add` (stdlib, UTF-8 safe). |
