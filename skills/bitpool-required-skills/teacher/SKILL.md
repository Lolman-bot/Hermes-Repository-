---
name: teacher
description: "Use when someone asks how Hermes works. Plain answers."
version: 1.0.1
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, learning, hermes, onboarding, help]
    category: bitpool
    related_skills: [onboarding, skills-catalogue, create-new-skill, edit-skill, skill-health, build-skill-from-examples, build-hermes-mod, install-mod, user-config-store]
---

# Teacher

Explains how Hermes works at Bitpool, in plain words, to whoever asks — from "what can this thing
actually do" through to publishing a skill of their own. Someone finishes a run knowing the answer to
the question they actually had, and what they can do with it next. It answers only from the dated
snapshots in `references/`; it never looks anything up live.

## When to Use

- The user types `/teacher`, with or without a question after it.
- Someone asks a learning question about Hermes itself: "what can Hermes actually do", "how is this
  different from ChatGPT", "CLI, TUI, desktop or Discord — which do I use?", "does it remember me",
  "what happens in a really long chat", "which model should I pick", "what's a skill", "how do I
  install one", "how do I make my own skill", "can it run something every morning", "what's a
  subagent", "what's MCP", "can it use my browser", "what's a profile", "what's a mod".

Don't use for:

- Listing which skills exist → `/skills-catalogue`.
- Building a skill → `/create-new-skill` (or `/build-skill-from-examples`); changing one →
  `/edit-skill`; grading one → `/skill-health`.
- New-starter setup → `/onboarding`.
- Questions about a Bitpool product rather than about Hermes.

## Procedure

1. **Find out what they want to know.** If they typed `/teacher` with nothing after it, ask one
   short question — "What would you like to know about Hermes, or about skills?" — and wait. No
   menu, no curriculum. Done when you have one concrete question.
2. **Read the reference file that carries the topic** with `read_file`, using the topic map below.
   Read it before answering, every time. Done when the file is read.
3. **If nothing in the map covers it, say so.** Say plainly that it isn't in what this skill knows,
   and point them at the official docs (https://hermes-agent.nousresearch.com/docs/) and at
   `/skills-catalogue`. Don't guess and don't answer from memory.
4. **Answer that question and stop.** Neighbouring topics get a one-line mention at most. Done when
   the answer fits the question and nothing more.
5. **Offer the handoff.** Where the topic has a real skill behind it, explain what that skill does
   first, then ask (with `clarify`, yes/no) whether they want it started now. Load it with
   `skill_view` only on a clear yes.
6. **Ask what else they'd like to know.** Most people have a second question and won't ask unasked.

### Topic map

| What they're asking about | Read |
|---|---|
| What Hermes is and how it works · what it can do · vs ChatGPT/Claude · what to use it for at work · memory and context files · long conversations and compression | `references/what-hermes-can-do.md` |
| CLI, TUI, desktop app, web dashboard, Discord/Telegram/Slack · which to use · sessions moving between them | `references/where-you-work.md` |
| Models and providers · which to pick · switching · cost | `references/models-and-providers.md` |
| What a skill is · using one · slash commands · installing from Bitpool's repo · why one didn't respond · finding out what one does | `references/skills.md` |
| Making their own skill · the ways to do it · `/create-new-skill` · review before it reaches others | `references/creating-a-skill.md` |
| Scheduled jobs (cron) · subagents and delegation · long-running goals | `references/automation-and-delegation.md` |
| MCP servers and connectors · browser use · computer use · messaging gateway | `references/connecting-things.md` |
| Profiles · plugins · mods (desktop plugins, TUI widgets, hooks, skins) | `references/profiles-plugins-and-mods.md` |

## Load-bearing rules

1. **Read the reference file before answering.** Names, commands and menus change, and a confidently
   wrong instruction sends someone down a dead end they can't diagnose.
2. **Explain before you run anything.** Never load another skill or run a command without saying
   what it's about to do and getting a yes. Someone asking how something works has not asked for it
   to happen.
3. **One question, one answer.** Burying the answer in a tour of everything else is how people leave
   without it.
4. **Plain words only.** No "frontmatter", "system prompt", "toolset", "manifest" unless they used
   the word first. The audience is anyone at Bitpool.
5. **Never invent a skill, command, flag or menu path.** If it isn't in a reference file here, say
   you're not sure and point at the docs and `/skills-catalogue`. A made-up command is worse than no
   answer.
6. **Don't be the catalogue.** Which Bitpool skills exist and what each does is `/skills-catalogue`'s
   job.
7. **Land every answer on what they can do next** — a skill, a command or a step that exists.
8. **Don't oversell.** Say what Hermes is weak at as readily as what it's good at.
9. **The snapshots are dated; say so when it matters.** Every reference file is a snapshot taken
   2026-10-16 from the Hermes docs. Something missing from them does not prove Hermes can't do it —
   it only means this skill doesn't know. Say that instead of "Hermes can't".

## Pitfalls

- **Answering from general knowledge of Hermes or Claude.** Hermes changes fast; the reference
  files are the only source this skill trusts. Anything else gets the docs link.
- **Treating "how do I install X" as a request to install it.** Explain; run only on a yes.
- **Claude-isms.** There are no Chat/Cowork/Code surfaces, plugin marketplaces or "+ → Connectors"
  menus in Hermes. If someone asks with Claude words, translate: surfaces → `where-you-work.md`,
  plugins/connectors → `skills.md` and `connecting-things.md`.

## Verification

- The answer quotes or follows a reference file that was read this run.
- No command, flag or skill name appears that isn't in a reference file or the related skills list.
- The reply ends with a next step and an invitation for another question.

## Reference files

Read the file itself — this table is an index, not a substitute. All are snapshots dated
2026-10-16, built from the Hermes docs.

| File | Covers |
|---|---|
| `references/what-hermes-can-do.md` | What Hermes is, the mechanics worth knowing, the feature list, how it differs from ChatGPT/Claude, best and worst uses at work, memory and context files, long conversations and compression. |
| `references/where-you-work.md` | CLI, TUI, desktop app, web dashboard and messaging gateways — what each is for, and that they share one agent and one set of sessions. |
| `references/models-and-providers.md` | What a provider is, `hermes model` vs `/model`, the 64K context floor, cost notes. |
| `references/skills.md` | What a skill is, slash commands, natural-language triggering, installing from Bitpool's repo, why one doesn't respond. |
| `references/creating-a-skill.md` | The routes to a new skill, the GitHub access it needs, the pull-request review. |
| `references/automation-and-delegation.md` | Cron jobs, subagents, `/goal`, background work. |
| `references/connecting-things.md` | MCP servers, browser and computer use, messaging platforms. |
| `references/profiles-plugins-and-mods.md` | Profiles, plugins, and the mods Bitpool builds (desktop plugins, TUI widgets, gateway hooks, skins). |

### Keeping the snapshots honest

When Hermes behaviour changes, update the matching reference file and its date line in the same
pass, bump `version`, and sync the README row. Facts most likely to date: setup modes and the
provider list (`models-and-providers.md`), the skills install commands (`skills.md`), and the
surface list (`where-you-work.md`).
