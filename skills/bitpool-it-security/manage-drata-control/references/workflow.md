# Workflow (default mode) — Steps 0–11 in full

> Relocated verbatim from this skill's `SKILL.md` when it was ported to Hermes; `SKILL.md` keeps the
> route and a summary of each rule, and this file is the full text. Bold section names refer to:
> **golden rules** → `references/golden-rules.md`; **Invoke the downstream skills** and **Bitpool
> context** → `references/bitpool-context.md`; **Batched policy changes**, **Writing a queue row** and
> **Rules for the index** → `references/policy-queue.md`; **Step 0–11** → `references/workflow.md`.

### Step 0 — Pre-flight: read the governing policy, don't audit its dates

`Drata_listPolicies(name="risk")` → read the `Risk Assessment Policy` (id `17`) for the scales and
the acceptable level of risk. Reading the content is the whole purpose of this step.

**Do not check, compute, or comment on `renewalDate` or `approvedAt`.** Every Bitpool policy is
expected to be out of renewal and unapproved until the single bulk promotion event, by decision —
see the golden rule above. Scoring against current content is correct and needs no caveat.

Then read the **policy queue** — the page file from disk for its rows, and the ticket
(`project = IRT AND labels = PolicyQueue`) for their detail — so you know which policies already
carry pending draft edits. **Read the comments, not just the page's Pending changes index**: the
index is a pointer list — row number, policy name and a link to the comment — so it cannot tell you
whether a queued change already covers your control. A change already queued is covered; raising it
a second time is the duplicate this step exists to prevent.

### Step 1 — Resolve the control and its current position

Read, in parallel:

- `Drata_searchControls` (list mode, no `query`) for the control — capture `code`, `name`,
  `description`, `rationale`, `activity`, `flags`, `frameworkTags`, `owners`. Note that search-mode
  `query` returns empty on this account. Fetch the one control with a cursor seek — take its
  numeric id from the Drata Controls Register URL, pass `cursor` = base64 of `id|<id + 1>` with
  `size: 1` and the default sort, and confirm the returned `code` — per `/ask-drata` gotcha #2.
  A different code back means the control is archived or disabled (gotcha #11), not missing.
- `Drata_searchRisks` with `controls=["DCF-xxx"]` — **does a risk already cover this control?**
  If yes, this is almost certainly an *amendment*, not a new entry. If empty, that is a
  traceability fact to interpret at Step 3 — for a clause control, empty is *correct*.
- Jira: `text ~ "DCF-xxx"` across all projects — not just `project = CSIP`. The control may be
  driven from `IRT`, or from a project that predates the convention. Capture status, `duedate`,
  assignee, labels and description of everything that comes back.
- **The control's `ICR` ticket** — the one the run was started from, or
  `project = ICR AND text ~ "DCF-xxx"`. Read its status and every comment. A ticket in a held status
  with no dated comment is an earlier run that ended with neither ending: say so. `Done` means an
  earlier run asserted the control audit ready — re-test that at Step 10, and if it no longer holds,
  reopening needs the user's yes. A hold by decision closes only on the user's yes.
- **Any Bitpool document that describes this control's subject** — find the domain in
  [Documentation Index](documentation-index.md), then read the controlled ISMS document
  itself from `security-documentation`. This is where the real position usually lives.

State plainly what exists today, as a table, before proposing anything.

> **Where a document mirrors a controlled document, read the controlled one.** Wiki pages that say
> "this table mirrors X" are copies, and the copy is often newer than the approved original — which
> is itself the finding. Locate the source under `security-documentation` and **quote it verbatim**;
> never reason about controlled text from its mirror.

### Step 2 — The gate: mandatory clause or Annex A?

Use `Drata_listRequirements` with `framework_tag=["ISO270012022"]` and `expand=["controls"]`, plus
`code_or_name` to narrow. (`"ISO27001"` is **not** the tag on this account and returns nothing —
a silent empty result, not an error.) **Do not guess the mapping** — this gate decides which
treatments are even legal.

- **Mandatory clause (4–10)** → Scenario 1 only. Say so explicitly, and state that neither
  acceptance nor a risk register entry is available.
- **Annex A control** → all four options available; continue.

**Then read `longDescription` — the verbatim requirement text — and quote the operative part.** This
is not optional colour; it is frequently the decision. Watch for:

- **Disjunctive lists.** "on the basis of appropriate education, training, **or** experience"
  (clause 7.2b) means any *one* suffices — so a certification nobody holds may not be required at
  all, and a document demanding one has raised its own bar.
- **"Where applicable"** and similar hedges, which create room the control description hides.
- **Sub-clauses with separate obligations.** Clause 7.2 has four (a–d); a gap may sit in only one of
  them, and naming which changes the fix entirely.

Note which *other* controls share the requirement (`controls` expansion). A clause is only as ready
as its weakest mapped control, and the one you were asked about is often not the weak one.

If the mapping is ambiguous, say so and ask rather than assuming Annex A (assuming Annex A wrongly
offers an acceptance route that doesn't exist).

### Step 3 — Establish what the gap is actually against

Four situations, four different answers. Decide which before going further:

1. **Gap against the standard/control wording** → a real gap; treat it.
2. **Gap against Bitpool's own ISMS document** (our document sets a higher bar than the standard) →
   a nonconformity against our own document. Either meet the bar or **change the document** —
   flag the second option, it's often the right answer and gets missed.
3. **No real gap — the control is met, the scope was just risk-based** → record the scoping
   rationale and stop. Do not manufacture a risk entry for a control that is actually satisfied.
4. **No gap in Drata, but one of our documents declares it** — the control is `isReady: true` with
   evidence attached, and an ISMS document, wiki page or open ticket still asserts a shortfall.
   **This is a documentation defect, not a control gap**, and it is the shape most often missed
   because every Drata signal is green.

Outcome 4 in detail, because it inverts the usual instinct:

- The exposure is **not** the thing the document says is missing. It is clause **7.5.3** (a
  controlled document that no longer states the truth), **9.3** (a management review that passed
  over it), and **10.2** (a self-imposed commitment that lapsed and was never re-planned or closed).
- **Check every date in the document against today.** A commitment whose date has passed, in a
  document whose version-control table records a later annual review, means the lapse was reviewed
  and left standing. That is materially worse than the original gap and is the actual finding.
- **Count how many places state the commitment.** Controlled document, wiki mirror, Jira `duedate`,
  Drata `anticipatedCompletionDate` — if they disagree, that alone discredits the rest of the
  register. Report the divergence as a table of source → date before proposing anything.
  **Two empty cells are the intended state, not a divergence:** Drata's `anticipatedCompletionDate`
  is blank by decision, and an IRT `duedate` is empty until the prioritisation pass. Only a
  *populated* IRT date that disagrees with its parent document is a conflict — report the blanks as
  blanks, and say they are deliberate.
- The fastest exposure reduction is usually **amending the document**, not performing the task it
  describes. Say so plainly, with the cost of each.

Read the control's literal wording before deciding. Controls are frequently narrower than the
Drata evidence guidance implies.

### Step 4 — Present the paths and ask

**Stop and ask here. Do not carry a presumed answer into Step 5.**

Put **2–3 named paths** in front of the user — never one, never all four ISO options as a survey.
Each path gets the five elements in `references/treatment-decisions.md` §7: what changes, what it
costs, which documents and tickets move, **what an auditor would make of it**, and the residual
exposure that remains after taking it.

Rules for this step:

- **Recommend one**, and say why in a sentence. A menu with no recommendation pushes the judgment
  back onto the user, which is the opposite of the point.
- **Correct the framing when a proposed path isn't legally available** — most commonly a "risk
  treatment plan" or an acceptance offered for a mandatory clause. Name the route that does exist.
- **Separate the unconditionals.** Anything that must happen whichever path is chosen (a mislabelled
  reference, a weaker sibling control found at Step 2) goes in its own
  short list *outside* the paths, so choosing a path never silently drops it.
- **Cost means cost.** Courses, licences, engineering days, document-editing effort. "Document
  change only, no spend" is a real and often decisive answer.
- **Every fact needed to choose goes inside the options table.** Not in prose above it, not in an
  earlier message, not in a summary that assumes the paths are still in the reader's head. Expand
  every internal shorthand in place — Jira project keys (`IRT`, `ICR`, `OP`, `CSIP`, `CYB`), clause
  numbers, and any mechanism the choice turns on. **Never invent a shorthand for a document
  location** — quote the sentence instead. Worked failure, 2026-08-24: a run coined "L128" for line
  128 of a policy and used it for several messages as though it were a real identifier, then
  summarised its recommendation while leaving the paths two messages back. The user could not
  choose, and said so twice.
- **Offer the pragmatic option too.** Where the work is small enough to just do, *"do it — no
  ticket, no risk entry, no document change"* is a legitimate path and often the best one. Same
  worked failure: three paths were offered for about one day of configuration work, every one of
  them carrying a register entry or a document amendment, and none saying the obvious thing.
  Offering only formal routes for trivial work reads as over-engineering and invites the user to
  reject the whole frame.
- Then ask, with the recommended option first.

Once the user picks: for a **clause** control skip Steps 5–7 entirely (no risk, no scoring) and go
to Step 8. For an **Annex A** control continue to Step 5.

### Step 5 — Choose the treatment

Walk `references/treatment-decisions.md` §2–3 with the user. Name the ISO term and the Drata field
value together (`MITIGATE` / `ACCEPT` / `AVOID` / `TRANSFER`). Recommend one; don't survey all four.

Reality check: a "pure acceptance" where compensating factors genuinely exist is really a
`MITIGATE` with a residual — and it is far easier to defend. Prefer it when it's honest.

**Does any compensating measure need to become its own control?** Almost never. Drata permits
control creation but it is outside this skill's write model, the enabled control set is already
large — read its size live — and an inflated set dilutes the real ones. The three-part test for a
new control is in `references/drata-fields.md` §4; the default answer is to link an existing DCF
and put the rule in a policy.

### Step 6 — Draft the risk in risk language

Write the risk as a consequence to information, not as a missing control. Bad/good pairs are in
`references/treatment-decisions.md` §4. Show the user the draft statement and get agreement on it
**before** scoring — the wording determines the score.

### Step 7 — Score it against the policy

Read `Risk Assessment Policy` (id `17`) for the scales and the acceptable level — its content, not
its dates (Step 0). Then:

- Set `impact` / `likelihood` / `score` (inherent).
- **Always set the residual triplet too — including for `ACCEPT`, where residual = inherent.**
  Leaving it null is Bitpool's most common register defect. An explicit equal residual reads as a
  decision; a blank one reads as an omission.
- If the residual exceeds the policy's acceptable level, stop and say so. That needs a further
  control or an escalated exception — not a quiet acceptance.

### Step 8 — Check the policy still tells the truth

You have just read the governing policy to score the risk (Step 7) and established what Bitpool
actually does (Steps 1–6). That is the exact moment policy drift becomes visible — so check for it
here, every run, not as a separate exercise. If Step 3 landed on outcome 2 or 4, the drift is
already identified and this step is where you write the handoff.

Ask: **does any policy now claim something this decision proves untrue?** Three common shapes,
detailed in `references/policy-alignment.md`:

- **The policy sets a bar we don't meet** — e.g. a competence page demanding a certification nobody
  holds. Either meet the bar or amend the policy; amending is often correct and usually overlooked.
- **The policy describes a control we implement differently** — the policy says one thing, the
  register and evidence say another.
- **The policy's criteria don't match our decisions** — e.g. accepting residual scores above the
  stated acceptable level. This one invalidates the decision itself, so raise it before Step 9.
- **The document states a commitment whose date has passed** — the drift shape that outcome 4 turns
  up. Quote the lapsed text and give the date; in your report to the user, give the elapsed time
  explicitly too ("end 2024 — `<n>` months before this review"). Any record in a registered
  target — the `IRT` description, the proposed policy wording — states absolute dates only, because
  an elapsed time is false a month later. An overdue self-imposed commitment that survived an annual
  review is a clause 10.2 finding on its own, independent of whatever the commitment was about.

**Before proposing a change, establish why the clause says what it does.** A policy clause that looks
wrong often had a reason that still applies, and the reasoning usually lives in meeting notes or
prior discussion rather than in the policy itself.

This skill does not read those sources. So: check the policy's own git history in
`security-documentation` (the commit that introduced the clause, and its message — see
`isms/_meta/commit-convention.md`), then **ask the user** whether there's a decision behind it you
should know about, naming the clause and the change you'd propose. Do not propose stripping a clause
whose rationale you have not established one way or the other — say that you couldn't establish it,
and let the user decide.

**When drift is found:** draft the corrected wording, state what evidence contradicts the current
text, **hand it to `/isms-draft`**, and **claim the row on the policy queue page and post its detail
comment on the queue ticket** (see **Batched policy changes**). Never edit policy text in
`security-documentation` from this skill, and never raise a per-control promotion subtask. If the
drift invalidates the treatment decision (third shape above), stop and resolve it first.

The corrected wording is **ISMS Policy** text under the writing standard, so draft it to that
profile. The evidence that proves the old text wrong — account names, observed configuration,
counts — stays in the handoff and the queue comment, where it belongs; the proposed wording states
the requirement and its basis in categories, and shows the durability check under it
(`policy-alignment.md` §4).

If no drift, say so in one line and move on — don't manufacture findings.

### Step 9 — Put the risk in front of the user, then write it

Render the **risk approval block** — `references/drata-fields.md` §4 — as formatted markdown in
the chat, get an explicit yes, and only then call `Drata_createRisk` or `Drata_updateRisk`. §4 is
the single definition of that block; do not restate its fields here or anywhere else.

**For a clause control there is no risk block, and nothing to stage for Drata at all.** A clause gap
takes no register entry, and the control's `rationale` field is a dead end (see Bitpool context).
Stage the rationale for the **`Rationale` column of `compliance/drata-controls-register.md`** instead
— how the clause is satisfied, on what basis, where the evidence sits, and its implementation state
(implemented, or not yet implemented with the plan referenced — the plan's closing step flips it
when the work completes; the register has no other home for it) — and route it via
`/bitpool-docs`. Do not invent a register entry to have something to stage. That rationale is
durable text in `security-documentation`: draft it to that repo's writing profile where the profile
exists, and stage it with the durability check.

The block's fields and its content rules live in `references/drata-fields.md` §4; what the words may
say is the Security Drata profile's. Two things sit outside it:

- **The IRT reference inside `treatmentDetails`** names **both** the ticket key and the recovery
  query — `tracked in IRT-7 (find by: project = IRT AND text ~ "SD-04")`. The key is permitted
  here because this skill is IRT's sole writer and must keep the reference current; the query is
  what still works if the ticket moves. See `references/irt-tickets.md` §6.
- **The evidence the control needs — split by when the artefact will exist.** Read what is
  already attached with `Drata_listEvidence(control_code="DCF-xxx")` *before* drafting, so you
  propose what is missing rather than what is there. **Do not trust `flags.hasEvidence`** — see
  the flags table in `drata-fields.md` §2; it goes `true` on evidence that is invalid or belongs
  to another control. The list of attached evidence is the authority; the flag is not.

  Then produce **two** lists under the house heading **"Evidence Drata will look for"** — the
  same phrase `/describe-dcf-jira-ticket` uses, so the two skills read as one system:

  1. **Available now** — artefacts that exist today, for measures already operating. This is what
     the user can upload immediately. It does **not** make the control ready — readiness is
     failure-driven, see `drata-fields.md` §2 — it arms the renewal clock that will make the control
     go *not* ready once the artefact lapses.
  2. **Produced by a subtask** — artefacts that will not exist until a planned item lands: the
     Jira workflow export after the workflow is configured, the first attestation record after
     the first attestation. **Never recommend these as though they were available**, and never
     describe evidence for a control state that does not yet exist. Each one is paired with the
     IRT subtask that creates it — see `references/irt-tickets.md` §6, "evidence is a subtask".

  Name each artefact specifically — what it is and where it lives (the bank's
  approval-configuration screen, a Jira workflow export, the Policy Centre approval record) — never a
  category like "documentation". In the chat lists, be as specific as helps the user find and
  capture the artefact — they are advice, outside the writing standard's register. Only an evidence
  `name` or `description` you draft for the user to paste into Drata is target text: it has Drata
  as its end location and follows Security Drata §3.1 — `name` is the artefact kind, and the
  description is true of every version the bucket will ever hold — with the durability check under
  it. **This skill cannot upload evidence** — `update:evidence` is not
  granted on this connection, so `Drata_updateEvidenceArtifacts` 403s if called; see the golden
  rule, and the **"Granted scope matrix"** section of `/ask-drata`'s
  `references/drata-mcp-gotchas.md` — so both lists are for the user, and they are repeated in the
  Step 11 summary.

  A measure with no plausible artefact behind it is usually not a control. That is the cheapest
  test available for the claims you are about to write, so apply it here rather than discovering
  it at audit.

### Step 10 — Close the loop outside Drata

- **Every commitment gets an IRT ticket — created undated, estimated, and recording where its date
  will come from.** The old gate conditioned the ticket's *existence* on its date having a valid
  source, and told you to stop if it had none. **That gate is retired (2026-09-15):** a ticket no
  longer needs a date in order to exist, so nothing is blocked, and the four-copies-of-one-date
  failure on `DCF-179` is now prevented by the field staying empty rather than by refusing to create.
  Record the provenance in the **description**, with real values:

  > *"`Date constraint:` controlled document `<path>` (version `<n>`, or quoted `<YYYY-MM-DD>`)
  > states verbatim: `"<quote>"` — an input to the prioritisation pass."* — **or, where no date
  > exists anywhere** — *"`Date constraint:` NONE KNOWN."*

  Two sources fail outright, and always have: a **wiki or GitBook mirror** (this is how `IRT-1` got a
  date six months after a mirror sync while the controlled document said "end 2024"), and a Drata
  **evidence `renewalSchema` date**, which is an artefact-freshness clock, not a deliverable's
  deadline. **That prohibition is the half of the old test that mattered**, and it survives untouched
  — it now governs what the prioritisation pass may copy from.

  **The 2026-08-24 correction is itself superseded, 2026-09-15.** It patched a test that offered a
  branch reading *"copied from `<riskId>`.`anticipatedCompletionDate`"* — a field this skill
  deliberately leaves blank — while also rejecting *"a date agreed in conversation"*, which left
  genuinely new work with no valid source at all and made the rule conclude "there is no ticket" for
  work that plainly needed one. The deferral dissolves that problem rather than patching it: the
  ticket gets created either way, because it no longer carries a date.
  See `references/irt-tickets.md` §6.

  Then, by driver:
  - `MITIGATE` with outstanding work → **kind A**, created with `duedate` empty, **label `RTP`**, an
    Original Estimate in hours, and the default assignee. **A missing parent-of-record date is no longer a
    reason not to create it** — that branch was retired on 2026-09-15, and "say so and stop" with it.
    Two halves survive unchanged: the date never comes from Drata, whose `anticipatedCompletionDate`
    is deliberately left blank (see **Dates live in Jira `IRT`** in the golden rules), and **never
    invent a date to give a ticket something to carry** — which is now simply how every ticket is
    created, rather than a caution against a temptation.
  - `ACCEPT`, or any stated review cadence → **no IRT ticket**, and nothing about the entry's own
    review in `treatmentDetails` — no cadence, no review date and no reviewing control. That
    re-examination belongs to the periodic risk review control (`DCF-16`) and its recurring `CYB`
    task (Security Drata §3.2; `references/treatment-decisions.md` §5, Scenario 2). Only a
    treatment item that is itself a recurring activity cites the policy that sets its cadence, once
    the version in force is confirmed to hold it (core rule 1). Route recurrence to **`CYB`**, which
    already generates an annual risk review on a schedule. Recommend the automation rule and name
    whose job it is; never write to `CYB`.
  - **A clause commitment or an ISMS-document objective → kind C**, named for the clause rather than
    a risk, because there is no `riskId` to name it after. **Label `Clause` + `Corrective`** for a
    10.2 nonconformity, **`Clause` + `Improvement`** for a 6.2 objective. The **controlled document keeps its
    date** — clauses 6.2(k) and 10.2 require it to — and that date is quoted into the ticket's
    description as its `Date constraint:`, never into `duedate`. **A kind C ticket whose document
    states a date while the ticket carries none is the expected state**, and must not be reported as
    drift.
  - **Never a `duedate` at creation.** The field stays empty because the `ICR` control review
    programme is still running and IRT's scope, priority and workload are not yet known; dates are
    set later, board-wide, in one prioritisation pass. This rule used to read *"Always a `duedate` —
    without one the ticket isn't even findable"*, and its premise was simply wrong: the backlog is
    found by the field's **absence** —
    `project = IRT AND duedate IS EMPTY AND statusCategory != Done AND labels in (RTP, Clause)`.
    An empty `duedate` on a new ticket is correct, and is **never** a finding.
  - **Always an Original Estimate on the `Task`, and never on a `Sub-task`.** Hours only (`16h`),
    covering the whole commitment — every subtask's effort plus any third party's. Suggest the figure
    and get agreement before staging; an estimate is a field, not a schedule. It is agreed now
    precisely *because* the date is not. See `references/irt-tickets.md` §5.
  - **Always a label, and it is load-bearing.** With `duedate` empty, the backlog query is the only
    thing that finds the ticket and it filters on `labels in (RTP, Clause)` — an unlabelled ticket is
    invisible to the prioritisation pass and will simply never be scheduled. Three combinations,
    never mixed: `RTP` · `Clause` + `Corrective` · `Clause` + `Improvement`. Full scheme, plus the
    three standing labels that sit outside it: `references/irt-tickets.md` §3.
  - **More than about three distinct items is a parent `Task` plus one `Sub-task` per item**, never a
    numbered list in one description. Sub-tasks are undated, unestimated and assigned to the default
    assignee like the parent — the `Task` is the planning unit, and sequence between subtasks is
    carried by `Blocks` links, not dates. A sub-task names its remaining deliverable as an outcome;
    its current state goes in a comment and moves as the work moves. Where a subtask brings an
    evidential artefact into existence, pair it with an evidence subtask naming the artefact
    **kind**, where it will be filed and its `DCF-xxx` — never a filename, a date, a resource list or
    who will upload it (Security Jira §3.3). See `references/irt-tickets.md` §6 and §8.
- **Three-project check before creating anything.** Run
  `project in (CSIP, ICR, IRT) AND text ~ "DCF-xxx"`, plus `text ~ "<riskId>"` where a risk exists,
  and report every hit with its status, its Original Estimate, and its `duedate` where one exists.
  Bitpool has **three** parallel per-control projects, so a fourth copy of one commitment is a
  finding, not coverage. **The test keys on the commitment, not on the date:**
  - A hit already carrying this commitment — same control code, same deliverable → do **not** create.
    Report it and stop, whether or not it carries a date.
  - An **`IRT`** hit with no date → **expected, and never a finding.** It is the backlog awaiting the
    prioritisation pass; reporting it would flag every correctly created ticket on the board.
  - An **`ICR`** hit's status or missing date is **never a finding**. `ICR` carries one `Workstream`
    per control tracking *audit readiness* rather than the remediation, so it is undated by design —
    and it is the ticket this run closes or holds at the end of this step. The query always returns
    it; report it as context. (Corrected 2026-09-15, same day it was written: naming `ICR` here would
    have raised a finding against the run's own review ticket every time.) What *is* a finding is a
    `Done` `ICR` ticket whose outcome comment relies on a carrier that has since closed, or on a
    record that is no longer true — re-test it at the end of this step.
  - A **`CSIP`** hit with no date → still a finding for the skill that owns that project, which is
    not under this deferral. No case here is licence to open another artefact.
- **A lapsed commitment is ticketed with its lapse stated in full — and still undated.** Stage the
  clause 10.2 record first — the nonconformity, why it slipped, the re-planned date to be minuted —
  then create the ticket with `duedate` empty and the lapse written into the description in
  absolute dates: what was committed, in which controlled document and version, and the date it
  passed — never an elapsed time, which is false a month later. **No exemption
  applies** (Bitpool decision, 2026-09-15); the management review minute is the clause 10.2 evidence
  until the prioritisation pass re-plans it. Opening a future-dated ticket over an already-lapsed
  commitment launders a nonconformity into "In Progress" — that is what `IRT-1` did on the only
  ticket IRT had — and you cannot launder a date you never write. **The new risk is the mirror
  image:** an unstated lapse is now invisible, because there is no wrong date left to notice it by.
  Write it out in full.
- **Retiring or re-scoping a ticket — mind the order.** When the chosen path removes the need for a
  commitment, the document that declares the gap is amended **first**, and only then is the ticket
  closed as superseded. Reversing that leaves a self-declared nonconformity with nothing tracking
  it. Prefer *re-scoping* to deletion: a ticket re-pointed from "close a competence gap" to "planned
  development" keeps its history, its assignee and its audit trail. It does **not** keep its estimate
  or its date — both are re-done for the new scope, and a pass-set date is cleared so the ticket
  returns to the backlog. `references/irt-tickets.md` §7 is the authority.
- **Every commitment the document keeps needs a ticket.** If an amended document still states two
  dated commitments and only one has a ticket, raise the second. Before finishing, confirm every
  commitment the document states has an IRT ticket **and that the ticket quotes the document's date
  as its `Date constraint:`** — do **not** compare that date against `duedate`, which is empty by
  design until the prioritisation pass. A commitment named in an ISMS document with nothing carrying
  it is the exact defect this project exists to prevent.
- **Risk owner acceptance** → for anything material, propose minuting it at a management review.
  Drata's owner field alone is weaker evidence than a dated minute, and clause 6.1.3(f) wants
  evidence a named person accepted the residual risk. The minute is where the name, the residual
  level and the date live; `treatmentDetails` carries at most the anchored event — *"accepted by the
  risk owner at management review on `<date>`; minuted"* — and never the person's name. **Until
  the minute exists, the acceptance is pending:** record it in the control's `ICR` outcome comment
  (below) — a pending acceptance does not hold the ticket — and list it in the Step 11 summary as
  awaiting management review. `treatmentDetails`
  never calls it pending (Security Drata §3.2) and carries no acceptance sentence until then; the
  edit that adds one is staged once the minute exists.
- **A lapsed commitment that already carries a date is closed out, not just re-dated.** Where an
  existing ticket's date has passed, a management review minute recording *why* it slipped and what
  the new plan is satisfies clause 10.2; silently editing the date to a future one does not, and
  reads worse than the original lapse. **A ticket created today has no date to re-date** — see the
  lapsed-commitment bullet above, which governs new ones.
- **End the run on the `ICR` ticket for the control you just reviewed — close it or hold it,
  never neither. This is how a run ends.** `ICR` — ISO27001 Control review (project id `13602`)
  carries one `Workstream` per control, and a run is usually started by someone pasting its link.
  That ticket tracks **audit readiness**: closing it asserts that *this control is ready for audit
  on its recorded position* — the position is recorded, every auditor-facing record states it
  truthfully, and every remaining gap is carried by an open `IRT` ticket. It does **not** assert
  that the control is implemented, that Drata reads it ready, or that the treatment work is
  finished. Bitpool decision, 2026-09-29, settled 2026-09-30; the rule it replaced, and why, is
  `references/icr-closure.md` §5.

  **The audit-ready gate — checked, never assumed.** The ticket closes only when all three hold
  and nothing under **Holds it** below remains — a control approval still configured holds it
  whatever else is carried. A failing monitoring test is a gap like any other: an open `IRT` ticket
  whose work will make it pass carries it — unless it fails because of how the test is set up in
  Drata, which is an owner step. The checks, and how to run each, are
  `references/icr-closure.md` §2:
  1. **Recorded** — in each home that applies: the Drata risk (Annex A, where one exists), the SoA
     row (Annex A), the controlled document and its kind C ticket (a clause control), the
     `Rationale` in the control's row of `compliance/drata-controls-register.md`, and this ticket's
     outcome comment.
  2. **True** — every auditor-facing record that applies states the position truthfully today, or
     its correction is carried: by an open `IRT` ticket other than the policy queue, or by a row
     on the policy queue page whose detail comment names this `DCF-xxx` — the row in
     `git show origin/main:compliance/isms-policy-queue.md`, after `git fetch origin` in
     `security-documentation`, and its draft edit on `main` — whichever run left the row.
  3. **Carried** — every remaining gap is carried by an open `IRT` ticket whose deliverable closes
     it. `CSIP`, `OP`, `CYB` and other `ICR` tickets are not carriers. A recorded acceptance is a
     position, not a gap, and needs none.

  **Never holds the ticket:** open `IRT` work, however far off; evidence that cannot exist yet and
  that an open `IRT` ticket will produce; a failing monitoring test that an open `IRT` ticket's work
  will make pass, by fixing the control or a custom test's logic; a queue row that meets gate 2; `Implemented: N`; a risk acceptance awaiting its
  management review (record it in the outcome comment, below).

  **Holds it:**
  - a gap no open `IRT` ticket carries;
  - an auditor-facing record that misstates the position with nothing carrying its correction,
    whichever run left it — an empty `Rationale` is one, and this run writes it rather than holds;
  - evidence that exists but is not uploaded, and any step only the owner can take in the Drata UI
    — removing a control approval still configured, granted or not, is the common one, and
    excluding resources from or reconnecting a test that fails because of how it is set up is
    another. Remapping or unmapping such a test happens only on the investigated basis in
    `references/icr-closure.md` §4, and is never recommended as a way to clear the flag;
  - Drata's not-ready flag, where its cause is a control approval still configured or a test failing
    because of how it is set up (both owner steps), or a failing monitoring test that no open `IRT`
    ticket's work will make pass — never where the only causes are evidence, or tests failing because
    the control is not operating or a custom test's logic is wrong, that open `IRT` tickets will
    produce or fix
    (`references/icr-closure.md` §4);
  - a correction this run made that is not yet on `security-documentation` `main`, and a queue row
    the gate relies on that is not yet in `origin/main`'s copy of the page, whichever run left it;
  - an outcome comment that itself records an item as untracked.

  **Remove the cause in this run where you can, then close.** Most holds are minutes of work: raise
  the missing `IRT` ticket, make the record true, write the empty `Rationale` via `/bitpool-docs`.
  What only the user can do, ask for there and then — upload the artefact, remove the control
  approval in the Drata UI, commit and push the corrections — then re-check it and close. Where you
  would leave a temporary state out of the gate because it reverts before audit — recorded only in
  an `ICR` comment with the trigger that reverts it, instead of amending a durable record — ask the
  user to confirm that first, every time.

  **This run's corrections land before the ticket closes, and "landed" means on `main`.** A register
  edit, a written `Rationale`, a policy draft edit with its row on the queue page: closing over a record
  that still misstates the position is the defect this skill exists to catch. The user commits and
  pushes, so ask them to, then confirm it — `git fetch origin`, and `git diff origin/main -- <path>`
  in `security-documentation` returns nothing for each edited file — and only then close. **The
  queue page is the exception**, because other runs' rows may be pending in the same working copy:
  confirm instead that this run's row — its number, policy and link — appears in
  `git show origin/main:compliance/isms-policy-queue.md`. An edit in the working tree has not
  landed, and neither has a commit that is not pushed.

  **The endings:**
  - **Close — the gate passes.** Comment the outcome first, one comment per control, headed with
    the date: the position reached, the basis for it, what was recorded where, and any limitation an
    auditor should see stated plainly rather than left implied. Then a **Gate** table — each
    remaining gap against the open `IRT` ticket carrying it, and each record checked — and an
    **`Observed <YYYY-MM-DD>`** section holding the measurements, counts, accounts, names and
    configuration values seen during the review: the sanctioned home that keeps them out of the
    risk, the control description and the `IRT` description. Where this run changed a risk's
    scores, treatment or `treatmentDetails`, or rewrote a control description, and the change record
    was not already posted with the change (golden rules), say here what changed, why and on whose
    decision (core rule 6). Where an acceptance is awaiting its management review, record it here —
    the risk, the residual level to be accepted and the forum that will minute it. This is a
    snapshot, so be specific — but security-sensitive identifiers such as public addresses, exposed
    ports on named hosts and administrator account names go to a restricted home, and the comment
    points there (Security Jira §3.5). Then transition to `Done` — `ICR` transition id `41`. A
    ticket already `Done` whose re-test passes stays where it is; the outcome comment is the record
    of the re-test.
  - **Hold — the gate fails and the cause cannot be removed in this run.** Comment the hold, headed
    *"Held open — `<date>`"*, or *"Reopened — `<date>`"* for a ticket that was `Done`: what is
    carried and by which `IRT` ticket, so no reader mistakes it for the blocker; each thing holding
    the ticket — the record or gap, what is true, and where that is recorded; and **what closes
    it**, as a condition a later run can check, never a date. Anything measured in this run goes in
    an **`Observed <YYYY-MM-DD>`** section of the hold comment. Then **read the ticket's transitions
    and ask the user which status to hold it in** — never pick one. `In Progress` means actively
    being worked on, and Bitpool adds statuses as it needs them. A ticket already in the status the
    user names stays where it is.
  - **Hold by decision** — the user directs a hold although the gate passes. The comment records it
    as the user's decision and what they said closes it. A few such holds outlast the programme —
    `ICR-12` defers the periodic risk review until the programme completes — and they do not stop
    the prioritisation pass (golden rules).
  - **Stopped early** — a run that stops before Step 10, at Step 4's ask or on a pivot, posts a
    dated *"Review in progress — `<date>`"* comment naming the decision it is waiting on.
  - **No `ICR` ticket exists** — say so in Step 11; never create one.

  A ticket that reaches `Done` with no comment reads as work that produced no evidence, and one left
  open with none reads as a review nobody did — both invite exactly the question you don't want.

  **The permission is narrow.** Comment on the `ICR` ticket of a control this run reviewed, close it
  with `41`, and move it to the hold status the user named. **Reopening a `Done` ticket, or closing
  one whose latest comment records a hold by decision, needs the user's yes for that ticket.** Never
  create an `ICR` ticket; never edit an `ICR` description. Audit mode reports only — a reopen or a
  close goes through `/manage-drata-control DCF-xxx` for that control.

  Where a run covered several controls, end **every** `ICR` ticket it reviewed on its own gate,
  each with its own comment — closing some and holding others is normal. Worked examples, including
  the one this rule was first written from: `references/icr-closure.md` §5.
- **CSIP is read-only from this skill. Never write to it, and never cross-reference it.** Read CSIP
  at Step 1 to establish what already exists, and stop there. Do not comment on a CSIP ticket, edit
  its description, or name a `CSIP-nnn` key in anything this skill stages or creates. Reasons, in
  order of weight:
  1. **Three skills already write CSIP.** `/describe-dcf-jira-ticket` owns its `description`,
     `/create-devsecops-ticket` edits descriptions in place, `/drive-iso27001` owns status and new
     tasks. A fourth writer on the same fields conflicts, exactly as `policy-alignment.md` refuses
     for policy files.
  2. **A cross-reference is a fact stated twice.** A `CSIP-nnn` pointer can't be verified by this
     skill after it's written and won't be maintained when the ticket is superseded — so it decays
     into a confidently wrong link, which is worse than no link. The durable identifier is the
     **control code `DCF-xxx`**; anything that needs to find the CSIP ticket can query for it.

  > **Do not justify this with "CSIP is Drata's lane" — that is false.** Verified 2026-08-21: only
  > **92 of 694** CSIP issues were created by `drata@bitpool.com` (13%), and the entire 2026 body of
  > dated work was authored by a person. The reason is overlapping skill ownership and the
  > un-maintainable pointer, not integration provenance.

  **`flags.hasTicket` is provenance, not coverage — and both it and the `ticket_status` filter are
  untrustworthy.** It reads `false` for `DCF-179` while `CSIP-521` exists and is `Done`, because
  `CSIP-521` was hand-created rather than made by Drata's integration. Worse, filtering
  `ticket_status="IN_PROGRESS"` returns 111 controls **all of which carry `hasTicket: false`** — the
  filter and the flag contradict each other outright. **Never use either as a gap signal, and never
  open a ticket on the strength of one.** Resolve ticket existence by Jira query on `DCF-xxx`.
- **Factual errors in ticket bodies get fixed regardless of path.** A description that mislabels a
  credential, a system or a date is evidence an auditor may read. Correct it as an unconditional.
- **Policy drift** → hand any Step 8 finding to `/isms-draft` with the drafted wording. Where a wiki
  page mirrors the amended document, the mirror must follow in the same breath — route it via
  `/bitpool-docs` and say so, or the two drift again immediately.
- **GitBook** → also when the decision creates a **procedure a human must follow** (e.g. how to
  request a software-whitelisting exception). Route via `/bitpool-docs`. Compliance rationale
  itself stays in Drata — GitBook is for people who don't have Drata licences, not a second copy
  of the audit trail.

### Step 11 — Summarise

The summary is chat, outside the writing standard's register, so counts, names and dates are
welcome here — this is where the specifics a durable field could not carry get reported.

State: the decision and the path chosen, where each fact now lives, **what was written to Drata and
what the returned record actually says** — the assigned `riskId`, the `owners` that came back (since
non-admin users are dropped silently), and confirmation that `reviewers` came back **empty** — the
evidence the user still has to upload,
the IRT tickets raised or changed with their Original Estimates — and that each was created with no
`duedate`, pending the prioritisation pass — **each `ICR` ticket's ending**: closed, naming the
`IRT` tickets carrying its open work; or held, naming what holds it, what closes it and the status
the user chose — any policy drift handed to `/isms-draft`, the unconditionals actioned, any
acceptance **awaiting management review** (recorded in the `ICR` outcome comment until its minute
exists), any change record staged for the user to post, and what is still unverified. Where an `ICR`
ticket was closed with treatment work still open, say so plainly and name the `IRT` ticket carrying
it — that combination is the expected outcome, not a loose end. **Never report a run as finished
while its `ICR` ticket has no comment from this run.**

**Reconcile the dates that exist.** Name the single authoritative date — the controlled document's,
where clause 6.2(k) or 10.2 obliges one — and confirm the IRT ticket's `Date constraint:` quotes it
verbatim. That quote is the only live date-against-date comparison left, and it is the defect the
skill most often exists to catch, so proving it closed belongs in the summary.

**Then state the intended absences affirmatively rather than omitting them**, because an omitted
field reads as an oversight while a stated one reads as a decision:
- The IRT `duedate` is **empty pending the prioritisation pass**.
- Drata's `anticipatedCompletionDate` is **blank by decision — where a risk exists at all.** On a
  clause commitment there is no Drata risk, so that row is **`n/a`**, never "blank": reporting a
  blank field asserts a record exists, which on a clause control is a false claim in this file's own
  vocabulary. See Step 9.
- Where no document states a date either, say so: the commitment is sized and unscheduled, and the
  prioritisation pass is the mechanism. That is a complete answer, not a gap.

**Never report a policy file as updated by this skill — it does not write policy text.** It invokes
`/isms-draft`, which does. So the truthful summary line names what `/isms-draft` actually wrote and
which policy queue row was added **with the link to that row's comment**, and lists the queue page
file as left for the user to commit and push — not "handed to `/isms-draft`", which describes an
intention rather than an outcome. Same for documentation: name the repo and path `/bitpool-docs` wrote. See **Invoke
the downstream skills** above; if you did not invoke them, the work is not finished.

It *does* write Drata risks and Jira directly, so report those as done — but quote what the API
returned, not what you sent. The two differ more often than you would expect.
