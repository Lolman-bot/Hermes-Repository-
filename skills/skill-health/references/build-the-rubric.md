# Building the rubric from the skill's own words

The rubric is not yours. It comes out of the `SKILL.md` of the skill under test, and every criterion
must be traceable to a line in it. This is what makes the review actionable: a ❌ points at a line
that already exists, so the fix has somewhere to go.

## Read first

- The skill's `SKILL.md` in full — frontmatter included, because activation is a criterion.
- Every `references/` file the run actually opened. Not all of them; a file the run never needed can't
  have caused a failure.
- The skill's own `## Reference files` index and any maintenance note at the end of `SKILL.md`. They
  usually name where the substance lives, which tells you whether a fix belongs in `SKILL.md` or a reference file.

## The seven default criteria

Every run gets these, whatever the skill is. They test the skill against its own claims.

| # | Criterion | What a ✅ looks like |
|---|---|---|
| 1 | **Fired at the right time** | The triggering request matches the `description` trigger or `## When to Use` (or was the `/skill-name` slash command), and no `Don't use for:` item applied. |
| 2 | **Followed its own route** | Every step in the skill's route ran, in the stated order, none skipped or merged. |
| 3 | **Honoured its load-bearing rules** | Each numbered rule in the skill, checked individually. One sub-item per rule. |
| 4 | **Read what it said it would read** | The reference files the route points at were actually opened, not paraphrased from the index table. |
| 5 | **Produced the stated deliverable** | The thing the skill says it produces exists, in the stated place, in the stated format. |
| 6 | **Stayed in scope** | No work the skill doesn't own, and no silent handoff it wasn't asked to make. |
| 7 | **Needed no correction** | The user didn't have to redirect, repeat themselves, or undo anything. |

Criterion 3 is not one line — **explode it**. A skill with nine load-bearing rules contributes nine
checklist sub-items, each cited separately. This is where most real findings come from, because a
load-bearing rule is by definition the thing that breaks the result when missed.

## Skill-specific criteria

Add one criterion per route step that has a checkable output. If the route says "show the diff and get
a yes before committing", that is a criterion with a clear ✅/❌ — not a restatement of criterion 2.

Cap the total at roughly 15 scored items, criterion-3 sub-items included. Past that the score stops
moving on anything that matters and every criterion becomes a rounding error.

## Weighting

Three tiers, and keep it coarse — fine-grained weights imply a precision the evidence doesn't support.

| Weight | For | Examples |
|---|---|---|
| **3** | The skill fails at its job if this is missed | Load-bearing rules; the deliverable existing; a required approval gate |
| **2** | The result is degraded but usable | Route order; reference files actually read; scope |
| **1** | Quality and polish | Formatting, naming, tone, house conventions |

Write the weight next to each criterion in the report so the arithmetic is checkable. A reader who
disagrees with the score should be able to see exactly which weight they'd argue with.

## When the skill has no explicit rules

Some skills — especially imported or older ones — have no numbered load-bearing rules and no ordered
route. Don't invent them and grade against your invention. Instead:

1. Score criteria 1, 5, 6 and 7, which need no internal structure to test.
2. Record "no explicit route" and "no load-bearing rules" as **findings in their own right**, and mark
   them structural. They are the highest-value fix available, and they're a house-rules failure.
3. Say plainly in the report that the score covers less ground than usual, and why.

A skill you can't build a rubric from is telling you what to fix first.

## Before you leave this step

- [ ] Every criterion names the `SKILL.md` line or section it came from.
- [ ] Criterion 3 is exploded — one sub-item per load-bearing rule.
- [ ] Weights are assigned and written down.
- [ ] Nothing in the rubric tests a behaviour the skill never claimed.
