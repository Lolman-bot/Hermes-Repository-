# What counts as a divergence

Read this **before** prompting. The prompt interrupts whatever the user was doing, so it has to be
worth the interruption. A prompt that fires on a non-divergence trains the user to say no to all of
them, and then the skill is worthless.

The test is simple: **would someone maintaining this skill want to know?** If the honest answer is
no, stop silently.

## The three qualifying types

Use these exact values in the `divergence_type` frontmatter field.

### `fact-contradicted`

The skill asserts something as fact, and what you just observed disproves it.

This is the highest-value type, because a wrong fact in a skill propagates silently into every
session that loads it, including sessions where nobody thinks to check.

> **Worked example.** A skill notes that a connector's personnel lookups are blocked
> account-wide. A personnel-list call returns results. The note is stale: the capability works.
> Everything downstream of it ("don't bother trying", "use this workaround instead") is now wrong
> advice.

Also counts: a documented path that does not exist, a stated limit that is no longer the limit, a
tool named as unavailable that is available (or the reverse), a `hermes` CLI flag or slash command
that doesn't exist, a claimed permission or scope that turns out to differ.

### `workflow-gap`

The skill ran, but its steps were incomplete, stale, ambiguous, or led somewhere wrong. You got
there anyway, by working around it, asking the user, or figuring it out, and the next person will
have to do the same work again.

> **Worked example.** A skill tells you to find the repo clone at
> `$HOME/Documents/GitHub/Hermes-Repository-`. On this machine it's somewhere else. The skill does
> say to ask rather than guess, so nothing broke, but every run pays the same detour.

Also counts: a step that assumes a tool or MCP server the skill doesn't mention, an instruction two
people would read differently, a reference file that contradicts `SKILL.md`, an ordering that only
works by luck, a step that only works on one OS or one surface (CLI but not a gateway).

### `trigger-miss`

The right skill existed and did not fire, or the wrong one did.

Worth logging because it's fixed in exactly two places, the frontmatter `description` (60
characters, of which Hermes's skill index shows 57) and the body's `## When to Use`, and it is
invisible from inside the skill. Only the session that went without it can see it.

Record what the user actually typed. The literal phrasing is the evidence; a paraphrase is not,
because the fix is a wording change and wording is the whole problem.

## Severity

| Severity | Means |
|---|---|
| `high` | It produced a wrong answer, or drove a wrong action, or would have if nobody had noticed. |
| `medium` | It cost real time, needed a correction, or forced a workaround. Nothing wrong shipped. |
| `low` | Cosmetic, stylistic, or a stale detail nobody would act on. |

When torn between two, take the **lower** one. Severity is a triage signal, and inflating it makes
the whole set useless for sorting.

## Not a divergence: do not prompt

- **Your own reasoning errors.** You misread a file, forgot a constraint, or made a bad call and the
  user corrected you. If no skill told you the wrong thing, there is nothing to log.
- **The user changing their mind.** A revised requirement is not a defect in a skill.
- **A genuine one-off.** A connector timed out, a network call failed, a service was briefly down.
  Log it only if the skill *claims* it never happens.
- **Something already logged this session.** One divergence, one file.
- **A skill you never actually loaded.** You cannot report on instructions you did not read. Load it
  with `skill_view` first, or say nothing.
- **A disagreement of taste.** If you cannot say what it would cause to go wrong, it does not go in
  the log.
- **A difference that only exists in a locally patched copy.** If `skill_manage` or the curator has
  already changed the installed skill on this machine, compare against the repo version before
  calling it a divergence.

## When you are unsure

Prompt. A user saying "no, skip it" costs one click; a lost finding costs the next session that
loads the skill. But make the question honest about the uncertainty: say what you observed and that
you are not certain it generalises.
