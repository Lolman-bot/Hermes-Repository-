# DevSecOps Ticket Workflow

Takes an existing (or newly described) piece of engineering/infrastructure work and gives the
devsecops team the ISO 27001 compliance angle: which Drata controls the work touches, how (not
just topical overlap), and where to look (Drata, GitBook, and any control's existing CSIP tracking
ticket). **Default action is editing the source ticket's own description in place** — appending a
clearly delimited section, never destroying what's already there. Only when there's no source
ticket at all does this fall back to creating a new standalone Task. The output is deliberately
high-level; it's a triage handoff, not a worked solution — "it will be up to the devsecops team to
take it from there."

**Two reference tickets this skill's design is grounded in:**
- [OP-80](https://bitpool.atlassian.net/browse/OP-80) ("Setup AWS control tower org wide") — the
  worked example for the control-mapping *mechanics* (Steps 4–5 below).
- [OP-83](https://bitpool.atlassian.net/browse/OP-83) ("Webhook transition from Discord to
  Teams") — the cautionary example for Step 3a. Its description is purely mechanical (migrate
  webhooks, route through SNS for flexibility) and says nothing about *why*. The real driver,
  supplied by Eric Sharp when this skill was designed: Discord accounts are owned by individuals,
  not the business, so a departing employee's chat history — and any business data in it — leaves
  with them. Mapping controls off the literal ticket text alone would land on integration-reliability
  controls and completely miss the actual angle: access deprovisioning, data retention, and
  unsanctioned/individually-owned tooling. **If a ticket's underlying reason isn't obvious from its
  own text, ask — don't guess.** A wrong "why" produces a wrong mapping no matter how carefully
  Step 4 is executed afterward.

---

## Bitpool config (hardcoded — do not look these up)

- **Jira Cloud ID:** `bitpool.atlassian.net` (or `d7442fe0-cadf-44e1-9313-6b27e16f3fbc`)
- **CSIP project key:** `CSIP` (Cyber Security ISO27001 Project) — where DCF-linked control tickets
  live, titled `Drata | Bitpool | DCF-xxx | [Control Name]`
- **Default assignee for a brand-new OP/BT ticket (Step 6b):** Dmytro Sirant,
  `712020:d29d2e09-46ab-4f86-aa0d-39af28631bb9` (`dsirant@bitpool.com`) — "assign like the others."
  Override only if the user names someone else. **Not used at all on the edit-in-place path** — an
  existing ticket already has its own assignee; don't touch it.
- **Default assignee for a new CSIP ticket (Step 4e, gap-filling):** Eric Sharp,
  `712020:997cf0e9-e968-446a-8639-a4664baf291c` (`esharp@bitpool.com`) — CSIP tasks go to Eric, not
  Dmytro; the two default-assignee rules are project-scoped, not interchangeable. Override only if
  the user names someone else.
- **Issue type for a brand-new ticket:** `Task`.
- **Drata control deep-link pattern** (confirmed on the GitBook register page itself — don't
  guess another format): `https://app.drata.com/compliance/control-details/<id>/overview`, where
  `<id>` is the control's numeric Drata `id` (not the `DCF-xxx` code).
- **CSIP `In Progress` transition (Step 7b):** transition **id `31`**, name `In Progress`, target
  status id `10494` — read live off the CSIP workflow on 2026-08-24. `transitionJiraIssue` takes
  only `transition: {"id": "..."}`; there is no by-name form, so this id *is* the config.
- **Every CSIP transition is global** (`isGlobal: true` on all of them), so `In Progress` is
  reachable from *any* status, including `Done`. The board's other transitions, for reference:
  `Ready` (3), `Staged` (4), `Backlog` (6), `Re-assess` (8), `Done` (41), `Blocked` (2),
  `To Discuss` (42).

**Golden rules**
- **Never present a draft for approval without the `## DevSecOps / ISO 27001 context` section
  already attached — Steps 4 and 5 are not optional, even when the user's own phrasing is a
  directive description of the engineering ticket itself.** Confirmed twice independently: a
  request phrased as "create a task in the OP board that does X, stays in backlog until Y" reads
  as license to just draft the described engineering work (Background + Task) and stop there —
  both a live session (CSIP-659/DCF-75, 2026-08-10) and this skill's own worked example earlier in
  the same day did exactly this, skipping GitBook's register search, `Drata_searchControls`, and
  the CSIP JQL lookup entirely, and asking "shall I create this?" on a ticket with zero Drata
  links, zero control table, zero CSIP cross-references beyond the source ticket. **Before drafting
  anything for approval, check: have Step 4a–4d actually been called this run?** If the honest
  answer is no, stop and run them — don't let a task-shaped prompt skip the compliance-mapping
  half of this skill's entire purpose. This is the single highest-value check in the whole
  workflow; if a future ticket looks thin, check here first, before Step 3a.
- **The DCF code is the only reliable identifier — match and create by it, never by control name
  text.** CSIP ticket titles drift: typos ("Resopnsible", "Managment"), abbreviations ("SDLC",
  "ISMS Plan"), or the code missing entirely (a real incident on 2026-08-07 found ~26 CSIP tickets
  titled with just the bare control name, no `DCF-xxx` at all — invisible to every prior Step 4c
  search that only humans had eyeballed, not machine-searched). Two consequences: (1) Step 4c's
  JQL (`text ~ "DCF-xxx"`) is the *only* trustworthy way to check whether a control already has a
  tracking ticket — never conclude "no ticket exists" from a control-name search, and never trust
  a title alone without confirming the code appears in it; (2) every ticket this skill creates or
  renames must contain the bare `DCF-xxx` code somewhere in its summary, so it stays discoverable
  by that same search next time.
- **A confirmed gap is a decision point, not just a finding.** Don't silently write "no CSIP ticket
  yet — gap" and move on — surface each gap to the user by DCF code and ask whether to create the
  CSIP tracking ticket now (see Step 4e). If yes for a code, create it, link it into the Step 5
  table in place of the gap, and add a short comment on the new CSIP ticket linking back to the
  source ticket (never a formal issue link — see the rule below).
- **Consult `/ask-drata` for connection-level Drata behavior.** Query-mode `Drata_search*` calls
  are broadly unreliable on this account (silent empty results, not evidence a control doesn't
  exist) and list-mode pagination must be followed to `cursor: null` before treating a code as
  absent — Step 4 below leans on both of these directly; this skill doesn't re-derive them.
- **Ground infrastructure action items in live AWS state — never assume a gap.** Before drafting
  what the devsecops team should *do* about infrastructure work, check what's actually deployed
  via Step 3c (`/aws-context` + `/aws-query`, using
  [AWS Evidence Map](aws-evidence-map.md) for which call answers which domain). Why: an
  early draft of a NACL/region-scoping ticket assumed a region-restricting SCP needed to be
  *created*, when Bitpool already had one — it had simply been applied after the production
  account was provisioned, so prod's pre-existing resources in non-approved regions were never
  retroactively cleaned up. The real task was reconciliation and cleanup, not "add the SCP." A
  wrong assumption about current state produces a wrong task list no matter how well the
  control-mapping table (Step 4) turns out.
- **On a brand-new ticket (6b), ask the user "just do it" vs. "two-part time quote" every time —
  never decide it alone (Step 3d).** Whether something is cheap/quick enough to just greenlight
  depends on cost and opportunity cost against whatever else devsecops has in flight — this skill
  has no visibility into that. Worked example: DCF-73's NACL check runs per-VPC; there's a genuine
  choice between editing every VPC's NACL by hand (the minimum fix) and managing the posture
  centrally via an SCP instead (the uplift, which also eases DCF-748 and VPC logging evidence).
  That choice — and whether it's even worth quoting instead of just doing — is the user's call,
  posed fresh each time via `clarify`.
- **Drata is READ-ONLY.** Never call `Drata_updateControl`/`Drata_createControl`/etc. — same rule
  as every other ISO 27001 skill in this section.
- **Never create a formal Jira issue link.** Don't call `createIssueLink` — not to a CSIP ticket,
  not to anything. Every cross-reference (CSIP tickets, Drata, GitBook) is a plain markdown
  hyperlink inside the description text. This was an explicit correction during design — don't
  reintroduce issue-linking.
- **Edit in place beats creating a new ticket.** If a source ticket exists, the devsecops context
  becomes a section *within* it — never a sibling ticket, and never at the cost of the ticket's
  existing content. Only create a new standalone Task when there is genuinely no ticket to edit.
- **Always broad, one section per ticket.** Don't produce one entry per matched control in
  isolation — it's a single consolidated section. The table's "Resolution impact" column (Step 5)
  is a one-line assessment of whether the action closes the gap, not a step-by-step remediation
  plan — the detailed how-to is still the devsecops team's job once they pick it up.
- **Never write anything without staged approval.** Draft the exact final text, show it, get a
  clear yes, then write it (`editJiraIssue` or `createJiraIssue`). Never on inference alone.
- **Render the preview, don't dump its source.** When showing the draft for approval, output it
  as actual rendered markdown in the chat response — real headings, bold, and tables — never
  wrapped in a fenced code block. A fenced block shows raw `|---|---|` and `##` syntax instead of
  a table and a heading, defeating the point of a review step: the user needs to see what the
  ticket will actually look like. The one exception is a small inline snippet *about* syntax
  (e.g. quoting a single cell's markdown) — the draft as a whole is never itself inside a fence.
- **Status is written on exactly one ticket, and only after asking: the *starting* CSIP ticket.**
  On the engineering ticket (OP/BT) this skill still only ever writes `description` — never
  `status`, `assignee`, `labels`, or anything else on it. The single exception in the whole
  workflow is **Step 7b**: once Step 7's write has succeeded, ask whether to move the starting CSIP
  ticket to `In Progress` and comment the new ticket onto it. **Ask — never infer.** Whether a
  given CSIP ticket is "the one this run came from" is a judgment about board state this skill
  can't make on its own, and because every CSIP transition is global a careless call can drag a
  `Done` ticket backwards. So the question is asked fresh every run, *after* the write, with the
  ticket's current status shown inside it — never folded into the Step 6 approval, and never
  done silently. Eric Sharp's explicit decision (2026-08-24): **no status guard, because the ask
  is the guard** — which is exactly why the status must appear in the question.

---

## Workflow

### Step 1 — Resolve the source ticket

- If the user gave a Jira key (e.g. `OP-80`) or it's already in the conversation, fetch it with
  `getJiraIssue` (`fields: ["*all"]` is fine — these are usually small). This is the ticket whose
  **description** will be edited.
- If no ticket exists yet and the user is describing new work with nothing to attach it to, that's
  the only case that falls back to creating a new ticket (see Step 6b).
- If neither a key nor a clear description is available, ask for one before doing anything else.
- **Also record the *starting* CSIP ticket, if there is one.** Runs frequently begin from a control
  tracking ticket — "create an OP task for CSIP-659" — rather than from the engineering
  ticket itself. That CSIP ticket is the **starting** ticket: distinct from the source ticket whose
  `description` gets edited, and the only ticket in this whole workflow whose *status* may ever be
  written (Step 7b). Note its key **and its current status** here, while you're already fetching
  it — Step 7b needs that status to put in its question and shouldn't re-derive it later.
- **The starting CSIP ticket is not the same thing as a CSIP ticket found at Step 4c or created at
  Step 4e.** Those are controls the work happens to touch. The starting ticket is the one that sent
  you here. Only it is ever a Step 7b candidate — conflating them writes a status onto an
  unrelated control ticket.

### Step 2 — Decide if this is ISO 27001-relevant (auto-detect first)

**A directive prompt doesn't end the workflow at Step 2.** If the user's own message reads like an
engineering-ticket description ("create a task that does X, put it in backlog until Y") rather
than "give me the compliance angle," that's still just Step 1/6b's raw material — it tells you
*what the ticket is about*, not that the compliance-mapping steps are now optional. Keep going
through Steps 3–5 regardless; see the first golden rule above.

Scan the source ticket's summary, description, labels, components, and worklog/comments for
infra/security signal: AWS/Azure/GCP, infrastructure, network, access/IAM, encryption, logging,
monitoring, backups, vendors/third parties, data handling, deployment/CI/CD, physical security,
incident response, communication tools, etc. **Most engineering work in Bitpool's infra/ops
projects (OP, BT) will clear this bar** — lean toward auto-detecting "yes" rather than asking, per
this skill's design decision.

**Only ask the user directly** ("Does this relate to ISO 27001 compliance?") when the ticket is
genuinely ambiguous — e.g. a pure UI copy change, a sales/marketing task, or something with too
little content to judge. A ticket that's obviously unrelated should just be told "this doesn't
look ISO 27001-relevant" and the skill should stop there rather than force a mapping.

### Step 3 — Understand what's actually going on

**3a. Confirm the underlying reason — ask if it isn't obvious.** Read past the literal task
description for *why* the work is happening. Some tickets state the reason plainly (OP-80: closing
an org-wide logging/guardrail gap). Others don't (OP-83: reads as pure webhook mechanics, but the
real driver is a data-ownership/leak risk from individually-owned Discord accounts). **If the
underlying motivation isn't stated or clearly inferable, ask the user what's actually driving the
action before mapping anything.** Guessing the "why" from thin context is exactly the mistake this
step exists to prevent — the wrong reason produces a plausible-looking but wrong control mapping.

**3b. Research the action itself.** Once the real reason is clear, understand what the described
work technically does from a security/compliance angle — this is what makes the mapping specific
instead of generic. For `OP-80` (AWS Control Tower), that meant knowing Control Tower ships an
org-wide CloudTrail trail, a centralized log-archive account, preventive/detective guardrails (SCPs
+ Config rules), and that GuardDuty/Security Hub/Inspector are *adjacent* services often rolled out
alongside it but not automatically included. For `OP-83`, once the real reason (data walks out with
departing staff) is in hand, the technical question becomes about access/data lifecycle on
individually-owned accounts, not webhook reliability.

Use existing knowledge for well-established technology. Reach for `web_search` only if the
technology is unfamiliar, niche, or details matter enough that guessing would be irresponsible.
Never fabricate specifics.

**Explicitly separate:**
- **Primary** — the work directly evidences or changes this control's state.
- **Adjacent / confirm scope** — plausibly related, but only if a further service/decision is
  actually in scope (name what that dependency is). Don't quietly promote an adjacent match to
  primary just to make the section look more thorough than the researched action supports.

**3c. Check live AWS state before drafting the task list (when infrastructure-shaped).** Research
in 3b tells you what the technology *generally* does; it says nothing about what Bitpool's account
actually has deployed right now. Ground the two before writing a single task-list item — the
failure mode this step exists to prevent runs in **both** directions: telling devsecops to build
something that already exists, and telling them nothing is wrong when it silently is.

1. **Relevance test.** Narrower than Step 2's ISO 27001 check — only run this when the *action
   itself* is something AWS can answer: network/firewall/VPC/region config, IAM/access,
   encryption, logging/monitoring, backups, SCPs/Organizations policy, resource inventory. Skip
   entirely for policy-drafting, training, vendor-management, or physical-security work — there's
   nothing to query.
2. **Session, then query — never inline CLI here.** If `aws sts get-caller-identity` hasn't
   succeeded yet this session, run `/aws-context` first (once per session, not before every call).
   Then use `/aws-query` to build and run the actual calls — it owns the account list, profile
   names, the multi-account loop pattern, and the JMESPath gotchas. For *which* call answers
   *which* domain, use [AWS Evidence Map](aws-evidence-map.md) — the same shared
   reference `/drata-control-insights` reads — rather than guessing. **Never inline `aws.exe`
   commands, profile names, or account IDs into this skill file**; that duplication is exactly
   what the shared reference exists to prevent.
3. **Budget: ≤2 domains, ≤6 calls.** This is a per-ticket grounding pass, not an audit. Production
   first, then org-wide accounts for anything inherently org-wide (SCPs, Organizations, Identity
   Center). Loop every account only when the question genuinely is org-wide, and do it with
   `/aws-query`'s single loop pattern — not one command per account.
4. **Read the result before drafting the task list, not after.** If a query shows a
   control/mechanism already exists (an SCP, a config rule, a policy), the task list must say so
   and scope the actual remaining gap — not repeat "implement X" for something already in place.
   Concretely: a region-restricting SCP that already exists but predates an account's creation
   means the task is "clean up what the SCP didn't retroactively cover" (and possibly remove
   resources — e.g. VPCs — in accounts/regions the SCP already treats as unapproved), not "add the
   SCP."
5. **Capture each finding as a dated observation, not a verdict.** "Region-restriction SCP `X`
   attached org-wide, created 2026-0X-XX; account `Y` was provisioned before that date and still
   has resources in non-approved regions" is useful and belongs in the Step 5 table. "Regions are
   locked down" is not, and isn't this skill's call to make — that's the devsecops team's job once
   they have the observation.
6. **Degrade cleanly, and don't pad every ticket with it.** No session and the user doesn't want to
   sign in, or the action isn't AWS-shaped at all → skip the Step 5 table entirely rather than
   rendering an empty or boilerplate version of it. If it's relevant but genuinely not checked,
   say so once in the chat response, not as a table row in the ticket — unlike
   `/drata-control-insights`'s single-control snapshot, a fleet of devsecops tickets each carrying
   a "not checked" row is noise, not signal.

**3d. Decide: just do it, or a two-part time quote? Ask the user, every time — this only applies
when there's no source ticket to defer to (Step 6b).** When editing an existing ticket in place
(6a), the source ticket already states the work; don't invent a task list for it — if 3c's
findings contradict something the existing text assumes, that becomes a flagged note inside the
Step 5 compliance-context section instead (never a rewrite of the original text). When there's no
source ticket, this skill has to author the actual "what to do" content itself, and *how* to frame
that is a judgment call this skill cannot make alone: whether something is cheap/quick enough to
just greenlight depends on cost and opportunity cost against whatever else devsecops has in
flight — context this skill doesn't have. **Always put the choice to the user via
`clarify`; never pick a path unprompted or infer it from ticket text alone.**

Frame the question with what 3b/3c actually found:
- **Is there a genuine choice of remediation approach**, or is this one well-defined action with
  no architecture/tooling decision? (Flip on Multi-AZ, use an already-encrypted connection method
  → no real choice. Manually editing NACLs per-VPC vs. managing the posture centrally via an SCP →
  a real choice — the worked example below.)
- **Does it look cheap/quick enough** to just greenlight, or substantial enough that committing
  time needs a quote first?

The two outcomes:
- **"Just do it."** Step 5's task section becomes a concrete action list, as this skill has always
  produced — but add one explicit line: *"If this turns out deeper than expected once you're in
  it, pause and flag back rather than pushing through."* This is the Multi-AZ / Encrypted Remote
  Production Access shape: usually a single well-understood change, occasionally not.
- **"Two-part time quote."** Step 5's task section becomes a quote *request*, not a set of
  instructions:
  1. **Quote 1 — minimum to achieve the control.** The smallest, most direct change that satisfies
     the control as it stands today (e.g., manually editing the NACL on each affected VPC).
  2. **Quote 2 — uplift to streamline and prevent recurrence.** A more durable, centrally-managed
     approach to the same problem (e.g., an SCP managing the posture across every VPC/region at
     once, instead of per-resource edits).
  Ask for **both estimates plus their reasoning** — quoting either number in isolation is hard, so
  the ask is for their discovery/thinking, not just a figure. Explicitly prompt them to note
  whether the uplift approach **also eases an adjacent control** — the worked example: DCF-73's
  NACL check runs per-VPC; going the SCP route instead of manual edits also reduces VPC sprawl and
  centralizes management, which plausibly makes DCF-748 (Segmentation of Networks) and VPC
  activity-logging evidence easier to produce too. That cross-control payoff belongs in the quote
  ask itself, not buried in Step 4's table alone.

### Step 4 — Map to real Drata controls

**4a. Shortlist candidate DCF codes from the local register.** `references/drata-controls-register.md`
ships with this skill and carries every enabled control — `DCF-xxx`, numeric Drata ID, name,
description, and whether a monitoring test is wired to it. **Search it** (`search_files`) for domain keywords ("logging",
"access review", "encryption at rest"); it's ~140 KB, so reading it whole wastes context. Reason over
the matching rows yourself to shortlist codes — don't rely on Drata's own AI search for this (see
`/ask-drata`: `Drata_searchControls` query mode is broadly unreliable — silent empty results are
common, not evidence the topic has no match).

The register is a **snapshot** (pulled 2026-08-07), so it shortlists but doesn't adjudicate: confirm
each shortlisted control against the live Drata record in 4b before writing it into a ticket. If a
code you'd expect isn't in the register, it may be newly added or disabled — say which you concluded
and why, rather than asserting the control doesn't exist.

**4b. Resolve numeric Drata IDs.** The register already carries each control's numeric ID inside its
DCF link (`.../control-details/<id>/overview`), so normally you can read the id straight off and go
directly to the live record. Only if a shortlisted code is missing from the register do you need the
fallback: page through `Drata_searchControls` in **list mode** (no `query`, `size: 50`, following
`cursor`) and match codes as you go. Bounded cost: the full control set is ~200 records,
so this is at most **4 pages** regardless of how many codes you're resolving. **Per `/ask-drata`
gotcha #2, a single page is never proof a code is absent** — results sort by internal `id`, not by
`DCF-xxx`, so a shortlisted code can land on any page; keep paging until every code is found or
the `cursor` comes back `null` before concluding one wasn't in the set. Build each control's Drata
link from its `id`: `https://app.drata.com/compliance/control-details/<id>/overview`.

**4c. Find each control's existing CSIP tracking ticket.** One combined JQL call covers every
shortlisted code:
```jql
project = CSIP AND (text ~ "DCF-79" OR text ~ "DCF-406" OR text ~ "DCF-90" ...)
```
Request `fields: ["summary", "status"]` only. A code with **no result is a real finding** — "no
CSIP ticket yet" is worth surfacing as a gap, not silently dropped.

**4d. The register's own Yes/No column is the `isMonitored` flag** (confirmed on the register
page itself) — use it directly rather than re-querying `Drata_searchControls` per control for
`flags`.

### Step 4e — Flag gaps, offer to fill them

For every shortlisted code that came back from Step 4c with no CSIP ticket (a genuine gap —
`cursor` exhausted per `/ask-drata`, not just page 1 of the JQL results), batch them into one
question to the user: which of these gaps should get a new CSIP task now? Use `clarify`
with `multi_select: true`, one choice per DCF code. A question caps at 4 choices — if a ticket has
more than 4 gaps, split across multiple questions (e.g. one per source ticket, or "primary" vs
"adjacent").

**Stage before creating — the Step 4e approval.** The new ticket's `summary` and `description` are
Security Jira text (SKILL.md rule 13): load `/bitpool-writing-standard` before drafting them. Show
each selected ticket's exact `summary`, `description` and item 2 comment, rendered rather than
fenced (golden rule), and directly under the staged text **one durability check** for the whole
block, in the format that skill sets (its `references/durability-check.md` §1) — where several
tickets are staged, its `Field` column names each by its code. Expect one handles row — the `DCF`
code, Drata's integration title format as stock text, and the control's name as the ticket's
subject — and, where Drata is quoted, one row for the quote: kept, anchored with its source and read
date. The comment is a snapshot and gets no check. Create only on a clear yes.

For each code the user selects and approves:
1. **Create the CSIP ticket** — `createJiraIssue`: `projectKey: "CSIP"`, `issueTypeName: "Task"`,
   `summary: "Drata | Bitpool | DCF-xxx | [Control Name]"` (control name exactly as it appears in
   the register — this is what keeps it discoverable per the DCF-identifier golden rule),
   `description` as below, `assignee_account_id` = Eric Sharp's ID
   (`712020:997cf0e9-e968-446a-8639-a4664baf291c`) unless told otherwise — CSIP tasks default to
   Eric, not Dmytro (Dmytro is only the Step 6b OP/BT default). **Note:** new CSIP tasks default to
   status **Staged** — don't assume it shares OP's `Backlog` default, the two projects differ.

   **The `description`** states what must be true when the control is met, as an outcome; the bare
   `DCF-xxx` code; and where its evidence will live — e.g. *"filed in the GRC evidence library
   against `DCF-xxx`"*. Never the register's control description copied verbatim: the register is a
   dated snapshot, and an unanchored copy of Drata's text keeps reading as current after the control
   is rewritten. Where Drata's wording is worth carrying, quote it from the live record read at Step
   4b — never from the register — under the lead-in *"Per Drata's description, as read
   `<YYYY-MM-DD>`:"*. A Step 3c observation stays out of the description; where it matters to this
   control, it goes in the item 2 comment.
2. **Comment back** — `addCommentToJiraIssue` on the new CSIP ticket: one or two sentences on why
   it was raised, plus a plain markdown link back to the source ticket, e.g. `Raised from
   [OP-83](https://bitpool.atlassian.net/browse/OP-83) (Webhook transition from Discord to Teams)
   — <short reason>.` Never `createIssueLink`.
3. **Update the Step 5 table** — the `CSIP ticket` cell for that code now links the new ticket
   with its status (e.g. `[CSIP-1047](...) (Staged)`) instead of "no CSIP ticket yet — gap".

Codes the user didn't select keep the plain "no CSIP ticket yet — gap" text in the table — don't
half-create anything on a no, and don't re-ask about the same gap within the same run.

### Step 5 — Draft the section (don't write anything yet)

Build a `## DevSecOps / ISO 27001 context` markdown section:

1. One or two sentences on what's actually happening and why (from Step 3 — including the real
   underlying reason if that took an extra question to establish).
2. **If Step 3c ran a live AWS check, a `Current AWS state (observed)` table** — this grounds
   whatever task content exists in what's actually true right now rather than what the ticket text
   assumed:

   | Area | Observed | Status | Implication |
   |---|---|---|---|

   - **Area** — the specific thing checked, e.g. "Region-restriction SCP", "VPCs in `aws-prod`".
   - **Observed** — the concrete finding plus the date, e.g. "SCP `deny-unapproved-regions`
     attached org-wide, created 2026-06-12 (`organizations list-policies`)."
   - **Status** — one of **in place** / **gap** / **partially in place**. Use the last for exactly
     this shape of finding — a control exists but doesn't cover everything it should (e.g. it
     predates an account). Never round a partial finding up to "in place."
   - **Implication** — what this means for the task content, in one line, e.g. "prod account
     predates the SCP — needs its own cleanup pass, not a new SCP."

   **Placement differs by path.** On a **6a** edit, this table stays right here, inside the
   appended section — the source ticket's own existing task text is untouched, so this table is
   the only place a discrepancy against it can be flagged (as a note, never a rewrite). On a
   **6b** brand-new ticket, move this table up so it sits between the authored Background and the
   Task section (Step 3d) instead — it directly informs the quote or action list that follows, so
   it reads better ahead of that content rather than after it.

   If Step 3c found the action isn't AWS-shaped, or no session was available, omit this table
   entirely rather than rendering an empty or boilerplate version of it (see Step 3c.6).
3. A markdown table, **Primary** controls first, **Adjacent — confirm scope** as a clearly
   separate second table:

   | DCF | Control | How it relates | Resolution impact | Drata | CSIP ticket |
   |---|---|---|---|---|---|

   **The Drata link goes on the `DCF` cell itself** (e.g. `[DCF-79](https://app.drata.com/...)`),
   using the pattern from Step 4b — not on the `Drata` column. The `Drata` column stays plain text:
   "Monitored"/"Not monitored" from the register's Yes/No. Each `CSIP ticket` cell either links
   the ticket (with its status) or reads "no CSIP ticket yet — gap" — the latter only stands once
   Step 4e's offer has been made and declined (or the code wasn't selected); a gap the user chose
   to fill gets the new ticket's link before this table is ever shown for approval.

   **`Resolution impact`** is a one-line, honest assessment of what the action actually does *to
   the control's state* — not a remediation plan, just where it lands:
   - **Directly resolves** — the action alone is sufficient once complete (name the artifact that
     becomes the evidence, e.g. "the mandatory guardrail itself").
   - **Assists** — necessary but not sufficient; name the specific remaining piece (e.g. "closes
     it only once CloudWatch alarms are wired to the new events" or "gives the practical basis for
     the policy, but the policy still has to be written").
   - **Doesn't resolve alone** — real but marginal; say what's actually missing.
   Don't default every row to "Directly resolves" — most infrastructure changes are partial, and
   overclaiming here is worse than a plain "how it relates" with no resolution column at all.
4. A GitBook doc link or two if a specific procedure page (not just the generic register) is
   genuinely relevant — e.g. the Logging and Monitoring Policy page for logging-domain work.

This `## DevSecOps / ISO 27001 context` section is the same content whether it ends up appended
to an existing ticket or inside a brand-new one — only its surroundings differ (Step 6), and on a
6b ticket it's preceded by the Background/Task content Step 6b now describes.

### Step 6 — Decide where it goes, show the exact text, get a yes

**Gate before drafting anything below: does the text you're about to show actually contain a
`## DevSecOps / ISO 27001 context` section with a real controls table in it — DCF links, CSIP
links, the lot — not just a Background/Task description of the engineering work?** If not, Steps
4–5 didn't actually run; go back and run them now. This is the first golden rule again, at the
last point where it's still cheap to catch.

**6a. Source ticket exists (the default path).** The new description is:
```
<the source ticket's EXISTING description text, verbatim, unchanged>

---

<the Step 5 section>
```
If the existing description is empty (as with `OP-80`), the result is just the Step 5 section —
there's nothing to preserve. **Never drop, summarise, or rewrite existing content** — append only.

**6b. No source ticket exists.** Only here does a new ticket get created — and only here does this
skill author the actual "what to do" content itself, since there's no existing ticket text to
defer to. `Task`, in whatever project the described work belongs to, assignee Dmytro Sirant's
account ID (unless told otherwise), summary naming the work. The description now has three parts,
in order:
1. **Background** — a short paragraph on what's actually happening and why (Step 3a/3b).
2. **Task for [team]** — shaped by Step 3d's answer: either a concrete action list (with the
   pause-if-deeper-than-expected line) or the two-part quote request. The Step 3c
   `Current AWS state (observed)` table, when there is one, sits between Background and this
   section (see the placement note in Step 5.2) — it's what the task/quote content is grounded in.
3. **The Step 5 `## DevSecOps / ISO 27001 context` section**, unchanged from the 6a case.

There's no existing content to preserve on this path because there's no ticket yet — all three
parts are freshly authored and shown together for approval.

**Either way:** show the user the exact final text — rendered, per the golden rule above, never
in a code fence — and ask **"Shall I write this?"** (6a) or **"Shall I create this ticket?"** (6b).
Do not proceed without a clear yes.

### Step 7 — Write it

**6a path:**
```json
{
  "cloudId": "d7442fe0-cadf-44e1-9313-6b27e16f3fbc",
  "issueIdOrKey": "<source ticket key>",
  "fields": { "description": "<final text from Step 6a>" }
}
```
via `editJiraIssue`. Touch only `description` — never `status`, `assignee`, `labels`, or anything
else on an existing engineering ticket. (The *starting CSIP* ticket's status is Step 7b's business,
and only after asking — it is never touched here.)

**6b path:**
```json
{
  "cloudId": "d7442fe0-cadf-44e1-9313-6b27e16f3fbc",
  "projectKey": "<project the work belongs to>",
  "issueTypeName": "Task",
  "summary": "<summary>",
  "description": "<final text from Step 6b>",
  "contentFormat": "markdown",
  "assignee_account_id": "712020:d29d2e09-46ab-4f86-aa0d-39af28631bb9"
}
```
via `createJiraIssue`. New Tasks in Bitpool's engineering projects (e.g. `OP`) default to
`Backlog` without any extra call — don't call `transitionJiraIssue` on the **new** ticket
unless it somehow landed somewhere else. That restriction is about the new ticket only; the
*starting CSIP* ticket's transition is Step 7b, below. **Never call `createIssueLink`** on either
path.

### Step 7b — Offer to move the starting CSIP ticket to In Progress

**Runs only when Step 1 recorded a starting CSIP ticket, and only once Step 7's write has actually
succeeded.** No starting CSIP ticket, or the write failed — skip straight to Step 8. Don't
transition anything off the back of a write that didn't land.

**Ask, don't infer — every run, no exceptions.** Put it to the user with `clarify`, and
**put the ticket's current status inside the question text**:

> Move `CSIP-659` — currently **Staged** — to **In Progress**, now that
> [OP-91](https://bitpool.atlassian.net/browse/OP-91) exists?
> - *Yes — transition it and comment the link on*
> - *No — leave the CSIP ticket exactly as it is*

Two things make the ask non-negotiable, and the status-in-the-question non-negotiable with it:

1. **Which CSIP ticket counts as "the one this came from" is not this skill's call.** A single run
   can touch several: the starting ticket, controls matched at Step 4c, tickets created at Step 4e.
   Only the first is ever a candidate. Infer it wrong and you write a status onto an unrelated
   control ticket.
2. **Every CSIP transition is global** (see the config block), so `In Progress` is reachable from
   `Done`, `Blocked`, `Re-assess` and `To Discuss` just as easily as from `Staged`/`Ready`/
   `Backlog`. There is deliberately **no status guard** — Eric Sharp's decision, 2026-08-24: the
   ask *is* the guard. That only holds if the current status is visible in the question, so saying
   yes to regressing a `Done` ticket is a deliberate choice rather than an accident. **Never omit
   the current status.**

**On a yes, do both — the transition and the comment travel together.** The comment is the audit
trail for why the status moved; a status change with nothing explaining it is the thing this pairing
exists to avoid.

1. **Transition it** — `transitionJiraIssue`:
   ```json
   {
     "cloudId": "d7442fe0-cadf-44e1-9313-6b27e16f3fbc",
     "issueIdOrKey": "<starting CSIP key>",
     "transition": { "id": "31" }
   }
   ```
   `31` is `In Progress` on the CSIP workflow (target status `10494`), from the config block above.
   The tool accepts **only** `transition: {"id": ...}` — there is no by-name form. If the id is
   rejected, re-read the live list with `getTransitionsForJiraIssue`, match on the transition
   **name** `In Progress`, use the id you find, and tell the user the config block above needs
   updating — don't guess a different id.

2. **Comment the link on** — `addCommentToJiraIssue` on that same CSIP ticket: one or two sentences
   with a plain markdown link to the ticket just written, e.g. `Engineering work raised as
   [OP-91](https://bitpool.atlassian.net/browse/OP-91) — <short reason>. Moving this to In Progress
   while that work runs.` Same shape as Step 4e.2, and the same hard rule: **never
   `createIssueLink`.**

**On a no, change nothing at all on the CSIP ticket** — no status, no comment — and don't re-ask
within the same run.

### Step 8 — Hand back

Share the ticket's URL and a one-line summary of what changed. Don't re-paste the whole section
back to the user — they just watched it get drafted. If Step 7b ran, add one line for it too:
either "`CSIP-659` moved Staged → In Progress, comment added" or "`CSIP-659` left as-is at your
request" — never leave the outcome of a status write unstated.

---

## Improving this skill over time

- **Control-mapping accuracy** lives entirely in Step 3 (understand the real reason, then research
  the action) and Step 4a (judgment over the real register text) — there's no keyword lookup table
  to maintain here on purpose, since the whole point is reasoning about what a specific action
  actually does and *why*, rather than pattern-matching topic words.
- **Step 3a (ask about the real reason) is the highest-leverage step to get right.** If this skill
  ever starts producing mappings that feel generic or miss the point, the failure is almost always
  here, not in Step 4's mechanics — re-check whether the real driver was actually confirmed or just
  assumed.
- If Bitpool ever adds a dedicated DevSecOps Jira project, Step 6b's "new ticket goes in the
  source's project" default is the one thing to revisit — re-confirm with the user before changing
  it, since edit-in-place-by-default was an explicit, corrected design decision, not a guess.
- **Refreshing the register is a deliberate maintenance task.** `references/drata-controls-register.md`
  is a 2026-08-07 snapshot. When it drifts far enough to mis-shortlist, re-pull the control set from
  Drata (read-only) and rewrite the file — don't patch single rows mid-run, and don't reach for the
  wiki at run time to work around a stale row.
- **2026-08-07 incident that shaped the DCF-identifier rule and Step 4e:** a project-wide CSIP
  cleanup found dozens of control-tracking tickets titled with just the bare control name (no
  `DCF-xxx` code at all, or the code buried in a typo'd/abbreviated title), which meant OP-80 and
  OP-83's own DevSecOps tables had recorded several controls as "no CSIP ticket yet — gap" when a
  ticket actually existed — just not findable by a title match. That's why Step 4c's JQL search is
  the only trusted check, why every ticket this skill creates must carry the bare code, and why
  Step 4e exists at all (previously a gap was just recorded, never offered as something to act on).
  If gaps start slipping through again, the fix is almost always here: confirm the JQL search
  actually ran to `cursor: null`, and confirm new/renamed tickets carry the literal `DCF-xxx`
  substring — not just the control's name.
- **2026-08-10 incident that added Step 3c and the AWS current-state table:** a drafted OP ticket
  for cleaning up NACL/region exposure (DCF-73) assumed a region-restriction SCP needed to be
  added, when Bitpool already had one — it simply post-dated the production account's creation, so
  prod was never retroactively brought into scope. The draft was about to tell devsecops to build
  something that already existed, while missing the actual gap (a reconciliation/cleanup pass, and
  possibly removing VPCs in accounts/regions the SCP already treats as unapproved). Fixed by adding
  Step 3c: check live AWS state via `/aws-context` + `/aws-query` before drafting the task list,
  not after, and surface findings in a dedicated `Current AWS state (observed)` table (Step 5.2) so
  the task list's premises are visible and checkable. If a future ticket's action items read as
  generic "implement X" for infrastructure that might already partially exist, the fix is almost
  always here — confirm Step 3c actually ran and its findings shaped the task list, not just the
  informational table.
- **Same session, the follow-up that added Step 3d and the two-part quote shape:** the DCF-73
  ticket above also exposed a second issue — its "Task for DevSecOps" section was written as a
  flat, prescriptive step list, when the real remediation had a genuine choice of approach (manual
  per-VPC NACL edits vs. an SCP-managed posture) and no visibility into cost or what else devsecops
  had in flight to judge which was worth doing. Eric Sharp's fix: on a brand-new ticket, ask
  every time whether to draft a concrete list ("just do it," for single well-understood changes
  like Multi-AZ or Encrypted Remote Production Access) or a two-part quote request (minimum vs.
  uplift, plus the assignee's own reasoning — sizing either alone is hard). If a future ticket's
  task section reads as a confident prescription for something that actually involved a real
  design choice, the fix is almost always here — confirm Step 3d's question was actually asked,
  not skipped in favor of drafting steps directly.
- **2026-08-24, the change that added Step 7b (starting-CSIP transition):** until now the skill
  raised the engineering ticket and left the CSIP ticket that sent it there sitting in `Staged`, so
  the board never showed that the control was actually being worked. Eric Sharp's fix: after the
  write lands, offer to move that starting CSIP ticket to `In Progress` and comment the new ticket
  onto it. Four design calls were made explicitly and shouldn't be quietly re-litigated: (1) it
  applies **any time a starting CSIP ticket exists**, not only on the 6b new-ticket path — but the
  skill **asks rather than infers** which ticket that is; (2) the ask is a **separate confirm after
  the write**, not folded into the Step 6 approval, so a failed write can't trigger a status change;
  (3) **no status guard** — `In Progress` is set from wherever the ticket currently is, with the
  current status shown in the question so a `Done` regression is a visible choice; (4) the
  **comment ships with the transition**, not independently. If a future run ever moves a CSIP
  ticket the user didn't nominate, or moves one silently, the fix is here: confirm the
  `clarify` call actually fired and carried the current status in its text.
- **2026-08-10, same day, the incident that added the "gate before drafting" golden rule:** a
  session asked to create an OP task for CSIP-659 (DCF-75) with a directive prompt ("create a task
  that does X, stays in backlog until Y") drafted a plain engineering ticket — Background, task,
  a comment for the source ticket — and asked "shall I create this?" having never consulted the
  controls register, `Drata_searchControls`, or the CSIP JQL lookup. Zero Drata links, zero
  controls table, zero CSIP cross-references. Steps 4 and 5 — this skill's actual reason to
  exist — were skipped outright, and nothing in the workflow forced a check before presenting the
  draft. Confirmed independently in this same conversation: an early draft of the DCF-73 ticket
  (above) made the identical mistake before a human caught it via the OP-82 comparison. Fixed by
  adding an explicit gate at Step 2 (a directive prompt doesn't end the workflow) and Step 6
  (verify the `## DevSecOps / ISO 27001 context` section is actually present, with a real table,
  before showing anything for approval). If a future ticket looks thin — no Drata links, no
  control table — the fix is almost always here: something let the model stop at "draft the
  engineering ticket" instead of continuing through Step 4.
