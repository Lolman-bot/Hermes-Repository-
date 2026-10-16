---
name: edit-mod
description: "Use when changing an existing mod. Edit, test, republish."
version: 1.0.1
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, mods, desktop-plugins, tui-widgets, hooks, plugins, skins]
    category: bitpool
    related_skills: [build-hermes-mod, install-mod, edit-skill]
---

# Edit Mod

Changes a Hermes mod that already exists (a desktop plugin, TUI widget, gateway hook, shell hook,
Python plugin or skin built by `/build-hermes-mod`) and sends the change back to where it's
published. The mod keeps its package layout (`README.md`, `docs/flow.mmd`, `hermes-home/`,
`tests/`), its tests still pass, and the change goes up the way the user chose.

## When to Use

- `/edit-mod`, or the user asks to change, fix or update a mod: "edit my git-chip mod", "the
  usage pane should also show...", "fix the Telegram alert in my mod and push it".

Don't use for:
- Building a new mod: `/build-hermes-mod`.
- Creating or changing a skill: `/create-new-skill`, `/edit-skill`.
- Installing or removing a published mod with no code change: `/install-mod`.
- Settings changes that touch no mod code: `hermes config set` directly.

## Prerequisites

- `terminal`, `read_file`, `write_file`, `patch`, `search_files`, `clarify`, `skill_view`.
- `node` / `python` as the mod's kind needs; `gh` signed in to republish.

## Procedure

Each step's output is the next step's input.

1. **Find the mod.** List the mod packages on this machine, ask which one with `clarify`, and
   confirm the folder and kind. Done on a yes. `references/find-the-mod.md`.
2. **Work out where it publishes** — `mods/<mod-name>/` in `Lolman-bot/Hermes-Repository-`, the
   mod's own repo, or nowhere yet — and run that destination's pre-flight (drift, open PRs). Done
   when the destination is said back and agreed. Same reference.
3. **Ask what to change** until it's a before and an after. Done when you can state both.
   `references/make-the-change.md`.
4. **Does it change what the mod does?** If yes, change the flow chart first, show it, read back
   what changed, and get a yes. If it's a pure fix, say so and skip. Done on a yes or a stated skip.
5. **Make the change.** Load the bundled `hermes-agent` skill and its reference for the kind first.
   Edit in the package, then update tests, `docs/flow.mmd`, the README and bump the README's
   **Version**. Done when all are in step. `references/make-the-change.md`.
6. **Run the tests and checks** for the kind (`references/mod-kinds.md`). If anything fails, back to
   step 5. Done when everything passes, nothing skipped.
7. **The user's check.** Sync the changed files to their live places, tell the user what to look
   for, ask "Does it work the way you wanted?" If no, back to step 5. Done on an explicit yes.
8. **Agree how it goes up.** Show the changed files and old/new version, then ask (`clarify`) for
   PR or direct push, the branch, and the commit message, with a proposed default for each. Done
   on three explicit answers. `references/republish.md`.
9. **Commit and push** exactly as agreed, then report the link, branch, commit and what happens
   next. Done when the push or PR is confirmed by GitHub. Same reference.

## Load-bearing rules

1. **Never guess which mod, or where it publishes.** Show the package folder, the kind and the
   destination and get a yes before the first edit. Package names and ids differ (`git-chip-mod`
   versus `/git-chip`).
2. **A folder's git is only its own if `git rev-parse --show-toplevel` is that folder.** A Hermes
   home or user home can itself be a git repo; without this check a commit lands in the wrong repo.
3. **The flow chart changes before the code does.** It's the agreement and ships in
   `docs/flow.mmd` and the README; changed behaviour with an unchanged chart is a lie.
4. **Keep the layout, keep the tests passing.** Same files in the same places. Every new branch of
   the chart gets a test. Never delete or weaken a test to make it pass unless the agreed chart
   says the old behaviour is gone.
5. **The mod may be live while you edit it.** Desktop plugins and TUI widgets hot-reload the live
   copy on save; a broken save shows up at once. Edit the package, test, then sync in one pass.
   Don't change the mod's on/off switch here; it's already on.
6. **Branch, commit message and PR-or-push are the user's call.** Propose a default with a reason,
   ask with `clarify`, and wait for an explicit choice every run.
7. **Never push to a protected branch, never force, never merge or approve.** `main` on
   `Lolman-bot/Hermes-Repository-` only takes reviewed PRs. If GitHub refuses, say what it said and
   stop. Never look for a way round a refusal.
8. **One open pull request per mod.** If this user already has one open on the mod, add to its
   branch and say that resets any approval. If someone else has one, stop and say who.
9. **Don't change how mods are built.** That's `/build-hermes-mod`; hand that kind of change to
   `/edit-skill`.
10. **Plain language with the user.** Jargon stays in the code.

## Pitfalls

- Editing the live copy (`$HERMES_HOME/desktop-plugins/...`, `hooks/...`) instead of the package
  leaves the package, tests and repo behind. Edit the package; sync to live.
- Gateway hook and Python plugin changes only load after `hermes gateway restart` / a new session.
- A plugin with a `desktop/plugin.js` half runs a **copy** in `desktop-plugins/<id>/`; after a sync,
  **Rescan** in Capabilities → Plugins, and `hermes plugins doctor <id>` warns if it's stale.
- `git add -A` in the wrong folder sweeps in unrelated files; add the mod's paths explicitly.

## Verification

- Chart, README chart and tests agree; tests and checks pass; README **Version** bumped.
- Live files match the package's `hermes-home/`; the user said yes.
- GitHub shows the commit on the agreed branch, and the PR link if one was raised.

## Reference files

Read the whole file you reach for; this table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/mod-kinds.md` | Per kind: files, live location, on/off, trial, tests. Same file as in `/build-hermes-mod`. |
| `references/find-the-mod.md` | Listing mod packages, confirming the folder, working out the destination, pre-flight, drift check, open-PR check. |
| `references/make-the-change.md` | Getting a specific change, when the chart changes first, editing within the layout, the version bump, tests, syncing to live, the user's check. |
| `references/republish.md` | The three choices and defaults, show-then-ask, the GitHub-API path to the Hermes repo, the git path for a mod's own repo, refusals, the report. |

The package layout and publishing rules come from `/build-hermes-mod`; if those change there, bring
`references/make-the-change.md`, `references/republish.md` and `references/mod-kinds.md` back in
line in the same pass.
