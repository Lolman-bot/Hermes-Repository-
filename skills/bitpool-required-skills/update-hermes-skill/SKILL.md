---
name: update-hermes-skill
description: "Use when a Bitpool repo skill changes. Bump, sync, verify."
version: 1.0.1
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, skills, authoring, github, housekeeping]
    category: bitpool
    related_skills: [create-new-skill, edit-skill, skills-catalogue]
---

# Update Hermes Skill

The housekeeping checklist that keeps the Bitpool Hermes skills repo (`Lolman-bot/Hermes-Repository-`)
consistent whenever a skill is added, edited, renamed or retired: the per-skill `version` bump, the
README **Skills** table row, Hermes frontmatter compliance and the verification checks. It ships a
working copy of the README house rules in `references/` and a runnable checker in `scripts/`; the
repo's own `README.md` stays the source of truth and is read fresh every run.

## When to Use

- `/update-hermes-skill`, or proactively whenever the working directory is a clone of the Hermes
  skills repo and a `skills/<section>/<name>/SKILL.md` or its support files are being added, edited, renamed
  or moved to `retired/`.
- Invoked without asking by `/create-new-skill` and `/edit-skill`, before their readiness check.
- When someone asks "is the repo consistent?", "bump the version", or "sync the README table".

Don't use for:
- Creating a skill from an idea, or importing one: `/create-new-skill` (it calls this skill).
- Changing what a skill does, or retiring one: `/edit-skill` (it calls this skill).
- Skills that live only in someone's local `$HERMES_HOME/skills/` and never go to the repo.

## Prerequisites

- `terminal` access on the machine holding the clone, with `git` and `python` (3.8+) on PATH.
- The clone's `origin` is `https://github.com/Lolman-bot/Hermes-Repository-.git`, and the session
  is on a branch named `add/<skill>`, `edit/<skill>` or `retire/<skill>`, never `main`.

## Procedure

1. **Read the repo's `README.md` fresh** with `read_file`, all of it, including the house rules and
   the note to future AI assistants. Done when you can name the current frontmatter shape and the
   description limit from the README itself, not from memory.
2. **Read `references/hermes-repo-house-rules.md` in full.** If it disagrees with the README, the
   README wins: apply the README and tell the user the reference file needs correcting. Done when
   any disagreement has been said out loud.
3. **Classify the change** with the table in the reference file: content edit, new behaviour, new
   skill, rename, retirement, or breaking change. Done when you know the bump level and which README
   row changes.
4. **Bump the skill's `version`** in its frontmatter (patch / minor / major per the table; a new
   skill starts at `1.0.0`). Every skill folder touched gets its own bump, including any other skill
   whose files you also changed (e.g. the `skills-catalogue` snapshot). Done when each touched
   `SKILL.md` carries a higher version than on `origin/main`.
5. **Sync the README Skills table**: add, reword or remove the row so it reads
   `` | `name` | one-sentence summary | references/, assets/ ... or — | ``, with the last column
   matching the folders actually present. Done when every skill folder has exactly one row and every
   row has a folder.
6. **Check for duplicated reference files** that another skill carries under the same filename
   (`search_files` with `target="files"` on `skills/*/*/references/<file>`). Change every copy and bump
   every skill that carries one. Done when no copy has drifted.
7. **Run the checker** from the repo root and fix every FAIL:

   ```bash
   git fetch origin --prune
   python ${HERMES_SKILL_DIR}/scripts/verify_repo.py . --base origin/main
   ```

   Inside the clone the same script is at `skills/bitpool-required-skills/update-hermes-skill/scripts/verify_repo.py`. Done
   when it exits 0 and every WARN has been read and either fixed or explained to the user.
8. **Stage, don't commit.** `git add -- skills/<section>/<name> README.md` (plus `retired/<section>/<name>` on a
   retirement). Commit only if the user explicitly asks; when this runs inside `/create-new-skill` or
   `/edit-skill`, those skills own the commit, branch and pull request. Done when `git status
   --short` shows only the intended paths staged.

## Load-bearing rules

1. **The README is the authority.** Never run this off a cached idea of the rules.
2. **No change ships without a `version` bump.** `hermes skills check|update` compares installed
   copies against `main`; an unbumped change is invisible to anyone deciding whether to update.
3. **`description` is 60 characters or fewer**, starts with `Use when`, ends with a period, is
   double-quoted. Hermes's index truncates at 57, so the trigger must read right in that window.
4. **Folder name == frontmatter `name` == slash command**, lowercase-hyphenated, inside a section
   folder: `skills/<section>/<name>/`. The section matches the skill's README `### ` group; names
   stay unique across sections.
5. **Hermes tools only, no machine-local paths, no `../` out of the skill.** The hub installer only
   bundles the skill's own folder and rejects escaping paths.
6. **Never on `main`.** `main` only changes through a pull request. If the session is on `main`
   with changes, say so before staging anything.
7. **Measure, don't eyeball.** Lengths, versions and README parity come from the checker's output.

## Pitfalls

- **Bumping only the skill you meant to change.** Refreshing the `skills-catalogue` snapshot is a
  change to `skills-catalogue` too, so it needs its own patch bump.
- **README column drift.** A skill that gains a `scripts/` folder but keeps `references/` in the
  last column misleads installers; re-derive the column from what is on disk.
- **Description in YAML without quotes.** A colon or comma in an unquoted description breaks YAML
  parsing and the skill silently fails to load.
- **Retiring with `rm`.** Retirement is `git mv skills/<section>/<name> retired/<section>/<name>`; `git status` must
  show `R`, not `D`, or history stops following the file.

## Verification

- `verify_repo.py ... --base origin/main` exits 0.
- `git diff --cached --stat` lists only the skill folder(s), `README.md`, and `retired/` if any.
- Summarise to the user in two or three sentences: skills touched, old -> new versions, README rows
  added/changed/removed.

## Reference files

| File | Covers |
|---|---|
| `references/hermes-repo-house-rules.md` | Working copy of the README house rules: frontmatter, body order, tool names, paths, the change-classification and bump table, README sync, retirement, and every verification check as a runnable `python`/`git`/`gh` command. |
| `scripts/verify_repo.py` | Stdlib-only checker (PyYAML optional): frontmatter, description limits, support paths, Claude-only leftovers, README parity, retired rows, and version bumps against a base ref. Run it; don't paraphrase it. |

When the house rules change, edit the repo's `README.md` first, then this reference file and the
checker in the same pull request so the three never drift.
