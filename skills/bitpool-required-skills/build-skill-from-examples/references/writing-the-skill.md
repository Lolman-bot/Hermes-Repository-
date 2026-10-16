# Writing the skill (steps 5 and 6)

Turn the examples (or their confirmed descriptions) and the approved diagram into a skill folder at
`$HERMES_HOME/build-skill/<skill-name>/skill/`. Start from `/create-new-skill`'s skill template if it
ships one (`skill_view(name="create-new-skill")` lists its files), copied, not retyped; otherwise
use the frontmatter block in the repo `README.md`'s house rules.

## Where each part comes from

| Part of the new skill | Comes from |
|---|---|
| **Name** | Ask. Propose one in lowercase-with-hyphens that says what it does, e.g. `monthly-energy-report`, and let the person change it. It becomes the folder name and the `/slash-command`. |
| **What it does** (title + opening paragraph) | The output examples or description: what the person ends up with. |
| **The procedure** (numbered steps) | The diagram — one step per box, in order. Question boxes become "if ... then ..." steps; each answer path is spelled out. Give each step a checkable "done when". Don't add steps the diagram doesn't have; ask instead. |
| **The load-bearing rules** | What was the same in every output example (or what the description says must look the same every time), plus anything the person said must always or never happen. Ask: "What would make the result wrong if it were missed?" Each rule gets a reason. |
| **When it switches on** | Ask how they'd actually ask for this job, in their own words. The shortest trigger goes in the `description` ("Use when ..."); two or three real phrasings go in `## When to Use`. |
| **What it stays out of** | Ask what this job is easily confused with, and which skill handles that instead. Check `/skills-catalogue` for overlaps. These become the `Don't use for:` list. |
| **What it needs** | The file types in the examples and what the steps do. Name the Hermes tools in the steps (`read_file`, `write_file`, `terminal`, `clarify`, `skill_view` for the `pdf`/`xlsx`/`docx` skills, ...), and set `platforms` from what actually runs. |

## What splits out of SKILL.md

Keep `SKILL.md` to the procedure, the rules and an index (roughly 100-200 lines). Move detail out:

- **`references/`** — how to read the input files, the format rules for the output, worked examples
  in prose, lookup tables. One file per topic.
- **`assets/`** — anything the output must match exactly: a template, a layout, a logo, a
  boilerplate paragraph. Copied byte for byte with `terminal` `cp` from a cleaned example
  (examples-intake.md, sensitive content).
- **`scripts/`** — only if a step is a repeatable calculation or transformation better run than
  described. Prefer standard-library Python so it runs on every platform.

## House rules to meet now

The repo `README.md` is the source of truth and `/create-new-skill` checks them again, but meet them
here so step 6 is clean:

- Frontmatter: `name` (== folder), quoted `description` of 60 characters or fewer that starts
  `Use when` and ends with a period, `version: 1.0.0`, `author: Bitpool, Hermes Agent`,
  `license: Proprietary`, `platforms`, and `metadata.hermes` with `tags` (including `bitpool`),
  `category: bitpool` and `related_skills` (only skills in the repo).
- Body order: title + intro, `## When to Use` (with `Don't use for:`), `## Prerequisites` if any,
  `## Procedure`, `## Load-bearing rules`, `## Pitfalls`, `## Verification`, `## Reference files`.
- Every file named in `SKILL.md` exists, and every file in the folder is named in `SKILL.md`.
- No `../` paths, no machine-local paths (use `$HERMES_HOME`), nothing fetched from the web at run
  time.
- No real customer data, names or figures anywhere in the folder.

## Step 6 — showing it

Print the whole `SKILL.md` in the chat, then list every other file with one line on what it holds.
Then point out, in plain words, anything you added that the person didn't say directly — every
rule, step or trigger phrase you inferred. Ask: "Does this read like your job?" Change what they ask
for and show it again. Move to step 7 only on an explicit yes.

If either end was described rather than shown, say so here — "the input side of this was built from
your description, not a real file" — and suggest trying the skill on a real job before it's
published. (To try it locally first, the person can copy the folder into
`$HERMES_HOME/skills/<category>/<skill-name>/` and run `/reload-skills`; remove it again before the
repo version is installed, or the two will shadow each other.)
