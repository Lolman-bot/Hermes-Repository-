# The report, and the score out of 100

The report is the deliverable. It goes in the chat — no file unless the user asks for one.

## The score

The checklist is the finding; the score is a headline derived from it. It exists so a skill can be
compared to itself over time, and it is only worth having if the arithmetic is visible.

```
score = 100 × Σ(weight × value) / Σ(weight)        ✅ = 1   ⚠️ = 0.5   ❌ = 0
```

Criteria scored `—` (couldn't tell) are **excluded from both sums**. They don't pass and they don't
fail; they reduce the coverage, and you say so.

### Rounding grain

Round to match what the evidence supports. A score of 73 implies a resolution one run does not have.

| n | Round to | Example |
|---|---|---|
| 1 | nearest **5** | 65, 70, 75 |
| 2 | nearest **5**, reported as a range across the two runs | "65–80" |
| ≥ 3 | nearest **1**, with the Wilson interval on the success rate alongside | "72, success rate 6/8 → 41–93%" |

### Bands

Give the band as well as the number — it's what people actually remember.

| Score | Band | Reads as |
|---|---|---|
| 90–100 | **Healthy** | Did its job; findings are polish |
| 75–89 | **Sound, with gaps** | Worked, but something load-bearing was soft |
| 55–74 | **Unreliable** | Got there with help, or half the rules didn't bind |
| Below 55 | **Not doing its job** | The skill isn't causing the outcome; the model is |

State coverage next to the score whenever anything came out `—`: *"72 / 100, on 11 of 14 criteria —
three couldn't be evidenced."*

## The report shape

Six sections, in this order.

### 1. Headline

Two lines. The score with its band and coverage, and the single most important finding.

```
skill-health: draft-marketing-email — 72 / 100 (Unreliable), on 12 of 14 criteria.
The CDN image verification step ran, but nothing in the skill made it blocking —
two of three runs published with a dead image.
```

### 2. What was reviewed

The skill and its path, n and the exclusions, and where the records came from — this conversation,
session logs, or both. Short; four lines. A reader who disagrees with a finding needs to know what you
looked at before they can argue with it.

### 3. The checklist

Every criterion, with weight, verdict and quoted evidence — the format in `single-run-review.md`.
Group by verdict, ❌ first, then ⚠️, then `—`, then ✅. Nobody reads past the failures, so don't put
them last.

The ✅ block can be one line per criterion with no quote, as long as the quotes exist for anything
that isn't a clean pass.

### 4. The statistics — n ≥ 3 only

Omit this whole section at n=1 and n=2. Say "single-run review — no statistics at n=1" once, in
section 2, and don't apologise for it again.

At n≥3, in the order `multi-run-statistics.md` produces them: the rate with its Wilson interval,
pass@k / pass^k, the per-stage funnel if the skill is a chain, the attribute-analysis ranking, and the
cost table.

### 5. Recommended edits

The structural findings only, ranked by `weight × severity`. One block each:

```
1. [weight 3] Make CDN verification blocking
   Criterion:    Load-bearing rule 4 — "every image verified live before publish"
   Evidence:     Run 2, turn 19: publish ran after a 404 on hero.png, no stop.
   Trace:        SKILL.md:58 says "verify every image is live" but never says the
                 publish is gated on it.
   Fix:          Add "— and stop if any image 404s" to line 58.
   Class:        Structural
```

Then the logged one-offs and the unclassified findings, as a short list under a clear heading. These
are not proposed edits; label them so nobody applies them.

If there are no structural findings, say that in one line. A clean review is a real result and padding
it with invented improvements is how the next one gets ignored.

### 6. What I couldn't see

Anything that came out `—`, and why. Truncated context, a reference file whose read you couldn't
confirm, cost figures unavailable, a run you excluded and the reason.

Never omit this section to make the report look tidier. It is what makes the rest of it credible, and
a reader who spots a gap you didn't declare stops trusting the sections you did.

## Then ask

End the report with the step-8 question and nothing else — no preamble about how the changes could be
applied. Ask whether to implement, and wait.

If yes, go to `apply-the-fixes.md`. If no, stop. Nothing has been edited at this point and nothing
should be.

## Before you leave this step

- [ ] The score's arithmetic is visible — weights, verdicts, both sums.
- [ ] Rounding grain matches n.
- [ ] Band and coverage are both stated.
- [ ] The checklist leads with the failures.
- [ ] No statistics section at n<3.
- [ ] Every recommended edit is structural, ranked, and passes the counterfactual test.
- [ ] "What I couldn't see" is present and honest.
