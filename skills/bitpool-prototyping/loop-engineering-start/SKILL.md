---
name: loop-engineering-start
description: "Use when starting a rubric-scored design-improvement loop."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, prototyping, loop, iteration, rubric, design, evaluation]
    category: bitpool
    related_skills: [project-context, generate-rubric, design-generation, design-evaluation, review-solution]
---

# Loop Engineering — Start

Entry point for the loop-engineering workflow — an iterative, rubric-scored
design-improvement loop (generate → evaluate → review → regenerate) that keeps
refining an artifact until it clears a quality threshold. Domain-agnostic:
documents, code, UI layouts, copy, presentations or anything else the agent can
produce. This is step 1 of 6 — it confirms intent, sets up the run folder, and
hands off to `project-context`; it does not capture context, define criteria, or
generate anything itself.

```
loop-engineering-start → project-context → generate-rubric → design-generation → design-evaluation
                                                                    ↑                    │
                                                                    └── review-solution ←┘
```

The loop exits when the design clears the rubric threshold, when the pass cap
is reached and the user declines to continue, or when the user stops it.

Hand-offs between the six skills are explicit: "invoke `<skill>`" means load it
with `skill_view(name='<skill>')` and follow it, exactly as if the user had typed
`/<skill>`.

## When to Use

- The user types `/loop-engineering-start`.
- Proactively, when the user says "start a loop", "loop engineer this", "run the
  loop-engineering process", or asks to iteratively improve a design, document,
  or piece of content against explicit weighted criteria.

Don't use for:

- Scheduling or repeating a prompt on a timer — that's a scheduled job
  (`cronjob`), not this loop.
- Capturing context, writing criteria or generating a design directly — those
  are `/project-context`, `/generate-rubric` and `/design-generation`, reached
  through this skill.

## Run state

All state for one run lives in a `.loop-engineering/` folder in the current
working directory:

```
.loop-engineering/
  project-context.md              — the user's brief (written by project-context)
  reference/                      — copied reference material
  rubric.json                     — goal, criteria, anchors, weights, threshold
  history.json                    — one record per pass: scores, overall, review
  designs/
    design-v1.<ext>               — the artifact produced on pass 1
    design-v1.rationale.md        — why it was built that way
    design-v2.<ext>
    ...
```

Nothing is written outside this folder unless the user asks for the winning
design to be copied somewhere specific at the end.

## Procedure

1. **Confirm intent.** Confirm the user wants to start a loop-engineering run
   (`clarify`, yes/no), and tell them what they're signing up for in one
   breath: *you'll be asked for 4-6 weighted criteria and a pass mark; the
   agent then generates a design, scores it against those criteria, and
   self-refines up to 4 times, checking in with you before going further.*
   - If **no**: exit the skill. Do nothing further.
   - If **yes**: continue.

   Done when the user has answered yes or no.

2. **Check for an existing run.** Look for `.loop-engineering/` in the current
   directory with `search_files(target='files')`. A run is **unfinished** if
   `history.json` exists, is non-empty, and its last record has no
   `"outcome": "threshold_met"` and no `"outcome": "stopped"`.

   | Situation | Action |
   |---|---|
   | No folder, or folder with empty history | Go to step 3. |
   | Unfinished run, user wants to **resume** | Skip `project-context` and `generate-rubric`. Read the existing `rubric.json` and `history.json`, then jump to the correct point: if the last pass has scores but no review, invoke `review-solution`; if it has a review but no newer design, invoke `design-generation`; if the newest design is unscored, invoke `design-evaluation`. |
   | Unfinished run, user wants to **start fresh** | Rename the folder to `.loop-engineering-archive-<YYYYMMDD-HHMMSS>/`, then go to step 3. Never delete it. |
   | Finished run, user wants another | Same as start fresh — archive, then step 3. |

   Ask which they want with `clarify`; don't guess. Show them the goal and last
   score from the existing run so the choice is informed.

   Done when there is no live run in the way, or the resume target is invoked.

3. **Hand off.** Invoke `project-context` to capture what the user is building
   before any criteria get defined. Do not ask context or criteria questions
   yourself — that is `project-context`'s and `generate-rubric`'s job. Done when
   `project-context` is loaded and running.

## Load-bearing rules

- **On a fresh run, `project-context` is always next** — never invoke
  `generate-rubric`, `design-generation`, `design-evaluation`, or
  `review-solution` directly, so that nothing is ever generated before the
  project's context is captured and a rubric exists to judge it. The resume
  path in step 2 is the only exception, and only because a rubric already
  exists on disk.
- **Never delete a previous run.** Archive by renaming; the history is the
  method.

## Pitfalls

- **Confusing this with a timer.** "Loop" here means generate → score → refine,
  not a recurring schedule.
- **Guessing resume vs fresh.** An unfinished run on disk always gets an
  explicit choice, with its goal and last score shown.

## Verification

- The user confirmed intent before anything was written.
- Any earlier `.loop-engineering/` folder still exists (resumed, or renamed to
  `.loop-engineering-archive-<timestamp>/`).
- The next skill loaded was `project-context` (fresh run) or the step the resume
  table names.
