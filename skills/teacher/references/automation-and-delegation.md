# Scheduled jobs, subagents and long goals

**Snapshot: 2026-10-16**, built from the Hermes Agent docs
(https://hermes-agent.nousresearch.com/docs/). Hermes changes quickly. If something isn't covered
here, that does **not** prove Hermes can't do it — only that this snapshot doesn't say. Point at the
docs rather than guessing.

## "Can it do something every morning / every hour?"

Yes — **scheduled jobs (cron)**. Ask in plain words ("every weekday at 8am, summarise new issues in
X and send it to me") and Hermes creates the job; or use `/cron` in a chat, or `hermes cron create`
in a terminal (`hermes cron list` to see them).

- A job can use one or more skills, and deliver its result back to the chat it was made in (e.g. a
  Discord channel), to a file, or to another configured platform.
- Each run is a fresh conversation. It doesn't remember earlier runs unless the job is set to carry
  the previous run's output forward — ask for that if it should "only report what's new".
- Jobs are run by Hermes's background **gateway** (`hermes gateway`), which checks for due jobs every
  minute; if the gateway isn't running (or the laptop is asleep), nothing fires.
- Advice from the docs: get your basic setup stable before adding scheduled jobs.

## "What's a subagent?"

> Hermes can hand pieces of a big job to helper agents that work in parallel, each with a clean
> slate, and report back a summary.

- Good for: researching several things at once, reviewing many files, splitting a large change.
- Each helper knows **only what it's told** — none of your conversation. Vague hand-offs get vague
  results.
- Only the summaries come back, which keeps your own conversation short.
- It happens when you ask for it ("split this up and do it in parallel") or when Hermes decides a job
  suits it.

## "Can it keep going until it's done?"

`/goal <what done looks like>` sets a standing goal: after each turn a checker decides if it's done
and, if not, Hermes carries on — up to a turn budget (20 by default). `/goal status`, `/goal pause`,
`/goal clear`. Any message you send interrupts it.

## Cautions

- Automated jobs act without you watching — start with read-only jobs (reports, checks).
- They cost tokens every run; a frequent job on an expensive model adds up.
