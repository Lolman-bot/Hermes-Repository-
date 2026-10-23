---
name: onboarding
description: "Use when a new starter sets up Hermes. One step at a time."
version: 1.1.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, onboarding, setup, new-starter, github]
    category: bitpool
    related_skills: [teacher, skills-catalogue, create-new-skill, edit-skill]
---

# Onboarding

Walks a brand-new Hermes user at Bitpool through getting fully set up, one step at a time, waiting
for them to confirm each step before the next. By the end they have a working model, GitHub signed
in, Eric asked to add them to the Bitpool skills repo, Git installed with a local clone of that
repo, the required skills installed, and they know which skills to reach for next. Purely conversational: it says what to run; the user runs it.

## When to Use

- The user types `/onboarding`.
- A new starter asks to get set up: "how do I get started with Hermes", "I'm new, how do I set this
  up", "walk me through onboarding".
- A hand-over from `/create-new-skill` or `/edit-skill` when the user has no usable clone of the
  skills repo, or Git isn't installed and signed in. Still run every step (rule 5); step 4 is the
  one that fixes their problem. At the close, tell them to run the skill they came from again.

Don't use for:

- Questions about what Hermes can do once someone is set up → `/teacher`.
- Just browsing which skills exist → `/skills-catalogue`.

## Procedure

Give **one step per message**, say exactly what to run or click, then wait for them to confirm
(a `clarify` with "Done" / "Stuck" choices works well). On "Stuck", help with that step only, using
the step's own troubleshooting line, then ask again. The command blocks are for the user to type in
their own terminal (PowerShell on Windows, Terminal on macOS/Linux).

1. **Hermes installed and set up.** If they're talking to you, Hermes is installed. Ask them to
   confirm they've run the setup wizard and picked a model:

   ```
   hermes setup
   ```

   If they're unsure which provider to choose, tell them to ask Eric which account Bitpool uses
   before entering a personal card. To change provider later: `hermes model`. Stuck → `hermes
   doctor` and read what it flags. Done when a normal chat gets a reply.
2. **Sign in to GitHub.** Bitpool's skills live in a GitHub repo, and Hermes uses the GitHub CLI's
   login to reach it. If `gh` isn't installed: Windows `winget install --id GitHub.cli`, macOS
   `brew install gh`, Linux see https://cli.github.com. Then:

   ```
   gh auth login
   ```

   Choose GitHub.com, HTTPS, and log in with a browser; create a GitHub account first if they don't
   have one. Done when `gh auth status` shows them logged in.
3. **Message Eric.** Tell them to send Eric their GitHub username so he can add them to the
   Bitpool skills repo, `Lolman-bot/Hermes-Repository-`. Then they must **accept the invitation**
   GitHub emails them (or the one at https://github.com/notifications). Done when they confirm
   they've messaged Eric — and, if the invite has already arrived, accepted it. If it hasn't
   arrived yet, carry on and come back to it.
4. **Install Git, sign it in, and clone the skills repo.** `/create-new-skill` and `/edit-skill`
   work in a copy of the repo on their own machine, and they won't run without one. Take it in
   three parts and wait after each:
   - **Install Git.** If `git --version` prints a version, it's already there. Otherwise, on
     Windows run `winget install --id Git.Git -e` (or install Git for Windows from
     https://git-scm.com/download/win with the default options), then open a new terminal. On a
     Mac, run `xcode-select --install`. Linux: the distro's package manager (`sudo apt install git`).
   - **Let Git use the GitHub sign-in from step 2**, so it can push later:

     ```
     gh auth setup-git
     ```

   - **Clone the repo** in a folder they choose (`Documents/GitHub` is a good default):

     ```
     git clone https://github.com/Lolman-bot/Hermes-Repository-.git
     ```

     Then check it: `git -C Hermes-Repository- remote get-url origin` must print
     `https://github.com/Lolman-bot/Hermes-Repository-.git`. A clone of the Claude plugin repo
     (`bitpool/ai-skills` or `ai-skills-beta`) won't work; clone fresh rather than repointing it.
     Publishing still needs Eric's invite from step 3 accepted, or the first push fails with 403.

   Done when they've confirmed all three parts.
5. **Install the required skills** straight from the Bitpool repo by full path (12 commands —
   paste them all at once). Skills sit in section folders, so the path includes
   `bitpool-required-skills/`:

   ```
   hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-required-skills/onboarding --category bitpool
   hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-required-skills/teacher --category bitpool
   hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-required-skills/skills-catalogue --category bitpool
   hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-required-skills/create-new-skill --category bitpool
   hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-required-skills/edit-skill --category bitpool
   hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-required-skills/skill-health --category bitpool
   hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-required-skills/log-skill-divergence --category bitpool
   hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-required-skills/update-hermes-skill --category bitpool
   hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-required-skills/user-config-store --category bitpool
   hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-required-skills/build-hermes-mod --category bitpool
   hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-required-skills/edit-mod --category bitpool
   hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-required-skills/install-mod --category bitpool
   ```

   Each install shows a security-scan panel and asks to confirm — that's expected for a company
   repo. Afterwards start a new conversation (or run `/reload-skills`). Stuck with "not found" or
   401 → the repo invite isn't accepted yet, or `gh auth login` didn't finish (back to steps 2-3).
   Done when `hermes skills list` shows them. Later, `hermes skills check` and `hermes skills
   update` keep them current.
6. **Optional: Discord.** Ask whether they want to talk to Hermes from Discord. If no, skip. If yes:
   they create a bot in the Discord Developer Portal (application → bot → turn on **Message Content
   Intent** → copy the bot token), then run:

   ```
   hermes gateway setup
   ```

   pick Discord, paste the token, and use the invite link it prints. `hermes gateway` starts it.
   Full steps: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord. Done when
   they confirm, or say they'll do it later.
7. **How a skill gets called.** Information, not a task — say it and carry straight on:
   type `/` and the skill's name (`/teacher`), optionally followed by what they want; or just ask in
   plain words and Hermes picks the matching skill. Works in the terminal, the desktop app and on
   Discord.
8. **Close out — where to go next.** Name all four, in this order, one plain line each:
   - `/teacher` — ask it anything about using or getting more out of Hermes day to day.
   - `/skills-catalogue` — see every Bitpool skill and mod available to install.
   - `/create-new-skill` — turn something they do repeatedly into a skill of their own, built through
     a plain-language interview and, once a reviewer approves it, published for everyone.
   - `/edit-skill` — change or retire a skill that already exists when it's wrong, out of date, or
     no longer needed.

   Say plainly that the last two are how skills get built and maintained here, and that they don't
   need to be able to code to use either.

## Load-bearing rules

1. **Always tell them to message Eric with their GitHub username, every single run.** Without it
   they never get added to `Lolman-bot/Hermes-Repository-`, can't install the Bitpool skills, and
   can't publish or change one. It's the step most easily glossed over as an aside.
2. **The close names all four skills, not a shortlist.** `/create-new-skill` and `/edit-skill` are
   the ones nobody discovers alone; a new starter who never hears them assumes skills are something
   other people make.
3. **One step at a time, and wait for them.** Never dump the whole checklist in one message. The
   one exception is step 7, which is an explanation — say it and go straight to the close.
4. **Never act on their behalf.** Don't run `terminal` commands, sign in, install skills, set up
   the gateway, install Git, clone the repo or send messages for them. You describe; they do it in their own terminal and
   accounts. Reading back output they paste is fine.
5. **Don't skip a step because they say it's already done.** Confirm quickly and move on, but every
   step is still said out loud — including the Eric message.
6. **Never ask for or accept a token or password in chat.** GitHub sign-in happens in their browser;
   the Discord bot token goes into `hermes gateway setup`, not into this conversation.

## Pitfalls

- **Unaccepted repo invite.** Eric adding them isn't enough; GitHub's invitation must be accepted
  before `hermes skills install` can see the repo. "Not found" almost always means this.
- **New skills not showing.** Skills installed mid-conversation need `/reload-skills` or a new
  conversation before their `/command` appears.
- **Profiles.** Skills install into the active profile. If they use a separate profile (e.g. for a
  Discord bot), they install there too (`hermes -p <name> skills install ...`).
- **Discord says nothing back.** In server channels the bot only answers when @mentioned; DMs
  always work. Unauthorised users are ignored — the setup wizard allow-lists the owner.

## Verification

- Every step 1-8 was said, in order, one per message (step 7 may share a message with step 8).
- The Eric message was said this run.
- The close named `/teacher`, `/skills-catalogue`, `/create-new-skill` and `/edit-skill`.
- No command was run on the user's behalf.
