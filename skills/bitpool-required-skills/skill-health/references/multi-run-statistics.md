# Multi-run statistics — n ≥ 3 only

Everything in this file assumes at least three comparable runs, counted per `run-record.md`. At n=1 or
n=2 none of it applies, and applying it anyway produces numbers that look measured and aren't.

Run `single-run-review.md` on every included run first. These six steps work across the aggregated
findings, not instead of them.

## 6. Aggregate success rate with pass@k and pass^k

A run "succeeds" when it clears the threshold you state up front — the honest default is **no ❌ on any
weight-3 criterion**. State the definition before computing anything; a success rate whose threshold is
chosen after the fact is fitted, not measured.

With `n` runs and `c` successes, use the unbiased estimators:

```
pass@k  = 1 − C(n−c, k) / C(n, k)     # succeeded at least once in k attempts — can it work at all
pass^k  =     C(c, k)   / C(n, k)     # succeeded in every one of k attempts — is it reliably good
```

`pass^k` is the one that matters. `pass@k` tells you the skill is capable; `pass^k` tells you whether
you can trust it unattended, which is the actual question when someone installs it.

Worked, at c=6 successes out of n=8:

| Metric | Arithmetic | Result |
|---|---|---|
| Raw rate | 6/8 | 75% |
| pass@2 | 1 − C(2,2)/C(8,2) = 1 − 1/28 | **96%** |
| pass^2 | C(6,2)/C(8,2) = 15/28 | **54%** |
| pass^3 | C(6,3)/C(8,3) = 20/56 | **36%** |

Report `pass@k` and `pass^k` together. The gap between 96% and 54% is the finding — a skill that
almost always works eventually but only half the time on the first go needs a different fix from one
that fails outright.

## 7. Put a confidence interval on that rate

Use a **Wilson score interval**, not a naive percentage and not the normal approximation. At small n
the normal approximation gives intervals that run past 0 or 1 and are badly wrong near the edges.

```
        p̂ + z²/2n              z          ⎧    p̂(1−p̂)     z²  ⎫
centre = ───────────    half = ─────  × √ ⎨    ──────  +  ──── ⎬
         1 + z²/n             1 + z²/n    ⎩       n        4n² ⎭

interval = centre ± half        z = 1.96 for 95%
```

Worked, at 6/8:

```
z² = 3.8416          1 + z²/n = 1.4802
centre = (0.75 + 0.2401) / 1.4802            = 0.669
half   = (1.96/1.4802) × √(0.023438 + 0.015006) = 0.260
                                       →  [0.409, 0.929]
```

So **6/8 is not "75%" — it's 75% observed, with a true rate anywhere from 41% to 93%.** Write it that
way. A bare 75% claims a precision eight runs cannot support, and it will be quoted later as if it
were solid.

Two consequences to state plainly in the report:

- **An interval that wide can't rank two versions.** If the old and new `SKILL.md` intervals overlap —
  and at n<20 they almost always do — you have not shown an improvement. Use the pairwise method in
  step 10 instead.
- **The interval is what tells you how many more runs you'd need.** Halving the width takes roughly
  four times the runs. Say so when someone asks whether the fix worked.

## 8. Check per-stage health for multi-stage skills

Some skills are a chain: `build-skill-from-examples` hands off to `create-new-skill`, which runs
`update-hermes-skill`; `edit-skill` calls the same, and a skill that uses `delegate_task` runs stages
in subagents. For those, one overall rate hides where the problem is.

Score each stage separately and lay it out as a funnel:

| Stage | Runs entered | Cleared | Rate |
|---|---|---|---|
| examples intake | 8 | 8 | 100% |
| diagram approved | 8 | 7 | 88% |
| skill written and approved | 7 | 4 | 57% |
| pull request raised | 4 | 4 | 100% |

Then look for the two patterns that only show up this way:

- **A late-stage symptom with an early-stage cause.** A stage that fails on inputs a previous stage
  produced badly. Fixing the failing stage does nothing; fix the one upstream of it.
- **A stage that never runs.** In the table above, the pull-request stage looks perfect — on the four runs
  that reached it. A stage with a small denominator is not healthy, it's untested. Report the
  denominator next to every rate.

## 9. Run attribute analysis across the aggregated findings

Work out which rubric criteria actually move the outcome. For each criterion, split the runs by how it
scored and compare overall success:

```
criterion "read what it said it would read":
  runs where ✅ : 5 runs, 5 succeeded  → 100%
  runs where ❌ : 3 runs, 1 succeeded  →  33%
  difference: +67 points              ← this criterion predicts the outcome
```

Do that for every criterion, then sort by the difference. Spend the fixing effort at the top. A
criterion where the rate is the same on both sides is adding noise to the total and nothing else —
worth saying out loud, because it's usually a criterion someone was proud of.

> **Warning.** At n under about 10 this is directional, not statistical. A 3-run-versus-5-run split
> will not survive a significance test and you should not run one and quote it. Say "this looks like
> the driver" and give the counts, so the reader can see the whole basis for the claim.

Watch for the criterion that correlates because it's the *same* failure counted twice — a route step
and a load-bearing rule that both describe showing the diff will always move together. Merge them and
say you did.

## 10. Use pairwise comparison to test a proposed edit

When testing whether an edit actually improved the skill, do **not** re-score both versions in
isolation and compare the numbers. Absolute scores drift between sessions — the same output scores
differently a week apart — and at these interval widths a 6-point gap means nothing.

Instead: run the same task through the old and the new `SKILL.md` and answer one question.

> Which of these two outputs is better, and on which criterion?

Pairwise judgements are far more stable than absolute ones, because both sides are in front of you at
once and the comparison doesn't depend on where your scale happens to sit today.

Rules for it to be worth anything:

- **Same task, same inputs, both versions.** One variable.
- **Judge blind where you can** — don't label which is which until after the verdict.
- **Answer per criterion, not overall.** "Better" without a criterion is a preference.
- **"No difference" is a real answer**, and the most common one for a fix that didn't land. Record it.

For three or more versions, run the pairings and build a win matrix, then an Elo rating from it:

```
E = 1 / (1 + 10^((R_opponent − R_self)/400))        expected score
R_self ← R_self + K × (S − E)                        S = 1 win, 0.5 draw, 0 loss
                                                     K = 32, everyone starts at 1500
```

Elo needs a decent number of comparisons before the ratings settle. With three versions and three
comparisons, publish the win matrix and skip the rating — a rating from three games is a number
pretending the matrix wasn't already clearer.

## 11. Track cost alongside quality, as a separate axis

Report per run, averaged across the n:

- tool calls
- conversational turns
- tokens, if available (say so plainly if not)

Plot or tabulate cost against the quality signal. **Never fold it into the score.** Blending them
hides exactly the trade-off you need to see: a skill winning on quality while burning five times the
tool calls should be visible as a choice, not averaged away into a mid-table number.

The two findings this axis produces, and neither shows up anywhere else:

- **Cost with no quality to show for it** — usually a route that re-reads the same reference file, or
  a search loop with no exit condition. The cheapest real win available.
- **A cheap version that scores nearly as well.** Worth reporting even when the user didn't ask, since
  the expensive version is often expensive by accident.

## Before you leave this step

- [ ] The success threshold was stated before any rate was computed.
- [ ] `pass@k` and `pass^k` both reported, with the arithmetic shown.
- [ ] Every rate carries its Wilson interval, and no bare percentage appears anywhere.
- [ ] Per-stage rates carry their denominators.
- [ ] Attribute analysis is labelled directional at small n, with counts given.
- [ ] Any version comparison is pairwise, not two absolute scores subtracted.
- [ ] Cost is reported on its own axis and is not in the score.
