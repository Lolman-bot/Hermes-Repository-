---
name: review-solution
description: "Use when a loop-engineering design missed its threshold."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, prototyping, loop, review, analysis, pareto]
    category: bitpool
    related_skills: [design-evaluation, design-generation, loop-engineering-start]
---

# Loop Engineering — Review Solution

Step 6 of the loop-engineering workflow. The design missed the threshold: work
out *why*, in a way that makes the next attempt better rather than merely
different, and write directives for it. Checks in with the user on this pass's
evaluator feedback and any earlier pass first, then analyses the scoring history
— attribute analysis, Pareto fronts, pairwise ranking, perturbation and
recombination, scaling the statistical rigour to how many scored candidates
exist — writes an ordered list of concrete directives, and sends the loop back
to `design-generation`.

## When to Use

- Automatically invoked by `design-evaluation` when a design misses the
  threshold.
- The slash command `/review-solution` also works, but invoke it directly only
  if the user explicitly asks to re-review a loop-engineering run.

Don't use for:

- Scoring a design that hasn't been graded yet — use `/design-evaluation`.
- Producing the next design once directives already exist — use
  `/design-generation`.

## Procedure

1. **Load everything.** Read `.loop-engineering/rubric.json`, the whole of
   `.loop-engineering/history.json`, and every design + rationale in
   `.loop-engineering/designs/` with `read_file`. Let **N** = number of scored
   candidates in history. Note this pass's evaluator feedback specifically —
   the per-criterion scores and `gap` fields `design-evaluation` just wrote —
   since that's what gets shown to the user in step 2, before any of your own
   analysis exists yet. Done when all files are read and N is known.

2. **Checkpoint with the user before analysing.** Show the user where the loop
   stands and give them a chance to steer it *before* the analysis locks in a
   direction. The loop should never analyse on AI-only judgment alone when a
   person has an opinion about where an earlier pass went wrong — that is
   exactly how the loop keeps building on a bad design instead of correcting
   it.

   Show, in one short message: the score trajectory across every pass so far
   (pass N → overall, one line each), and this pass's evaluator feedback — the
   per-criterion scores and `gap` fields from step 1. Then ask, plainly:

   > "Here's how this pass scored and what the evaluator flagged. Anything
   > you'd like changed about pass 1, pass 2, etc. — or about this pass's
   > feedback — before I work out what to change next?"

   - **They name something specific** ("pass 2's structure was better than
     pass 3's", "keep pass 1's opening, drop the table from pass 3", "ignore
     the evaluator's note about X, that's intentional") — record it verbatim.
     It becomes the highest-priority input to steps 3-4: the analysis and the
     directives it produces must account for it, ahead of the automated
     findings where the two conflict.
   - **They say go ahead, or have nothing to add** — proceed on the evaluator
     feedback alone.

   Record what they said, or `"none"` — it goes into `review.user_feedback` in
   step 5. Wait for their answer before continuing to step 3 — don't treat
   silence or an assumption of "obviously fine" as a response. Done when the
   user has replied.

3. **Pick your tier.** The six techniques are the same ideas at three levels
   of rigour, detailed in `references/analysis-techniques.md` (read it with
   `read_file`). **Run the tier that matches N.** Running a statistical method
   on 3 data points produces a confident-sounding coefficient that is pure
   noise — and a directive built on noise is worse than no directive, because
   it looks justified.

   | N | Tier | Run |
   |---|---|---|
   | 1-2 | **Diagnostic** | §A |
   | 3-6 | **Comparative** | §A + §B |
   | 7+ | **Statistical** | §A + §B + §C |

   State which tier you're running and why, in one line. Never present a
   Comparative-tier finding in Statistical-tier language. Where step 2
   produced specific user input, weave it into this analysis rather than
   treating it as a separate afterthought — e.g. if they said pass 2's
   structure held up better, that constrains which attribute the Pareto-front
   and recombination steps should treat as worth keeping. Done when the tier's
   techniques have been run and findings written. (Statistical-tier arithmetic
   goes through `execute_code` or `terminal` Python, not mental maths.)

4. **Write the directives.** Distil everything into an **ordered list of 3-6
   concrete, actionable directives** for the next attempt. Ordered by expected
   score impact — importance-weighted gap size, gates first. If the evidence
   genuinely supports fewer than three, open the directives section with one
   explicit line: "N directives given — evidence does not support more,
   because: <reason>." Do not give fewer than three without that line.

   Each directive states **what to change**, **which criterion it targets**,
   and **what evidence supports it**. Compare:

   - ✗ *"Improve clarity."*
   - ✓ *"Replace the three prose paragraphs in §2 with a comparison table — Scanability scored 4/10 (importance 9) and its gap field names dense prose; the two table-based candidates both scored ≥7 there."*

   Where step 2 gave specific user input, its instructions win over the
   automated analysis wherever the two disagree — say so explicitly in the
   directive rather than quietly picking one.

   Also record, explicitly:

   - **Hold fixed** — the elements scoring well that the next pass must not
     regress.
   - **Confidence** — one line on how much the analysis actually rests on.
     With N=2 say so plainly. Overstating confidence here compounds through
     every later pass.

   Done when there are 3-6 directives (or the explicit fewer-than-three line),
   a hold-fixed list and a confidence line.

5. **Persist and hand off.** Write the review into the **last record** of
   `.loop-engineering/history.json`, replacing its `review: null`:

   ```json
   "review": {
     "tier": "diagnostic | comparative | statistical",
     "n_candidates": 3,
     "attribute_table": [ { "pass": 1, "attributes": {}, "scores": {}, "overall": 0 } ],
     "findings": ["string"],
     "pareto_front": [2, 3],
     "directives": [
       { "change": "string", "targets": "criterion name", "evidence": "string" }
     ],
     "hold_fixed": ["string"],
     "confidence": "string",
     "user_feedback": "string, or \"none\""
   }
   ```

   Then invoke `design-generation` (`skill_view(name='design-generation')`,
   same as `/design-generation`) for the next pass. The trajectory was already
   shown in step 2 — no need to repeat it here. Done when `history.json` parses
   with the review in its last record and `design-generation` is loaded.

## Load-bearing rules

- **User checkpoint first.** No analysis before the user has answered step 2;
  their specific input outranks automated findings where they conflict.
- **Tier matches N.** No statistics on fewer than 7 candidates.
- **Don't manufacture insight.** If the history genuinely doesn't support a
  conclusion — N is small, scores are flat across dissimilar candidates, no
  attribute separates the good from the bad — say that, and fall back to the
  evidence-backed `gap` fields from the evaluator. "Not enough data to tell
  which attributes matter; working directly from the scoring gaps this pass"
  is a completely legitimate review, and a far more useful one than an
  invented pattern.

## Pitfalls

- **Vague directives** ("improve clarity") — each needs change, target
  criterion and evidence.
- **Overstated confidence** at N=2 compounds through every later pass.
- **Quietly overriding the user.** Where their input and the analysis
  disagree, say which won and why.

## Verification

- The last `history.json` record has a `review` with `tier` matching N's band,
  3-6 directives (or the explicit fewer-than-three line), `hold_fixed`,
  `confidence` and `user_feedback`.
- The user's step-2 reply (or `"none"`) is recorded verbatim.
- `design-generation` was loaded next.

## Reference files

| File | Covers |
|---|---|
| `references/analysis-techniques.md` | The six techniques behind step 3's tier table — §A diagnostic, §B comparative, §C statistical — full detail on each. |
