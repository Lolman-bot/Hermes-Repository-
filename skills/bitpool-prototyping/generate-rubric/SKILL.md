---
name: generate-rubric
description: "Use when a loop-engineering run needs its scoring rubric."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, prototyping, loop, rubric, criteria, evaluation]
    category: bitpool
    related_skills: [project-context, design-generation, loop-engineering-start]
---

# Loop Engineering — Generate Rubric

Step 3 of the loop-engineering workflow. Reads the project context that
`project-context` just captured, interviews the user to sharpen it, then elicits
4-6 weighted scoring criteria with observable scoring anchors and the pass
threshold, writes them to `.loop-engineering/rubric.json`, then hands off to
`design-generation`. This rubric is the single highest-leverage artifact in the
loop: if it is vague, the scores across passes are noise and the loop cannot
tell whether it is improving.

## When to Use

- Automatically invoked by `project-context` once
  `.loop-engineering/project-context.md` exists.
- The slash command `/generate-rubric` also works, but invoke it directly only
  if the user explicitly asks to build or rebuild the rubric for an existing
  loop-engineering run.

Don't use for:

- Starting a brand-new run from scratch — use `/loop-engineering-start` first,
  which sets up the run folder and hands off through `project-context`.

## Procedure

Ask the questions below **one at a time** — use `clarify` where the answer is a
choice, plain conversation where it is open-ended. Do not dump the whole
interview in one message.

1. **Read the project context.** Load `.loop-engineering/project-context.md`
   with `read_file` and list `.loop-engineering/reference/` with
   `search_files(target='files')` — both written by `project-context`. Record
   the description as `goal`; record the reference material paths as
   `source_files`. Done when `goal` and `source_files` are drafted.

2. **Interview to sharpen it — do not skip this.** A first description is
   underspecified almost every time; treat it as a draft, not a brief. Read
   it back to yourself and work out what's still genuinely unclear — who it's
   for, what's explicitly in and out of scope, any hard constraints (format,
   length, tone, technical limits), what "done" looks like in concrete terms,
   and whether there's an existing example, good or bad, to react to. Ask
   **several targeted questions, one at a time**, built from what's actually
   missing in *this* description — not a fixed checklist recited regardless
   of what they already said. Skip a question the description already
   answered; don't ask it just to have asked something.

   Fold every answer back into `goal` (and `source_files`, if they name more
   files). The criteria in the next step are built on this sharpened
   understanding, not on the original one-liner — an interview that gets
   skipped or rushed here is the most common way the whole rubric ends up
   scoring the wrong thing well. Done when every genuine gap has been asked
   about and folded into `goal`.

3. **Elicit criteria.** Ask for **4-6 named criteria**, each with a
   one-sentence description of what "good" looks like. A criterion may point
   at a reference file the design must be compared against — a brand guide, a
   spec, a competitor example, a style sheet. Record that path as
   `reference_file`.

   Push back gently outside the 4-6 range: fewer than 4 under-specifies
   quality and the loop converges on something thin; more than 6 dilutes each
   weight until scoring becomes noise.

   If the user is stuck, offer a starting set of **criteria names only** —
   weights, anchors and threshold are still asked for one at a time. Done when
   4-6 criteria have names and descriptions (or the user chose otherwise after
   the push-back).

4. **Draft scoring anchors — do not skip this.** For each criterion, write
   concrete, observable descriptions of three score bands:

   - `0-3` — what a failing version of this criterion actually looks like
   - `4-7` — what a partial / acceptable-but-flawed version looks like
   - `8-10` — what full satisfaction looks like

   Anchors must be **checkable by looking at the artifact**, not judgement
   words. "Clear" is not an anchor. "Every section opens with its conclusion;
   no paragraph exceeds 5 lines" is an anchor.

   Show the user the drafted anchors **in full, as they will be written to
   `rubric.json`** — a summary or "what good looks like" column is not the
   anchors — and ask them to correct anything that doesn't match what they
   meant. Ask this **in its own question, separate from the threshold and
   pass-cap questions** — bundling it with unrelated questions means the
   anchors themselves never get an explicit yes. This is the step that makes
   scores comparable across passes — without it, the same design can score 62
   and 78 on two runs and the loop will chase its own tail. Done when the user
   has explicitly approved the anchors.

5. **Weight each criterion.** Ask the user to rate the importance of each from
   **1 (nice to have)** to **10 (critical)**. Record as `importance`. Done when
   every criterion has an `importance`.

6. **Optional hard gates.** Ask whether any criterion is a *must-pass* — one
   where a bad score should sink the whole design no matter how well
   everything else does (common for compliance, brand, safety, or a hard
   technical constraint). If so, record `min_score` on that criterion. A
   design that scores below `min_score` on any gated criterion fails the pass
   regardless of its weighted total. Done when the user has answered.

7. **Set the threshold.** Ask for the minimum overall score (0-100) at which
   the loop should accept a design and stop. Suggest **80** if they're unsure.

   Sanity-check the answer: with a cap of 4 refinement passes, a threshold
   above ~90 across 5+ criteria is often unreachable and just burns the whole
   budget. If they pick something that high, say so once and let them decide —
   they may genuinely want the loop to grind and report a near miss. Done when
   `threshold` is set.

8. **Confirm the pass cap.** Default `pass_cap` is **4** refinement passes
   before the loop stops to check in. Mention it; change it if they want. Done
   when `pass_cap` is set.

9. **Write the run files.** Create `.loop-engineering/` in the current working
   directory if needed, then write `rubric.json` with `write_file`:

   ```json
   {
     "goal": "string",
     "source_files": ["optional/path.ext"],
     "criteria": [
       {
         "name": "string",
         "description": "one sentence on what good looks like",
         "importance": 7,
         "reference_file": "optional/path.ext",
         "min_score": 6,
         "anchors": {
           "0-3": "observable description of failure",
           "4-7": "observable description of partial success",
           "8-10": "observable description of full satisfaction"
         }
       }
     ],
     "threshold": 80,
     "pass_cap": 4
   }
   ```

   `reference_file` and `min_score` are optional — omit them rather than
   writing `null`. Also create `.loop-engineering/history.json` containing
   `[]`, and the empty folder `.loop-engineering/designs/`. Done when all three
   exist and `rubric.json` parses as JSON.

10. **Play it back.** Show the user a compact table of criteria, weights, gates
    and threshold, and ask for a final yes before generating. **Do not invoke
    `design-generation` until they answer.** A rubric error caught here costs
    one message; caught at pass 3 it costs the whole run. Done when the user
    has said yes.

11. **Hand off.** Once `rubric.json`, `history.json`, and `designs/` exist and
    the user has confirmed, invoke `design-generation`
    (`skill_view(name='design-generation')`, same as `/design-generation`).

## Scoring scale

Each criterion is scored **0-10** at evaluation time against its anchors. The
overall score is the importance-weighted average, rescaled to 0-100:

```
overall = 100 × Σ(score_i × importance_i) / Σ(10 × importance_i)
```

A design meeting every criterion fully scores 100. Missing a heavily-weighted
criterion costs more than missing a light one. Any criterion scoring below its
`min_score` fails the pass outright, whatever the weighted total says.

## Pitfalls

- **Judgement-word anchors.** "Clear", "engaging", "professional" can't be
  checked by looking at the artifact; rewrite them as observable statements.
- **Bundling the anchor approval with other questions.** The anchors then never
  get an explicit yes.
- **Reciting a fixed interview checklist.** Ask only what this description
  leaves genuinely unclear.
- **Writing `null` for optional fields.** Omit `reference_file` / `min_score`
  instead.

## Verification

- `.loop-engineering/rubric.json` parses, has 4-6 criteria (or a recorded user
  override), each with `importance` and all three anchor bands.
- `.loop-engineering/history.json` is `[]` and `.loop-engineering/designs/`
  exists.
- The user gave an explicit yes to the anchors and to the final play-back
  before `design-generation` was loaded.
