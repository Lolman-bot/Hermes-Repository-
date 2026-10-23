# Creating a skill

**Snapshot: 2026-10-16**, built from the Hermes Agent docs
(https://hermes-agent.nousresearch.com/docs/). Hermes changes quickly. If something isn't covered
here, that does **not** prove Hermes can't do it — only that this snapshot doesn't say. Point at the
docs rather than guessing.

Anyone at Bitpool can write one. The hard part is knowing how the job should be done — which is the
part they already have.

## The ways in

| Way in | What you hand over | Best for |
|---|---|---|
| **`/create-new-skill` interview** | Describe the job in plain words; attach examples, documents or code. | Most skills. Also brings in a skill folder you already have. |
| **Let Hermes save one for you** | Do the job with Hermes once, then ask it to save the approach as a skill. | A personal skill on your own machine. It is *not* shared until it goes through `/create-new-skill`. |

Whichever way: **the detail is theirs** — steps, numbers, rules, format, one example that came out
well. Hermes can shape it; it can't invent how Bitpool does the job.

## Before you can publish one

Bitpool's skills live in the GitHub repo **`Lolman-bot/Hermes-Repository-`**. To publish, you need
GitHub signed in on your machine (`gh auth login`) and to be added to the repo — message Eric your
GitHub username. `/onboarding` walks through both. Nothing stops you starting the interview first.

## What `/create-new-skill` is like

- Plain-English questions: what the job is, when it should switch on, what comes out, a good example.
- **A real example is the single most useful thing you can give it.**
- It shows you the finished skill and waits for your yes before writing anything.
- It checks the skill against the repo's house rules and asks whether it's really finished — try it
  on a real task first.

## What happens when it's finished

It opens a **pull request** on the repo — a request for a reviewer to check the skill and merge it
to `main`. Until it's merged, nobody else has it; after that, colleagues get it by installing it,
or with `hermes skills update` if they already have an earlier version.

## Where this hands over

- "Start it now" → `/create-new-skill`, on a yes.
- "Change one that exists" → `/edit-skill`.
- "It didn't work properly" → `/skill-health`.
