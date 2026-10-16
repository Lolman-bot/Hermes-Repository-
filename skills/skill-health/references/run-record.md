# Evaluation mode, and capturing the run record

Two jobs here, in this order: work out how many comparable runs you actually have, then capture each
one properly. Getting the count wrong is the more expensive mistake — it decides whether the maths in
`multi-run-statistics.md` applies at all.

## Determine the mode first

Count runs of the named skill **on comparable tasks**.

| Comparable runs | Mode | Steps |
|---|---|---|
| n = 1 | Single-run checklist | `single-run-review.md` only |
| n = 2 | Single-run checklist, twice, reported side by side | `single-run-review.md` on each; no statistics |
| n ≥ 3 | Checklist **and** statistics | `single-run-review.md` then `multi-run-statistics.md` |

At n=2 the temptation is to say "one of two, so 50%". Don't. Two points support a comparison, not a
rate. Report both checklists and note what differed between them.

### What counts as comparable

A run is comparable when the skill was asked to do **the same kind of job**, not the same job. Two
`draft-marketing-email` runs for different campaigns are comparable. A run where the user abandoned it
halfway, or where they interrupted with something unrelated, is not — exclude it and say you did.

Also exclude:

- Runs against a **different version** of the skill (the frontmatter `version` changed, or the
  `SKILL.md` text differs), unless you're deliberately doing the pairwise comparison in
  `multi-run-statistics.md`. Mixing versions makes the rate measure nothing.
- Runs where the skill fired but the user immediately redirected it to something else. That's an
  activation finding, not a performance sample — log it under criterion 1.

State the n and the exclusions in the report. A rate with an unexplained denominator is unusable.

## Capturing the record

For each run, capture four things. All four, or the review has gaps you'll end up guessing across.

1. **The triggering request** — the user's words, verbatim, that made the skill fire: the
   `/skill-name` slash command and the text after it, or the request that led to a
   `skill_view(name=...)` call. Needed for criterion 1 and nothing else can substitute for it.
2. **The full tool-call sequence** — every call in order, with what it touched. This is the evidence
   for criteria 2 and 4: a route step that ran leaves a tool call behind, and a reference file that
   was read leaves a `skill_view(..., file_path="references/...")` or `read_file` call. Calls made
   inside a `delegate_task` subagent live in the child session, not the parent; follow it.
3. **The final output** — the actual deliverable, and where it landed. `read_file` it if it's on
   disk; don't score a deliverable you only saw described.
4. **Every user correction or pushback that followed** — including tone. "No, I meant the other one"
   and "that's fine I'll fix it myself" are both criterion-7 evidence, and the second one is the more
   serious of the two.

### From this conversation

Everything above is in context when the run happened in this chat. Prefer it — it's complete. If
context compression ran since, older turns may be summarised; treat anything summarised as `—`
unless you recover the original from the session store below.

### From earlier sessions

Hermes keeps every session — CLI, TUI, desktop, dashboard, gateway, cron and subagent — in the
profile's `$HERMES_HOME/state.db` (SQLite: a `sessions` table with metadata and token counts, a
`messages` table with full history, `tool_calls` stored as JSON). Read it through the tools, in this
order:

1. **`session_search`** (exposed as chat-history lookup on some surfaces). Discovery: pass `query`
   with the skill name, e.g. `query="skill-health"`, optionally bounded with `after`/`before`
   (`7d`, `2w`, ISO dates) and `exclude_session_ids` to keep finding new ones. Read: pass
   `session_id` alone for the whole session. Scroll: `session_id` + `around_message_id` to read the
   turns around a hit. It searches tool names and tool-call arguments too, so `skill_view` calls
   naming the skill are findable.
2. **`hermes sessions export <file>.jsonl --session-id <id> --redact`** via `terminal`, when you need
   one whole session as a file to search through with `search_files` or Python.
3. **Read-only SQL** for cost figures, which live on the session row (`message_count`,
   `tool_call_count`, `input_tokens`, `output_tokens`, `reasoning_tokens`, `estimated_cost_usd`).
   Open it read-only so you never contend with a running gateway:

   ```bash
   python -c "import os,sqlite3; db=os.path.join(os.environ['HERMES_HOME'],'state.db'); c=sqlite3.connect('file:'+db.replace(os.sep,'/')+'?mode=ro',uri=True); print(c.execute('select id,source,title,message_count,tool_call_count,input_tokens,output_tokens from sessions where id=?',('<session-id>',)).fetchall())"
   ```

   Never write to `state.db`.

> **Warning.** Sessions are per profile and per machine. Runs on another machine, in another
> profile, or in sessions that were pruned or deleted are not there; say so rather than assuming
> they went well.

**If you can't reach three comparable runs, run single-run mode and say so.** Do not pad the count
with partial or non-comparable runs to unlock the statistics — an n=3 built from one real run and two
near-misses is worse than an honest n=1, because the numbers make it look otherwise.

## Cost, captured at the same time

While you're in the record, capture per run: total tool calls, conversational turns, and token usage.
This feeds the cost axis in `multi-run-statistics.md` and it's much harder to reconstruct later than
to note now. The session row's token counts cover the **whole session**: if the skill ran in a
session that also did other work, count the run's own tool calls and turns from its messages and say
the token figure is session-wide (or unavailable for the run alone).

## Before you leave this step

- [ ] n is stated, with exclusions named.
- [ ] All four record items captured for every included run.
- [ ] The deliverable was read, not inferred.
- [ ] Cost figures noted, or their absence (or session-wide scope) noted.
- [ ] You did not inflate n to reach 3.
