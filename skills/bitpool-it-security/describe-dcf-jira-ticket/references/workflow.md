# Describe DCF Jira Ticket — Bitpool context and full workflow

The detailed Bitpool context and the nine-step workflow behind `/describe-dcf-jira-ticket`. SKILL.md
carries the golden rules and the condensed route; this file carries every step in full. Read it
whole before Step 1. Golden rules are cited by number ("rule 3") and live in SKILL.md.

Jira calls (`getJiraIssue`, `editJiraIssue`, `addCommentToJiraIssue`, `getTransitionsForJiraIssue`,
`transitionJiraIssue`) are the Atlassian MCP server's tools; `Drata_*` calls are the Drata MCP
server's tools. If the names differ on this Hermes install, find them with `tool_search`.

## Bitpool context

- **Jira Cloud ID:** `bitpool.atlassian.net` · **Project:** `CSIP` (Cyber Security ISO27001 Project)
- **DCF ↔ CSIP linkage:** the control code is embedded in the parent title —
  `Drata | Bitpool | DCF-xxx | [Control Name]`. Find a control's ticket with
  `project = CSIP AND text ~ "DCF-xxx"`.
- **These tickets are reported by `drata@bitpool.com`** and arrive with `description` set to Drata's
  stock one-liner. That stub is the thing this skill exists to replace.
- **Labels in use:** `Control` on every DCF parent; `AWS` additionally on infrastructure controls —
  a useful (not authoritative) first signal for whether step 5 applies.
- **Consult `/ask-drata` before concluding a Drata record doesn't exist.** Search-mode `query`
  params are unreliable on this account; use structured list mode and follow `cursor` to `null`.

---

## Workflow — full step detail

### Step 1 — Resolve the ticket and read what's already there

Parse the URL (or key) to an issue key. `getJiraIssue` with
`fields: [summary, description, status, labels, assignee, reporter, updated, comment]` and
`responseContentFormat: "markdown"`.

Extract `DCF-xxx` from the summary. No DCF code in the title → **stop and ask**; do not infer it
from the control name (rule 4).

**Read the existing description now, not later.** It decides the write mode in step 7, and reading
it after you've drafted invites the temptation to overwrite. Classify it as one of:

- **stub** — Drata's stock one-liner and nothing else,
- **human** — contains notes, links, decisions, or anything not from Drata,
- **already-described** — carries a previous run's explainer.

**Read the comments too, and read the parent's comments even when a sub-task owns the question.** A
DCF parent's comment thread routinely carries the decisive fact: a vendor's written answer to a
scoping question, a decision taken and never folded into the description, a blocking dependency on
another ticket. Comments do not propagate between parent and sub-task, so an empty comment list on
the sub-task proves nothing about the parent — fetch the parent's separately. Anything a comment
settles is **verified** for rule 3 purposes, so don't write it up as an open question — but the
comment stays the home of what it says. State the requirement the settled fact implies and point
at the comment by its date (*"scope confirmed in the ticket comment of `<YYYY-MM-DD>`"*); never copy
its values — a vendor's answer, names, dates, figures — into the description.

### Step 2 — Pull the real Drata control record (READ-ONLY)

`Drata_searchControls` for `DCF-xxx`. Capture and keep **verbatim**: `code`, `name`, `description`,
`activity` (Drata's evidence guidance), `flags` (`isReady`, `hasEvidence`, `hasPolicy`, `hasOwner`,
`isMonitored`, `hasTicket`), `frameworkTags`, `owners`, `updatedAt`. Note the date you read it: the
quote's lead-in carries it (rule 2).

Then `Drata_listRequirements` with `framework_tag=["ISO27001"]` and `expand=["controls"]` to get the
real clause / Annex A mapping (rule 8). Don't guess it — it changes the language the description is
allowed to use.

If Drata returns nothing, consult `/ask-drata` and paginate in list mode before concluding the
control doesn't exist. **Never draft against a control record you couldn't read** — the verbatim
quote is load-bearing and cannot be reconstructed from the ticket title.

### Step 3 — Classify the shape

`flags.isMonitored` plus the control's subject matter put it in one of three shapes, which decide
the structure of sections 3 and 4. The full detail is in `references/description-format.md`:

| Shape | Looks like | Sections 3–4 become |
|---|---|---|
| **Automated infrastructure** | AWS / M365 integration, `isMonitored: true` | Resource table + account-level enforcement argument; evidence as prose |
| **Tooling / endpoint** | application control, device management, a SaaS platform | Capability table + any known operational tension; evidence as bullets |
| **Governance / clause** | management review, competence, audit coordination | Mandatory inputs & outputs bullets + a **Concretely:** paragraph; evidence as bullets, optionally closing with *The audit question* |

### Step 4 — Bounded research

Establish what the control actually does, why it exists, and what concretely satisfies it at a
company shaped like Bitpool. Check `references/documentation-index.md` for an existing policy or
procedure in the control's domain, and search Jira for sibling DCFs that share a posture —
cross-references like *"Similar to DCF-75, the strongest posture is…"* are part of the house style
and genuinely useful.

The index is a snapshot, so cite a page it lists, but don't write *"no procedure exists"* on the
strength of an absent entry — either phrase that section as a requirement, or ask the user. A
documentation gap belongs in the step 9 hand-back, never in the description.

**The ticket's own comments are a research source, and the cheapest one you have.** You already
pulled them in step 1 — read them before searching further. Scoping answers, decisions and blocking
dependencies land in comments far more often than they get folded back into the description.

**Bound it.** This is a ticket description, not a report. Research only what changes what someone
would *do*. If a detail wouldn't alter an action or an evidence choice, leave it out.

**Where you don't know a Bitpool fact, either query it (step 5) or phrase it as a requirement.**
Never fill the gap with a plausible assumption (rule 3).

### Step 5 — Ground it in live AWS state (ask first)

**The relevance test:** does whether this control is satisfied depend on how AWS is configured? If
yes, it's in scope. The `AWS` label is a hint, not the test — some `Control`-only tickets are
genuinely infrastructure-shaped and some `AWS`-labelled ones turn on policy.

If relevant: **name the checks you'd run and ask.** On a yes, `/aws-context` once if the session
isn't already confirmed, then `/aws-query` for the calls — that skill is the single owner of AWS
call construction; never inline CLI commands, profile names, or account IDs here. **Budget: ≤8
calls for one control.**

Then:

- **Observations go in the report, not the description.** What you saw — settings, gaps, counts,
  account and resource names — is current state. Report it to the user at step 8, headed with the
  date (*"observed `<YYYY-MM-DD>`"*); that is chat, out of the register, so be as specific as is
  useful. A date does not make an observation durable: a dated gap in the description still reads
  as the control's position after it is fixed, and `/drata-control-insights` reads this description.
  Their durable home is the **dated observations comment** offered at step 8 (rule 6); if the user
  declines it, the chat report is their only home.
- **The description keeps the requirement.** An observation changes the framing — which rows the
  *What to demonstrate* table carries, which posture the posture block argues for, which check an
  auditor will run. Name the check and the target posture, never the result.
- **At most one anchored verification line**, and only where the explainer's own claim rests on it
  and its result has a home the line can point at — the observations comment on this ticket once
  approved, an ICR comment, the evidence on the control in Drata — per the standard's core rule 4. A
  result that exists only in this chat has no such home, so the line is left out (and is dropped if
  the user declines the comment).
- **A gap is not a failure to report here.** Report it in chat, never in *In practice*; if it needs
  work, hand it to `/drive-iso27001` or `/create-devsecops-ticket` at step 9.
- **Not relevant, or not queried?** Say nothing about current state at all. Write requirements.

### Step 6 — Draft in the house format

Follow `references/description-format.md` exactly, check the draft against
`references/golden-examples.md`, and apply the Security Jira profile (rule 11). The examples set
shape and voice; where one conflicts with the standard or with `description-format.md` §6, the
prohibition wins. The four sections, in this order, always:

```
### DCF-xx — [Control Name]

**What it is**            → one paragraph: the intent, and the exposure it prevents
---
**What it actually requires**  → Drata quoted verbatim, then how it's monitored
---
**In practice for Bitpool**    → the shape-specific table(s) + the opinionated posture block
---
**Evidence Drata will look for**  → prose (automated) or bullets (manual)
```

### Step 7 — Choose the write mode

| Existing description | Action |
|---|---|
| **stub** | **Replace.** Drata's one-liner isn't lost — it becomes the verbatim quote in section 2. |
| **human** | **Preserve in full at the top**, then the explainer below it, separated by a blank line. Never edit or trim what was there. |
| **already-described** | **Offer to refresh in place.** Show what changes and why. Never append a second explainer — duplicated sections are how these tickets become unreadable. |

State which mode you're using and why, as part of the approval request. A refresh replaces the old
explainer; it never records its own history in the description (no *"updated `<date>`"* or
*"previously said"* lines) — Jira's changelog holds the edit, and the approval block says what
changed and why.

### Step 8 — Stage, approve, write

Show the complete description as **rendered markdown**, not in a code fence (rule 5).

Directly under it, show the **durability check** in the format `/bitpool-writing-standard` sets
(`references/durability-check.md` §1) — one formatted markdown table, never a fenced code block,
run on the final wording (rule 11). For this description:

- **One handles row** collapses the `DCF` codes and sibling cross-references, clause and Annex A
  numbers, and requirement-level identifiers — AWS resource types, AWS Config rule names, setting
  names and ports stated as what must be true.
- **The control's name** in the heading takes one row: *kept — subject: the control this explainer
  is about, as Drata titles it (durability-check §4); a Drata rename is picked up at the next
  refresh*. Anywhere else in the description, a control is named by its `DCF` code, not its title.
- **The verbatim Drata quote** takes one row: *kept — verbatim quote of the Drata control, anchored
  with its source and read date* (rule 2). If Bitpool has customised that control text and it names a
  product, an account or another current-state value, it is still quoted verbatim — flag it in the
  step 9 hand-back for `/manage-drata-control`, which owns rewriting control descriptions.
- **Judgement rows** for whatever else survived flagging — a named product kept because the control
  names it, a boundary stated as a criterion, a pointer to a policy confirmed to hold the value, an
  anchored verification line.
- **Removed before staging** lists what the draft had and where it went — typically an observation
  moved to the report, a product generalised to its capability, a date or owner left to its Jira
  field.

Then, outside the description and the check, say plainly what is verified, what is
researched-but-unverified, and what was observed in AWS and when — with the observations
themselves (step 5). That part is a report to the user, so it can be as specific as it needs.

**Where there are AWS observations, or a correction reason, stage the optional comment** (rule 6),
rendered as markdown under its own heading: *"Observations — `<YYYY-MM-DD>`"* — what was checked, how,
and what was found, as specific as is useful, plus the correction reason for a refresh that fixes a
wrong statement. Security-sensitive identifiers (public addresses, exposed ports on named hosts,
administrator or break-glass accounts) are not written into it; say they were found and point to
where they are recorded. The comment is a snapshot, so no durability check.

Ask for everything in **one** question, so the user answers once — e.g. *"Post updated description,
add the dated observations comment, and transition to To Discuss?"* — and accept a yes to any part
on its own. `To Discuss` is the default worth offering for a CSIP DCF parent, since describing a
control is what makes it ready to discuss.

Resolve the transition before you ask, never after: `getTransitionsForJiraIssue` on the issue, and
use the returned **transition id**, not the name. Workflows differ between projects, and a
hardcoded status name will eventually be wrong. If `To Discuss` isn't among the available
transitions, don't substitute a guess — list what *is* available and ask which, or offer the write
alone.

On approval: `editJiraIssue` on the `description` field, then `addCommentToJiraIssue` **only** if
the comment was approved, then `transitionJiraIssue` **only** if the transition was approved. A yes
to the description alone is not a yes to the comment or the move.

### Step 9 — Hand back

Report what was written, **whether the observations comment was posted, and whether the ticket
moved** — name the status it landed in, or say it was left where it was. A transition performed and never mentioned again is a silent change to
someone else's board.

Then, briefly, what's still open: a documentation gap for
`/bitpool-docs`, an AWS gap for `/create-devsecops-ticket`, a control that isn't going to be met
— or a customised Drata control description carrying current-state values (step 8) — for
`/manage-drata-control`, or a monitoring gap for `/create-drata-test`. If a refresh corrected a
wrong statement rather than re-shaping a right one, say so: the Security Jira profile puts the
reason for a correction in a comment beside Jira's changelog — the optional observations comment
carries it when approved, and the report does otherwise (rule 6). Offer `/drata-control-insights` if the user wants to *see* the control's
status, now that the description it reads from actually exists.

Don't re-summarise the description you just wrote — the user can read the ticket.
