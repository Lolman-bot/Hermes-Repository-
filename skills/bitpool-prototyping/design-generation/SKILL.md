---
name: design-generation
description: "Use when a loop-engineering pass needs a new design."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, prototyping, loop, design, generation]
    category: bitpool
    related_skills: [generate-rubric, design-evaluation, review-solution, loop-engineering-start]
---

# Loop Engineering — Design Generation

Step 4 of the loop-engineering workflow. Produces (or re-produces) the actual
artifact against the rubric, applying the review directives from the previous
pass, then hands off to `design-evaluation` for scoring. Everything needed is on
disk in `.loop-engineering/`. It never grades its own work.

## When to Use

- Automatically invoked by `generate-rubric` on pass 1 and by `review-solution`
  on every refinement pass.
- The slash command `/design-generation` also works, but invoke it directly
  only if the user explicitly asks to regenerate a design for an existing
  loop-engineering run.

Don't use for:

- Starting a new run — use `/loop-engineering-start`.
- Scoring a design that's already written — use `/design-evaluation`.

## Procedure

1. **Read all context** with `read_file` (images via `vision_analyze`):
   - `.loop-engineering/rubric.json` — goal, criteria, **anchors**, weights,
     `min_score` gates, threshold.
   - Every file named in `source_files` and in any criterion's
     `reference_file`. **Read them in full.** A criterion that names a
     reference document cannot be satisfied — or fairly scored — from a
     skim of it.
   - `.loop-engineering/history.json`. If non-empty this is a refinement
     pass: read the last record's `scores` (per-criterion, with the
     evaluator's reasoning and evidence) and its `review.directives`.
   - The previous design and its rationale in `.loop-engineering/designs/`.

   The pass number `N` is `len(history) + 1`. Done when every listed file has
   been read in full and `N` is known.

2. **Aim at the anchors, not at the description.** Each criterion's `8-10`
   anchor is a concrete, checkable statement of what full marks looks like.
   Treat it as the specification. Before writing, note for each criterion what
   specifically in the artifact will make an evaluator able to say the 8-10
   anchor is met. Done when every criterion has that note.

3. **Budget effort by weight, and clear the gates first.** An importance-9
   criterion deserves roughly three times the design attention of an
   importance-3 one. Any criterion with a `min_score` is a hard gate — a
   design that fails one is rejected outright no matter how good the rest is,
   so satisfy those before optimising anything else. Done when the gated
   criteria are planned for first.

4. **On a refinement pass, apply the review directives.**
   `review.directives` is an ordered list of specific changes. Work through
   them. Two standing rules:

   - **Don't regress what already scored well.** Chasing a weak criterion at
     the cost of a strong one usually leaves the weighted total flat. If the
     review explicitly says a trade is worth it, make it and note it;
     otherwise preserve the high-scoring elements and say which ones you're
     holding fixed.
   - **Change something real.** A pass that produces a cosmetically different
     artifact with the same underlying weaknesses is a wasted pass. If the
     directives are all minor but the gap to the threshold is large, make a
     structurally different attempt instead — different approach, structure,
     or framing — and say plainly that you did.

   Done when every directive is applied or explicitly set aside with a reason.

5. **Write the artifact** with `write_file` to
   `.loop-engineering/designs/design-v<N>.<ext>`, choosing an extension that
   fits (`.md`, `.html`, `.py`, …). Never overwrite a previous version; the
   loop's whole method depends on the history. For an artifact with no natural
   file form — a strategy, a plan, an argument — still write it to `.md`. The
   loop scores files. Done when the new file exists and no earlier version
   changed.

6. **Write the rationale** to
   `.loop-engineering/designs/design-v<N>.rationale.md`, one to three
   paragraphs covering:
   - the main design choices and which criteria each one targets;
   - what you deliberately traded off, and why;
   - an explicit **attribute list** for this candidate — the dimensions that
     vary between attempts (structure, format, tone, density, length,
     approach, feature set, whatever applies here), each with the value this
     version chose.

   That attribute list is not decoration. `review-solution` reads it to work
   out which attributes actually move the score across passes; without it the
   review degrades to guesswork. Done when the rationale exists with an
   attribute list.

7. **Hand off.** Invoke `design-evaluation`
   (`skill_view(name='design-evaluation')`, same as `/design-evaluation`),
   giving it the pass number and the path to the design just written.

## Load-bearing rules

- **Do not grade your own work here.** Don't predict, claim, or imply how well
  this design will score — not in the rationale, not in the handoff. That is
  `design-evaluation`'s job, and seeding it with an optimistic self-assessment
  measurably inflates the grade, which is the one failure mode that quietly
  breaks the entire loop. State what you built and why. Stop there.
- **Never overwrite a previous design version.**
- **Every pass writes a file**, even for artifacts with no natural file form.

## Pitfalls

- **Skimming reference files.** A criterion tied to a reference can't be met
  from a skim; read it in full.
- **Cosmetic passes.** Same weaknesses, new wording = a wasted pass.
- **Regressing strong criteria** while chasing a weak one.

## Verification

- `.loop-engineering/designs/design-v<N>.<ext>` and
  `design-v<N>.rationale.md` exist; earlier versions are untouched.
- The rationale has an attribute list and contains no predicted score.
- `design-evaluation` was loaded with the pass number and design path.
