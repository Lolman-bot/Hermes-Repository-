# Test, try and switch on (steps 7 to 10)

Run everything from the package folder, `$HERMES_HOME/mods/<mod-name>/`, with `terminal`. Note
`hermes --version` (first line): it goes in the README's at-a-glance table.

## Step 7 — tests and checks

| Kind | Must pass |
|---|---|
| Desktop plugin | `node --import ./tests/register-sdk-stub.mjs --test "tests/*.test.mjs"` |
| TUI widget | `node --test "tests/*.test.mjs"` |
| Gateway hook | `python -m pytest tests`; `HOOK.yaml` parses with a non-empty `events` list of real gateway events |
| Shell hook | the script's tests; after placing it (step 8): `hermes hooks doctor` and `hermes hooks test <event>` |
| Python plugin | `python -m pytest tests`; `hermes plugins doctor hermes-home/plugins/<id> --ci`; `hermes plugins validate hermes-home/plugins/<id>` |
| Skin | `python -m pytest tests` |

If `pytest` isn't installed, write the tests with `unittest` and run `python -m unittest discover
tests`; don't install packages without asking. If anything fails, read the whole output, fix the
cause in the mod (not in the test, unless the test disagrees with the agreed chart), and run all of
it again. Don't move on with a failing or skipped test. Show the user the final passing output, in
short.

## Step 8 — the trial

Place the files for the trial only (copy from `hermes-home/` to the same paths under
`$HERMES_HOME`, never over an existing file), then give the user the one thing to do and, from the
chart, what should appear, what to type and what should happen. List each command to try.

| Kind | Trial | Back out |
|---|---|---|
| Desktop plugin | Copy to `<root Hermes home>/desktop-plugins/<id>/`; it inventories as off (`defaultEnabled: false`). The user flips it on in **Capabilities → Plugins**. | Flip it off. |
| TUI widget | Copy to `tui-widgets/`, run `/widgets-reload` (must list it under `loaded:`), then `/<id>` in `hermes --tui`. | `/<id>` to close; delete the file. |
| Gateway hook | No one-session mode. Copy to `hooks/<id>/`, `hermes gateway restart`, trigger the event on the user's platform. Check `logs/gateway.log` for a `[hooks] Skipping` line. | Move the folder out of `hooks/`, `hermes gateway restart`. |
| Shell hook | Copy the script, add the `hooks:` entry (step 10's rules), `hermes hooks test <event>`, then one new session; approve the consent prompt. | Remove the entry, `hermes hooks revoke <command>`. |
| Python plugin | Throwaway profile: `hermes profile create mod-trial --clone`, copy into `<root>/profiles/mod-trial/plugins/<id>/`, `hermes -p mod-trial plugins enable <id>`, then `hermes -p mod-trial` and `/plugins`. | `hermes profile delete mod-trial`. |
| Skin | Copy to `skins/<id>.yaml`, then `/skin <id>` (this session only). | `/skin <previous>`. |

Tell the user plainly whether the trial is visible anywhere else (the desktop toggle and a gateway
hook are; the rest are not).

## Step 9 — the answer

Ask: "Does it work the way you wanted?" If not, ask what was wrong or missing, fix it (step 5),
update the chart if behaviour changed, re-copy the changed files over the trial copies, then run
step 7 and step 8 again. Only an explicit yes moves on.

## Step 10 — switch it on

Show the exact change first, then make it:

| Kind | Switch on |
|---|---|
| Desktop plugin | Already placed; it stays on if the user left the toggle on. Confirm it shows as enabled. |
| TUI widget | Already placed (`/<id>` works in every TUI session). Auto-open only if agreed in step 2. |
| Gateway hook | Already placed and loaded after the restart. |
| Shell hook | The `hooks:` entry, already added in the trial. |
| Python plugin | Copy into the user's own `$HERMES_HOME/plugins/<id>/`, `hermes plugins enable <id>`, delete the trial profile. |
| Skin | Note the current `display.skin` (`hermes config get display.skin`), then `hermes config set display.skin <id>`. |

Rules for `config.yaml` (shell hooks; anything else a mod needs): read it first, keep a dated copy
(`config.yaml.bak-<yyyy-mm-dd-hhmm>`), add only the mod's entry under the existing key, never
reorder or reformat other keys, and re-read afterwards. Use `hermes config set` /
`hermes plugins enable` instead of a hand edit wherever one exists.

**The check:** the live files match `hermes-home/` (compare with `cmp` or a hash), the switch shows
the mod on (`hermes plugins list`, `/plugins`, `hermes hooks list`, the desktop toggle,
`display.skin`), and every other plugin, hook and setting is as it was. Then tell the user when it
takes effect (now / next session / after the gateway restart).
