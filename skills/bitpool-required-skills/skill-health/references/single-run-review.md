# Single-run review — the checklist and the causal trace

This is the whole method at n=1, and the first half of the method at n≥3. Five steps. The output is a
scored checklist plus a ranked list of candidate edits, each one tied to a specific failure.

## 1. Score the checklist, not a continuous number

Three verdicts only, per criterion:

| Verdict | Means |
|---|---|
| ✅ | Met, with cited evidence |
| ⚠️ | Partially met, or met by accident rather than by the instruction |
| ❌ | Not met, with cited evidence |
| — | **Couldn't tell.** Evidence absent or truncated. Not a score. |

No fractional scores at the criterion level, and no 0–10 scales. There is no distribution behind a
single sample to justify decimal precision, and a made-up 6.5/10 is indistinguishable in a report from
a measured one.

Every verdict carries a quote. Format each line so the evidence sits next to the verdict:

```
❌  Rule 4 — "show the diff and get a yes before pushing"  [weight 3]
    Evidence: `git commit` at turn 14 follows `git add -A` at turn 13 directly.
    No `git diff --cached` call anywhere in the run, and no question to the user
    between the add and the commit.
```

`⚠️` is the honest verdict for the common case where the right thing happened but not because the
skill said so — the model would have done it anyway, so the instruction isn't earning its place. Note
that explicitly; it's a different fix from a ❌.

The `—` verdict matters. A criterion you can't evidence is excluded from the score's denominator, not
scored as a pass. Say in the report how many criteria came out `—` and why.

## 2. Trace each ❌ and ⚠️ to a specific instruction

For every miss, find the exact cause. One of three shapes:

- **A line that says the wrong thing.** Quote it, with its line number.
- **A line that says the right thing in a place the run never reached.** Usually buried in a reference
  file the route didn't point at, or below the point where a long `SKILL.md` stopped being read.
- **A gap** — nothing in the skill covers this at all. Name what's absent, specifically. "No rule
  requires the diff to be shown" is a trace; "insufficient guidance" is not.

This is causal tracing on one case. You are not claiming the line causes failures in general — you are
claiming it caused *this* one, and the evidence from step 1 is what backs that.

Where a miss has two plausible causes, say so and name both. A confident single cause you can't
distinguish from an alternative is a guess with better formatting.

## 3. Apply the counterfactual test

For each traced miss, ask exactly this:

> What is the **minimal** edit to this skill that would have prevented this specific failure?

A fix passes the test only if all three hold:

1. It names the rubric criterion it addresses.
2. It cites the evidence from step 1.
3. Had it been in place, this run would have gone differently — and you can say how.

**Reject these, every time:**

| Rejected fix | Why |
|---|---|
| "Improve clarity" | Not an edit. Nothing to apply. |
| "Add more detail about X" | Unbounded. Grows the file without changing behaviour. |
| "Emphasise that the rule is important" | The rule was already there; emphasis isn't the cause. |
| "Add a rule covering everything in this class" | Not minimal. Fix the case you have evidence for. |
| A rewrite of a whole section | You can't attribute the outcome to any part of it afterwards. |

Prefer, in this order: **move** an existing line to where the run would reach it → **sharpen** an
existing line → **add** one line. Adding is last because every added line dilutes the ones already
there, and a `SKILL.md` nobody finishes reading is the failure mode this whole review exists to catch.

Where the trace was "a line in a reference file the route never pointed at", the fix is almost always
a pointer in the route, not a duplicate of the line.

## 4. Classify each finding as one-off or structural

| Class | Test | What happens |
|---|---|---|
| **One-off** | Caused by something particular to this run — odd phrasing, an unusual input, an interruption. A future run wouldn't hit it. | Log it. Change nothing. |
| **Structural** | Any future run doing this job hits the same thing. | Candidate edit. |

Be honest about which you're looking at, in both directions. Over-classifying as structural bloats the
skill; over-classifying as one-off means the same failure comes back next month with nobody having
written it down.

At n=1 you genuinely cannot always tell. When you can't, say **"unclassified — needs a second run to
distinguish"** and leave it as a logged finding, not an edit. That is the correct answer, and it's the
single most useful thing single-run mode produces: a specific thing to watch for next time.

## 5. Rank what came out

Order the structural findings by `weight × severity`, highest first — a weight-3 ❌ before a weight-3
⚠️ before a weight-2 ❌. This is the order they go into the report, and the order they'd be applied in
step 8.

Then hand back: to `multi-run-statistics.md` if n≥3, otherwise straight to `report-and-score.md`.

## Before you leave this step

- [ ] Every criterion has a verdict, and every ✅/⚠️/❌ has a quote.
- [ ] `—` verdicts are counted and explained, not quietly scored as passes.
- [ ] Every miss has a trace naming a line, a location, or a specific absence.
- [ ] Every proposed fix passes all three counterfactual conditions.
- [ ] No fix is a section rewrite, and no fix is "improve clarity".
- [ ] Each finding is one-off, structural, or explicitly unclassified.
