# Bitpool Hermes skills catalogue — snapshot

**Snapshot taken: 2026-10-16.** Mirrors the Skills table of the `README.md` in
**https://github.com/Lolman-bot/Hermes-Repository-**, which is the live catalogue and the authority.
If something someone asks about isn't below, that means it wasn't in the repo on the snapshot date —
it does **not** prove it doesn't exist today. Say so and point at the README.

## How anyone uses a skill

1. **Type the command.** It's always the skill's own name — `/teacher`, `/create-new-skill`.
2. **Just ask in plain words.** "Help me make a skill for site reports" finds `/create-new-skill`.

Works in the terminal, the desktop app and on Discord/Telegram/Slack.

## How to install one

Needs access to the repo (see `/onboarding`). Install each skill by its full path, which includes
its section folder (`bitpool-required-skills` or `bitpool-design-foundations`):

```
hermes skills install Lolman-bot/Hermes-Repository-/skills/<section>/<skill-name> --category bitpool
```

Start a new conversation (or `/reload-skills`) so the `/command` appears. `hermes skills check` and
`hermes skills update` keep installed skills current.

## Skills — required (`skills/bitpool-required-skills/`, baseline on every Bitpool Hermes install)

| Skill | What it does |
|---|---|
| `build-hermes-mod` | Builds a Hermes mod (desktop plugin, TUI widget, gateway hook or skin) from a plain description — flow chart for a yes, tests, README, a trial run — then a pull request adding it to the repo's `mods/` folder. |
| `build-skill-from-examples` | Builds a new skill from examples of the work coming in and going out, plus a process you draw on a point-and-click canvas, then hands it to `create-new-skill` for the pull request. |
| `create-new-skill` | Takes a new skill from idea to a pull request — a plain-language interview, bringing in a skill you already have, or a hand-over from `build-skill-from-examples` — with readiness checks and your confirmation before it goes to a reviewer. |
| `edit-mod` | Changes a Hermes mod you already have — the change, its tests, README and flow chart kept in step — then publishes it back the way you confirm. |
| `edit-skill` | Changes or retires a skill that already ships in the repo, as one pull request once you confirm it's finished. Retiring archives it to `retired/`, never deletes. |
| `install-mod` | Installs a mod from the repo's `mods/` folder onto your machine, or removes one — follows the mod's own install steps, shows every change for a yes first, never changes the repo. |
| `log-skill-divergence` | Records when a skill's documented claim turns out to be wrong (or it misfired), so the finding reaches whoever maintains it. Asks first; logs only. |
| `onboarding` | Walks a new starter through getting set up with Hermes, one step at a time — model, GitHub, repo access, installing the required skills. |
| `skill-health` | Grades how well a skill actually performed on a run, scores it out of 100, traces each miss to its cause, then offers to apply the fixes. |
| `skills-catalogue` | This one — the repo link and what's in it. |
| `teacher` | Explains how Hermes works in plain words — surfaces, models, memory, long conversations, skills, scheduled jobs, subagents, connections, profiles and mods. |
| `update-hermes-skill` | Keeps the skills repo internally consistent whenever a skill changes — version bumps, README table sync, frontmatter compliance. |
| `user-config-store` | Remembers a per-person setting a skill needs — a path, a browser profile — so the skill only asks once. Never stores secrets. |

## Skills — design foundations (`skills/bitpool-design-foundations/`, brand layer for visual and customer-facing work)

| Skill | What it does |
|---|---|
| `bitpool-brand-guidelines` | How Bitpool sounds — the five voice pillars, naming rules, ready-made boilerplate and positioning — for any copy, name or message written as Bitpool. |
| `bitpool-design-system` | How Bitpool looks — the six non-negotiables, light and dark tokens, components, the cube logo and a starter HTML template — for any page, deck, report or visual. |
| `bitpool-search` | A drop-in, on-brand predictive search box (typeahead, cyan highlights, keyboard control) for Bitpool pages with lists or tables. |

## Skills — support (`skills/bitpool-support/`, building-automation engineering and hands-on Bitpool Cloud work)

| Skill | What it does |
|---|---|
| `bacnet-diagnostics` | Diagnoses and fixes BACnet network alerts (MS/TP, BACnet/IP, BBMD, traffic rates, TrendLogs) and ASHRAE 135-2008 errata from vendor-confirmed reference entries. |
| `bitpool-dashboard-builder` | Builds, extends or rearranges Bitpool Cloud dashboards by driving a signed-in browser, with permission gates on every write. |
| `bitpool-hvac-schematics` | Builds self-contained, on-brand HTML BMS/SCADA graphics for HVAC and central plant with live data chips, animated flow and alarms. |
| `bitpool-report-builder` | Builds paginated Bitpool Cloud reports (wizard, canvas, data sources, Preview PDF) by driving a signed-in browser, with permission gates on every write. |
| `bitpool-training-deck-builder` | Turns raw training material into a reviewed, self-contained Bitpool HTML training deck built from a 28-layout template. |

## Skills — prototyping (`skills/bitpool-prototyping/`, rubric-driven generate → evaluate → review design loop)

| Skill | What it does |
|---|---|
| `loop-engineering-start` | Entry point to the rubric-scored generate → evaluate → review loop: confirms intent, sets up, resumes or archives `.loop-engineering/`, and hands off to `/project-context`. |
| `project-context` | Captures the user's project brief verbatim and copies their reference files into `.loop-engineering/` before any criteria are set. |
| `generate-rubric` | Interviews to sharpen the brief, then builds 4-6 weighted criteria with observable 0-10 anchors, optional gates, a threshold and a pass cap in `rubric.json`. |
| `design-generation` | Produces the next versioned design and its attribute rationale against the rubric anchors and review directives, without grading itself. |
| `design-evaluation` | Scores a design blind against the anchors with evidence, calibrates against history, logs the pass and routes to finish, review or a cap check-in. |
| `review-solution` | Checks in with the user, then analyses scoring history at a rigour tier matched to the number of candidates and writes 3-6 evidence-backed directives for the next pass. |

## Skills — images and videos (`skills/bitpool-images-and-videos/`, Gemini / Veo prompt-writing for Bitpool visuals)

| Skill | What it does |
|---|---|
| `bitpool-3d-image` | Writes Gemini image-to-image prompts that turn an attached photo, plan or diagram into a Bitpool archviz render, with an optional HTML mockup or handoff page. |
| `bitpool-cinematic-photo` | Writes Gemini prompts for Bitpool marketing stills (towers, plant rooms, data centres, cutaways, exploded views) from seven master templates, with optional HTML. |
| `bitpool-cinematic-video` | Writes 8-second Veo/Gemini video prompts for Bitpool assembly sequences, fly-throughs and exploded views, with an optional timed HTML animation preview. |

## Mods

None in `mods/` on the snapshot date. `/build-hermes-mod` creates them; `/install-mod` installs them.

## Outside Bitpool

Public skills from the Hermes Skills Hub (not Bitpool's): `hermes skills browse` and
`hermes skills search <word>`. Those are third-party — read before installing.

## A few things worth knowing

- **Skills ask before doing anything irreversible** — publishing, installing, sending.
- **Skills don't make up facts.** If one needs something it can't find, it stops and asks.
- **You don't have to pick the right one.** Describe what you want; if two could apply, you'll be
  asked which you meant.
