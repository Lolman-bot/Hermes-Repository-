---
name: create-new-skill
description: "Use when making a new Bitpool skill. Idea to pull request."
version: 1.1.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, skills, authoring, github]
    category: bitpool
    related_skills: [onboarding, edit-skill, update-hermes-skill, skill-health, skills-catalogue, user-config-store]
---

# Create New Skill

Takes a new Hermes skill from "I have an idea" (or "here's a skill I already have") to one pull
request on the Bitpool Hermes skills repo, `Lolman-bot/Hermes-Repository-`, waiting for an approver.
`main` only changes through a pull request, so the work happens on an `add/<skill-name>` branch and
the pull request is raised **once**, after the user confirms the skill is finished.

## When to Use

- `/create-new-skill`, or when the user asks to create, make, build or bring in a skill: "I want to
  make a skill", "turn this into a skill", "here's a SKILL.md, publish it".
- Importing an existing Claude skill (a `SKILL.md` or folder) and converting it to Hermes format.

Don't use for:
- Changing or retiring a skill that already ships: `/edit-skill`.
- Housekeeping with no new skill (version bump, README row): `/update-hermes-skill`.
- A purely personal skill that never goes to the repo: save it with `skill_manage` directly.

## Prerequisites

- `terminal` on the machine that holds (or will hold) the clone, with `git`, `gh` (signed in) and
  `python`. On a messaging gateway the terminal runs on the gateway host, so the clone must be there.
- Write access to `Lolman-bot/Hermes-Repository-`. Without it the push fails with 403; see
  `references/publish.md`.
- The clone path, remembered with `/user-config-store` (`get create-new-skill clone_path` / `set create-new-skill clone_path`). Check it
  first and confirm it with `git -C "<clone_path>" rev-parse --show-toplevel`. If it's missing, ask
  once with `clarify`, explain it will be remembered, and save it. Never probe guessed paths.

## Requirements check (before step 1)

**Check the requirements first, and send anyone who doesn't meet them to `/onboarding`.** This
skill needs two things on the machine the `terminal` runs on:

- **A local clone of `Lolman-bot/Hermes-Repository-`**, with `origin` set to it. A clone of the
  Claude plugin repo (`bitpool/ai-skills` or `ai-skills-beta`) won't work.
- **Git installed and signed in to GitHub** (`gh auth login` plus `gh auth setup-git`), so it can
  fetch and push.

Check both **before step 1**, not at the pre-flight in step 3, so nobody sits through an interview
for a skill they can't publish. If either is missing (no clone, a Claude-repo clone, `git` not
found, or `git fetch` / `gh auth status` refused for sign-in), stop. Tell them in one line which
requirement isn't met, then hand over to `/onboarding` (load it with `skill_view`), which walks them
through installing Git, signing in and cloning the repo. Don't fix it in place: never clone,
install Git or repoint remotes for them. Once they're set up, they run `/create-new-skill` again.
The checks themselves are the first rows of the pre-flight table in `references/publish.md`.

## Procedure

1. **Ask which route** with `clarify`, in plain words (two options):
   - **Build it with me** — the interview in `references/skill-interview.md`.
   - **I already have one** — the import and Claude-to-Hermes conversion in
     `references/import-existing-skill.md`.

   Don't infer the route unless the user has plainly handed over a folder or file. Done when the
   route is chosen.
2. **Run that route** to a finished skill folder: `SKILL.md` built from
   `assets/SKILL.md.template`, plus any `references/`, `assets/`, `scripts/`, `templates/`. Done
   when the user has seen the full `SKILL.md` in chat and said yes to it.
3. **Pick the section, then pre-flight, branch and write it into the repo** at
   `skills/<section>/<skill-name>/`. The section is the README `### ` group the skill belongs to
   (e.g. `bitpool-required-skills`, `bitpool-design-foundations`). Ask with `clarify`, listing the
   existing sections plus "a new section"; a new section needs its own README heading and table. Then, per
   `references/publish.md`: clean tree, `origin` is the Hermes repo, `git fetch`, no open pull
   request already adding that name, branch `add/<skill-name>` from `origin/main`. Byte-exact files
   are copied with `cp`, never retyped. Done when the files are on disk on the branch, uncommitted.
4. **Run `/update-hermes-skill`** yourself, every run, without asking: version `1.0.0`, the README
   Skills row, frontmatter compliance. Done when its checker exits 0.
5. **Refresh the `skills-catalogue` snapshot** from the README's updated Skills table and bump its
   date line and that skill's `version` (patch), per `references/publish.md`. Done when the snapshot
   lists the new skill.
6. **Readiness check** — `references/publish.md`. Show the checker output as a pass/fail table, fix
   every failure, show the full `SKILL.md` and the staged diff, then ask with `clarify`: **It's
   finished — raise the pull request**, **Try it out first** (recommended when the skill has never
   run on a real task; installs a local copy for testing), or **Not yet**. Offer `/skill-health` on a
   real run here. Done when the user has given an explicit answer.
7. **Commit, push, raise the pull request** — only on **It's finished**, per
   `references/publish.md`. Report the link, the path, the slash command, the install command, that
   it isn't live until approved and merged, and that pushes from here reset the approval. Done when
   `gh pr view` returns the PR and the clone is back on `main`.

## Load-bearing rules

1. **Read the repo's `README.md` fresh before writing anything.** It is the source of truth; this
   skill's references are a convenience. If they disagree, the README wins — say so.
2. **Hermes frontmatter exactly as the README specifies**: quoted `description` of ≤ 60 chars that
   starts `Use when` and ends with a period, `version: 1.0.0`, `author`, `license`, `platforms`,
   `metadata.hermes.tags` (incl. `bitpool`), `category: bitpool`, `related_skills` from this repo.
3. **Folder name == `name` == slash command**, lowercase-hyphenated, under `skills/<section>/`.
4. **Self-contained.** Detail in `references/`, byte-exact content in `assets/`/`templates/`,
   code in `scripts/`. Nothing fetched at run time, no `../` links, no machine-local paths.
5. **No pull request until the user says it's finished.** "Probably", "close enough" or silence is
   not a yes. Work in progress stays on the local branch — never a PR, never a draft.
6. **One pull request, never half of it.** The skill folder, README row and catalogue snapshot go up
   together. If this user already has a PR open for the name, add to it; if someone else does, stop
   and say who.
7. **Never write on `main`.** Everything goes on `add/<skill-name>`.
8. **Plain language with the user.** Someone who has never written a skill must be able to follow
   every question.
9. **`/skill-health` is an offer, not an action**, and only before the PR. Its fixes join this
   change.

## Pitfalls

- **Description written like a Claude `ACTIVATION:` paragraph.** It gets truncated at 57 chars in
  the index; move triggers and anti-triggers to `## When to Use`.
- **Testing with a local copy and forgetting it.** A copy in `$HERMES_HOME/skills/bitpool/` shadows
  or blocks the hub install; remove it before installing the merged version.
- **Retyping a template** instead of `cp` — a regenerated asset is a different asset.
- **`git add -A` from the repo root** sweeps up unrelated files; always pass a pathspec.

## Verification

- `python skills/bitpool-required-skills/update-hermes-skill/scripts/verify_repo.py . --base origin/main` exits 0.
- `gh pr view add/<skill-name> --repo Lolman-bot/Hermes-Repository- --json url,state` shows `OPEN`.
- The PR diff contains `skills/<section>/<skill-name>/`, the README row and the snapshot refresh, nothing else.

## Reference files

| File | Covers |
|---|---|
| `references/skill-interview.md` | The plain-language interview for building a skill from scratch: the eight questions, mapping answers onto Hermes frontmatter and body sections, when to split into `references/`. |
| `references/import-existing-skill.md` | Bringing in an existing skill — especially a Claude `SKILL.md` — and converting it: frontmatter rewrite, tool-name map, path and connector conversion, the compliance audit. |
| `references/publish.md` | Pre-flight and open-PR check, branching, writing files, the snapshot refresh, readiness checks, the ready question, trying it out locally, commit/push/PR, what to report, the `/skill-health` offer. |
| `assets/SKILL.md.template` | The skeleton for a new Hermes `SKILL.md` in house section order. Copy it, then fill it in. |
