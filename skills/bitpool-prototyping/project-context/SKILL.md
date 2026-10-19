---
name: project-context
description: "Use when a loop-engineering run needs its project brief."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, prototyping, loop, iteration, context, brief]
    category: bitpool
    related_skills: [loop-engineering-start, generate-rubric]
---

# Loop Engineering — Project Context

Step 2 of the loop-engineering workflow. Captures what the user is trying to
build or improve, in their own words, gathers any reference material (photos,
documents, existing files) they want considered, writes it to
`.loop-engineering/project-context.md`, copies the reference material into
`.loop-engineering/reference/`, then hands off to `generate-rubric`. This is the
raw material `generate-rubric` interviews against — thin or vague here means the
interview in the next step has nothing solid to sharpen.

## When to Use

- Automatically invoked by `loop-engineering-start` on a fresh run.
- The slash command `/project-context` also works, but invoke it directly only
  if the user explicitly asks to rewrite the context for an existing
  loop-engineering run.

Don't use for:

- Defining scoring criteria, weights, or a pass threshold — that's
  `/generate-rubric`'s job, not this one.
- Starting a brand-new run from scratch — use `/loop-engineering-start` first,
  which sets up the run folder.

## Procedure

1. **Ask for the project context.** Ask the user to describe, in their own
   words, the project they want to complete — what it is, and what "done"
   looks like to them. Let them write as much or as little as they want; this
   is a first draft, not a final brief. Do not interview or push back on it
   yet — sharpening it is `generate-rubric`'s job. This skill's job is only
   to capture it faithfully and completely. Done when you have their
   description.

2. **Ask for reference material.** Ask whether there's anything else worth
   considering — photos, documents, an existing file the project builds on,
   a competitor example, a style guide. This is optional; if they have
   nothing, move straight to step 4. Done when they've named files or said
   there are none.

3. **Copy reference material in.** Create `.loop-engineering/reference/` if
   it doesn't exist. For each file the user points to (a path, or a file they
   attached in chat — use the local path Hermes gives for the attachment), copy
   it in verbatim with `terminal` (`cp`/`copy`, or a Python `shutil.copy2`
   one-liner), keeping the original filename (add a numeric suffix on a
   collision). Never modify or move the original — copy only. If a path
   doesn't resolve, say so and ask for a corrected path rather than silently
   dropping it. Done when every named file is in `reference/` or the user has
   withdrawn it.

4. **Write `project-context.md`** to `.loop-engineering/` with `write_file`:

   ```markdown
   # Project Context

   <the user's description, verbatim or lightly cleaned up for readability —
   never summarised or reinterpreted>

   ## Reference material
   - reference/<filename> — <one line on what it is and why it's relevant,
     from the user, not invented>
   ```

   If there was no reference material, keep the `## Reference material`
   heading with a single line saying so, rather than omitting the section.
   Done when the file exists with both sections.

5. **Hand off.** Invoke `generate-rubric` (`skill_view(name='generate-rubric')`,
   same as `/generate-rubric`). Done when it is loaded and running.

## Load-bearing rules

- **Don't do generate-rubric's job.** Don't ask about criteria, weights, or a
  pass threshold here — that's a separate interview, and doing it here means
  the user answers overlapping questions twice. This skill only establishes
  *what* the project is; the next skill decides *how it will be judged*.
- **Capture, don't reinterpret.** The description goes in verbatim or lightly
  cleaned; reference-file notes come from the user, not invented.
- **Copy only.** Originals are never modified or moved.

## Pitfalls

- **Silently dropping a bad path.** Ask for a corrected one instead.
- **Omitting the reference section when empty.** Keep the heading with a
  one-line "none" so later skills can tell nothing was supplied.

## Verification

- `.loop-engineering/project-context.md` exists with `# Project Context` and
  `## Reference material`.
- Every file listed under Reference material exists in
  `.loop-engineering/reference/`.
- No criteria, weight or threshold question was asked in this step.
