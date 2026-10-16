# Where the log goes, and how to address it

Resolve everything fresh every run. **Never hardcode a username or a path.** The bundled
`scripts/divergence_log.py` does the location, filename and index work cross-platform (UTF-8, no
BOM, LF), so run it with `terminal` rather than reimplementing it in the shell:

```
python ${HERMES_SKILL_DIR}/scripts/divergence_log.py locate
python ${HERMES_SKILL_DIR}/scripts/divergence_log.py free-name <YYYY-MM-DD_HHmm> "<title or summary>"
python ${HERMES_SKILL_DIR}/scripts/divergence_log.py index-add "| ... |"
```

Write the log file itself with `write_file`, in one piece.

> **Never round-trip Markdown through Windows PowerShell.** `Get-Content` defaults to the ANSI
> codepage, so a read-modify-write turns every em-dash into `â€”`; PowerShell 5.1's
> `Set-Content -Encoding utf8` prepends a BOM. Both were observed the first time the Claude version
> of this skill ran. Build the content once and write it once.

## The locations

### 1. Shared (preferred): the Team SharePoint library

```
<Team library>/Hermes Skill logging/
├── index.md                                   <- every row, newest first
├── 2026-10-16_1116_<slug>.md                  <- open logs, flat
└── Archive/
    └── 26-10/                                 <- processed logs, by month RESOLVED
```

The Team library is the synced **Bitpool-Team - Documents** SharePoint library:

| OS | Where the sync client puts it |
|---|---|
| Windows | `%USERPROFILE%\Bitpool Pty Ltd\Bitpool-Team - Documents` |
| macOS | `~/Library/CloudStorage/OneDrive-SharedLibraries-*/Bitpool-Team - Documents` (unverified on a Bitpool Mac; check and fix this line if wrong) |
| Linux | No official client. Use the local fallback. |

`Hermes Skill logging` is a sibling of the Claude-era `Claude Skill logging` folder, not the same
folder: Hermes skill names, paths and repo differ, and mixing the two would send whoever triages a
Claude log to the wrong repo. If the library resolves but the folder doesn't exist yet, creating it
is fine: it's inside a synced library, so it reaches the team.

Write the log **flat** into that folder. No per-person subfolder. `Archive/` is the only
subfolder, and this skill never writes into it.

### 2. Fallback: local to this Hermes install

`$HERMES_HOME/skill-divergence/`, same layout. Used only when the Team library doesn't resolve
(Linux, an unsynced machine, a gateway host, a Docker install).

A local log is **not shared**, and a log nobody sees reads as done when it isn't. So when the
fallback is used:

- Say so in the one-line report: "Written locally (not shared): `<path>`".
- Give the sync instructions below, and offer to move the file and its index row into the
  shared folder once it syncs.
- `/skill-health` reads this folder too, so the finding still reaches the next skill review on
  this machine.

To sync the library: open
<https://bitpoolau.sharepoint.com/sites/bitpool-team/Shared%20Documents/Forms/AllItems.aspx>, click
the **…** (ellipsis) and choose **Sync**. Never create a fake `Bitpool Pty Ltd/...` folder by hand:
an unsynced local folder of that name looks like it's working while going nowhere.

## Who logged it: in the file, not the path

A folder name is metadata encoded in the path, and it's lost the moment the file is archived. The
person's name goes in the frontmatter as `logged_by`.

Get it from `user-config-store`: load it with `skill_view`, then
`get log-skill-divergence display_name`. If it's missing, ask once with `clarify` ("What name should
skill-divergence logs show as the author? I'll remember it.") and `set` it. Only if the user won't
give one, use the OS username (`USERNAME` / `USER`). Never write `unknown`.

## Session identity

| Field | Source |
|---|---|
| `session_id` | `${HERMES_SESSION_ID}` (substituted into this skill's text when loaded), or `$HERMES_SESSION_ID` in a `terminal` subprocess. Subagents inherit the parent's session context. `unknown` if neither is set. |
| `session_title` | `hermes sessions list` and match the id. New sessions often have no title yet: use `unknown` and slug the divergence summary for the filename instead, noting it in `Confidence and caveats`. |
| `hermes_version` | First line of `hermes --version`. |
| `hermes_profile` | The active profile name (the last path segment of `$HERMES_HOME` when it sits under `profiles/`), else `default`. |
| `surface` | Where the session is running: `cli`, `tui`, `desktop`, `dashboard`, `gateway:<platform>`, `cron`. |

## The skill's identity

`skill` and `skill_version` come from the offending skill's own frontmatter as loaded
(`skill_view <name>`). The version matters: a later version may already have fixed it.

`skill_source`: `Lolman-bot/Hermes-Repository-` if it was installed from this repo (check
`hermes skills list`), `bundled` for skills shipped with Hermes, `local` for skills created on this
machine (e.g. with `skill_manage`), or the hub source shown by `hermes skills list`.

`skill_path` is **repo-relative** for repo skills (`skills/<name>/references/<file>.md:42`). For
bundled or local skills, give the path relative to `$HERMES_HOME/skills/`. Never an absolute path.

## Filename collisions

Files are flat and shared, so two people can produce the same stem in the same minute. `free-name`
appends `-2`, `-3`, ... and never returns an existing name. Never overwrite a log, and never assume
a matching name is your own earlier file: check `logged_by` and `session_id`.

## Writing

1. Build the file content once, in memory, fully redacted, from `assets/divergence-log.md.template`.
2. `free-name` for the path.
3. `write_file` it.
4. `index-add` the row (creates `index.md` from `assets/index.md.template` if needed).
5. `read_file` the log back and confirm the index row exists. Report the path in one line, then
   return to the interrupted task.

Never report success for a write you did not verify.
