---
name: build-hermes-mod
description: "Use when asked for a new Hermes mod. Charts, builds, PRs it."
version: 1.0.1
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, mods, desktop-plugins, tui-widgets, hooks, plugins, skins]
    category: bitpool
    related_skills: [edit-mod, install-mod, create-new-skill, build-skill-from-examples, edit-skill]
---

# Build Hermes Mod

Turns "here's the mod I want" into a working Hermes mod: a desktop plugin, TUI widget, gateway
hook, shell hook, Python plugin or skin, built in its own package folder with tests, a README and a
flow chart of everything it does, tried once, switched on, and published to `mods/<mod-name>/` in
`Lolman-bot/Hermes-Repository-` through a pull request.

## When to Use

- `/build-hermes-mod`, or the user asks for a new mod in their own words: "build me a mod that...",
  "I want a pane / status chip / TUI panel / toast that...", "alert me on Telegram when...",
  "make a skin that...".

Don't use for:
- Building a skill rather than a mod: `/create-new-skill` or `/build-skill-from-examples`.
- Changing a skill: `/edit-skill`.
- Fixing or changing a mod that already exists: `/edit-mod`.
- Installing a published mod: `/install-mod`.

## Prerequisites

- `terminal`, `read_file`, `write_file`, `patch`, `clarify`, `skill_view`.
- `node` for desktop plugins and TUI widgets, `python` for hooks, plugins and skins.
- `gh` signed in with write access to `Lolman-bot/Hermes-Repository-` for step 11 only.

## Procedure

Each step's output is the next step's input.

1. **Take the description.** The user says what they want in a sentence or two. Say it back in one
   sentence. Done when you've said it back and built nothing.
2. **Ask until the idea is clear** with `clarify`: what it shows or does, which surface (desktop,
   TUI, CLI, messaging), when it fires, what it remembers, commands, what it must never do, the
   name. Pick the kind from `references/mod-kinds.md`. Done when every row in
   `references/intake-and-flow-chart.md` has an answer and the kind is agreed.
3. **Draw the flow chart.** A Mermaid `flowchart TD` of the mod's full behaviour, shown and read back
   in plain words. Done when it passes the checks in `references/intake-and-flow-chart.md`.
4. **Get a yes.** If no, change it and go back to step 3. Done on an explicit yes; save it to
   `docs/flow.mmd` in the package folder.
5. **Build the package** at `$HERMES_HOME/mods/<mod-name>/`. Load the bundled `hermes-agent` skill
   (`skill_view(name='hermes-agent')`) and its reference for the kind first, then follow
   `references/mod-folder-layout.md`. Done when every file the layout lists for the kind exists.
6. **Write the tests and README.** One test per branch of the chart; README from
   `templates/mod-README.md`. Done when both exist and the README chart equals `docs/flow.mmd`.
7. **Run the tests and checks** for the kind (`references/test-try-and-switch-on.md`). If anything
   fails, back to step 5. Done when everything passes with nothing skipped.
8. **Try it once**, the kind's trial (`/skin` for one session, a desktop toggle, `hermes -p
   mod-trial`, ...). Tell the user what to look for, from the chart. Done when the user has tried it.
9. **Does it work the way you wanted?** If no, back to step 5, then 6, 7 and 8. Done on an explicit
   yes.
10. **Switch it on** the kind's way (`references/mod-kinds.md`), showing the exact change first.
    Done when the check in `references/test-try-and-switch-on.md` passes.
11. **Raise the pull request.** Show what goes up, ask "raise it now?", then branch
    `add-mod/<mod-name>` → `mods/<mod-name>/` → one PR to `main`
    (`references/publish-to-hermes-repo.md`). Done when the PR link exists, or the user said not now.
12. **Report:** the package folder, the live files and switch, the commands it adds, and the PR link
    with "live in the repo once an approver merges it".

## Load-bearing rules

1. **No code before the flow chart gets a yes.** The chart is the agreement; building before it is
   building a guess.
2. **The chart ships in `docs/flow.mmd` and the README, and matches the code.** A fix that changes
   behaviour updates the chart in the same pass, or the documentation lies.
3. **Every mod has tests and a README** with install, uninstall and the at-a-glance table. Nothing
   is switched on or pushed without both, and the kind's checks passing.
4. **The user tries it before it's switched on everywhere.** A broken plugin or hook gets in the way
   of every session; the trial comes first.
5. **Never overwrite or rewrite the user's setup.** Never write over an existing file under
   `$HERMES_HOME`; change only the mod's own `config.yaml` entry, through `hermes config set` /
   `hermes plugins enable` where one exists. A wrong edit can switch off their other extensions.
6. **One pull request per mod, asked for first, never a push to `main`.** `main` only changes
   through a reviewed PR. If GitHub refuses anything, say so and stop. Never force-push, merge or
   approve, and never look for a way round a refusal.
7. **Plain language with the user.** Events, panes and settings in everyday words; jargon stays in
   the code.

## Pitfalls

- Desktop plugins are app-level: they go in the **root** Hermes home's `desktop-plugins/`, not a
  profile's. Ship `defaultEnabled: false` so placing the file isn't the switch-on.
- Gateway hooks run only in the messaging gateway and load at gateway start; a hook for CLI or
  desktop needs a shell hook or plugin hook instead.
- Python plugins are inert until enabled; `/plugins` in a new session shows what actually loaded.
- No JSX syntax in `plugin.js` or `.mjs` widgets; they load uncompiled.
- Hardcoded colours break under other skins; use theme variables / tones.

## Verification

- `docs/flow.mmd` == the README's mermaid block; every branch has a test; the kind's checks pass.
- The switch-on check passes and the user has said yes after trying it.
- The PR (if raised) adds only `mods/<mod-name>/` and has a link.

## Reference files

Read the file itself; this table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/mod-kinds.md` | Per kind: files, install location under `$HERMES_HOME`, on/off switch, trial, tests, uninstall. Shared with `/edit-mod` and `/install-mod`. |
| `references/intake-and-flow-chart.md` | The intake questions, naming, drawing and checking the Mermaid chart, getting the yes. |
| `references/mod-folder-layout.md` | The package folder (`README.md`, `docs/`, `hermes-home/`, `tests/`) and what each file holds per kind. |
| `references/test-try-and-switch-on.md` | Running the tests and Hermes checks per kind, the one-time trial, the switch-on edit and its check. |
| `references/publish-to-hermes-repo.md` | Pre-flight, what goes up, the branch + single commit + PR through `gh`, refusals. |
| `templates/mod-README.md` | The README every mod ships with. |
| `assets/desktop-test-kit/` | Byte-exact Node stub kit so `plugin.js` can be tested with `node --test` outside the desktop app. |

How each kind works inside belongs to the bundled `hermes-agent` skill and changes with Hermes
releases; don't copy it here. To change where mods publish, edit
`references/publish-to-hermes-repo.md` and rule 6 together, and bring `/edit-mod` in line.
