# Environment setup: WSL Ubuntu + Python

`send-via-graph.py` runs in **WSL Ubuntu**, not native Windows Python — the same
reason every WSL-dependent skill in this repo works this way (see `transcribe-video`,
`docx-to-md`, `pdf-to-md`): the native Windows `python`/`python3` here are the broken
Microsoft Store stubs.

Check readiness in order, tier by tier. **Stop at the first tier that fails** and hand
that step to the user — don't skip ahead and don't attempt a later tier's check while
an earlier one is broken. Re-run from tier 1 after any fix, since a WSL install can
change what later tiers see.

## Tier 1 — Is WSL itself installed?

```bash
wsl.exe --status
```

If this errors, or says WSL isn't installed/enabled — **stop. This is a Windows
feature change, and the agent must never make it.** Enabling WSL can require a restart
and always requires elevation. Tell the user:

> WSL isn't installed on this machine yet. Open a terminal yourself (PowerShell or
> Command Prompt) and run:
> ```powershell
> wsl --install -d Ubuntu
> ```
> This needs admin rights and may ask you to restart. Once it's done, come back and
> we'll continue.

Don't attempt this yourself even with elevation available — it's a system-level
change (see Bitpool's operating rules around modifying system settings) and the
next tier needs the user's own hands anyway (see below).

## Tier 2 — Is the standard Ubuntu distro installed?

```bash
wsl.exe -l -v
```

Look for a distro literally named `Ubuntu` (not `Ubuntu-22.04` or similar — this
skill standardises on plain `Ubuntu`, matching `wsl --install -d Ubuntu`'s default).
If it's missing, same hand-off as Tier 1 — the command above installs both the WSL
feature and the Ubuntu distro in one shot if neither exists yet, so a user who hit
Tier 1 doesn't need a separate step here.

## Tier 3 — Has the Ubuntu user account actually been created?

The **first ever launch** of a fresh Ubuntu distro prompts interactively for a UNIX
username and password, right there in the terminal window. **The agent cannot do this
step, ever** — it's a live interactive prompt for credentials the user creates, and
entering a password on someone's behalf is out of bounds regardless of context.

```bash
wsl.exe -d Ubuntu -- whoami
```

If this hangs, errors, or never returns a normal username, tell the user:

> Ubuntu is installed but hasn't been set up yet. Open **Ubuntu** from the Start
> Menu, and when it asks you to create a UNIX username and password, go ahead and set
> those yourself — Hermes won't and can't do this part. Once you're sitting at a
> Linux shell prompt, come back and we'll continue.

## Tier 4 — Is the toolchain (python3 + `requests`) ready?

This is the one tier the agent *can* mostly do itself. Unlike `transcribe-video` (which
needs a dedicated venv because `whisper-ctranslate2` isn't packaged for Ubuntu),
`send-via-graph.py` only needs `requests` — and Ubuntu ships that as a normal `apt`
package (`python3-requests`), which installs straight into system Python without
tripping PEP 668's externally-managed-environment guard. No venv needed here.

Check:

```bash
wsl.exe -d Ubuntu bash -lc 'python3 -c "import requests" && echo OK || echo MISSING'
```

If it prints `MISSING` — installing it needs `sudo`, which means an interactive
password prompt. **Same rule as every other tier that needs `sudo` or a credential:
hand it to the user, don't run it yourself.**

> The Python toolchain isn't set up in WSL yet. Paste this into a terminal, then tell
> me when it's done:
> ```powershell
> wsl -d Ubuntu -- bash -lc 'sudo apt-get update && sudo apt-get install -y python3-requests && echo DONE'
> ```

After they confirm it printed `DONE`, re-run the Tier 4 check and proceed. (Verified
2026-07-29: this is genuinely how `requests` got onto the machine every real send in
this skill's development was tested against — not a venv, which was never actually
built despite an earlier draft of this doc describing one.)

## Once all four tiers pass

Run the script with the system `python3` directly — no venv, no special interpreter
path:

```bash
wsl -e bash -lc 'python3 -u /mnt/c/path/to/send-via-graph.py --check-only --subject "..." --html-file "..." --to "..."'
```

### Path translation (Windows → WSL)

Same as every other WSL-dependent skill in this repo: `C:\Users\<you>\...` →
`/mnt/c/Users/<you>/...` (lowercase the drive letter, forward slashes, quote the
whole path if it has spaces).

## Why this whole tiered structure exists

Every tier above Tier 4 either changes a system-wide Windows feature or requires
entering a password interactively — both are things this skill (and this project's
broader operating rules) keep strictly on the user's side. The agent's job is to
**detect exactly which tier is blocking**, hand over the smallest possible next step
with a copy-paste command, and pick back up automatically once it's done — never to
find a workaround that routes around the user having to do it themselves.
