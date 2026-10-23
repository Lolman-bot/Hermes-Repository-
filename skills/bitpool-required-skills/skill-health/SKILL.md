---
name: skill-health
description: "Use when grading how a skill ran. Scores it, offers fixes."
version: 1.0.2
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, skills, evaluation, quality, rubric, statistics]
    category: bitpool
    related_skills: [edit-skill, log-skill-divergence, create-new-skill, update-hermes-skill]
---

# Skill Health

Grades a Hermes skill on what it actually did in a run, not on what its `SKILL.md` claims. You end up
with a cited checklist, a score out of 100, a ranked list of minimal edits that would each have
prevented a specific failure, and — if the user says yes — those edits applied.

Two modes, and the branch is not optional. One run gets a checklist and causal tracing. Three or more
comparable runs get statistics as well: pass@k / pass^k, Wilson intervals, attribute analysis,
pairwise A/B, and cost as its own axis. The maths is meaningless at n=1, so applying it there
produces confident nonsense.

## When to Use

- `/skill-health`, or the user asks how a skill performed or wants one graded: "how did that skill
  do", "score that skill", "why did the skill miss that".

Don't use for:

- Creating a skill: `/create-new-skill`.
- A change already decided on: `/edit-skill`.
- Recording a divergence for later instead of grading a run: `/log-skill-divergence`.
- Repo housekeeping: `/update-hermes-skill`.

## Procedure

Eight steps, in order. Each step's output is the next step's input. Steps 1-7 are read-only.

1. **Ask which skill.** If several skills fired in the conversation, name them in a `clarify`
   question and let the user pick. Never grade a skill the user didn't name.
   *Done when:* one skill is named.
2. **Read the skill under test.** `skill_view(name=...)` for its `SKILL.md` in full, plus any
   `references/` the run actually opened (`skill_view` with `file_path`).
   *Done when:* you hold the exact text and `version` the run used.
3. **Build the rubric from that skill's own words** — its procedure steps and load-bearing rules
   become the checklist items. `references/build-the-rubric.md`. *Done when:* every criterion names
   its source line and weight.
4. **Determine the evaluation mode and capture the run record(s).** Count comparable runs, from this
   conversation and from past sessions via `session_search`; n=1 or 2 goes to step 5 only, n≥3 to
   steps 5 and 6. `references/run-record.md`. *Done when:* n, exclusions and the four record items
   per run are written down.
5. **Single-run review** — score the checklist, trace each miss to a line, apply the counterfactual
   test, classify one-off vs structural. `references/single-run-review.md`.
   *Done when:* every criterion has a verdict with a quote or `—`.
6. **Multi-run statistics** — only when n≥3. pass@k / pass^k, Wilson interval, per-stage health,
   attribute analysis, pairwise comparison, cost axis. `references/multi-run-statistics.md`.
7. **Report the findings and the score out of 100** in the chat.
   `references/report-and-score.md`. *Done when:* the report ends with the step-8 question.
8. **Ask whether to implement the changes.** No → stop, nothing edited. Yes → find where the skill
   lives: this repo's skills go to `/edit-skill`; local-only skills are patched with `skill_manage`.
   `references/apply-the-fixes.md`.

## Load-bearing rules

Break any one of these and the review reads authoritative while being unfounded — which is worse than
no review, because it gets acted on.

1. **The rubric comes from the skill's own `SKILL.md`, never from your own idea of a good skill.** Its
   procedure steps and load-bearing rules are the checklist. A rubric you invented grades the skill
   against a job it never claimed to do, and every finding from it is unactionable.
2. **Every ✅ / ⚠️ / ❌ cites evidence, quoted.** Name the tool call, the output, or the user's own
   words. A verdict with no citation is an opinion, and opinions don't survive the counterfactual
   test in step 5.
3. **Never apply the multi-run maths at n=1.** No pass@k, no confidence interval, no correlation, no
   trend. There is no distribution behind one sample.
4. **Every miss traces to a specific line or a specific gap.** The exact `SKILL.md` line that caused
   it, or the named absence that allowed it. "The instructions were unclear" is not a trace.
5. **Every proposed fix is minimal, counterfactual and named.** It answers "what is the smallest
   edit that would have prevented *this* failure?" and ties to a rubric criterion plus cited
   evidence. Reject "improve clarity", "add more detail", "strengthen the wording".
6. **One-off and structural are different findings and get different treatment.** One-off gets
   logged, not edited. Structural — any future run hits this too — is a candidate edit. Editing on
   one-offs is how a `SKILL.md` bloats into something nobody reads.
7. **The score out of 100 derives mechanically from the checklist, and never appears without it.**
   Weighted criteria, ✅=1 / ⚠️=0.5 / ❌=0, rounded to the nearest 5 at n=1.
8. **Cost is a separate axis, never folded into the quality score.** Tool calls, turns and tokens are
   reported alongside quality, never blended into it.
9. **Nothing is edited before the user says yes at step 8.** Steps 1-7 are read-only, including on the
   skill's own repo and its installed copy. The review and the change are two decisions.
10. **Say what you couldn't see.** A missing or compressed transcript, a subagent session you couldn't
    open, a reference file you can't confirm was read — state it and leave the criterion unscored. An
    assumed ✅ is the one error that makes the whole report untrustworthy.

## Pitfalls

- **Grading the current `SKILL.md` against an old run.** If the skill's `version` changed since the
  run, grade against the text that ran, or say you couldn't recover it.
- **Missing the subagent half.** Work done through `delegate_task` lives in the child session; the
  parent only shows the summary. Follow it before scoring the steps it covered.
- **Reading session-wide tokens as the skill's cost.** The session row's token counts include
  everything else in that session; say so.
- **Patching a hub-installed copy "just to test".** `skill_manage` edits mark it user-modified and
  `hermes skills update` stops updating it. Declare it, every time.
- **Editing this skill from inside a review of itself.** Hand the findings to `/edit-skill`.

## Verification

- The score's arithmetic is visible: weights, verdicts, both sums, rounding grain matching n.
- No statistics section at n<3; every rate at n≥3 carries its Wilson interval and denominator.
- Every recommended edit is structural, ranked, and passes the counterfactual test.
- "What I couldn't see" is present.
- Nothing was edited before the step-8 yes, and only the fixes the user picked were applied.

## Reference files

Read the whole file you reach for; skimming for the line you expect is how a rule gets missed.

| File | Covers |
|---|---|
| `references/build-the-rubric.md` | Turning the skill's own steps and load-bearing rules into weighted criteria, the seven default criteria, weighting, and skills with no explicit rules. |
| `references/run-record.md` | Choosing the mode, what a comparable run is, capturing the record, and finding earlier runs in Hermes's session store (`session_search`, `hermes sessions export`, read-only `state.db`). |
| `references/single-run-review.md` | Scoring ✅/⚠️/❌/— against quoted evidence, causal tracing to a `SKILL.md` line, the counterfactual test, and one-off versus structural. |
| `references/multi-run-statistics.md` | n≥3 only: pass@k and pass^k, the Wilson interval worked through, per-stage health, attribute analysis, pairwise comparison and Elo, and the cost axis. |
| `references/report-and-score.md` | The report shape, the score arithmetic, rounding grain per n, and the bands. |
| `references/apply-the-fixes.md` | Step 8: where the skill lives, the handoff to `/edit-skill` for this repo's skills, `skill_manage` patches for local-only skills, and the update freeze on patched hub or bundled skills. |

The two modes are the substance and live in `references/single-run-review.md` and
`references/multi-run-statistics.md`; change the method there, not here. The step-8 handoff depends
on `/edit-skill`'s route; if that changes, update `references/apply-the-fixes.md` in the same pass.
