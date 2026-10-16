# Uninstalling a mod

No fetch from GitHub is needed: the record of what was installed is the package at
`$HERMES_HOME/mods/<mod-name>/`.

## 1. Find it

List `$HERMES_HOME/mods/*/` and match the user's name against the folder names, with or without the
`-mod` ending. If there's no clear single match, show the list and ask with `clarify`. If there's
no package but a live extension with that id exists (`desktop-plugins/<id>/`, `hooks/<id>/`,
`plugins/<id>/`, `tui-widgets/<id>.mjs`, `skins/<id>.yaml`), say it wasn't installed by this skill,
show what's there, and ask before touching it.

Read the package README's **Installs**, **Switch on** and **Uninstall**.

## 2. Show the plan and wait for a yes

- The switch-off step and its before → after (`switch-on-and-off.md`).
- Each live file or folder from **Installs** that will be removed. If a live file differs from the
  package copy, say so: the user may have edited it. Offer to keep a `.bak-` copy.
- The package folder, and the question: **Keep it** (the safe default; `/install-mod` can switch it
  back on) or **Delete it**. Deleting moves it to the Recycle Bin / Trash where the platform allows;
  never a permanent delete.
- Anything the README's **Uninstall** asks for beyond that.

## 3. Do it

Switch off first (back up `config.yaml` if it's touched), then remove the live files, then deal
with the package as the user chose.

## 4. Check it

Run the check in `switch-on-and-off.md`: the mod shows as off, every **Installs** path is gone,
every other plugin, hook and setting still there.

## 5. Report

Which mod was removed, the switch before and after, backups made, what happened to the package, and
what may need a restart before it disappears (the gateway for a hook; a new session for a plugin or
shell hook).
