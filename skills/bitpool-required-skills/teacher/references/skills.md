# Skills — what they are and how to use one

**Snapshot: 2026-10-16**, built from the Hermes Agent docs
(https://hermes-agent.nousresearch.com/docs/). Hermes changes quickly. If something isn't covered
here, that does **not** prove Hermes can't do it — only that this snapshot doesn't say. Point at the
docs rather than guessing.

## What is a skill?

> A skill is a set of written instructions Hermes loads when it's relevant, so it does a particular
> job the same careful way every time instead of improvising.

- **It's how we bottle the way Bitpool does something.** The person who knows how it should be done
  writes it down once; everyone else gets that standard.
- **Only a one-line description is always loaded**; the full skill loads when it's used, so having
  many installed costs almost nothing.
- A skill can ship templates, scripts and reference notes as well as instructions.
- Hermes also writes its own skills as it learns, and ships with a set of general-purpose ones.
  Bitpool's live in one GitHub repo, `Lolman-bot/Hermes-Repository-`, and install into a `bitpool`
  category.

## How do I use one?

1. **Type `/` and the skill's name** — `/teacher`, `/skills-catalogue`. You can add the request
   after it: `/create-new-skill a skill for weekly site reports`. Works in the terminal, the desktop
   app and on Discord/Telegram/Slack.
2. **Just ask in plain words.** Hermes picks a skill when what you've asked matches what it's for.

## How do I install one?

Unlike Claude, there are no plugins to install — skills install one at a time, straight from the
repo by full path (needs GitHub access to the repo — `/onboarding` covers it). Skills sit in section
folders such as `bitpool-required-skills` and `bitpool-design-foundations`:

```
hermes skills install Lolman-bot/Hermes-Repository-/skills/<section>/<skill-name> --category bitpool
```

Then start a new conversation (or run `/reload-skills`) so the new `/command` appears. Updates:
`hermes skills check` shows what's changed upstream; `hermes skills update` pulls it.

Public skills from outside Bitpool: `hermes skills browse` and `hermes skills search <word>`.
Installs from outside Bitpool run through a security scan first — still read what you're installing.

## Why didn't the skill respond?

In order of likelihood:

1. **It isn't installed on this profile.** `hermes skills list` shows what is. Install it (above).
2. **It was installed during this conversation** — run `/reload-skills` or start a new one.
3. **Wrong profile** — each profile has its own skills.
4. **The wording was too far from what it covers.** Typing `/name` settles it.

If a skill *should* have worked and didn't do the right thing, that's `/skill-health` (grade and fix
a run) or `/log-skill-divergence` (record that it was wrong).

## How do I find out what a skill does?

1. Ask Hermes to show you the skill — every skill explains itself at the top.
2. `/skills-catalogue` — every Bitpool skill with a line on each.
3. The repo README (`Lolman-bot/Hermes-Repository-` on GitHub) — the live list.

## Where this hands over

- "What skills do we have?" → `/skills-catalogue`.
- "How do I make one?" → `references/creating-a-skill.md`.
