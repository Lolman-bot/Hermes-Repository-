# Profiles, plugins and mods

**Snapshot: 2026-10-16**, built from the Hermes Agent docs
(https://hermes-agent.nousresearch.com/docs/). Hermes changes quickly. If something isn't covered
here, that does **not** prove Hermes can't do it — only that this snapshot doesn't say. Point at the
docs rather than guessing.

## "What's a profile?"

> A profile is a completely separate Hermes — its own settings, API keys, memory, skills, saved
> conversations and scheduled jobs.

- `hermes profile create <name>` makes one, and it becomes its own command (`<name> chat`,
  `<name> setup`). `hermes -p <name>` runs any command against it; `hermes profile list` shows them.
- Use one for a separate role — a work bot on Discord, a research agent — so their memories don't mix.
- **Never run two agents on the same profile at once** — they'd write over each other's memory.
- Skills install per profile, so a new profile needs the Bitpool skills installed again.

## "What's a plugin?"

In Hermes a plugin is **code** that adds tools or hooks — not a bundle of skills like a Claude
plugin. Plugins are off until switched on: `hermes plugins` to toggle, `/plugins` in a chat to list.
Only enable plugins you trust; they run code on your machine.

## "What's a mod?"

At Bitpool a **mod** is an add-on that changes how Hermes looks or behaves, kept in the repo's
`mods/` folder:

| Kind | What it does |
|---|---|
| Desktop plugin | Adds a pane, widget or command to the desktop app. |
| TUI widget | Adds a live panel to the terminal UI. |
| Gateway hook | Runs a small script when something happens on Discord/Telegram etc. (e.g. alert on a long task). |
| Skin | Changes colours and branding of the terminal and app. |

- `/build-hermes-mod` builds one from a plain description, with tests and a README.
- `/install-mod` installs (or removes) one from the repo, showing every change first.
- `/edit-mod` changes one you already have.

## Where this hands over

- Which mods exist → `/skills-catalogue`.
- Building one → `/build-hermes-mod`, on a yes.
