---
name: edit-skill
description: "Use when editing or retiring a Bitpool skill. Ends in a PR."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, skills, authoring, github]
    category: bitpool
    related_skills: [create-new-skill, update-hermes-skill, skill-health, skills-catalogue, user-config-store]
---

# Edit Skill

Changes or retires a skill that already ships in the Bitpool Hermes skills repo,
`Lolman-bot/Hermes-Repository-`, and leaves the repo consistent: the skill folder, its `version`, its
README **Skills** row and the `skills-catalogue` snapshot, all in one pull request. Work happens on an
`edit/<skill-name>` (or `retire/<skill-name>`) branch, and the pull request is raised **once**, after
the user confirms the change is finished.

## When to Use

- `/edit-skill`, or when the user asks to change, fix, update, rename, delete, retire or archive a
  skill that's already in the repo: "edit the bacnet-diagnostics skill", "it keeps firing when I
  don't want it", "get rid of the X skill".
- Applying fixes `/skill-health` proposed for a published skill.

Don't use for:
- A brand-new skill, or importing one: `/create-new-skill`.
- Housekeeping with no content change (a missing README row, a version bump): `/update-hermes-skill`.
- Mods under `mods/`: `/edit-mod`.
- A skill that only exists in the user's own `$HERMES_HOME/skills/`: patch it with `skill_manage`.

## Prerequisites

- `terminal` on the machine that holds the clone, with `git`, `gh` (signed in) and `python`. On a
  messaging gateway the terminal runs on the gateway host, so the clone must be there.
- Write access to `Lolman-bot/Hermes-Repository-`.
- The clone path, remembered with `/user-config-store` (`get edit-skill clone_path` / `set edit-skill clone_path`); confirm
  it with `git -C "<clone_path>" rev-parse --show-toplevel`. If missing, ask once with `clarify` and
  save it. Never probe guessed paths.

## Procedure

1. **Pre-flight, locate the skill, branch** — per `references/choose-and-pull.md`: right `origin`,
   clean tree, `git fetch`, README read fresh from `origin/main`, the skill resolved to exactly one
   `skills/<name>/` path and confirmed with the user, no competing open PR, branch
   `edit/<skill-name>` from `origin/main`. Done when the user has said yes to the path and you're
   on the branch.
2. **Ask which route** with `clarify`: **Change it** (`references/edit-route.md`) or **Retire it**
   (`references/retire-route.md`). Never infer it — "fix X" and "get rid of X" are one word apart.
   Done when the user has picked one (rename the branch to `retire/<skill-name>` for retire).
3. **Run that route** to a finished on-disk state, nothing committed. Done when the route file's
   closing checklist is all ticked and the user has seen the full changed `SKILL.md` (edit) or the
   rename list (retire).
4. **Run `/update-hermes-skill`** yourself, every run, without asking: `version` bump, README row,
   compliance checker. Done when the checker exits 0.
5. **Refresh the `skills-catalogue` snapshot** from the README's updated Skills table, bump its date
   line and that skill's `version` — `references/publish.md`. Skip only when the skill being edited
   *is* `skills-catalogue` and the edit already covers the snapshot. Done when the snapshot matches
   the README.
6. **Readiness check** — `references/publish.md`. Checker output as a pass/fail table, fix every
   failure, show the full diff, then ask with `clarify`: **It's finished — raise the pull request**,
   **Try it out first** (recommended when the changed behaviour hasn't run on a real task), or **Not
   yet**. Offer `/skill-health` on a real run here. Done on an explicit answer.
7. **Commit, push, raise the pull request** — only on **It's finished**. Report the link, what's in
   it, that it isn't live until approved and merged, how installed copies pick it up, and that pushes
   from here reset the approval. Done when `gh pr view` returns it and the clone is back on `main`.

## Load-bearing rules

1. **Fetch and branch from `origin/main` before editing — never edit on `main`.** A stale checkout
   edits a version that no longer exists and can revert someone else's work on merge.
2. **Read the repo `README.md` fresh every run.** It is the source of truth; if this skill's
   references disagree, the README wins — say so.
3. **Never guess which skill.** Search, show the full path, get a yes before the first edit. Names
   can differ by one word (`pdf-to-md` / `pdf-to-md-rich`).
4. **Retiring means moving, never deleting.** `git mv skills/<name> retired/<name>`; `git status` must
   show `R`, not `D`.
5. **Hermes frontmatter stays exactly as the README specifies**; every change bumps `version`
   (patch / minor / major per `/update-hermes-skill`).
6. **Folder == `name` == slash command.** A rename moves all three together and fixes every
   `related_skills` entry and `/old-name` mention in other skills.
7. **Duplicated reference files get the same change in every copy**, and every carrying skill bumps.
8. **Everything in one pull request**; never one per file or per fix.
9. **No pull request until the user says it's finished.** "Probably", "close enough" or silence is
   not a yes. Work in progress stays on the local branch — never a PR, never a draft.
10. **One open pull request per skill.** This user's → add to it; someone else's → stop and say who.
11. **`/skill-health` is an offer, never an action**, and only before the PR; its fixes join this
    change.

## Pitfalls

- **Rewriting a step from your own idea of the job.** Read the current step back and ask what it
  should say; the substance is the user's.
- **Trigger changes left in prose.** "It fires when it shouldn't" is fixed in `## When to Use` /
  `Don't use for:` and, if needed, the 60-char `description` — not deep in a reference file.
- **Testing over the installed copy.** Copying the branch version over the hub-installed skill marks
  it locally modified, so `hermes skills update` skips it; after merge run
  `hermes skills update <skill-name> --force`.
- **Renames strand installed users.** Installs track `skills/<old-name>`; after a rename people must
  `hermes skills uninstall <old-name>` and install the new name. Say so in the PR and the report.
- **A dead pointer after retirement.** Another skill's `Don't use for:` or `related_skills` still
  naming the retired skill misroutes users; sweep with `search_files`.

## Verification

- `python skills/update-hermes-skill/scripts/verify_repo.py . --base origin/main` exits 0.
- Retire route: `git status --short` shows `R  skills/<name>/... -> retired/<name>/...`, no `D`.
- `gh pr view <branch> --repo Lolman-bot/Hermes-Repository- --json url,state` shows `OPEN`.

## Reference files

| File | Covers |
|---|---|
| `references/choose-and-pull.md` | Finding the clone, git pre-flight and what each failure means, reading the README fresh, locating the named skill, duplicated reference files, confirming the path, the open-PR check, making the branch. |
| `references/edit-route.md` | Getting a specific answer about what to change, where each kind of change belongs, keeping it compliant, and handling a rename. |
| `references/retire-route.md` | The `git mv` into `retired/`, removing the README row, fixing pointers from other skills, and the closing checklist. |
| `references/publish.md` | Housekeeping and snapshot refresh, the readiness checks and the ready question, trying the change locally, commit/push/PR, what to report, the `/skill-health` offer. |

This skill pairs with `/create-new-skill` (idea → published) and calls `/update-hermes-skill`
(housekeeping); if the split between the three changes, update all three together.
