# Mod kinds: layout, install location, switch on and off

A Bitpool "mod" is a Hermes extension. This file is the per-kind contract: which files make it,
where they live under `$HERMES_HOME`, how it is switched on and off, how to try it, and how to
test it. The same file ships in `/build-hermes-mod`, `/edit-mod` and `/install-mod`; keep the three
copies identical.

Checked against the Hermes docs (`user-guide/features/hooks.md`, `plugins.md`, `skins.md`,
`developer-guide/desktop-plugin-sdk.md`, `developer-guide/plugins/index.md`) and the bundled
`hermes-agent` skill's `references/desktop-plugins.md`, `tui-widgets.md`, `themes.md`. How each
kind works *inside* (SDK calls, hook payloads, skin keys) is not copied here: load the bundled
`hermes-agent` skill with `skill_view(name='hermes-agent')` and read its reference for the kind
before writing code. When this file and the Hermes docs disagree, the docs win; fix this file.

`$HERMES_HOME` is the active profile's home (`<root>/profiles/<name>/` under a named profile).
Desktop plugins are the exception: they are app-level and live in the **root** Hermes home, not a
profile's.

## Picking the kind

| The user wants... | Kind |
|---|---|
| A pane, status-bar chip, command-palette command, page, keybind or in-app toast in the **desktop app** | Desktop plugin |
| A live panel or modal tool in the **TUI** (`hermes --tui`) | TUI widget |
| Something to happen on a **messaging gateway** (Discord, Telegram, Slack...) event: an alert, a log line, a webhook | Gateway hook |
| To block, rewrite or react to tool calls / LLM turns / session start-end on **every surface**, in any language, with no Python plugin | Shell hook |
| New tools, `/commands`, `hermes <cli>` subcommands, or Python hooks on **CLI and gateway** | Python plugin (optionally with a `desktop/plugin.js` half) |
| A new look: colours, spinner, branding, on CLI, TUI and desktop at once | Skin |

A notification ("toast") maps by surface: desktop in-app = `host.notify` / OS = `ctx.os.notify`
(desktop plugin); messaging = gateway hook that posts a message; CLI/TUI = a plugin or shell hook
on the right event. If the user wants several surfaces, it is one mod with several parts; the
README's install section lists each.

## Mod folder in the repo

Every mod, whatever the kind, sits at `mods/<mod-name>/` in `Lolman-bot/Hermes-Repository-`:

```
mods/<mod-name>/
├── README.md        at-a-glance table, flow chart, install, uninstall, use, tests, privacy
├── docs/flow.mmd    the approved flow chart, exactly
├── hermes-home/     the installed files, at the same relative paths they take under $HERMES_HOME
└── tests/           the mod's tests
```

`hermes-home/` mirrors `$HERMES_HOME`, so installing is "copy each file under `hermes-home/` to
the same path under `$HERMES_HOME`, then do the switch-on step", and uninstalling is the reverse.
Nothing outside `hermes-home/` is installed.

## Desktop plugin

- **Files:** `hermes-home/desktop-plugins/<id>/plugin.js` — one plain-JS ESM file, no build step,
  no JSX syntax (use `jsx()` from `react/jsx-runtime`). Imports only `@hermes/plugin-sdk`, `react`,
  `react/jsx-runtime`. Folder name == plugin `id`. Template: the `hermes-agent` skill's
  `templates/plugin.js`.
- **Installed at:** `<root Hermes home>/desktop-plugins/<id>/plugin.js` (app-level, all profiles).
- **Loads:** the app watches the folder; it loads within seconds and hot-reloads on every save.
  Fallback: Cmd/Ctrl-K → **Reload desktop plugins**. A load failure shows a toast naming the error.
- **On / off:** **Capabilities → Plugins** toggle, live, no restart. With no user choice the
  plugin's `defaultEnabled` applies (default `true`). Bitpool mods ship `defaultEnabled: false`
  so placing the file never switches anything on by surprise; the user's toggle is the switch-on.
- **Try:** place the file, have the user flip it on, check, flip off if wrong.
- **Test:** export pure helpers as named exports from `plugin.js` and test them, plus
  `plugin.register(fakeCtx())`, with `node --test`. The SDK only exists inside the app, so the
  tests import it through the stub kit in `/build-hermes-mod`'s `assets/desktop-test-kit/`
  (copied into the mod's `tests/`):
  `node --import ./tests/register-sdk-stub.mjs --test "tests/*.test.mjs"`.
- **Uninstall:** toggle off, then delete `desktop-plugins/<id>/`.

## TUI widget

- **Files:** `hermes-home/tui-widgets/<id>.mjs` — default-exports `register(sdk)`; everything
  (`h`, `Box`, `Text`, `defineWidgetApp`...) comes from the `sdk` argument; no JSX, no imports.
  Template: the `hermes-agent` skill's `templates/clock.mjs`.
- **Installed at:** `$HERMES_HOME/tui-widgets/<id>.mjs`.
- **Loads:** at TUI start and hot-loads within about a second; `/widgets-reload` forces a rescan
  and lists the file under `loaded:`. The widget's `id` becomes the `/<id>` command.
- **On / off:** a placed widget is only a command until run. `/<id>` opens it, `/<id>` again
  closes an ambient one. Auto-open (`sdk.openWidget(...)` at the end of `register`) only if the
  user asked for it.
- **Try:** place the file, `/widgets-reload`, then `/<id>` in `hermes --tui`.
- **Test:** `node --test` with a fake `sdk` object passed to `register`, capturing the app given to
  `defineWidgetApp`; test `init`, `reduce` and pure helpers. No stub kit needed.
- **Uninstall:** close it, delete the `.mjs`, `/widgets-reload`.
- **Crash log:** `$HERMES_HOME/logs/tui_gateway_crash.log` if it never appears.

## Gateway hook

- **Files:** `hermes-home/hooks/<name>/HOOK.yaml` (`name`, `description`, non-empty `events` list,
  e.g. `agent:end`, `session:start`, `command:*`) and `hermes-home/hooks/<name>/handler.py` with a
  function named `handle(event_type, context)` (sync or async).
- **Installed at:** `$HERMES_HOME/hooks/<name>/`.
- **Runs:** in the messaging gateway only (never CLI, TUI, desktop or cron), loaded once at gateway
  start.
- **On / off:** trusted by placement. There is no enable list; placing both files is the
  switch-on, removing or renaming the folder (or `HOOK.yaml`) is the switch-off.
  `plugins.enabled` does not apply. Takes effect after `hermes gateway restart`.
- **Try:** the gateway has no one-session mode, so the try is: tests pass, place it, restart the
  gateway, trigger the event on the user's platform, with the rollback (move the folder out,
  restart) ready before you start.
- **Test:** `pytest` (or `python -m unittest`) calling `handle()` with a synthetic `context` for
  every event and branch. Read `$HERMES_HOME/logs/gateway.log` for `[hooks] Skipping ...` lines
  after the restart.
- **Uninstall:** delete the folder, `hermes gateway restart`.

## Shell hook

- **Files:** the script, `hermes-home/agent-hooks/<script>` (any language with a shebang), plus a
  `hooks:` snippet the README shows for `config.yaml`:
  `hooks: { <event>: [ { matcher?, command, timeout?, fail_closed? } ] }`. Events are the plugin-hook
  names (`pre_tool_call`, `post_tool_call`, `pre_llm_call`, `on_session_start`, ...).
- **Installed at:** `$HERMES_HOME/agent-hooks/<script>` and an entry under `hooks:` in
  `$HERMES_HOME/config.yaml`.
- **Runs:** CLI, gateway, desktop, TUI and dashboard chat, as a subprocess.
- **On / off:** the `config.yaml` entry, then a first-use consent prompt per (event, command)
  (allowlist `$HERMES_HOME/shell-hooks-allowlist.json`). Off: remove the entry and
  `hermes hooks revoke <command>`.
- **Try:** `hermes hooks test <event>` fires it on a synthetic payload; then one new session.
- **Test:** the script's own tests in `tests/`, plus `hermes hooks doctor` and
  `hermes hooks test <event>` after placing it.
- **Uninstall:** remove the `hooks:` entry (only that one), `hermes hooks revoke`, delete the script.

## Python plugin

- **Files:** `hermes-home/plugins/<name>/plugin.yaml` (`name`, `version`, `description`,
  `provides_tools`, `provides_hooks`) and `__init__.py` with `register(ctx)` (`ctx.register_tool`,
  `register_hook`, `register_command`, `register_cli_command`...). Optional `desktop/plugin.js`
  (a desktop half the app copies into `desktop-plugins/<id>/`) and `dashboard/` backend.
- **Installed at:** `$HERMES_HOME/plugins/<name>/`.
- **On / off:** opt-in. `hermes plugins enable <name>` / `hermes plugins disable <name>` (writes
  `plugins.enabled` / `plugins.disabled` in `config.yaml`). Loads in the next session; `/plugins`
  lists what is loaded. A desktop half has its own toggle in **Capabilities → Plugins**, also off
  by default.
- **Try:** `hermes plugins doctor <folder> --ci` (runs `register(ctx)` in a temporary
  `HERMES_HOME`), then enable it and open one new session. Or try it in a throwaway profile:
  `hermes profile create mod-trial --clone`, install there, `hermes -p mod-trial`, then
  `hermes profile delete mod-trial`.
- **Test:** `pytest` on the handlers, `hermes plugins doctor <folder> --ci`, and
  `hermes plugins validate <folder>` (the catalog admission check, incl. the security scan).
- **Uninstall:** `hermes plugins disable <name>`, then delete the folder (or
  `hermes plugins remove <name>`, which also clears it from the enable lists).

## Skin

- **Files:** `hermes-home/skins/<name>.yaml` — missing keys inherit from `default`. Template: the
  `hermes-agent` skill's `templates/skin.yaml`. Never name it after a built-in (`default`, `mono`,
  `slate`, `classic`...).
- **Installed at:** `$HERMES_HOME/skins/<name>.yaml`.
- **On / off:** `hermes config set display.skin <name>` (every surface repaints within about a
  second). Off: set it back to what it was before (note it first), usually `default`.
- **Try:** `/skin <name>` changes the current session only, a true one-session trial.
- **Test:** a test that parses the YAML and checks every key it sets is a known skin key and every
  colour is `#rrggbb`; then look at CLI, TUI and desktop.
- **Uninstall:** switch back to the previous skin first, then delete the file.

## Rules that hold for every kind

- Never write over an existing file under `$HERMES_HOME`; ask first and keep a dated `.bak-` copy.
- Change only the mod's own entries in `config.yaml` (`plugins.enabled`, `hooks:`,
  `display.skin`), with `hermes config set` / `hermes plugins enable` where one exists, never a
  hand-rewrite of the whole file.
- Colours come from theme variables / tones, never hardcoded, so mods survive skins.
- A mod runs with the user's full permissions. Nothing leaves the machine unless the flow chart
  says so and the README's Privacy section names it.
