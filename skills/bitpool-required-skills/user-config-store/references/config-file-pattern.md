# Config file pattern

## Where the file lives

Resolved fresh on every call, never hardcoded. `scripts/user_config.py` implements exactly this
order; the first match is the **write target**, and reads check every location in order.

| Order | Location | When it resolves |
|---|---|---|
| 1 | `<OneDrive root>/skill-config/<skill>.md` | Windows: `OneDriveCommercial` env var, then `OneDrive`. macOS: exactly one `~/Library/CloudStorage/OneDrive-*` folder (shared-library folders excluded; one containing "Bitpool" wins if there are several). |
| 2 | `$HERMES_HOME/bitpool-config/<skill>.md` | Always available. `HERMES_HOME` defaults to `%LOCALAPPDATA%\hermes` on Windows and `.hermes` in the home directory on macOS/Linux, and points at the profile's home when a profile is active. |

Why OneDrive stays first: it syncs the person's values across all their machines and is the same
folder the Claude versions of these skills already use, so a value set once works in both. Linux
has no official OneDrive client, so Linux installs normally use the fallback.

If the macOS check finds several OneDrive folders and none is obviously Bitpool's, the helper
falls back to `$HERMES_HOME`. Tell the user; don't guess a folder.

## File format

```markdown
# <skill-name> — stored user values

<!-- Written by user-config-store. Never store secrets, passwords, or credentials here. -->

- <key>: <value>
```

Plain `- key: value` lines under one heading, UTF-8 without BOM, one value per line. Keys are
`[A-Za-z0-9_.-]`, lowercase snake_case by convention (`repo_path`, `edge_profile_directory`). A
file can hold several keys.

## The ask-once-then-remember flow

1. `python ${HERMES_SKILL_DIR}/scripts/user_config.py get <skill> <key>`
2. Found: use the value, don't ask.
3. Missing: ask with `clarify`, explaining once that it will be remembered. Then
   `set <skill> <key> "<value>"`.
4. A value needs to change: `set` refuses with `refused: exists`. Confirm the new value with the
   user, then re-run with `--overwrite`. Never overwrite silently.
5. To forget a value: `unset <skill> <key>` (removes it from every location).

When another skill calls this pattern, `${HERMES_SKILL_DIR}` is *that* skill's folder. Load
`user-config-store` with `skill_view` first and use the `[Skill directory: ...]` it reports, or
follow the format above with `read_file` / `write_file` directly.

## Which store?

| Need | Use |
|---|---|
| A per-person value one skill reads on demand, discovered at run time, should follow the person | **This store** |
| A fact about the user that should shape every conversation | `memory` tool |
| A machine-level setting the skill author can declare up front | `metadata.hermes.config` → `config.yaml` `skills.config.*` |
| An API key, token or password | `required_environment_variables` → `$HERMES_HOME/.env` (`hermes config set NAME value`) |
| An OAuth token / credential *file* | `required_credential_files` (relative to `$HERMES_HOME`) |

## Worked example: a repo clone path

A skill that publishes to `Lolman-bot/Hermes-Repository-` needs the person's local clone:

- `get create-new-skill clone_path`. Found: `cd` there and carry on.
- Missing: ask "Where is your clone of Lolman-bot/Hermes-Repository-? (I'll remember it.)",
  check the path exists and is that repo (`git -C <path> remote -v`), then
  `set create-new-skill clone_path "<path>"`.

## Snippet for another skill's `SKILL.md`

> **Remember `<key>` instead of asking every time.** Before asking the user for `<value
> description>`, load `user-config-store` with `skill_view` and run its helper:
> `python <its skill dir>/scripts/user_config.py get <this-skill-name> <key>`. If found, use it.
> If not, ask once with `clarify`, say it'll be remembered, and `set` it. Never store secrets
> this way.
