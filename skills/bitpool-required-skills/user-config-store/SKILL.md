---
name: user-config-store
description: "Use when a skill needs a per-user value. Ask once, store it."
version: 1.0.1
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, config, preferences, onedrive, per-user]
    category: bitpool
    related_skills: [log-skill-divergence, create-new-skill, edit-skill]
---

# user-config-store

Remembers a value that's specific to the person running a skill (a repo checkout path, a browser
profile name, a display name, a personal preference) so the skill asks for it once and never
hardcodes one person's layout for everyone. Each skill gets one small `<skill-name>.md` file of
`- key: value` lines. It lives on the person's OneDrive when that's present, so it follows them
across machines, and under `$HERMES_HOME/bitpool-config/` when it isn't.

## When to Use

- A skill is about to hardcode a path, profile or setting that differs per person.
- A skill is about to ask the user for something they already told it in an earlier session.
- The user runs `/user-config-store` to view, set or clear a stored value.

Don't use for:
- **Secrets** (passwords, API keys, tokens, connection strings, OAuth files). Decline and point
  to Hermes's credential handling: `required_environment_variables` (values land in
  `$HERMES_HOME/.env`, set with `hermes config set NAME value` or `hermes setup`) or
  `required_credential_files`.
- **Facts about the user** that should shape every turn (name, role, working style). That's the
  `memory` tool: injected into every session. This store is read on demand, by one skill, for one
  value.
- **Settings a skill author can declare up front** for this machine only. Prefer the skill's own
  `metadata.hermes.config` entry (stored in `config.yaml` under `skills.config.*`, injected when
  the skill loads). Use this store when the value is discovered at run time or should follow the
  person across machines.
- General note-taking or documentation.

## Prerequisites

`python` (stdlib only) for the bundled helper. OneDrive is optional.

## Procedure

The helper resolves the location fresh every call and prints one JSON object:
`python ${HERMES_SKILL_DIR}/scripts/user_config.py <path|get|set|unset> <skill> [key] [value]`.
Run it with `terminal`.

1. **Resolve the file.** Run `path <skill>`. Done when you know the `write_target` and whether
   OneDrive was found (`onedrive_found`).
2. **Look the value up.** Run `get <skill> <key>`. It reads OneDrive first, then the
   `$HERMES_HOME` fallback. Done when you have the value (exit 0, use it without asking) or
   `found: false` (exit 1).
3. **Ask once if missing.** Use `clarify` to ask for the value, saying once that it will be
   remembered so they won't be asked again. Refuse and stop if the value is a secret. Done when
   you have a non-secret, single-line value.
4. **Write it.** Run `set <skill> <key> "<value>"`. If it returns `refused: exists`, show the
   current and new value with `clarify` and only re-run with `--overwrite` on an explicit yes.
   Done when `set` returns `ok: true` with the value read back.
5. **Hand the value back** to the calling skill, or to the user if they invoked
   `/user-config-store` directly. If the value came from the fallback while OneDrive is now
   present (`in_write_target: false`), offer to copy it to OneDrive with `set`.

## Load-bearing rules

1. **Never store secrets.** Plain markdown on a synced drive, no encryption. The helper refuses
   secret-looking keys, but the rule is yours to enforce on values too.
2. **Never hardcode the location.** OneDrive folder names contain the org and the username;
   `$HERMES_HOME` differs per OS and per profile. Always go through the helper or the rules in
   `references/config-file-pattern.md`.
3. **One file per skill, named exactly after the Hermes skill** (`build-hermes-mod.md`, not the
   old Claude name), so any skill can find its file without a lookup table.
4. **Ask before writing a new value or changing an existing one.** A silent overwrite produces a
   confusing failure elsewhere with no visible cause.
5. **Create the folder and file on first use.** Zero setup burden; the helper does it.

## Pitfalls

- **The OneDrive `skill-config/` folder is shared with the Claude counterparts of these skills.**
  Keep the format compatible: `- key: value` lines, UTF-8. Files written by hand or PowerShell
  may have a BOM or bare `key: value` lines; the helper reads both and normalises on write.
- **The fallback is per Hermes profile and per machine.** `$HERMES_HOME` changes with the active
  profile, so a value stored without OneDrive won't appear in another profile or on another PC.
- **Messaging gateways:** the store is on the machine running Hermes, not the chat user's device.
  On a shared gateway host, don't store per-person values for different people under one skill
  file.
- **Don't round-trip the file through Windows PowerShell** (`Get-Content`/`Set-Content` mangle
  UTF-8 and add a BOM). Use the helper or `write_file`.

## Verification

- `get <skill> <key>` returns the value just written, from the expected `location`.
- The file contains no secret-looking keys or values.

## Reference files

| File | Covers |
|---|---|
| `references/config-file-pattern.md` | Location resolution order on Windows/macOS/Linux, file format, ask-once algorithm, store-vs-memory-vs-config.yaml-vs-.env table, worked example, and the snippet other skills copy. |
| `scripts/user_config.py` | Stdlib helper: `path`, `get`, `set` (refuses silent overwrite and secret-looking keys), `unset`. |
