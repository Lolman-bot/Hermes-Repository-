# IRT — ISO 27001 Risk Treatment Plans (Jira)

Where risk treatment plans are **recorded, owned, sized and — once scheduled — chased**. Drata holds
the risk record; IRT holds the work itself, its owner and its Original Estimate, and the date it is
eventually given.

> **Load `/bitpool-writing-standard` before drafting text for one of its registered targets — and
> only then.** Three of the outputs this file governs land in that standard's register:
>
> | Output | End location | Writing profile |
> |---|---|---|
> | Task and Sub-task `summary` and `description` (§3, §4, §6), and a retraction's replacement description (§5) | Jira `IRT` | **Security Jira** — durable |
> | Comments: the creation comment (§4), why an estimate or date changed (§5, §6), what re-scoped or superseded a ticket (§7) | Jira `IRT` | **Security Jira** — dated snapshots, and specific by design |
> | The `IRT-n` pointer, with its recovery query, in a risk's `treatmentDetails` (§6) | Drata — Risk register | **Security Drata** — a durable handle |
>
> Load the standard's `SKILL.md` for the target gate and the six rules, then the named profile,
> before drafting any of them. The profile's split is what the templates below are built on: the
> `summary` and `description` are durable; comments are snapshots, where the counts, names, accounts
> and dates belong; `assignee`, `duedate`, Original Estimate, labels and links are structured, and
> the description never restates them. Every approval block that stages a summary or description
> shows the durability check (`references/durability-check.md` §1 of that skill) directly under the
> staged text — §4, "Staging a create". **Everything else this file mentions is outside the
> register**, and the standard does not apply there: `CYB`, which this skill never writes, and the
> report to the user. `CSIP` is registered, but this skill never writes it (§6).
>
> **Requires `/bitpool-writing-standard` (section `bitpool-general`).** Before drafting text for an
> `IRT` ticket, load it. If it is not installed, **stop and tell the user once per chat**:
> *"`/bitpool-writing-standard` isn't installed, so the Security Jira writing profile can't be
> applied. Installing it from the `bitpool-general` section is recommended. Proceed without it?"* Continue
> only on a yes, and do not ask again in the same chat.

---

## 1 — Why this project exists

Confirmed with Drata support (Dratanaut, technical support, 2026-08-18), quoting their answer:

> "Short answer: no — there isn't a built-in trigger for the Anticipated Completion Date. […]
> date-based triggers (like 'Anticipated Completion Date passed without Completed Date filled') are
> not available. So the Anticipated Completion Date and Completed Date fields are mainly for record
> keeping and tracking on the risk itself, rather than automated alerts."

**Read that answer as narrowly as it was given — it is about `anticipatedCompletionDate` on a risk.
Never write "Drata cannot alert on a date."** Drata workflows can trigger on risk score changes,
treatment option changes, evidence updates and personnel compliance status. And Drata's **Evidence
Library does have a dated engine, which Bitpool already uses**: verified 2026-08-21, `DCF-179`
carried evidence id `184` with `renewalSchema ONE_YEAR` and `renewalDate 2027-07-17`.

But an evidence `renewalDate` is a **document-freshness clock that resets each time the artefact is
re-provided** — not a deliverable's deadline. On `DCF-179` that day, it was renewing annually while
the training commitment underneath it had been lapsed since end 2024, and the control read
`isReady: true`. **An evidence renewal re-attests a gap; it does not chase one.** That distinction is
the single most useful thing in this file.

So the gap IRT fills is narrower than "Drata has no dates":

| | Drata | IRT (Jira) |
|---|---|---|
| The risk record, scores, treatment rationale | ✅ authoritative | ✗ |
| `anticipatedCompletionDate` / `completionDate` | record-keeping only, no trigger | ✗ |
| Evidence `renewalSchema` | ✅ fires — but re-attests the artefact, not the deliverable | ✗ |
| **A specific deliverable with an owner and a size** | ✗ no home | ✅ the ticket itself — plus `duedate`, once the prioritisation pass sets it |
| Execution status, assignee, and an audit trail of date changes | ✗ | ✅ |

### Be equally honest about what `duedate` buys: a field, not a trigger

Jira does not alert on a due date without an Automation rule. **`IRT` has one. `CSIP` does not.**
That distinction was missed until 2026-09-15 — correct the old blanket claim wherever it survives.

**`IRT` is covered.** An Automation for Jira rule raises an **"IRT overdue"** sub-task on any IRT
ticket whose due date has passed. Verified 2026-09-15 from its *output*, not from the rule itself —
this connection exposes no verb for Automation rules: `IRT-16` (raised 2026-08-24 against `IRT-4`,
due 2026-08-22) and `IRT-64` (raised 2026-09-14 against `IRT-28`, due 2026-09-11). Its schedule, and
whether it also notifies by email, are unconfirmed. Those alert tickets carry the
**`AutomationAlert`** label (§3) so they stay out of the prioritisation backlog.

This is knowledge for this skill, **never text for a ticket**: no IRT description says what watches
it, what reads it or why its date is empty (§4).

**`CSIP` is not covered.** Measured 2026-08-21: most open dated `CSIP` issues were already past due,
several by more than two months, and nothing had fired.

> **Corrected 2026-09-15.** This section read *"Jira does not alert on a due date without an
> Automation rule, and Bitpool has none for this."* The second half was false, and it had been copied
> into the `Reader:` line of **eleven** IRT tickets — each one telling any auditor who read it that
> nothing watched Bitpool's ISO 27001 commitments. It understated a control Bitpool actually
> operates. All eleven ticket bodies were corrected the same day. It is why the §4 templates carry
> no `Reader:` line and no scheduling state at all: a claim about a mechanism, copied into every
> ticket body, goes false in all of them at once.

The mechanism at Bitpool that generates recurring work on a schedule is **`CYB` — Cyber Security
Recurring Tasks** (project id `13173`), where Automation for Jira generates Bitpool's recurring ISO
tasks — the annual risk review among them. What chases that work is the generation itself, not a
`duedate`: Bitpool's working chaser is **scheduled generation, not a date field.**

**So be exact about what creating an IRT ticket buys.** It makes the *commitment* findable in one
query; it gives you Jira's changelog as an audit trail of every date change; and — **once the ticket
carries a date** — it brings the ticket within scope of the overdue rule above. All three are real.
`project = IRT AND duedate < now() AND statusCategory != Done` is the overdue query, and it applies
to legacy tickets and to everything the prioritisation pass has dated — never to a ticket created
under the rule below. **An undated ticket is chased by nothing**, which is the deferral's accepted
cost, stated plainly rather than implied.

### Dates are deferred to the IRT prioritisation pass — create every ticket undated

**Bitpool decision, 2026-09-15.** Create every new IRT ticket with **no `duedate` at all** — not a
date copied from a controlled document, not a date agreed with the risk owner. This changes *when* a
date is set, not *where* it lives: IRT is still the only place a date will ever exist, and every rule
in this file about mirrors and about Drata's blank `anticipatedCompletionDate` is unchanged.

**Why.** A date chosen one ticket at a time, during a programme still discovering what the work is,
is a guess made without the two things that actually decide it — what else is already committed, and
how much of it there is. The **`ICR` control review programme** (ISO27001 Control review, project id
`13602`) is still running, so neither the full scope of IRT nor the relative priority inside it is
known yet. Twenty individually plausible dates do not add up to a plan, and they cannot be quietly
re-planned afterwards either: by then Jira's changelog shows twenty date changes, each of which §6
obliges you to explain.

**What carries the load instead.** The **Original Estimate**, already mandatory on every `Task` (§5).
Size the work now, while the control is in front of you and the estimate is cheap and honest;
schedule it later, once, against the whole board. That is exactly what §5 says the estimate is for —
*"a precondition for planning timelines later, and the reason it is being captured now."*

**When the deferral ends.** In one dedicated prioritisation-and-planning pass over the whole board,
once every `ICR` ticket has closed on the audit-ready gate (`SKILL.md` Step 10) — a few deliberate
holds excepted — and the IRT board is complete. **That pass is not this skill** — it
is a separate session with every ticket in front of it at once, tracked by its own standing ticket
(below). **Check whether the pass has already run before applying this rule.** It is deliberately
temporary, and a temporary rule that outlives its reason does more damage than the rule it replaced.

**It is still findable, which was the old rule's entire premise.** The undated backlog is:

```
project = IRT AND duedate IS EMPTY AND statusCategory != Done AND labels in (RTP, Clause)
```

Drop the `labels` clause and the legacy "ISO27001 Running Tasks" issues come back with it — they
follow none of these conventions. Keeping it makes the labelling rule in §3 **newly load-bearing**:
an unlabelled ticket is invisible to the pass. Say so if you ever stage one without a label.

**No new label for the undated state.** The empty field *is* the state. A label asserting the same
thing is a second copy that goes stale the moment someone sets a date — the defect the rest of this
file exists to prevent.

**What it costs — say so on every ticket you stage.** An undated ticket cannot appear in an overdue
query, so until the pass runs, *nothing at all* chases it. That is an accepted cost, not a neutral
change, and the user is entitled to hear it each time it is incurred: say it in the approval block,
and record it in the ticket's creation comment (§4). **Never in the description** — *"not yet
scheduled"* there goes false for every ticket at once when the pass runs. It is affordable because a
date on its own chases nothing — see the `CSIP` measurement above — and the overdue rule reaches a
ticket only once it carries a date.

**Not retrospective — as a rule. The board did not hold to it.** The rule: a ticket that already
carries a date keeps it, as *input* the pass reconciles rather than a backlog to be normalised. Never
strip a date from an existing ticket to bring it into line with this rule. In practice, `IRT-1`'s
changelog shows its `duedate` cleared on 2026-09-15, and by 2026-09-24 `IRT-20` and many other
pre-deferral tickets carried none. So read which tickets carry a date live —
`project = IRT AND duedate IS NOT EMPTY` — never from this file. A cleared date is history: Jira's
changelog holds it, and a description that still states or reasons from it is a factual error (§6).

**Two exemptions, and only two:**

| Ticket | Why it carries a date |
|---|---|
| The standing **`PolicyQueue`** ticket | Its `duedate` *is* the bulk-promotion mechanism, not a deliverable this programme is scoping |
| The standing **prioritisation-pass** ticket | Its `duedate` is what makes the pass happen — below |

### The prioritisation-pass ticket

One standing `Task` in `IRT`, assigned to the default assignee (§5). Its own `duedate` is when the
pass happens — read it from the ticket, never from this file or from another ticket's body:

`IRT prioritisation pass | schedule the board after the ICR control review programme`

It is the second and last legitimate `duedate` on the board, and it exists for the same reason the
`PolicyQueue` ticket does: **a bulk event that nothing triggers does not happen.**
`treatment-decisions.md` §6 already names the failure mode — *"Perpetual 'in progress'"* — and a
backlog with no date, no trigger and no owner is its undated twin.

Labelled **`PrioritisationPass`**, which takes neither `RTP` nor `Clause` — it is a standing
mechanism ticket, not a per-commitment deliverable, exactly like `PolicyQueue` (§3). Find it with
`project = IRT AND labels = PrioritisationPass`. **There is exactly one.** A search returning none is
the only case for creating one, and it is staged for approval like any other write. Its description
takes the standing-ticket shape (Security Jira profile, §3.4) — what the pass does, how it is run,
and pointers, with everything dated in comments — and points at the doc-layer page in §3 for the
convention, never at this skill file, whose repository path can change.

It also carries **no Original Estimate**: it is a scheduling act, not a commitment to be sized, and
an estimate on it would land in any board total as if it were delivery work.

**Point every undated ticket at it when you stage one** — by its label query, never by its key or
its date (§4) — so that the answer to *"when will this be done?"* is a named mechanism with a date on
it, rather than a shrug. That sentence is also the honest answer to give an auditor during the
programme: the schedule exists, it is board-wide, and it is dated — it is just not yet expressed per
ticket.

> **IRT has one doc-layer page, and this file is still framed as a proposal.** That page is
> `security-documentation/risk-management/risk-treatment-tracking.md` (§3): it states the purpose,
> the naming convention and the Drata support finding, and it mirrors this file — keep the two in
> step. `CSIP` also has a documented convention and a JQL library. This file is the working
> authority for how a ticket is created, and it still calls its conventions a **proposal** rather
> than codified Bitpool practice; it says so wherever it matters.
>
> **Never quote an IRT count from this file.** An earlier version asserted `totalCount` was **1**
> and called the project "nearly empty"; on 2026-08-24 a newly created ticket came back as
> **`IRT-20`**, so it was wrong by an order of magnitude. IRT also predates this use (it was
> "ISO27001 Running Tasks"), so most of what it holds follows none of these conventions. Get the
> live figure instead: `project = IRT ORDER BY created DESC`, or
> `project = IRT AND labels = RTP` for the subset this convention actually governs.

---

## 2 — Project metadata (verified 2026-08-18)

Stable configuration. If a create call rejects a field, re-read it with
`getJiraIssueTypeMetaWithFields` rather than guessing.

- **Cloud id:** `bitpool.atlassian.net` · **Project key:** `IRT` · **Project id:** `13535`
- **Project name:** `ISO27001 Plans` — verified live 2026-08-26. It was `ISO27001 Risk Treatment
  plans` when this file was written; it has since been renamed, so don't quote the old name back at
  the user as though it were current.
- **Issue types:** `Workstream` `11648` (hierarchy 1) · `Task` `11649` (hierarchy 0) ·
  `Sub-task` `11650` (subtask, needs `parent`)
- **Transitions:** To Do `21` · In Progress `31` · Done `41`
- **Statuses:** To Do `11907` · In Progress `11908` · Done `11909`
- **Priority:** default `Major` (`3`). Others: Blocker `1`, Critical `2`, Minor `4`, Trivial `5`

Fields available on `Task`:

| Field | Key | Use |
|---|---|---|
| Summary | `summary` | required — see §3 naming |
| Description | `description` | required by convention — see §4 |
| **Due date** | **`duedate`** | **leave empty at creation** — the prioritisation pass sets it, board-wide. **Not** a mirror of Drata; see §1. Optional on `Task` only since 2026-09-15 — see the note below |
| **Original Estimate** | **`timetracking.originalEstimate`** | effort for the whole commitment, in hours — always set **on a `Task`, never on a `Sub-task`**. See §5, "Original Estimate" |
| Assignee | `assignee` | **always the default assignee** — the person is named once, in `SKILL.md`'s Bitpool context; the convention is §5, "Assignment and retraction". The body names no person; see the same section |
| Start date | `customfield_11501` | optional |
| Labels | `labels` | see §3 |
| Priority | `priority` | default Major |
| Category | `customfield_11515` | JWM category — `allowedValues` currently empty |
| Team | `customfield_11200` | optional |
| Budget | `customfield_12631` | float — optional |

> **`cf[10200]` is `Rank`** (`gh-lexo-rank`), the board's drag-order field — **not** a date and not
> meaningful data. The saved board JQL sorts by it purely for manual ordering. Never read or write
> it as if it carried information.

> ### ⚠️ `duedate` was a **required** field on `Task`, and will be again
>
> Until 2026-09-15 the project's field configuration made `duedate` **required on `Task`** (`11649`)
> but not on `Sub-task` (`11650`). That made the deferral in §1 literally impossible for a `Task`:
> the create call and the clear call both returned `{"duedate": "Due date is required."}`. The risk
> owner made it optional the same day, which is the only reason the convention can be followed.
>
> **It is to be switched back to required once the prioritisation pass has run** (find its ticket
> with `project = IRT AND labels = PrioritisationPass`) — at which point every ticket carries a date
> and the requirement costs nothing. So this is a temporary
> configuration matching a temporary convention, and the two must move together: **if the field is
> required again, §1's deferral cannot be followed and this file is out of date.** Check
> `getJiraIssueTypeMetaWithFields` before concluding a create failure is your error rather than the
> configuration.

---

## 3 — Naming and labels

Mirror the CSIP convention so the driver can be found from its ticket and vice versa. CSIP encodes
the control (`Drata | Bitpool | DCF-xxx | [Control Name]`). IRT encodes **whatever drives the
commitment**, and there are two forms because there are two kinds of driver.

**Form 1 — risk-driven** (an Annex A risk in the register):

```
Drata | Risk | <riskId> | [Commitment]
```

The `riskId` is the search handle; the Drata risk title is not copied, because `/manage-drata-risks`
rewrites it and a copied title goes stale (writing profile **Security Jira**, §3.2). This applies to
new tickets. Existing form-1 tickets carrying a risk title are not retrofitted unless the user asks
(§6, *Legacy content*).

**Form 2 — clause-driven** (a mandatory clause 4–10, or an objective stated in an ISMS document):

```
Drata | Clause | <clause> | <DCF-xxx> | [Commitment]
```

e.g. `Drata | Clause | 7.2 | DCF-179 | ISMS lead competence development`

In both forms, `[Commitment]` names the durable commitment by its outcome, not the route chosen to
deliver it. A named course, vendor or tool goes in a sub-task or the creation comment (§4), so the
title survives a change of route — writing profile **Security Jira**, §3.2. Where the ticket exists to act on a
named object — a vendor to assess, a platform to retire — the object's name *is* the commitment.

> **Why form 2 exists, and the honest status of both.** A clause gap is a nonconformity, not a risk
> — it has **no `riskId`**, so form 1 is literally unusable for it. If the driver is a clause, there
> is no risk id to look for and its absence is **correct**; never invent one to satisfy the naming
> convention.
>
> **Both forms are proposals, not established Bitpool practice.** IRT predates this use and holds
> legacy issues following neither form — `IRT-1` was hand-created 2026-07-17 with no labels. The
> first ticket created under each form sets the precedent: **`IRT-20`** (2026-08-24, risk `CR-06`,
> endpoint clock synchronisation) is the first under form 1, in its earlier risk-title shape. Say so
> when staging under either, and resolve any claim about what IRT contains with a **live count at runtime**
> (`project = IRT AND labels = RTP`) — never a remembered figure from this file.

Find a ticket by its driver: `project = IRT AND text ~ "<riskId>"` for form 1,
`project = IRT AND text ~ "DCF-xxx"` for form 2. **Run both** when you don't yet know which applies.
There is no Drata API field holding the Jira key, so these strings are the only link — never omit
them.

**Vendor first reviews — handed over by `/manage-drata-vendors`** (its staging note, section 10).
A deferred first security review is outstanding treatment for the register risk that carries
third-party supplier security exposure, so it takes **form 1 and `RTP`** — no new form, no new
label. Resolve that risk live (`Drata_searchRisks` against the vendor-review controls, or ask);
never carry a risk id from this file. Then:

- **That risk already has an IRT treatment `Task`** (`project = IRT AND text ~ "<riskId>"`) → the
  review is a **`Sub-task`** under it, named for the vendor: `First security review — <vendor>`.
  The vendor is the named object the sub-task exists to act on (§3 above), so its name is the scope.
- **It has none** → a form 1 `Task`: `Drata | Risk | <riskId> | First security review — <vendor>`,
  created undated and estimated like any other, with the hand-off's outcome and closing step as its
  definition of done.
- **No register risk carries supplier exposure** → do not force the ticket under an unrelated risk,
  and do not invent a label. The missing risk is the finding: raise it through this skill's default
  mode first, then file the review against it.

Either way the ticket points at the Drata vendor record and never copies its scores, owner or status
(Security Jira profile §3.2), and the hand-off's creation-time context goes in the dated creation
comment staged with the create.

Labels:

**Three combinations — one per ticket, never mixed** (Bitpool decision, 2026-08-26; supersedes the
two-label scheme of 2026-08-21):

| Labels | When | Driver |
|---|---|---|
| `RTP` | Risk Treatment Plan — the driver is a risk in the Drata register, and that risk's record points back here. Parents and their sub-tasks alike | A `CR-xx` register entry |
| `Clause` + `Corrective` | Closing a nonconformity against a mandatory clause. No register entry exists, because a mandatory clause has no acceptance route | Clause 10.2 |
| `Clause` + `Improvement` | Planned betterment against a stated information security objective — no risk, no nonconformity, nothing in Drata | Clause 6.2 |

`RTP` never appears alongside `Clause`. Applied across the whole project on 2026-08-26.

> **The label is now load-bearing, which it was not before.** The prioritisation pass finds its
> backlog with `labels in (RTP, Clause)` (§1), so an **unlabelled ticket is invisible to it** and
> will simply never be scheduled. Before, a missing label cost you a tidy extract; now it costs the
> ticket its place in the plan. Never stage one without a label.

> **The open question is closed.** An earlier edition of this file asked whether a clause-driven
> corrective action should stretch `RTP` or take a third label, and provisionally chose `RTP`. The
> decision went the other way: it takes `Clause` + `Corrective`. Two reasons. **`RTP` now means one
> thing** — `project = IRT AND labels = RTP` is a clean extract of the risk treatment plan with no
> clause work mixed in, which is what an auditor asks for. And **the second label is load-bearing**:
> a corrective action must record a root cause and a check that the nonconformity did not recur
> (clause 10.2 a) and e)); an improvement objective carries neither. A bare `Clause` would hide
> which obligation applies.

**Do not invent a fourth *driver* label.** An earlier version of this file carried five
(`risk-treatment`, `treatment-execution`, `risk-review`, `accepted-risk`, `improvement-objective`)
encoding distinctions that belong in the ticket body, and asserted that an auditor would read a Jira
board and tell them apart. With one issue in the project that claim had no basis. If a ticket seems
to need another label, the distinction goes in the description — the header block already names
either the `CR-xx` register key or the clause.

Four labels sit outside the scheme, and none of them takes `RTP` or `Clause`:

| Label | Marks |
|---|---|
| **`PolicyQueue`** | The standing document-control queue. Its own `duedate` is the bulk-promotion mechanism rather than a per-commitment deliverable — one of the only two dates on the board (§1) |
| **`PrioritisationPass`** | The standing ticket that schedules the board (§1). The other of the two dates |
| **`AutomationAlert`** | An **"IRT overdue"** sub-task raised by Automation for Jira against a ticket whose due date has passed (§1). Applied to the rule itself on 2026-09-15, so new alerts carry it automatically; `IRT-16` and `IRT-64` were labelled by hand the same day |
| **`retracted-in-error`** | A ticket raised in error (§5) |

> **Why `AutomationAlert` is not optional.** An alert ticket is a notification, not a commitment. Left
> unlabelled it is invisible to the backlog query — which is harmless — but labelled `RTP` it would
> enter the prioritisation pass as though it were treatment work to be scheduled. It is neither
> estimated nor dated, and it closes when the thing it points at is dealt with.

> **`PrioritisationPass` was added 2026-09-15** and is not a fourth *driver* label — see the
> prohibition below, which governs drivers. The deferral created a standing ticket that the
> three-combination scheme has no slot for: `RTP` would put a scheduling act into the auditor's risk
> treatment plan extract, and `Clause` would assert a clause drives it. Leaving it unlabelled would
> break §1's own rule that nothing is staged without a label.

`Improvement` also has a real evidentiary use: a filtered view
(`project = IRT AND labels = Improvement`) is legitimate evidence that improvement objectives are
being pursued and tracked. Reference the JQL in the management review minute rather than pasting a
screenshot, so the evidence can be re-run rather than trusted.

Bitpool's doc-layer page for this pairing is
`security-documentation/risk-management/risk-treatment-tracking.md` — keep the two in step. That page
is written through `/bitpool-docs`, and its repo is a registered target of `/bitpool-writing-standard`
(writing profile **Security Documentation**, kept in the repo's own `_meta/writing-standard.md`) —
the standard's target gate decides whether that profile applies.

---

## 4 — Description template

A ticket carries enough to **do the work** — what the commitment delivers, its definition of done
including the closing step, and pointers back to Drata and the controlled document — and nothing
needed only to re-assess the risk without opening Drata. The `summary` and `description` are durable
text under the **Security Jira** writing profile (the block at the top of this file). What is true
only on the day the ticket is created goes in its creation comment, below.

**Form 1 — risk-driven:**

```
Risk: <riskId> — scores, treatment, owner and linked controls in Drata
Register: Risk Management (Drata)
Evidences: <DCF-xxx — only the codes this commitment's deliverable directly evidences; omit the
line where it evidences none>

What this ticket is for:
<the outcome this commitment delivers, and the gap it closes stated qualitatively as the problem>

<Accountable: <role> — only where this ticket itself assigns an accountable role>

Scheduling: scheduled by the standing IRT prioritisation pass
(project = IRT AND labels = PrioritisationPass).

Date constraint: <NONE KNOWN
| <controlled document, path> (<version n | quoted YYYY-MM-DD>) states verbatim: "<quote>" — an
  input to the prioritisation pass
| LAPSED: <controlled document, path> (<version n | quoted YYYY-MM-DD>) committed "<quote>";
  that date passed on <date>. Minuted at management review under clause 10.2, <minute ref>>
<Where this run also drafted a replacement date, write the pair (§6) instead of a single line:
Date constraint (approved): <the approved document's quote, anchored as above>
Date constraint (queued): "<the drafted replacement>" — policy queue row <n>>

On completion:
Set completionDate on <riskId> in Drata, and re-check the residual score still holds.
<Where the control's Rationale row in compliance/drata-controls-register.md reads "not yet
implemented": flip it to "implemented", via /bitpool-docs.>
Before closing, correct every record that still describes this work as outstanding — the register
Rationale, the SoA row, treatmentDetails.
```

**Form 2 — clause-driven.** No risk, no scores; the source document replaces the register:

```
Clause: <clause> — <clause title>
Control: DCF-xxx <— a Drata link in the ?q=DCF-xxx form, if one is wanted (§6)>
Driver: <corrective action under 10.2 | improvement objective under 6.2>

Source document: <controlled document, path in the isms repo>
States (<version n | quoted YYYY-MM-DD>): "<verbatim commitment text from that document>"
Mirror page: <the page's title and link, if a wiki page mirrors it>

What this ticket is for:
<the outcome this commitment delivers — the commitment itself, not the route chosen to deliver it>

<Accountable: <role> — only where this ticket itself assigns one; otherwise the source document
does>

Scheduling: scheduled by the standing IRT prioritisation pass
(project = IRT AND labels = PrioritisationPass).

Date constraint: <controlled document, path> (<version n | quoted YYYY-MM-DD>) states verbatim:
"<quote>" — an input to the prioritisation pass.
<If that date has already passed, add: LAPSED — passed on <date>; minuted at management review
under clause 10.2, <minute ref>. Where this run also drafted a replacement date, write the
(approved) and (queued) pair from form 1 instead.>

On completion:
Attach the evidence to DCF-xxx in Drata, update the source document (via /isms-draft) and its
mirror page, and confirm all copies state the same outcome. Before closing, correct every record
that still describes this work as outstanding, the register Rationale included.
```

Those closing blocks matter — closing the Jira ticket without updating the record leaves Drata or
the ISMS document still saying the work is outstanding. Always include one.

**The records come first, the ticket second — and that includes the records a closed `ICR` ticket
relied on.** An `ICR` ticket closes on the audit-ready gate with this ticket named as the carrier of
a gap (`SKILL.md` Step 10, `icr-closure.md`), so the register `Rationale`, the SoA row and the risk's
`treatmentDetails` describe that gap as still open. Close this ticket first and they are false, with
nothing left carrying their correction — and the `ICR` closure rests on a false record. Bitpool
decision, 2026-09-30, after `IRT-49` closed as done on 2026-09-29 while the `DCF-777` row still said
the Azure tagging had not been applied.

**The creation comment — staged with the create, in the same approval.** Everything true on the day
the ticket is created and expected to change belongs here, never in the description:

```
State at creation — <YYYY-MM-DD>

Created undated. Nothing chases this ticket until the prioritisation pass gives it a date; until
then it is found in the IRT backlog:
project = IRT AND duedate IS EMPTY AND statusCategory != Done AND labels in (RTP, Clause)

<Where the gap was measured: what was measured, when, by what method, and where the full result
sits — the control's review outcome (project = ICR AND text ~ "DCF-xxx") or the evidence on
DCF-xxx.>
<Where a delivery route is already chosen: the route — the course, vendor, tool or product.>
<Where part of the work was already done when the estimate was set: what was done, so the Original
Estimate reads as what remained (§5).>
```

It is a snapshot, so be specific — the counts, the accounts, the named confirmer, the date — within
the Security Jira profile's limit on security-sensitive identifiers (§3.5), which go to a restricted
home the comment points at. Correct it later by adding a comment, never by editing this one.

**Filling the templates.**

- **`What this ticket is for` states the durable outcome, not the instance.** Say what the commitment
  delivers as a capability or a category that stays true while the estate changes, then the gap it
  closes, as the problem — *"environments are separated at the network layer, not the account
  boundary; the outcome is separate development and production accounts"* — never the measurements
  behind the gap, which go in the creation comment. A ticket that exists to act on a named object — a
  vendor to assess, a platform to retire — names it, because the name is the scope. A review is
  never what an IRT ticket is for (§5).
- **The pointers carry what the ticket does not copy.** The `Risk:` line stands in for the scores,
  treatment, owner and linked controls; `Evidences:` names only the codes the deliverable directly
  evidences, never a control's name; the `Scheduling:` line points at the pass by its label query,
  never its key, its date or this ticket's scheduling state. Refer to another record's item by what
  it is — *"the application-control item on CR-01"* — never by its number, unless that record
  declares its item numbers stable (`drata-fields.md` §4): numbers there are assigned once and never
  reused, so an item may then be cited by number.
- **The `Date constraint:` forms are this skill's, and §6 says which to use.** What the anchor adds
  is that the quote names the document's version, or the date it was quoted, so it reads as what the
  document said then rather than what it says now. A lapse is stated in absolute dates — what was
  committed, in which document, and the date it passed — never an elapsed time. A clause ticket's
  document keeps its own date; §5, kind C, says why.
- **Every `<controlled document, path>` — in these templates and in §6 — is the approved copy in the
  `isms` repo (`isms/<Policy Name>.md`), never its draft.** That holds for the `Source document:`
  line and every `Date constraint:` quote alike. ISMS policies exist under `security-documentation`
  only as drafts in `ISMS/ISMS - Draft/` and `ISMS/ISMS - Draft (New)/`, and a run that queues a
  policy change edits that draft — so a ticket naming the draft as its source stops matching its own
  quote on the day it is written. The draft appears only on a `Date constraint (queued):` line,
  through its policy-queue row. An earlier form 2 template named the `security-documentation` path;
  corrected 2026-10-19.
- **No mechanism narrative.** Why `duedate` is empty, what reads the ticket, whether an automation
  watches it, what the Drata connection can or cannot upload — none of it goes in a ticket. It lives
  in this file and in `/ask-drata`, and copied into ticket bodies it goes false in all of them at once
  (the `Reader:` correction in §1). In particular, never name Drata's
  `<riskId>.anticipatedCompletionDate` as a date constraint: it is deliberately blank (`SKILL.md`,
  "Dates live in Jira IRT and nowhere else"), so naming it points at an empty field. An earlier
  template offered it as the first date source; corrected 2026-08-27.

**Never restate scores, treatment, owner or rationale — in either form.** On a risk ticket they are
Drata's fields, and every re-score or owner change would silently falsify the copy. A clause ticket
has none: if you find yourself reaching for `treatmentPlan` on a clause commitment, the gate at
Step 2 was misread.

**Staging a create.** One approval block per ticket, in this order: the summary and description;
**the durability check** on both, directly beneath them (`references/durability-check.md` §1 of
`/bitpool-writing-standard`); the creation comment, which is a snapshot and takes no check; then
Original Estimate, assignee, labels and `duedate: (none — set in the prioritisation pass)`. Say the
cost of the ticket being undated in the block itself (§1). A sub-task is staged the same way, less
the estimate (§5), and with a comment only where it has a current state to record (§6).

---

## 5 — The two ticket kinds

### Kind A — treatment execution

For `MITIGATE` risks with outstanding work.

- `duedate` = **not set.** Create it empty; the prioritisation pass schedules the whole board at
  once (§1). Where a controlled document already states a date, quote it in the body under
  `Date constraint:`, anchored by version or quote date (§4), as an input to that pass — never into
  the field.
  Drata's `anticipatedCompletionDate` is **deliberately left blank** — the old "mirror the date,
  Drata is authoritative" rule was removed on 2026-08-21 and must not be reinstated. There is still
  exactly one place a date for this commitment can ever live, and it is `duedate` here.
- Labels: `RTP`
- Assignee: **the default assignee** — see "Assignment and retraction" at the end of this section.
  The accountable party is the risk owner, whose holder is Drata's `owners` field on the risk; the
  body's `Risk:` line points there and names no person.
- On Done → human sets `completionDate` in Drata.

### Periodic review is NOT an IRT ticket

**Deleted 2026-08-21.** A stated review cadence goes to the mechanism that already fires.

**`CYB` — Cyber Security Recurring Tasks** (project id `13173`) generates recurring ISO tasks by
Automation for Jira, including `"Annual Risk review"` and its `"Review risks in register"` sub-task.
Where a record needs to mention it, name it by what it does — never by its size.

So: **do not open an IRT ticket for a review cadence**, and never build a self-perpetuating chain of
them — a manual chain duplicating a working automation is strictly worse than the automation.
Instead:

- The risk's `treatmentDetails` does not state the entry's own review at all — no cadence, no
  review date and no reviewing control. That belongs to the periodic risk review control (`DCF-16`)
  and its `CYB` recurring task (writing profile **Security Drata**, §3.2). Only a treatment item
  that is itself a recurring activity cites the policy that sets its cadence — never the cadence
  itself, and never the generator's schedule; where no policy in force sets one, the standard's core
  rule 1 applies.
- Where no recurring generator covers it, **recommend the `CYB` automation rule and name whose job
  it is.** This skill never writes to `CYB`.
- Jira Cloud has no native recurring issues, so scheduled *generation* is the only real recurrence —
  never imply a review will reappear on its own.

This also fits the label scheme: `RTP` and `Improvement` have no slot for a review ticket, which was
the signal that IRT was the wrong home for one.

### Kind C — clause commitment

For a commitment whose driver is a **mandatory clause (4–10)** or an objective stated in an
ISMS document. No risk exists, so form 1 naming and the score fields don't apply.

- Naming: **form 2** — `Drata | Clause | <clause> | <DCF-xxx> | [Commitment]`
- `duedate` = **not set**, exactly as for kind A. The controlled ISMS document is still
  authoritative on what was committed — quote its date verbatim in the body under `Date constraint:`,
  anchored by version or quote date (§4), so the prioritisation pass inherits it.
  **The document's own obligation is untouched.** Clause 6.2(k) requires an objective to state when
  it will be completed and clause 10.2 requires a corrective action to be dated; this deferral moves
  the *Jira field*, not the document, so no ISMS document loses a date it is required to carry and
  the change raises no conformity question. If the pass later wants a date the document contradicts,
  **the document still wins** — amend it via `/isms-draft` in the same change, minuting the lapse
  under 10.2 where the original date had already passed, rather than letting the two disagree.
- Labels: **`Clause` + `Improvement`** where the deliverable is betterment; **`Clause` + `Corrective`**
  where it closes a real nonconformity. Never unlabelled, and never a bare `Improvement` — §3's
  three-combination scheme is the authority, and the pairing is what the backlog query keys on.

  > **Corrected 2026-09-15.** This bullet still carried the superseded answer (*"`RTP` where it
  > closes a real nonconformity"*) and pointed at *"the open question in §3"*, which §3 records as
  > **closed** since 2026-08-26 in favour of `Clause` + `Corrective`. Harmless while labels were
  > only an extract convenience; not harmless now that `labels in (RTP, Clause)` decides whether a
  > ticket is visible to the prioritisation pass.
- Assignee: **the default assignee** (§5, "Assignment and retraction"). The body points at the
  source document that assigns the competence, task or objective; it names no person.
- On Done → attach evidence to the control in Drata, then update the source document **and its
  mirror** so no copy still states the commitment as outstanding.

**One ticket per stated commitment.** A document that names two commitments needs two tickets.
This is the most common way a commitment goes unchased: the first gets a ticket, the second is
assumed covered by it, and only the first is ever visible on the board.

---

### Original Estimate — on the `Task`, never on a `Sub-task`

Bitpool decision, 2026-08-26. Every IRT `Task` carries an **Original Estimate** so the board can
later be used to plan due dates, sequencing and capacity. Until now IRT held dates with no notion of
how much work sat behind them, so two tickets due the same week were indistinguishable whether one
was an hour of admin and the other a fortnight.

**Field:** `timetracking`, set as `{"timetracking": {"originalEstimate": "16h"}}`. Verified
2026-08-26 via `getJiraIssueTypeMetaWithFields` on project `IRT`: `timetracking` is present and
settable on **both** `Task` (`11649`) and `Sub-task` (`11650`), with operations `set` and `edit`.

#### The four rules

1. **Write it in hours — always `Nh`, never `d` or `w`.** `40h`, not `1w`. Whole hours, minimum
   `1h`; the precision available here does not justify `2.5h`.

   > **Know what Jira does with it, because the board will not show you what you typed.** Verified
   > 2026-08-26 by writing all eight estimates and reading them back: Jira stores the value as
   > **seconds** (`originalEstimateSeconds`) and re-renders it using the site's working-day config —
   > so `48h` came back as `"1w 1d"`, `80h` as `"2w"`, `45h` as `"1w 5h"`. The stored number is
   > exact and config-independent; only the rendering is not. **So never read an estimate back off
   > the board and treat the `d`/`w` string as what was recorded** — compare
   > `originalEstimateSeconds`, or divide it by 3600. An earlier draft of this rule claimed hours
   > "never depend on the config"; that is true of what is stored and false of what is displayed,
   > and the difference is exactly where a misreading would come from.

2. **`Task` level only. Never set it on a `Sub-task`** — even though Jira will happily accept one.
   This is a convention Jira does not enforce, so it has to be held deliberately. The reason is that
   Jira rolls subtask estimates up and displays the sum **alongside** the parent's own value: set
   both and the two disagree the moment either is edited, and no reader can tell which number the
   plan was built from. One estimate, on the unit that is actually planned and sequenced — the
   `Task`.

3. **The `Task` estimate is whole-of-commitment.** It covers *all* the effort under that ticket:
   every subtask's work plus anything done at parent level. A `Task` with nine subtasks must not
   read smaller than a standalone one that happens to be a single day's work. This follows directly
   from rule 2 — with subtasks unestimated, the parent is the only place the total can live.

4. **Third-party work counts — estimate the whole engagement, not Bitpool's share of it.** Bitpool
   decision, 2026-08-26. `IRT-18`'s estimate covers the external auditor's fieldwork, not just the
   hours spent sourcing and contracting them; `IRT-1` and `IRT-2` cover the full external course and
   examination, not just the booking.

   > **The direct consequence, and it must be stated wherever a total is quoted: the sum of this
   > board is not Bitpool's workload.** It mixes our capacity with other people's. Never present a
   > board-wide total as "the team's remaining effort", and never use it to argue for or against
   > taking on other work, without first separating the third-party lines out by hand.

#### Be as honest about the estimate as §1 is about the date

An Original Estimate is **a field, not a plan.** Nothing in Jira derives a `duedate` from it, nothing
schedules from it, and no Bitpool automation reads it today. What it buys is that the number behind
each date is written down and comparable — which is a precondition for planning timelines later, and
the reason it is being captured now. **Never tell the user that estimating a ticket has scheduled,
sequenced or resourced it.**

#### Estimating, changing and closing

- **Estimate the work that actually remains, not the work as originally conceived** — the same rule
  as "write the work, not the wish" in §6. If some of a `Task`'s subtasks are already Done when the
  estimate is first set, size what is left, and say so in a comment on the ticket — the creation
  comment, where the estimate is set at creation (§4) — because the field is called *Original*
  Estimate and a reader will otherwise assume it was the whole job. The description never carries the
  count, or the estimate itself: the field is its home.
- **Do not decrement it as subtasks close.** Original Estimate is a baseline; Jira's Remaining
  Estimate and worklog are the fields that move, and Bitpool uses neither. A baseline that gets
  quietly rewritten as work completes can never show that anything was underestimated.
- **Suggest; never set or change an estimate unasked.** Propose the figure with the reasoning that
  produced it and get agreement — on the original value *and* on any later change. Identical to the
  date rule in §6, and for the same reason: it is a commitment being made on someone's behalf.
- **When an estimate changes, add a Jira comment saying why.** Scope grew, the third-party quote came
  in, three subtasks turned out to be one. The changelog proves *what* changed; only the comment
  explains *why*, and an estimate that doubles with no recorded reason reads as the record of a bad
  estimate being tidied away.
- **Re-scoping re-estimates.** §7 prefers re-scoping a ticket to closing it — a re-scoped ticket
  keeps its date (where one has been set), its assignee and its history, and it must get a fresh
  estimate in the same change, not inherit the old one. An estimate carried across a change of purpose is worse than no estimate,
  because it looks deliberate.
- **A retracted ticket keeps its estimate.** Leave it as-is under the §7 retraction procedure. It is
  part of the record of what was believed at the time, and the ticket is going to Done anyway.

---

### Assignment and retraction — assignment settled 2026-09-15

**Every IRT ticket is assigned to the default assignee — the default person named in `SKILL.md`'s
Bitpool context** (Bitpool decision, 2026-09-15). This file never names the person, so a change of
owner is one edit there. This is the convention now, not a workaround to be explained away: IRT is
a single-owner board, and the pass that schedules it is a single-owner exercise. The assignee is a
structured field — the description never restates it.

The project also enforced it. Verified 2026-08-21, two other staff accounts were rejected with
`User '<accountId>' cannot be assigned issues.` — so there was never a second option, and a ticket
staged for anyone else failed at the write. Project access may have changed since; the convention
above does not depend on it.

> **Superseded 2026-09-15.** This section used to treat single-assignee as a *limitation*: it told
> you to declare the assignee a stopgap in the body, name who the ticket should belong to, and raise
> the project-access gap so the workaround had an expiry. Drop all three — there is no workaround to
> expire. What survives is the measured fact above, which is why staging anyone else is pointless.

**The body says who answers for the work — by role and pointer, never by name.** Kind A's
accountable party is the **risk owner**, whose holder is Drata's `owners` field on the risk the
`Risk:` line names; kind C's is whoever the source document assigns the objective or the competence
to. Name a role in the body only where the ticket itself assigns the accountability (the writing
standard's rule 5). The `assignee` field says who is driving the work; the body points at who answers
for it; the person holding that role lives in exactly one home. Never leave a ticket unassigned to be
technically correct — an unassigned backlog item has nobody to plan it, and on the board it reads as
work no one has picked up.

**The Atlassian MCP has no delete verb.** A ticket raised in error cannot be removed from here.
Retract it instead, in this order:

1. Rewrite `summary` to `RETRACTED — <one-line reason>`.
2. Replace `description` with why it was wrong and what supersedes it — a reader landing on it in
   six months must not have to reconstruct that.
3. Clear `duedate` (pass `null`) **only if one was ever set** — a ticket created under §1 has none.
4. Replace the labels with `retracted-in-error`.
5. Transition to Done (`41`).

**Finish steps 3–5 in the same run.** Step 4 is what drops the ticket out of the prioritisation
backlog (`labels in (RTP, Clause)`) and step 5 is what drops it out of `statusCategory != Done`.
A retraction abandoned after step 3 leaves a retracted, undated, still-labelled ticket sitting in the
very census the pass will schedule from — and since every write here is separately staged and
approved, stopping half way is a real outcome, not a hypothetical.

Then tell the user it can be hard-deleted in the UI if they prefer. Never quietly close a mistaken
ticket with its original text intact — a closed ticket that still reads as a real commitment is
worse than an open one.

---

## 6 — Rules

- **More than about three distinct items means a parent Task plus Sub-tasks — not a numbered list
  in one description.** A treatment plan with nine items crammed into one ticket body has one status
  and one assignee for nine separate pieces of work, so nothing can be closed or owned individually,
  and the board shows one open item where there are nine. Create the parent `Task` (form 1 or 2
  naming), then a `Sub-task` (`11650`, set `parent`) per item — **assigned to the default assignee
  like every other IRT ticket (§5)**, with an accountable role in the body only where the sub-task
  assigns one — but **no `duedate`** (§1) and **no estimate**, which stays on the parent alone (§5).
  The parent's Original Estimate is the whole job including every subtask.

  > **Corrected 2026-09-15.** This read *"per item with its assignee"*, written when subtasks were
  > expected to carry different owners. Since only the default assignee could be assigned in this
  > project (verified 2026-08-21, §5), staging one assignee per subtask passed the approval gate and
  > then failed at every write — leaving a parent with no children and a half-finished run.

  **The planning unit is therefore the `Task`.** The parent is what the prioritisation pass sequences
  and dates, because the parent is where the only estimate lives; sequence *between* subtasks is
  carried by `Blocks` links (§8), not by dates. The old roll-up rule — *"the parent's `duedate` is the
  latest subtask's"* — cannot be computed from undated subtasks and is retired from the creation
  rules; it returns, if wanted, as a rule for the pass. Being a subtask was never a licence to invent
  a date, and now there is no date to invent.
- **Write the work, not the wish.** A subtask's summary and description name the remaining
  deliverable as an outcome; its current state goes in a comment and moves as the work moves. If a
  GuardDuty configuration is written but not deployed, the item is "deploy to every account and
  capture the export for `DCF-xxx`", not "write the configuration" — otherwise the ticket reads as
  outstanding work that is already done, and the real remaining step is invisible. *"Written, not yet
  deployed"* is the comment, never the description: it goes false the day the deployment lands.
  **Policy promotion is the one thing that never becomes a subtask at all:** a policy draft edited
  but not promoted is recorded in the policy queue — a detail comment on the standing `PolicyQueue`
  ticket and its row on the queue page. See the policy-promotion bullet in §6 and **Batched policy
  changes** in `SKILL.md`.
- **Evidence is a subtask, not a footnote — "do the thing" then "upload evidence of the thing".**
  Where completing a subtask brings an evidential artefact into existence — a Jira workflow
  export, a GuardDuty configuration, a Policy Centre approval record — pair it with an evidence
  subtask naming the artefact **kind**, where it will land and the `DCF-xxx` it attaches to — *"the
  configuration export, filed in the GRC evidence library and attached to `DCF-xxx`"* — never a
  filename, a date, a resource list or the person who will upload it. A line inside a description is
  not a unit that can be owned, estimated, scheduled or closed; a subtask is, and it appears on the
  board and in the prioritisation backlog in its own right.

  This is also what keeps the evidence honest. The artefact does not exist until the work is
  done, so it cannot be recommended or uploaded before then — pairing it with the subtask that
  creates it is what makes the timing self-evident instead of something to remember. Evidence
  for measures **already operating** does not need pairing: it exists now, so it goes in one
  "upload the evidence available today" subtask.

- **Stage every write, then execute.** Never create or edit an IRT ticket without showing the exact
  summary, description, **original estimate**, assignee and labels first and getting a yes — and show
  the due date too, written on a create as `duedate: (none — set in the prioritisation pass)` rather
  than quietly omitted, so a reader can see it was a decision and not an oversight. A real staged date
  appears only when one is genuinely being set or changed. Wherever a summary or description is
  staged — a create or an edit — the **durability check** sits directly under it, and a create stages
  its creation comment in the same block (§4, "Staging a create"). Same rule `/drive-iso27001`
  applies to CSIP.
- **Search before creating.** `project = IRT AND text ~ "<riskId>"` — prefer updating an existing
  ticket to opening a duplicate.
- **Policy promotion is never a ticket you create.** There is one standing `PolicyQueue` Task
  holding every pending policy change — the detail in one comment per change, indexed on the queue
  page in `security-documentation` — promoted in a single bulk event. Claim the row on the page and
  post its comment; do not raise a subtask. Find it with `project = IRT AND labels = PolicyQueue`,
  and see **Batched policy changes** in `SKILL.md` for the comment format, the index columns and the
  claim-first order that keeps concurrent runs from taking the same row number.
- **Never create a ticket *with* a `duedate`.** Not a date copied from a controlled document, not a
  date agreed with the risk owner — see §1. An empty `duedate` on a new ticket is **correct**, and
  must never be reported as a defect, a finding or an omission by this skill or any other. The only
  two standing exemptions are named in §1, and neither is produced by an ordinary control review.
- **Never create a `Task` with no Original Estimate**, and never put one on a `Sub-task`. Hours only
  (`16h`), whole-of-commitment including any third-party effort — see §5, "Original Estimate", for
  all four rules and for what the field does *not* buy.
- **The parent-of-record test is no longer a creation gate — it is the prioritisation pass's test.**
  Nothing is sourced at creation because nothing is set. What the ticket does at creation is record
  the *constraint*, so that the pass inherits it instead of rediscovering it:
  - **A date already exists somewhere** → quote it verbatim in the body from the **controlled
    document** that states it, anchored by the document's version or the date it was quoted:
    *"`<controlled document, path>` (`<version n | quoted YYYY-MM-DD>`) states verbatim:
    `"<quote>"`."* The anchor is what keeps the quote true after the document is revised — it reads
    as what the document said then (writing profile **Security Jira**, §3.2).
    **Quote the currently *approved* document, never a draft edit made in this run** — a queued draft
    is not yet controlled (see **Batched policy changes** in `SKILL.md`). Where this run drafted a
    replacement, record both: `Date constraint (approved):` with the lapsed quote, and
    `Date constraint (queued):` with the drafted replacement and its policy-queue row number, so the
    pass can see which is which. Two
    sources fail outright and always have: a wiki/GitBook **mirror**, and a Drata **evidence
    `renewalSchema` date** (artefact freshness, not a deliverable deadline). Read the controlled
    document, never its copy. **This prohibition is the half of the old test that mattered, and it is
    untouched** — it now governs what the pass may copy from, rather than what you write today.
  - **No date exists anywhere** → write `Date constraint: NONE KNOWN` and stop. Do **not** agree one
    with the risk owner to fill the gap. When the pass does agree a date, IRT is still its sole
    origin, `anticipatedCompletionDate` still stays blank, and there is still only ever one copy.

  > **What this replaces, and why the 2026-08-24 correction is no longer needed.** That correction
  > existed to unblock work: the old test offered a branch *"copied from
  > `<riskId>`.`anticipatedCompletionDate`"* — a field the skill forbids populating — while also
  > rejecting *"a date agreed in conversation"*, so genuinely new work had **no** valid source at all
  > and the rule concluded *"there is no ticket"* for work that plainly needed one. The deferral
  > resolves that more cheaply: the ticket is created regardless, because it no longer needs a date in
  > order to exist. `IRT-20` — the Intune endpoint-clock task under `CR-06`, the worked example that
  > forced the 2026-08-24 fix — was a pre-deferral ticket with an agreed date, and by 2026-09-24 no
  > longer carried it. See **Not retrospective** in §1.

  > **Corrected 2026-08-24, because the old test was self-contradictory and blocked real work.** It
  > offered a first branch — *"copied from `<riskId>`.`anticipatedCompletionDate`"* — while §1 and
  > `SKILL.md` simultaneously require that field to stay **blank**. Both cannot hold: the branch
  > pointed at a field the other rule forbids populating. And because the test also failed "a date
  > agreed in conversation", genuinely new work had **no** valid source at all, so the rule
  > concluded *"there is no ticket"* for work that plainly needed one. Worked example: an Intune
  > endpoint-clock task under risk `CR-06` had neither a risk date nor a document date, and the
  > honest answer was to agree one and let `IRT-20` be its single home.
  >
  > What survives is the prohibition on **mirroring** — sourcing a `duedate` for a commitment whose
  > date already lives somewhere else, and getting it wrong. That is what produced four conflicting
  > dates on `DCF-179`. Originating a date and badly copying one are different acts, and only the
  > second is the defect.
- **Three-project check first.** `project in (CSIP, ICR, IRT) AND text ~ "DCF-xxx"`, plus
  `text ~ "<riskId>"` where a risk exists. Bitpool runs three parallel per-control projects, so a
  fourth copy of one commitment is a finding, not coverage. **Don't carry their sizes from this
  file** — the figures once written here (`CSIP` 694, `ICR` 30, `IRT` 2) were a 2026-08-21 snapshot
  and the IRT one was already wrong by 2026-08-24; the query above is the answer.

  **The duplicate test is the commitment, not the date.** A hit already carrying this commitment —
  same control code, same deliverable — means **don't create**: report it and stop, whether or not it
  carries a date. Then for the hits that do *not* already carry it:
  - **In `IRT`, an undated hit is the expected state** and is never a finding. Say so rather than
    reporting it, or you will flag every correctly created ticket on the board.
  - **An `ICR` hit's status or missing date is never a finding.** `ICR` carries one `Workstream` per
    control, tracking *audit readiness* rather than any remediation, so it is undated by design — and
    it is the very ticket this run closes or holds at the end. The three-project query always
    returns it; report it as context, never as a defect. What *is* a finding is a `Done` `ICR` ticket
    whose outcome comment relies on a carrier that has since closed, or on a record that is no
    longer true — re-test it at Step 10 (`icr-closure.md`).
  - **A `CSIP` hit with no date is still a finding** for the skill that owns that project. `CSIP` is
    not under this deferral, and nothing here changes what a missing date means in it.

  > **Corrected 2026-09-15**, same day it was written. The bullet originally named `CSIP`, `ICR` and
  > `CYB` together, which would have raised a finding against the control's own `ICR` Workstream on
  > **every single run** — and `CYB` was in the branch while absent from the query above it, so that
  > third of the rule could never fire at all.
- **Suggest dates; never set or change one unasked.** Propose the date with your reasoning and get
  agreement — on the original value *and* on any later change. This is a Bitpool rule (2026-08-21),
  not a courtesy. **Since 2026-09-15 it governs the prioritisation pass rather than ticket creation**,
  because no date is proposed at creation at all. That makes it stronger, not weaker: the pass sets
  every date on the board in a single act, and that act is not taken unilaterally.
- **When a date changes, add a Jira comment saying why.** Jira's changelog proves *what* changed;
  only the comment explains *why*, and the why is what an auditor asks for. A date moved without a
  recorded reason reads as the record of a lapse being overwritten.

  **A first date is an origination, not a change.** When the prioritisation pass gives an undated
  ticket its `duedate`, record the pass and the reasoning that placed it where it landed — do not
  write it up as a move, because nothing moved. The lapse-overwriting concern applies only to shifting
  a date that already existed.
- **A lapsed commitment is ticketed with its lapse stated in full — and still undated.** Stage the
  clause 10.2 record first, then create the ticket with `duedate` empty and the lapse written into the
  body: what was committed, in which controlled document, and the date it passed — absolute dates,
  never an elapsed time, which is wrong a month later (the `LAPSED` form in §4).
  **No exemption applies here** (Bitpool decision, 2026-09-15) — re-planning happens in the
  prioritisation pass, and until then the **management review minute is the clause 10.2 evidence**,
  which is what §7 already says: the minute is the evidence, the ticket is only the alarm.

  The old laundering risk is *reduced* by this, not created: a future-dated ticket over an
  already-lapsed commitment turned a nonconformity into "In Progress", and you cannot quietly
  overwrite a lapsed date if you never write one. **But the new failure mode is the mirror image and
  must be guarded deliberately** — a lapse left unstated in the body is now invisible everywhere,
  because there is no wrong date left to notice it by. Write it out in full. See §7.
- **One ticket per commitment**, not one per risk — and past about three, they become
  subtasks of a parent `Task` under the subtask rule above, or a `Workstream` if it is genuinely a
  programme of work.
- **Don't restate the rationale.** The treatment reasoning lives in Drata `treatmentDetails`, and
  the scores, treatment, owner and linked controls in the risk's own fields. IRT carries the
  commitment, its outcome and definition of done, the date (in `duedate`, once set) and a pointer —
  not a second copy that will drift (§4).
- **Legacy content:** IRT predates this use (it was previously "ISO27001 Running Tasks"), so it holds
  items that aren't risk treatment plans. Don't assume every IRT issue follows this convention, and
  don't retrofit old ones unless asked.
- **Fix factual errors in a description on sight.** A ticket body that mislabels a credential, a
  vendor, a system or a date is evidence an auditor may read, and it's wrong regardless of which
  path the user picks. Stage the correction as an unconditional, not as part of a path. The corrected
  text replaces the old; the reason goes in a comment beside Jira's changelog entry — never a
  *"Corrected `<date>`: this line read…"* paragraph inside the description (writing profile
  **Security Jira**, §3.1).
- **Never cross-reference a `CSIP` key.** Not in a summary, not in a description, not in a comment.
  Three skills already write CSIP — `/describe-dcf-jira-ticket` owns its `description`,
  `/create-devsecops-ticket` edits descriptions in place, `/drive-iso27001` owns status and new
  tasks — so a fourth writer collides, exactly as `policy-alignment.md` refuses for policy files.
  And a `CSIP-nnn` pointer is a fact stated twice that this skill cannot keep true, so it decays into
  a confidently wrong link **that this skill has no means to repair**, since it never writes CSIP
  again after staging. Reference the **control code `DCF-xxx`** instead — it is stable, and anything
  needing the CSIP ticket can query `project = CSIP AND text ~ "DCF-xxx"`. Same for `ICR` and `CYB`.

  > **This is about write ownership, not about ticket keys being bad in general.** An `IRT-n` key
  > *is* permitted in Drata `treatmentDetails`, because this skill is IRT's sole writer and can keep
  > that reference current — see the ownership rule below. The distinction is maintainability, not
  > the shape of the identifier.

  > **The reason is overlapping ownership, not "CSIP is Drata's lane."** That second claim is false
  > and must not be used: verified 2026-08-21, only a small minority of the CSIP issues existing that
  > day had been created by Drata's integration account, and the whole 2026 body of dated work had
  > been authored by a person. A governing rule resting on a false premise is the rule that gets
  > overturned later.
- **Reference controls by code, never by Drata's internal numeric id.** `DCF-179` is the durable
  handle; `app.drata.com/compliance/control-details/210/...` embeds surrogate key `210`, which is an
  implementation detail of Drata's database, not an identifier Bitpool controls. If a URL is wanted,
  keep the `?q=DCF-179` form and say which control it is in text, so the link degrades to something
  a human can still resolve.
- **The test is ownership, not re-derivability: reference what this skill owns; never reference what
  it doesn't.** This is the principle behind both rules above, and it is the one to reason from.
  - This skill is **`IRT`'s sole writer**, so an `IRT-n` key is one it can keep true — it will be
    here when the ticket is renamed, re-scoped or superseded, and §7 obliges it to update the
    reference. So **an `IRT-n` key in Drata `treatmentDetails` is permitted** (Bitpool decision,
    2026-08-21).
  - It writes **none** of `CSIP` or `CYB`, and on `ICR` it only posts comments on, closes or holds
    the reviewed control's ticket (`SKILL.md` Step 10), so a key into any of those is a claim it has no
    means to maintain. Those get referenced by **control code** and a query instead.
  - A Drata internal numeric id (`control-details/210/`) is owned by nobody at Bitpool — it is
    Drata's surrogate key. Never use it as an identifier.
- **A permitted reference carries a maintenance duty.** If you write `IRT-n` into Drata
  `treatmentDetails`, then whenever that ticket is superseded, re-scoped or closed, the Drata prose
  is part of the change — stage the `treatmentDetails` edit in the same block as the ticket change,
  never as a follow-up. That block spans two profiles, so its one durability check carries a
  `Profile` column (Security Jira for the ticket text, Security Drata for `treatmentDetails`), and
  the dated comment recording the `treatmentDetails` change goes on this same `IRT` ticket. A reference this skill *could* maintain but didn't is worse than one it
  never made, because the rule above promises it is current.
- **Belt and braces: name the `riskId` alongside the key.** Write
  `tracked in IRT-7 (find by: project = IRT AND text ~ "SD-04")` rather than the bare key. The key
  is what a human reads; the query is what still works if the ticket is moved or deleted. Costs one
  clause and removes the only real failure mode of the decision above.

---

- **A dependency between tickets is a Jira link, never a sentence.** Where one item gates
  another, create a `Blocks` link — see §8 for the direction, which is easy to reverse.

## 7 — Retiring, re-scoping and superseding

The skill creates tickets far more often than it removes them, which is why this gets its own
section: **the removal is where the damage happens.**

### The sequencing rule

> **Amend the document first. Close the ticket second. Never the reverse.**

An IRT ticket is frequently the *only* artefact evidencing clause 7.2(c) / 10.2 — "actions taken"
against a gap the organisation has declared in writing. Close it while the ISMS document still says
the gap exists, and you have converted a tracked commitment into an untracked self-declared
nonconformity. That is strictly worse than either end state.

Order every staged plan explicitly:

```
1. /isms-draft amends <document> — removes/updates the declared gap   ← must land first
2. Wiki mirror follows via /bitpool-docs
3. IRT-n re-scoped or closed as superseded                            ← only after 1 and 2
```

If the user wants the ticket dealt with today and the document change will take longer, **leave the
ticket open** and say why. An open ticket against a stale document is a known, tracked state. The
inverse is an invisible one.

### Prefer re-scoping to closing

A ticket re-pointed at a new purpose keeps its assignee, its history and its audit trail. Closing and
re-raising loses all three, and looks like the commitment was abandoned and quietly restarted.

**It does not keep its date.** Where the pass had already dated it, the date is cleared and the
ticket returns to the backlog — the table below is the authority, and §5's re-estimate rule gives the
reason: something carried across a change of purpose looks deliberate. History, assignee and audit
trail survive a re-scope; a commitment to a date does not.

| Situation | Do this |
|---|---|
| The gap is gone, but the work is still wanted | **Re-scope** to kind C, relabel to `Clause` + `Improvement`, and **re-estimate for the new scope**. If the pass had already dated it, **clear the `duedate` and return it to the backlog** — a date carried across a change of purpose is the same defect as an estimate carried across one, and for the same reason: it looks deliberate. Comment what changed and which document version changed it. |
| The gap is gone and the work is no longer wanted | Close as superseded, with a comment naming the document change that removed the need |
| The gap remains, the date has passed | **Re-date, and minute the lapse** — see below. Don't silently edit the date. Applies to a ticket that *has* a date; an undated one has nothing to re-date and waits for the pass, with the lapse stated in its body (§6) |
| The commitment split into two | Keep the ticket for the first, raise a sibling for the second — and **split the estimate across the two**, don't leave the original on both |

When closing, always leave a comment recording **what superseded it** — the document, the version,
and the decision date. A ticket that goes to Done with no explanation reads as completed work that
produced no evidence, which invites exactly the question you don't want.

### A lapsed date is not fixed by re-dating it

> **This subsection applies only to a ticket that already carries a date** — a pre-deferral one, or
> one the prioritisation pass has dated. **A ticket created under §1 has no date to move:** state the
> lapse in full in its body, minute it under clause 10.2, and let the pass schedule it (§6). Scoped
> 2026-09-15, because §6's lapsed-commitment rule cites this subsection as its authority and a reader
> following that pointer landed on what read as an unconditional instruction to date the ticket.

Where a commitment's date has already passed, editing it to a future date is **not** a corrective
action — it's the record of the lapse being overwritten. Clause 10.2 wants the nonconformity, its
cause, and the action taken.

So: re-date the ticket **and** minute at management review why it slipped and what changed. Note the
new date in the minute. The minute is the evidence; the ticket is only the alarm.

Worth stating plainly to the user, because the instinct runs the other way: **a lapsed commitment
that was reviewed and honestly re-planned is a healthy management system. A lapsed commitment whose
date was quietly moved is a finding.**

---

## 8 — Dependencies between tickets: link them, never narrate them

**Bitpool decision, 2026-08-27.** Where one IRT item cannot start until another lands, that
dependency is expressed as a **Jira issue link**, not as a sentence inside a description or a
`treatmentDetails` item.

Prose dependencies do not survive. They cannot be queried, they do not appear on a board, they
break silently when items are renumbered, and they are invisible to anyone who opens the blocked
ticket rather than the risk entry. `CR-07` carried three of them — *"Must precede item (7)"*,
*"Due ahead of item (5)"*, *"firing ahead of the control-approval expiry in item (7)"* — none of
which any tool could act on.

### The link type

Verified on this instance, 2026-08-27:

| Type | id | inward | outward |
|---|---|---|---|
| **Blocks** | `10000` | `is blocked by` | `blocks` |
| Relates | `10003` | `relates to` | `relates to` |
| Cloners | `10001` | `is cloned by` | `clones` |
| Duplicate | `10002` | `is duplicated by` | `duplicates` |

`Blocks` is the one that matters. Use `Relates` only for genuine non-blocking association — two
items that inform each other but neither gates the other. The remaining types on this instance are
Jira Service Management and Polaris artefacts; never use them.

### The direction, which is the part that gets reversed

`createIssueLink` takes **`inwardIssue` = the blocker** and **`outwardIssue` = the blocked**.

Read it as: *"outwardIssue **is blocked by** inwardIssue."*

So to record that `IRT-25` (produce the evidence) must land before `IRT-23` (approve the control):

```
createIssueLink(
  type          = "Blocks",
  inwardIssue   = "IRT-25",   <- the blocker, the thing that must happen first
  outwardIssue  = "IRT-23"    <- the blocked, the thing that waits
)
```

`IRT-23` then shows **is blocked by IRT-25**, and `IRT-25` shows **blocks IRT-23**.

**Get this backwards and the board is actively misleading** — it will show the finished work waiting
on the work that has not started. Before creating the link, say the sentence out loud with real
keys: *"IRT-23 is blocked by IRT-25."* If that is the truth, `inwardIssue` is the second key named.

### When to create one

- **The §6 evidence pairing: the work subtask blocks its evidence subtask.** The artefact does not
  exist until the work lands, so the **work** is `inwardIssue`. Say it aloud: *"the evidence subtask
  is blocked by the work subtask."* Do **not** read this direction off the `IRT-25`/`IRT-23` example
  above — that is the opposite shape, where evidence that already exists gates an approval.
- A subtask that produces evidence, blocking the subtask that acts on that evidence.
- A policy or document change queued in the policy queue ticket, blocking a Statement of
  Applicability flip that depends on it.
- A scoping or definition task blocking the first execution of the thing being scoped.
- A tooling or access prerequisite blocking the work that needs it.

**Do not** link merely sequential work that could be reordered without breaking anything — that is
ordinary prioritisation, and over-linking makes the real dependencies invisible.

### Staging and approval

Links are a write, so they follow the same rule as every other Jira write in this skill: **stage the
full set, get an explicit yes, then create them.** Show them as a table of
`blocker → blocked` with the plain-English sentence beside each, because that is the form in which a
reversed direction is obvious:

| Blocker (`inwardIssue`) | Blocked (`outwardIssue`) | Reads as |
|---|---|---|
| `IRT-25` | `IRT-23` | IRT-23 is blocked by IRT-25 |

### Cross-project limits

- **`IRT` to `IRT`** — the normal case, and this skill owns both ends.
- **`IRT` to the policy queue ticket** — permitted; it is an `IRT` ticket.
- **Never link to `CSIP`, `ICR` or `CYB`.** This skill never writes `CSIP` or `CYB` and only
  comments on, closes and holds `ICR` tickets, and a link is a write to both ends. Where a dependency genuinely crosses into one of them, state it in the IRT
  ticket description and leave the link to the skill that owns that project.

### Dates and links are different instruments

A link records **order**. A `duedate` records **when**. They are not substitutes, and a link is not
a schedule.

Until a control review completes, the ordering is usually known long before the dates are. Create
the links as soon as the dependency is understood, and leave `duedate` unset rather than inventing
one to express sequence — an invented date is a commitment nobody agreed to, and the link already
carries the constraint.

> **This paragraph used to contradict §6 outright, and it is now the rule.** It has always said to
> leave `duedate` unset and let the ordering carry the constraint, while §6 simultaneously said
> *"never create a ticket with no `duedate`"*. The deferral of 2026-09-15 resolves that in this
> paragraph's favour and generalises it: dates get set once the **whole board** is scoped, in the
> prioritisation pass (§1) — not merely once the review that scoped one ticket has finished.

Links also carry the sequence **between subtasks**, which are undated too (§6). With the `Task` as the
planning unit, a `Blocks` link is the only thing recording that one subtask must land before another.
