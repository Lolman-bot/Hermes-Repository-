# What Hermes can do, and why it's worth your time

**Snapshot: 2026-10-16**, built from the Hermes Agent docs
(https://hermes-agent.nousresearch.com/docs/). Hermes changes quickly. If something isn't covered
here, that does **not** prove Hermes can't do it — only that this snapshot doesn't say. Point at the
docs rather than guessing.

These are the questions people ask before they've decided Hermes is worth learning. Answer the one
they asked honestly, then connect it to what's available here — Bitpool's skills are the reason the
answer at Bitpool is better than the answer in general. Don't oversell.

## "What is Hermes, and how does it work?"

> Hermes Agent is an open-source AI agent from Nous Research. It isn't a model itself — it's the
> program that drives a model (Claude, GPT, Gemini, an open model…) and gives it tools: it can run
> commands, read and write files, search the web, drive a browser, remember things and follow
> Bitpool's written procedures (skills).

Three mechanics worth giving, in plain words:

- **It works by using tools, not just by talking.** Ask it something and it can run a command, open a
  file or search the web to find out, then answer. That's why it's called an *agent*.
- **It only knows what it's been given.** The model's training, the current conversation, its memory
  notes, any project instruction files, and whatever its tools can reach. A pasted-in source beats a
  described one.
- **The model is swappable.** Hermes works with many providers; which one you run is a setting
  (`references/models-and-providers.md`).

The features worth knowing exist, one line each, with the file that covers it:

| Feature | In one line |
|---|---|
| **Chat + tools** | Ask, draft, brainstorm — and it can actually run things to check. |
| **Many places to use it** | Terminal, desktop app, web dashboard, Discord/Telegram/Slack — `references/where-you-work.md`. |
| **Skills** | Bitpool's written procedures, each one a `/slash-command` — `references/skills.md`. |
| **Memory** | Short notes about you and your setup carried between conversations — below. |
| **Scheduled jobs and subagents** | Run something every morning; split a big job across helpers — `references/automation-and-delegation.md`. |
| **Connections** | MCP servers, browser and desktop control — `references/connecting-things.md`. |
| **Profiles and mods** | Separate agents with separate setups; add-ons that change how Hermes looks or behaves — `references/profiles-plugins-and-mods.md`. |

Don't read the table out. Pick the row they're circling and hand over to the file.

## "What can it actually do?"

The useful framing is **it does work, not just answers**: reads long documents and pulls out what
matters, writes and rewrites, works through data, writes and debugs code, runs commands on your
machine, drives a browser, builds files you can open, and works through a job in steps.

Then the part that matters here:

> On its own it's a capable generalist. What makes it useful at Bitpool is that we've written down
> how we do things and handed those instructions to it. That's what a **skill** is.

## "How is it different from ChatGPT (or Claude)?"

Answer from what we've built, not a feature comparison — those date in months.

> Two differences matter day to day. First, it **acts**: it runs on your machine (or a server) with
> real tools, rather than only replying in a box. Second, Bitpool has built its own way of working
> into it as skills that everyone installs from one repo. A general chatbot doesn't know any of that.

If they push: Hermes can run Claude or GPT models underneath — it's the harness, not a rival model.

## "What are the best things to use it for at work?"

> Best on work that's **repeatable, has a right way of being done, and eats time** — and on anything
> where running a command or reading a file beats guessing. Weakest where the value is a judgement
> only you can make.

- Anything with a house format, once there's a skill for it.
- Getting things out of documents, logs, spreadsheets.
- Jobs on your own machine or repo — it can look, not just advise.
- Recurring checks and reports (a scheduled job delivers them to you).
- First drafts of anything.

Advice to give with it: **start with something you do repeatedly and dislike** — that's also a
candidate skill (`references/creating-a-skill.md`).

Honest weak spots: it can be confidently wrong, it can misread a vague request, and it acts on your
machine — so it asks before risky commands, and you should read what it proposes.

## "Does it remember me between conversations?"

**Yes, in a bounded way.** Memory is on by default (unless someone chose the minimal "Blank Slate"
setup). Hermes keeps two small notes files — one about you, one about your environment and lessons
learned — and reads them at the start of each new conversation.

Four kinds of remembering people conflate:

| What | What it remembers |
|---|---|
| **Memory** | Short notes about you and your setup. Small on purpose (a couple of thousand characters). |
| **Past sessions** | Every conversation is saved; Hermes can search old ones when it needs history. |
| **Project instruction files** | An `AGENTS.md` (or `.hermes.md`) in a project folder tells Hermes how that project works, whenever it's started there. |
| **Skills** | Not memory of *you* — memory of *how Bitpool does a job*. Written once, everyone gets it. The one worth investing in. `user-config-store` covers per-person settings a skill needs. |

Honest cautions:

- **"I'll remember that" isn't proof.** Memory only saves when Hermes actually writes it; if it
  matters, ask it to show you the memory entry.
- **New memories show up in the *next* conversation**, not one already running. Start a new one with
  `/new`.
- **Memory is per profile.** A Discord bot on another profile doesn't share your notes.
- **Don't rely on it for anything exact.** Say important numbers again.

## "Can it handle a really long conversation?"

Yes. When a conversation approaches the model's limit, Hermes **summarises the older part** so the
work carries on (by default at around half the context window). The thread survives; exact early
wording may not. You can also do it yourself with `/compress`.

Practical advice:

- **A new job deserves a new conversation** — `/new`. Focused conversations get better answers, cost
  less, and let memory refresh.
- **On Discord/Telegram a chat never ends by itself** — it's one long session until you `/new`.
- **Attach or paste the source rather than describing it.**
- **Installed skills cost almost nothing** — only a one-line description is always present; the full
  skill loads when it's used.

## Where this hands over

- "So what skills are there?" → `/skills-catalogue`.
- "Where am I meant to use it?" → `references/where-you-work.md`.
- "That thing I do every week — could that be a skill?" → yes: `references/creating-a-skill.md`.
