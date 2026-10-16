---
name: install-mod
description: "Use when installing or removing a Bitpool Hermes mod."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, mods, install, desktop-plugins, tui-widgets, hooks, plugins, skins]
    category: bitpool
    related_skills: [build-hermes-mod, edit-mod, onboarding]
---

# Install Mod

Puts a mod from `mods/` in `Lolman-bot/Hermes-Repository-` onto this machine, ready to use, or
takes one off again. The package lands in `$HERMES_HOME/mods/<mod-name>/` as the record of what was
installed, its `hermes-home/` files go to their live places, the mod's README install steps switch
it on, and the user gets a short report of what changed and what's left to do by hand.

## When to Use

- `/install-mod`, or the user asks to install, set up, list, remove or uninstall a mod: "install
  the git-chip mod", "what mods can I install?", "uninstall the telegram-alert mod".

Don't use for:
- Building a new mod: `/build-hermes-mod`.
- Fixing or changing a mod: `/edit-mod`.
- Installing a skill (`hermes skills install ...`) or a third-party plugin from the Hermes catalog
  (`hermes plugins install ...`).

## Prerequisites

- `terminal`, `read_file`, `clarify`; `git` to fetch the repo.
- Read access to `Lolman-bot/Hermes-Repository-` (`/onboarding` covers getting it).

## Procedure

Each step's output is the next step's input.

1. **Install or uninstall?** Take it from the request; if unclear, ask with `clarify`. Uninstall
   follows `references/uninstall.md` from here. Done when the direction is known.
2. **Fetch approved `main` into a temp folder**: a shallow, sparse checkout of `mods/` only, never
   the user's own clone. Done when `mods/` is listed. `references/find-and-fetch.md`.
3. **Which mod?** Match the user's name against `mods/` (with or without `-mod`, any case). No name
   or no single match: list every mod with its kind and first README sentence and ask with
   `clarify`. Done on one confirmed mod. Same reference.
4. **Read the mod's README in full** and pull out the at-a-glance table, **Install**, **Uninstall**
   and **Use**. No Install section → stop and say so; don't guess. Done when every install step is
   listed. Same reference.
5. **Show the plan and wait for a yes**: each file and where it goes under `$HERMES_HOME`, any file
   it would replace, the exact switch-on change (before → after), and any other README step. Done
   on an explicit yes.
6. **Install**: copy the package to `$HERMES_HOME/mods/<mod-name>/`, copy each `hermes-home/` file
   to its live place, then do the switch-on step for the kind. Done when every step ran.
   `references/switch-on-and-off.md`.
7. **Check it**: live files match the package, the switch shows the mod on, `config.yaml` (if
   touched) re-reads cleanly with every other entry intact. Then delete the temp folder. Done when
   all checks pass.
8. **Report**: which mod and version, where each file went, the switch before and after, backups
   made, when it takes effect, how to use it (the README's **Use**), and anything left to do by hand.

## Load-bearing rules

1. **Follow the mod's own install steps.** Its README is the authority; this skill carries them
   out, it doesn't invent its own. A step that does more than install the mod (sends data
   somewhere, changes unrelated settings, downloads from elsewhere) is left out and listed in the
   report for the user to decide.
2. **Never change anything in the repo.** Don't edit, check out, pull or fetch in a user's clone of
   the Hermes repo; read from a throwaway temp copy. The clone may hold unfinished work.
3. **Install from `main` only.** That's the reviewed version. A branch may hold unreviewed changes.
4. **Back up before touching, and change only the mod's own entry.** A dated `.bak-` copy of any
   file replaced and of `config.yaml` before an edit; every other plugin, hook, skin and key stays
   as it was. Prefer `hermes plugins enable` / `hermes config set` to hand edits.
5. **Show every change first and wait for a clear yes.** Silence or "probably" is not a yes.
6. **Never overwrite without asking.** An existing `$HERMES_HOME/mods/<mod-name>/` or live file may
   be the user's own edited copy.
7. **Uninstall puts things back as they were.** Switch off, remove only the files the README's
   **Installs** lists, and ask before deleting the package.
8. **Never report success without checking.** Say it's installed only after the checks in step 7.

## Pitfalls

- Desktop plugins go in the **root** Hermes home's `desktop-plugins/`, not a profile's, and Bitpool
  mods ship them off: the user flips them on in **Capabilities → Plugins**.
- Python plugins stay inert until `hermes plugins enable <id>`; gateway hooks until
  `hermes gateway restart`; shell hooks ask for consent on first use.
- A mod's README written for an older Hermes may name a command that's gone. If a command fails as
  unknown, stop and report it; don't substitute a guess.

## Verification

- Every path in the README's **Installs** exists live and matches the package byte for byte.
- The switch shows the mod on (`hermes plugins list`, `hermes hooks list`, `/widgets-reload`
  output, the desktop toggle, `hermes config get display.skin`).
- Temp folder gone; backups listed in the report.

## Reference files

Read the file itself; this table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/mod-kinds.md` | Per kind: files, live location, on/off switch, uninstall. Same file as in `/build-hermes-mod`. |
| `references/find-and-fetch.md` | Fetching `main` into a temp folder, listing mods, matching a name, reading the README, copying the package and live files. |
| `references/switch-on-and-off.md` | The switch-on and switch-off step per kind, `config.yaml` backup and edit rules, and the check afterwards. |
| `references/uninstall.md` | Taking a mod off: finding it, the plan, switching off, removing files, the package question, check, report. |

How each mod installs lives in that mod's README in `mods/<mod-name>/`; change it there. The
per-kind switches are shared with `/build-hermes-mod`; if they change, update
`references/mod-kinds.md` and `references/switch-on-and-off.md` here in the same pass.
