# Switching a mod on and off (step 6, and uninstall)

Do exactly what the mod's README **Switch on** / **Uninstall** says. The table is what that is per
kind, so you can tell when a README asks for something unusual (show it in the plan if it does).

## Per kind

| Kind | Switch on | Takes effect | Switch off |
|---|---|---|---|
| Desktop plugin | Nothing to run: the file inventories as off. The user flips it on in **Capabilities → Plugins**. | Live, no restart | The user flips it off (or you delete the folder; a removed plugin unloads) |
| TUI widget | Nothing to run. `/widgets-reload` in a running TUI must list it under `loaded:`; `/<id>` opens it. | Next TUI start, or `/widgets-reload` | Close it with `/<id>`, delete the file, `/widgets-reload` |
| Gateway hook | `hermes gateway restart` (placing the folder is the opt-in) | After the restart | Delete the folder, `hermes gateway restart` |
| Shell hook | Add the README's `hooks:` entry to `config.yaml` (rules below) | Next session, after the consent prompt | Remove that entry, `hermes hooks revoke <command>` |
| Python plugin | `hermes plugins enable <id>` | Next session (`/plugins` to confirm) | `hermes plugins disable <id>` |
| Skin | Note `hermes config get display.skin`, then `hermes config set display.skin <id>` | Within about a second, every surface | `hermes config set display.skin <the noted value>` (usually `default`) |

Gateway hooks: say before restarting that the messaging gateway will drop for a moment. If the user
doesn't run a gateway (`hermes gateway status`), say the hook will load the next time it starts.

## Editing `config.yaml`

Only for a step with no command (a shell hook's `hooks:` entry, or a README that asks for a key).

1. **Back it up first:**

   ```bash
   cp "$HERMES_HOME/config.yaml" "$HERMES_HOME/config.yaml.bak-$(date +%Y-%m-%d-%H%M)"
   ```

   Note the backup's path for the report.
2. **Read the whole file.** Add the mod's entry under the existing key (e.g. append to
   `hooks.<event>` if it exists, create it if not). If an identical entry is already there, don't
   add it twice.
3. **Touch nothing else.** Don't reorder keys, reformat the file or tidy other entries.
4. **Show the before and after** of that one block in the plan.

Use `hermes config set <dotted.key> <value>` instead whenever the change is a single scalar.

## Removing an entry

Remove only that mod's entry. If it leaves an empty list under `hooks.<event>`, remove that event
key too, but leave `hooks:` and every other event alone.

## The check afterwards

1. If `config.yaml` was touched, re-read it with `read_file`, then run `hermes config check` and
   `hermes config get <the key you changed>`. If either errors or the value isn't what you wrote,
   restore the backup at once and tell the user.
2. The mod shows as on (install) or off (uninstall): `hermes plugins list`, `hermes hooks list`,
   `hermes config get display.skin`, or ask the user to look at the desktop toggle.
3. Every other plugin, hook and setting that was there before still is.

Tell the user when it takes effect (now, next session, after the gateway restart).
