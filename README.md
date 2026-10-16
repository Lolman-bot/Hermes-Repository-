# Bitpool Hermes Skills

Bitpool's skills for [Hermes Agent](https://hermes-agent.nousresearch.com/docs/), the Hermes
counterpart of the Claude plugins in `bitpool/ai-skills`. Everything here is a Hermes-format skill
that installs straight from GitHub with `hermes skills`, plus the Hermes mods (desktop plugins,
TUI widgets, hooks, skins) that the mod skills build and install.

## Install

```bash
# One-time: add this repo as a skill source (tap)
hermes skills tap add Lolman-bot/Hermes-Repository-

# Install one skill into the bitpool category
hermes skills install Lolman-bot/Hermes-Repository-/skills/<skill-name> --category bitpool

# Later: pull updates for everything installed from here
hermes skills check
hermes skills update
```

Once installed, every skill is a slash command: `/onboarding`, `/teacher`, `/create-new-skill`, ...
Start a new session (or run `/reload-skills`) after installing so the skill index picks it up.

## Structure

```
README.md                  this file: catalogue + house rules (source of truth)
skills/<skill-name>/       one folder per skill, exactly one level under skills/
  SKILL.md                 Hermes frontmatter + body
  references/  assets/  scripts/  templates/   optional support files
mods/<mod-name>/           Hermes mods built by /build-hermes-mod (README + tests each)
```

`hermes skills tap` reads exactly one level under `skills/`, so skills are never nested in
category folders here. The category (`bitpool`) is chosen at install time with `--category`.

## Skills

### Required (baseline on every Bitpool Hermes install)

| Skill | What it does | Ships alongside `SKILL.md` |
|---|---|---|
| `build-hermes-mod` | Turns a plain description into a Hermes mod (desktop plugin, TUI widget, hook, Python plugin or skin): intake, agreed flow chart, build, tests, trial, switch-on, then a PR to `mods/`. | references/, templates/, assets/ |
| `build-skill-from-examples` | Builds a new skill from the user's input/output examples and a point-and-click process diagram, then hands it to `/create-new-skill`. | references/, assets/, scripts/ |
| `create-new-skill` | Takes a new or imported skill from idea to one reviewed PR on this repo, converting Claude skills to Hermes format. | references/, assets/ |
| `edit-mod` | Changes an existing mod: chart first, tests kept passing, live copy synced, user-checked, then republished. | references/ |
| `edit-skill` | Changes or retires a published skill on its own branch, keeping version, README row and catalogue snapshot in one PR. | references/ |
| `install-mod` | Lists mods on `main`, installs one into `$HERMES_HOME` following its README and switches it on, or uninstalls it cleanly. | references/ |
| `log-skill-divergence` | Asks yes/no/silence-for-this-session, then logs a wrong, gappy or mistriggered skill to the shared Team library (or `$HERMES_HOME`) for `/skill-health` and `/edit-skill`. | references/, assets/, scripts/ |
| `onboarding` | Walks a new starter through Hermes setup, GitHub sign-in, repo access via Eric and installing the required skills, one step at a time. | — |
| `skill-health` | Grades a skill's real run(s) against its own rules with a cited checklist and score (statistics at 3+ runs), then applies chosen fixes. | references/ |
| `skills-catalogue` | Gives the repo link and lists every Bitpool skill and mod from a dated snapshot. | references/ |
| `teacher` | Answers questions about how Hermes works in plain words from dated reference snapshots, then points to the next step. | references/ |
| `update-hermes-skill` | Housekeeping for any skill change: version bump, README row sync, and a runnable house-rules checker. | references/, scripts/ |
| `user-config-store` | Asks once for a per-person, non-secret value a skill needs and stores it on OneDrive, or under `$HERMES_HOME/bitpool-config/`. | references/, scripts/ |

### Design foundations (brand layer for visual and customer-facing work)

| Skill | What it does | Ships alongside `SKILL.md` |
|---|---|---|
| `bitpool-brand-guidelines` | Bitpool's verbal brand: the five voice pillars, naming rules, boilerplate and positioning for any copy written as Bitpool. | references/ |
| `bitpool-design-system` | Bitpool's visual system: six non-negotiables, light/dark tokens, components, the cube logo and a starter HTML template. | references/, assets/ |
| `bitpool-search` | Drop-in on-brand predictive search (typeahead, cyan highlights, keyboard nav) for Bitpool pages, lists and tables. | references/, assets/ |

## House rules for authoring skills

These rules are the source of truth. `/update-hermes-skill` carries a working copy of them in its
`references/`; if the two disagree, this README wins and the reference copy gets fixed.

### Folder, name and slash command

- Folder name == frontmatter `name` == slash command. Lowercase, hyphen-separated, ≤ 64 chars.
- One folder per skill directly under `skills/`. No category subfolders.

### Frontmatter (Hermes format)

```yaml
---
name: skill-name
description: "Use when <trigger>. <one-line behaviour>."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, ...]
    category: bitpool
    related_skills: [other-skill-in-this-repo]
---
```

- **`description` is 60 characters or fewer**, one sentence pair, ends with a period, starts with
  `Use when`. Hermes's skill index truncates at 57 characters, so the trigger must make sense in
  that window. Wrap it in double quotes (it almost always contains a colon or comma). Triggers,
  anti-triggers and detail go in the body's `## When to Use`, not here.
- **`version`** is semver. Patch for a wording/content fix, minor for new behaviour or a new
  reference file, major for a change that breaks what the skill writes or where it publishes.
- **`author`** credits Bitpool first, then Hermes Agent.
- **`platforms`** is audited from what the skill actually runs. Hermes tools + cross-platform CLIs
  (`gh`, `git`, `python`) = all three. bash-only pipelines = `[linux, macos]`.
- **`related_skills`** names only skills that exist in this repo (or ship bundled with Hermes).

### Body

Section order: `# Title` + 2-3 sentence intro, `## When to Use` (with a `Don't use for:` list),
`## Prerequisites` (if any), `## Procedure` (numbered, each step with a checkable completion
criterion), `## Load-bearing rules` (if the skill has hard rules), `## Pitfalls`, `## Verification`,
`## Reference files` (an index of `references/`, when there is one).

- **Name Hermes tools, not raw shell or Claude tools.** `terminal`, `read_file`, `write_file`,
  `patch`, `search_files`, `clarify` (questions with choices), `skill_view` / `skill_manage`,
  `delegate_task`, `cronjob`, `memory`, `web_search` / `web_extract`, `browser_*`, `vision_analyze`.
  Never `AskUserQuestion`, `Read`, `Edit`, `Glob`, `Grep`, `Bash`, `ToolSearch` or `Skill`.
- **No machine-local paths.** Resolve the Hermes home from `$HERMES_HOME` (never hardcode
  `~/.hermes`); write repo paths relative to the repo root.
- **No `../` links out of a skill's own support folders.** The hub installer rejects
  `references/../...` and only bundles the skill's own folder; a skill that links outside itself
  installs broken.
- **Keep SKILL.md tight** (~100-200 lines). Detail goes in `references/*.md`, byte-exact content
  (templates, scaffolds, vendored JS) in `assets/` or `templates/`, executable code in `scripts/`.

### Self-contained, no live wiki

A skill never fetches its own instructions from a wiki, page or API. Wiki-derived content ships as a
dated snapshot in `references/` that states its date and says what an absent entry does *not*
prove.

### Publishing

- `main` only changes through a pull request. Work on a branch named `add/<skill>`,
  `edit/<skill>` or `retire/<skill>`.
- Every change to a skill bumps its `version` and syncs its row in the **Skills** table above. A
  new skill adds a row; a retired skill moves to `retired/<skill-name>/` and loses its row.
- Installed copies update through `hermes skills update`, which compares against this repo's
  `main`. Nothing merged = nothing shipped.

### Verify before opening the PR

- Every `skills/*/SKILL.md` parses as YAML frontmatter with `name` == folder name and a
  `description` of 60 characters or fewer.
- Every `references/`, `assets/`, `scripts/`, `templates/` path named in a `SKILL.md` exists.
- Every skill folder has a README row and every README row has a folder.
- No `SKILL.md` names a Claude-only tool or a machine-local path.

## Note to future AI assistants

Read this README fresh before changing anything in the repo; it is the source of truth for the
rules above. Don't make anyone grep `SKILL.md` files to know what's published: keep the Skills
table in sync in the same pull request as the skill change.
