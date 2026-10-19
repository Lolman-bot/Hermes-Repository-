---
name: design-evaluation
description: "Use when a loop-engineering design needs scoring."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, prototyping, loop, evaluation, scoring, rubric]
    category: bitpool
    related_skills: [design-generation, review-solution, generate-rubric, loop-engineering-start]
---

# Loop Engineering — Design Evaluation

Step 5 of the loop-engineering workflow. Scores the current design against the
rubric's anchors, computes the weighted overall score, logs the pass to
`history.json`, and routes: threshold met → finish and report; missed within the
pass cap → `review-solution`; missed at the cap → report and ask the user
whether to keep looping. Grade this pass's artifact honestly, log it, and route
the loop.

## When to Use

- Automatically invoked by `design-generation` once a design is written.
- The slash command `/design-evaluation` also works, but invoke it directly
  only if the user explicitly asks to re-score an existing loop-engineering
  design.

Don't use for:

- Producing a design in the first place — use `/design-generation`.
- Working out why a design missed the threshold — use `/review-solution`.

## Procedure

1. **Read the rubric first.** Load `.loop-engineering/rubric.json` with
   `read_file` before looking at the design — criteria, `anchors`,
   `importance`, `min_score` gates, `threshold`, `pass_cap`. Load any
   `reference_file` a criterion names, in full (images via `vision_analyze`).
   You cannot score against a reference you haven't read. Done when the rubric
   and every reference file are read.

2. **Read the design.** Load `.loop-engineering/designs/design-v<N>.<ext>` and
   its `.rationale.md`. Judge **the artifact as it exists**, not the intent
   described in the rationale. If the rationale claims something the artifact
   doesn't actually deliver, score the artifact and note the discrepancy. For
   visual artifacts (HTML, images), render or screenshot them and inspect with
   `vision_analyze` / the browser tools rather than scoring markup alone. Done
   when the artifact itself has been examined.

3. **Score each criterion 0-10 against its anchors — blind.** Write all scores
   and their reasoning out in full before opening `history.json`. Those
   written scores are the blind record, and may only change in step 4 with a
   `calibration_notes` entry saying why. For each criterion record:

   - `score` (0-10),
   - `reasoning` — one or two sentences tying the score to the anchor band,
   - `evidence` — a direct quote, line reference, or specific element from the
     artifact that justifies it,
   - `gap` — what specifically would have to change to reach the next band.

   Every score needs evidence pointing at something concrete in the artifact.
   A score you cannot attach evidence to is a guess, and guesses across passes
   are indistinguishable from noise — which makes the entire loop useless.
   Done when every criterion has all four fields written out.

4. **Calibrate against history.** *Now* read `.loop-engineering/history.json`.
   For each criterion, compare this pass's score to the previous pass's score
   and reasoning. Ask: does the score difference match the actual difference
   in the artifacts? If a criterion is clearly better this pass but scored the
   same or lower — or clearly unchanged but scored higher — the drift is in
   the scoring, not the design. Correct it, and record the correction in
   `calibration_notes`. Do not adjust scores just to manufacture an upward
   trend. Done when every changed score has a `calibration_notes` entry.

5. **Compute the overall score.**

   ```
   overall = 100 × Σ(score_i × importance_i) / Σ(10 × importance_i)
   ```

   Round to one decimal. Then apply the gates: if any criterion with a
   `min_score` scored below it, the pass **fails** regardless of `overall`.
   Record `gate_failures` listing which. Done when `overall` and
   `gate_failures` are computed (do the arithmetic in `execute_code` or
   `terminal` Python, not in your head).

6. **Log the pass.** Append a record to `.loop-engineering/history.json`:

   ```json
   {
     "pass": 1,
     "design_file": ".loop-engineering/designs/design-v1.md",
     "attributes": { "structure": "...", "tone": "...", "length": "..." },
     "scores": [
       {
         "criterion": "string",
         "score": 7,
         "reasoning": "string",
         "evidence": "string",
         "gap": "string"
       }
     ],
     "overall": 74.3,
     "gate_failures": [],
     "calibration_notes": "string, or omitted",
     "outcome": "threshold_met | below_threshold | stopped",
     "review": null
   }
   ```

   `attributes` is copied from the rationale's attribute list. `review` is
   filled in later by `review-solution`; leave it `null` here. Done when
   `history.json` parses and its last record is this pass.

7. **Route.** Let `N` = this pass number, `cap` = `rubric.pass_cap`
   (default 4).

   | Condition | Action |
   |---|---|
   | `overall ≥ threshold` **and** no gate failures | Set `outcome: "threshold_met"`. Go to **Finish — success**. |
   | Below threshold (or a gate failed) **and** `N ≤ cap` | Set `outcome: "below_threshold"`. Report the score briefly, then invoke `review-solution` (`skill_view(name='review-solution')`). Do not ask permission — refining within the cap is what the user already signed up for. |
   | Below threshold (or a gate failed) **and** `N > cap` | Set `outcome: "below_threshold"`. Go to **Finish — cap reached**. |

## Finish — success

Report, then stop:

- the winning design (its path, and the artifact itself if it's short enough
  to show inline; on a messaging platform, attach it as
  `MEDIA:/absolute/path/to/design`);
- its overall score and the per-criterion breakdown;
- the score trajectory across every pass, so the user can see the improvement;
- one line on what got it over the line.

Then ask whether they'd like the design copied out of `.loop-engineering/` to
a real location in their project. Don't move it without asking.

## Finish — cap reached

Report, then ask:

- the most recent design and its score, plus which criteria and gates it
  missed;
- the full score history for every pass, per criterion — including which
  criteria have been stuck flat across passes, since those are where the
  approach itself, not the execution, is the problem;
- the best-scoring pass so far if it wasn't the last one. **Say so explicitly
  if an earlier design outscored the current one** — the loop does not
  guarantee monotonic improvement, and quietly presenting the latest as the
  best would be wrong.

Then ask the user with `clarify`: **continue the loop, or stop here?**

- **Continue** → invoke `review-solution`. The cap resets for another `cap`
  passes.
- **Stop** → set the last record's `outcome` to `"stopped"`, and offer to copy
  the best-scoring design out to a real location.

## Load-bearing rules — grade honestly

You are scoring an artifact you wrote a moment ago, and the pull toward
generous marking is strong and quiet. Two rules hold it in check:

- **Score the gap, not the effort.** Do not credit a criterion for being
  attempted, for being hard, or for being better than last time. The anchors
  are absolute — 8-10 means the 8-10 anchor is true of this artifact right
  now.
- **A pass with no 6s or below is a suspicious pass — as is a pass whose
  scores are near-uniform, or whose total lands within a point of the
  threshold.** If everything scored high but the artifact plainly still has
  room to improve, the scoring is wrong, not the design. Re-read the anchors
  and score again.

An inflated score ends the loop early and hands the user a worse design than
they asked for. That is the single worst outcome this workflow can produce.

**Option — fresh-context grader.** Because the generator's own context is the
source of that pull, steps 1-3 (and only those) may be handed to a subagent with
`delegate_task`: give it the absolute paths to `rubric.json`, the design, its
rationale and any reference files, plus the step 1-3 rules above, and ask for
the per-criterion `score`/`reasoning`/`evidence`/`gap` back. Don't give it
`history.json` (that keeps the blind record blind) or any hint of how the
design should score. Wait for its result, then do steps 4-7 yourself — a
subagent can't `clarify` with the user. The method is unchanged; only who
writes the blind scores differs.

## Pitfalls

- **Opening `history.json` before the blind scores are written.**
- **Scoring the rationale's claims instead of the artifact.**
- **Presenting the latest pass as the best** when an earlier one scored higher.
- **Moving the design out of `.loop-engineering/` without asking.**

## Verification

- The last record in `history.json` has a score, reasoning, evidence and gap
  for every rubric criterion, `overall` matches the formula, and
  `gate_failures` lists every gated criterion below its `min_score`.
- Every score changed during calibration has a `calibration_notes` entry.
- The route taken matches the table in step 7.
