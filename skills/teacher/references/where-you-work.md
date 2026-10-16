# Where you work — terminal, desktop, dashboard, chat apps

**Snapshot: 2026-10-16**, built from the Hermes Agent docs
(https://hermes-agent.nousresearch.com/docs/). Hermes changes quickly. If something isn't covered
here, that does **not** prove Hermes can't do it — only that this snapshot doesn't say. Point at the
docs rather than guessing.

Lead with this:

> It's one agent with several front doors. Same settings, same skills, same memory, same saved
> conversations — you can start in one and pick it up in another.

If they genuinely don't know, **start with the desktop app** (if it's installed) or **`hermes --tui`**
in a terminal. Both are the everyday choice.

| Front door | Start it with | Best for |
|---|---|---|
| **Desktop app** | the Hermes app, or `hermes desktop` | Everyday chat with a proper window — file browser, tabs, settings panes, live view of subagents. macOS, Windows, Linux. |
| **TUI** (modern terminal UI) | `hermes --tui` | The recommended terminal experience: overlays, mouse selection, type while it works. |
| **Classic CLI** | `hermes` | The original terminal interface; same commands and sessions. |
| **Web dashboard** | `hermes dashboard` | Settings, API keys, sessions, logs, scheduled jobs, skills and MCP in a browser on your own machine (`http://127.0.0.1:9119`). Has an optional chat tab. |
| **Messaging (gateway)** | `hermes gateway setup`, then `hermes gateway` | Talk to Hermes from Discord, Telegram, Slack, Teams, WhatsApp, email and more — with full tools, not just chat. |
| **Editor (ACP)** | `hermes acp` | Using Hermes inside an editor such as VS Code, Zed or JetBrains. |

## Worth saying unprompted

- **Skills follow you.** Every installed skill is a `/command` in the terminal, the desktop app and
  on Discord (where they appear in Discord's own `/` menu after the gateway restarts).
- **Resuming:** `hermes --continue` (or `hermes -c`) picks up the last terminal conversation;
  `hermes --tui -c` does it in the TUI.
- **Profiles are separate.** A conversation saved in one profile isn't visible from another
  (`references/profiles-plugins-and-mods.md`).
- **On chat apps the conversation doesn't end by itself.** Use `/new` at natural breaks.
- **In a Discord server channel** Hermes answers only when @mentioned, unless the channel is set as
  free-response; in DMs it answers everything.

## Where this hands over

- Setting up from scratch → `/onboarding`.
- Connecting Discord or another chat app → `references/connecting-things.md`.
