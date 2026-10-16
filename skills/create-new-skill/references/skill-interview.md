# Route A — build the skill from scratch, with the user

The route for someone who has a job they do repeatedly and wants Hermes to do it the same way every
time. Assume they have never written a skill and don't want to learn what YAML frontmatter is.

## How to run the conversation

- **One question at a time.** Ask, listen, reflect it back in your own words, then move on.
- **Use `clarify` when there's a genuine choice** with a small set of answers (up to four choices;
  the user can always type their own). Use plain chat when the answer is prose — a description of
  their job can't be multiple choice. On a messaging gateway, keep choices short; they render as a
  numbered list.
- **No jargon.** Not "frontmatter", "description field", "reference file", "toolset". Say "the words
  that make it switch on", "the detailed instructions", "what it needs to be able to do".
- **Answer for them where you can.** If you can infer the name, the trigger words or the tools it
  needs, propose your answer and ask them to confirm.
- **Never invent the substance.** How their job actually gets done — the steps, numbers, rules,
  format — is theirs. If they're vague, ask for a real example of the finished thing.
- **Show your work.** After the interview, print the whole `SKILL.md` in chat before writing it.

## The eight questions

Ask in this order. Stop when you have enough — later questions are often already answered.

### 1. What's the job?

> "Tell me about the thing you want Hermes to do. Describe it the way you'd describe it to a new
> starter on your team."

Is this one repeatable job, or three? If three, say so and offer to build the most valuable one
first. A skill that tries to do everything fires at the wrong times.

### 2. When should it switch on?

> "What would you actually type or say when you want this? Give me two or three ways you'd ask."

And the inverse, which matters as much:

> "Is there anything close to this that it should stay out of?"

Their phrasings become the `## When to Use` bullets; the near-misses become the `Don't use for:`
list. The 60-character `description` is a compressed version of the trigger, not the whole list.

### 3. What comes out at the end?

> "When it's finished, what have you got? A file? A document? A message posted somewhere?"

Push for specifics — a filename, a format, where it lands. "A report" is not an answer; "a one-page
HTML file I can print to PDF" is.

### 4. Have you got a good example of one?

> "Do you have one you've already made that came out well? That's the most useful thing you can
> give me."

If they have one, read it in full. Anything byte-exact in it — a template, layout, logo, scaffold —
becomes an `assets/` or `templates/` file, copied verbatim with `terminal` `cp`. Anything that's a
rule or a step becomes `references/`.

### 5. What does it need to be able to do?

> "Does it need to read or write files, run commands, open a browser, search the web, or use a
> service like Jira or Drata?"

This becomes `## Prerequisites` and decides `platforms`:

- Hermes tools only, or cross-platform CLIs (`git`, `gh`, `python`) → `[linux, macos, windows]`.
- bash-only pipelines (`sed`, `awk`, `xargs` chains) → `[linux, macos]`, or rewrite in Python.
- A service like Jira, Drata or a BI database → an MCP server the user adds with `hermes mcp`.
  Name it as a prerequisite and say what the skill does without it.

### 6. What has to be true every single time?

> "Is there anything that must always happen, or must never happen? Something that would make the
> result wrong if it were missed?"

These become `## Load-bearing rules`. The highest-value question in the interview — ask it even if
you think you know.

### 7. What goes wrong?

> "When this job goes wrong — for you or a new starter — what's usually the cause?"

These become `## Pitfalls`: a rule plus one clause of why. Two real ones beat six invented.

### 8. What should it be called?

Propose the name yourself, then confirm:

> "I'd call it `[proposed-name]`, so you'd type `/[proposed-name]`. Does that read right?"

Lowercase, hyphen-separated, an action or a subject — `draft-marketing-email`, `bacnet-diagnostics`.
Not `helper`, not `tool2`. Check it isn't already taken:

```bash
python -c "import pathlib,sys; p=pathlib.Path('skills',sys.argv[1]); print('TAKEN' if p.exists() or pathlib.Path('retired',sys.argv[1]).exists() else 'free')" "[proposed-name]"
```

## Turning the answers into files

Copy `assets/SKILL.md.template` and fill it in:

| From the interview | Goes in |
|---|---|
| Q1, Q3 — the job and deliverable | `# Title` intro and the `## Procedure` steps |
| Q2 — phrasings and near-misses | `## When to Use` + `Don't use for:`, and the ≤ 60-char `description` |
| Q5 — capabilities | `## Prerequisites` and `platforms` |
| Q6 — what must always hold | `## Load-bearing rules` |
| Q7 — what goes wrong | `## Pitfalls` |
| Sometimes-needed detail | one `references/<topic>.md` per coherent topic |
| Q4 — byte-exact material | `assets/` or `templates/`, copied verbatim |

The `description`: `"Use when <trigger>. <behaviour>."`, ≤ 60 characters, double-quoted. Measure
it, don't estimate:

```bash
python -c "import sys; d=sys.argv[1]; print(len(d), d[:57])" "Use when ..."
```

The first 57 characters are what the skill index shows — make sure the trigger reads right there.

Sizing: `SKILL.md` ~100-200 lines. Past ~200 there's almost always a reference file hiding in it.
Each Procedure step ends with "Done when ..." — a criterion someone could check.

## Before you leave this route

Fix rather than report:

- [ ] `name` matches the proposed folder name and slash command.
- [ ] Frontmatter matches the README's shape exactly, `version: 1.0.0`.
- [ ] `description` ≤ 60 chars, starts `Use when`, ends `.`, quoted.
- [ ] Body sections in house order; every Procedure step has a completion criterion.
- [ ] Every support file named exists, and every file in the folder is named.
- [ ] Nothing tells the skill to fetch its own instructions from a wiki, page or API.
- [ ] The user has seen the full `SKILL.md` in chat and said yes.

Then go to `SKILL.md` step 3.
