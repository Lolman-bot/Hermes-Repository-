# Treatment decisions — the ISO mechanics

How to decide, and how to word, the treatment for a control whose position is unresolved. Read §1–3
at Step 2 of the skill, **§7 at Step 4** before putting any option to the user, and §4–5 when
drafting.

---

## 1 — The gate: clause vs Annex A

This determines which treatments are legally available. Get it wrong and the whole decision is void.

| | **Clauses 4–10** (the management system) | **Annex A controls** (the 93) |
|---|---|---|
| Examples | 6.1.2 risk assessment, 7.2 competence, 9.2 internal audit, 9.3 management review | A.8.8 vulnerability management, A.8.19 software installation |
| Can be declared "not applicable"? | **No** | Yes, with justification in the SoA |
| Can the risk of not doing it be accepted? | **No** | Yes |
| Not meeting it means | **Nonconformity. Fix it.** | A risk decision — legitimate if documented properly |

**A control mapped to a mandatory clause has exactly one route: a committed plan to comply.** There
is no "we accept the risk of not having competent people" or "of not running an internal audit".

**Two instruments deliver that plan, and which one applies is a real fork — decide it, don't default
to the first.** Added 2026-09-15, because this file named only 10.2 while the ticket label scheme has
carried both routes since 2026-08-26, so a 6.2 objective was being funnelled into "nonconformity" at
this gate and never recovering:

| The gap is | Instrument | IRT label |
|---|---|---|
| A **nonconformity** — a requirement Bitpool is bound by and is not meeting | **Corrective action, clause 10.2.** Needs a root cause and a check that it did not recur | `Clause` + `Corrective` |
| **Planned betterment** — nothing is being breached, the work is simply wanted | **Information security objective, clause 6.2** — its completion date is 6.2(k). Needs neither | `Clause` + `Improvement` |

Neither gets a risk register entry. Both get an IRT ticket, created undated and estimated
(`irt-tickets.md` §1 and §3).

**And no risk register entry either.** This is the part people get wrong after they've absorbed the
"can't be accepted" rule. A clause gap is a **nonconformity**, handled as a **corrective action
under clause 10.2** — not scored, not treated, not entered in the register. If someone proposes a
"risk management plan" or "risk treatment plan" for a clause control, the honest answer is that the
instrument doesn't exist for this control, and the one that does is a corrective action with an
owner, a completion date **stated in the controlled document** (clause 10.2 requires one there), and
a management review minute closing out any prior lapse. Its IRT ticket is created undated and
estimated; the ticket's `duedate` arrives at the prioritisation pass — see `irt-tickets.md` §1. The
document's date and the ticket's empty field are not a contradiction.

Resolve the mapping with `Drata_listRequirements` (`framework_tag=["ISO270012022"]`,
`expand=["controls"]`, plus `code_or_name` to narrow) — never from memory. Note the tag: on this
account `"ISO27001"` matches nothing and **returns an empty list rather than an error**, which is
easy to misread as "no mapping exists". If it's ambiguous, ask; assuming Annex A wrongly opens an
acceptance route that doesn't exist.

### Read the clause text, not just the clause number

`longDescription` on the requirement carries the verbatim ISO wording. **Read it and quote the
operative part** — it decides more of these questions than the control description does.

What to look for, and why it matters:

| Feature | Why it changes the answer |
|---|---|
| **Disjunctive lists** — "education, training, **or** experience" (7.2b) | Any one satisfies it. A document demanding a certificate has raised its own bar above the standard's — so the gap may be in *our* document, not our competence. |
| **"Where applicable"** (7.2c) | Creates conditional scope the control description flattens into an absolute. |
| **Separate sub-clauses** (7.2 a–d) | A gap in (c) "evaluate the effectiveness of the actions taken" is a different fix from a gap in (d) "retain documented information". Name the sub-clause. |
| **NOTE paragraphs** | Often enumerate acceptable means — 7.2's note allows mentoring, re-assignment, hiring or contracting, not only training. Widens the legitimate options considerably. |

Also read the `controls` expansion: a clause is only as ready as its **weakest** mapped control, and
the control you were handed is frequently not the weak one. Name the sibling explicitly rather than
letting the run imply the clause is covered.

---

## 2 — The four ISO treatment options

Use ISO's vocabulary and Drata's field value together — auditors listen for the former, the register
stores the latter.

| ISO term | Drata `treatmentPlan` | Meaning |
|---|---|---|
| **Modify** | `MITIGATE` | Reduce the risk with controls — now, or on a committed plan |
| **Retain** | `ACCEPT` | Consciously live with it. No new controls. |
| **Avoid** | `AVOID` | Stop the risky activity (decommission, drop the feature) |
| **Share** | `TRANSFER` | Insurance, or contractually pushed to a supplier |

There is no fifth option. "Mitigate partially and accept what's left" is `MITIGATE` with a residual —
which is what clause 6.1.3(f) requires for *every* treated risk, not just awkward ones.

---

## 3 — The three real-world scenarios and what each needs

| | **1. Plan to rectify** | **2. Accept the risk** | **3. Mitigate + accept residual** |
|---|---|---|---|
| SoA position | Applicable · **not yet implemented** · plan referenced | Applicable · **not implemented** · justification | Applicable · **implemented (partially / by alternative means)** |
| `treatmentPlan` | `MITIGATE` | `ACCEPT` | `MITIGATE` |
| Residual score | Target score once done | **= inherent** (nothing changed yet) | Must be **visibly lower** than inherent |
| Must have | Owner, **dated milestones**, resourcing | **Why it isn't worth doing** — cost/benefit, and the score within acceptance criteria | Compensating controls **enumerated individually**, and how they meet the control's intent |
| Approved by | Risk owner; slipping dates → management review | **Risk owner + top management** — minuted at management review, never by naming a reviewer on the risk (`drata-fields.md` §7). Don't sign this one alone. | Risk owner |
| Review | At each milestone | **At every periodic risk review** (`DCF-16`, raised in `CYB`) and at management review — the cadence is owned there and never restated in the entry — at the interval the Risk Assessment Policy in force sets; an acceptance whose latest `DCF-16` review falls outside it is reportable (`drata-fields.md` §7) | The same, and whenever the workaround changes |
| Auditor reaction | Fine if the plan is real and dates hold | **Hardest to defend.** Expect probing. | Usually fine — the normal answer |
| Fails when | Dates slip repeatedly with no re-plan | Score exceeds our own acceptance criteria, or no top-management sign-off **in a minute** (a reviewer on the risk is not sign-off) | Mitigations vague, or residual unchanged from inherent |

> **Where "dated milestones" live during the control review programme.** That row is the audit test
> for a treatment plan, and it does not move: an auditor asks what the plan is, who owns it, what it
> costs and when it lands, and an answer must exist. What changed on **2026-09-15** is only *which
> artefact holds the "when"*. The IRT ticket is created undated with a mandatory Original Estimate,
> and every date on the board is set in one prioritisation pass (`irt-tickets.md` §1). Until that
> runs, the honest answer to *"when?"* is the named, dated mechanism — the standing
> `IRT prioritisation pass` ticket (`project = IRT AND labels = PrioritisationPass`), whose due date
> is read from the ticket rather than carried here — together with the estimate and, for a clause
> commitment, the date its controlled document states.
>
> **Do not read the deferral as removing the requirement for a schedule.** It defers where the
> schedule is expressed, nothing more. The rest of this table is untouched: slipping dates still
> escalate to management review, an auditor still tests whether dates hold, and a plan still fails
> when dates slip with no re-plan.

**Two non-negotiables:**

1. **Acceptance criteria are pre-defined**, in the Risk Assessment Policy (clause 6.1.2a). You cannot
   decide after the fact that whatever residual you're left with happens to be acceptable.
2. **Annex A says *what*, not *how*.** "Implemented by alternative means" is legitimate,
   under-used, and well received. Meeting the intent differently is not a gap.

---

## 4 — Write the risk, not the control gap

The most common failure. A risk restated as a missing control can only be treated by doing the
thing you just said you won't do — and it signals the register was built backwards from the control
list rather than from the business.

| ❌ Control gap dressed as a risk | ✅ An actual risk |
|---|---|
| "Risk that we don't apply application whitelisting to developer machines" | "Unauthorised or malicious code executes on developer endpoints, which hold source code, cloud credentials and production access paths" |
| "Risk that estimating.bitpool.com has no authenticated pen test" | "Exploitable vulnerabilities behind authentication in partner-facing web applications go undetected, exposing partner and customer data" |
| "Risk of not having an internal audit programme" | (trick question — this maps to clause 9.2, so it is a nonconformity, not a risk) |

Test: can the statement be scored for impact and likelihood without referring to the control? If
not, rewrite it.

---

## 5 — Wording templates

**Every template here produces durable text for a registered target of `/bitpool-writing-standard`.**
Scenario 1 and the scope-was-risk-based text go in the `Rationale` column of
`compliance/drata-controls-register.md` — the `security-documentation` repo, profile **Security
Documentation**. Scenarios 2 and 3 go in Drata `treatmentDetails` — profile **Security Drata**, §3.2.
Load the standard and the named profile before filling one, and show the durability check in the
approval block (`drata-fields.md` §4). The placeholders take categories, criteria, roles and
pointers. None of them takes a score, a policy threshold, a cadence or review date, a named person,
a product (except where the standard's core rule 3 allows one — a relied-on provider, a system of
record named as a pointer, the record's subject), a count, or a list of systems in or out — those
have homes of their own.

**Scenario 1 — plan to rectify.** Goes in the `Rationale` column of
`compliance/drata-controls-register.md` (route via `/bitpool-docs`) — **not** the control's Drata
`rationale` field, which is a dead end; see `drata-fields.md` §2:

> Applicable; not yet implemented — plan referenced. Gap: [what is missing, stated qualitatively as
> the problem]. Treated under [riskId]; the plan delivers [the outcome], relied on once [the
> condition], tracked in [IRT-n] (find by: project = IRT AND text ~ "[riskId]"). Interim position:
> [what covers it meanwhile, if anything].
> Plan approved by the risk owner at [the control review or management review] on [date]; recorded
> in [the minute or the dated change-record comment].

**No `target [date]` in this template** — Bitpool decision, 2026-09-15. With the IRT `duedate` empty
until the prioritisation pass and Drata's `anticipatedCompletionDate` blank by decision, a target
here would be **the only date in the system**, and an auditor would read it as authoritative — making
Drata the home of a date this skill spent three corrections moving out of it. Clause 6.1.3 requires
the plan and its owner, not a date in the SoA. The `[IRT-n]` pointer is what leads to the schedule,
and `[riskId]` is what leads to the owner: the current owner is Drata's `owners` field, so the row
never names one. Implementation state **stays in the row** — the register has no other home for it,
and the Security Documentation profile (§3.3) asks the Rationale for the position, implemented or
not. It is the standing position, not progress: the plan's closing step — the `IRT` ticket's
*On completion* block (`irt-tickets.md` §4) — flips it to *"Applicable; implemented"* when the work
completes. The approval date stays, because it is an anchored historical fact rather than a
commitment — written with the approving role and where the approval is recorded, and removed by the
edit that changes the plan, since an approval covers only the plan it approved.

**Scenario 2 — accept** (`treatmentDetails`):

> Risk retained (accepted). [The activity or asset class, bounded by the criterion that defines it]
> is not covered by [the capability the control requires] because [cost / technical infeasibility /
> disproportionate to exposure]. The risk is retained under the acceptance criteria in the Risk
> Assessment Policy. Compensating factors, though not relied on as controls: [each as a capability
> or condition]. Accepted by the risk owner and top management at the management review of [date];
> minuted.

**No score, no threshold, no review line.** The scores are Drata's fields, and the acceptance
criteria are the policy's — cite the policy, once the version in force is confirmed to hold the
criteria; where they exist only in the draft awaiting promotion, the profile's *"(pending promotion,
`<ticket>`)"* form applies. The review cadence belongs to the periodic risk review control, and each
review is raised in `CYB`, which this skill does not write to — so neither the cadence nor a
`CYB-nnn` key goes in the entry (a `CYB` key would be an unmaintainable pointer). An `IRT-n` key
**is** permitted (this skill owns IRT) — use it for execution work, not for reviews.

**Write an acceptance only once it has happened.** The acceptance sentence is an anchored event —
its date, the accepting roles and the forum, and where it is recorded. An acceptance still waiting
for its management review is not written as pending; the edit that follows the minute adds the
sentence. Until the minute exists, the pending acceptance is recorded in the control's `ICR`
outcome comment (`SKILL.md` Step 10) — it does not hold that ticket — and listed in the Step 11
summary as awaiting management review; the edit adding the acceptance sentence is staged once the minute exists, and the hygiene
sweep asks after any `ACCEPT` entry still without one (`hygiene-sweep.md` check 4). The minute names
the people and the residual level; the entry names the roles.

**Scenario 3 — mitigate + accept residual** (`treatmentDetails`; for what to take from the `CR-01`
precedent, and what not to, see `drata-fields.md` §5):

> Risk modified. [The capability the control requires] protects [the protected set, defined by the
> criterion that decides membership and the policy or register that sets it]; outside that
> boundary, [why the boundary sits there]. Compensating measures, each stated as a capability and
> each a separate claim: (1) … (2) … (3) …. Together they address the control's intent by
> [reasoning]. Residual accepted by the risk owner at [the control review or management review] on
> [date]; recorded in [the minute or the dated change-record comment]. Execution tracked in [IRT-n]
> (find by: project = IRT AND text ~ "[riskId]").

**The boundary replaces an exclusion list.** The older form of this template asked for a
*"[Sub-scope] is excluded"* clause, which invites naming the excluded systems — an inventory that
is wrong the moment anything is deployed (`drata-fields.md` §4, *boundary, not inventory*). A
compensating measure that maps to an existing DCF goes in `control_ids`, not the list (content rule
4). The scores — the residual visibly lower than inherent — are Drata's fields and appear in the
approval block, not in the prose.

**Scope-was-risk-based, no gap** (Step 3 outcome 3 — the scoping rationale, in the `Rationale`
column like Scenario 1):

> Applicable; implemented — scope determined by risk: [the higher-exposure set, by the criterion
> that defines it] receives [fuller treatment]; [the lower-exposure set, by its criterion] receives
> [lighter treatment] because [reason]. No residual risk beyond the accepted register position for
> [riskId].

---

## 6 — Traps

- **"Not applicable" used as a dodge.** N/A means the control genuinely cannot apply to our context.
  If the risk exists and we simply aren't addressing it, that's Scenario 2. Auditors test this hard
  and it's the fastest route to a major nonconformity.
- **Perpetual "in progress."** A plan whose date has passed twice with no re-approval is worse than
  an honest acceptance.
- **Acceptance with no re-examination.** Every acceptance must resurface — at each periodic risk
  review under `DCF-16`, whose recurrence is raised in `CYB`, and at management review (clause
  9.3). That control owns the cadence; the entry never carries a review date or a cadence line.
  An acceptance covers the residual and treatment in force when it was given, so the edit that
  changes either one removes the acceptance sentence until the next acceptance restores it.
- **Mitigations that don't move the score.** If inherent = residual on a `MITIGATE`, you haven't
  mitigated — you've accepted. Label it honestly.
- **Self-signed acceptances.** Clause 6.1.3(f) wants the risk *owner*. For anything material, get
  top management named too — **in a management review minute, never by naming a reviewer on the
  risk** (`drata-fields.md` §7).
- **Treatment prose that claims a reviewer exists.** False by construction: Bitpool records no
  reviewer on any risk. It also survives the field being cleared, so it outlives the thing it
  described — live example, `CR-07` item 15, corrected 2026-08-26. Delete the reviewer claim; keep
  any genuine approval, named as what it actually is.
- **One risk per control.** Not required and usually wrong. Risks and controls are many-to-many —
  `SD-04` legitimately covers a whole family of controls. A register with one risk per Annex A
  control is a red flag that it was reverse-engineered from the control list.
- **Prose quality.** `treatmentDetails` is auditor-facing prose. Typos and garbled sentences in a
  justification undermine its credibility. Proofread before staging.

---

## 7 — The paths format (Step 4)

The skill's job at Step 4 is to convert everything gathered into **a choice the user can actually
make**, then get out of the way. Two or three paths. Never one — that's a decision taken on their
behalf. Never four abstract ISO options — that's a textbook, not advice.

### The five elements

Every path carries all five. Drop one and the user can't compare.

| Element | What it answers |
|---|---|
| **What changes** | The concrete edits: which document, which field, which ticket, which score |
| **What it costs** | Money, licences, engineering days, study time — or explicitly "document change only, no spend" |
| **Documents & tickets** | Every artefact that moves, and **in what order** (document before ticket, always) |
| **What an auditor makes of it** | The clause they'd test it against, and what they'd probe |
| **Residual exposure** | What's still open *after* taking this path — never "none" |

### Shape

```
PATH A — <short name>
What changes ......... …
Cost ................. …
Documents / tickets .. … (in order)
Auditor's view ....... Tests against clause X. Likely probe: "…". Verdict: defensible / expect
                       challenge / nonconformity.
Residual exposure .... …

PATH B — <short name>
… same five …

RECOMMENDED: <A|B|C> — <one sentence why>

UNCONDITIONAL (whichever path you pick)
1. …
2. …
```

### Rules

- **Recommend one, in one sentence.** Not a paragraph of hedging. If two are genuinely close, say
  which is less work and which is more defensible, and let that be the distinction.
- **Name the paths for their substance**, not their number — "Competent now, cert as objective"
  beats "Option 2". The user will refer back to them by name.
- **Correct an unavailable path rather than silently omitting it.** If the user proposed something
  the gate forbids, say why it doesn't exist and what replaces it. Omission reads as agreement.
- **Unconditionals go outside the paths.** Factual errors in ticket bodies, a weaker sibling control
  under the same requirement, a control carrying no policy at all — these happen regardless of the
  choice. Inside a path, they get lost when another path is picked. **Policy `renewalDate` and
  `approvedAt` are never unconditionals** — see the policy-queue rules in `SKILL.md`; they are the
  expected state between bulk promotions and must not be raised at all.
- **Every fact needed to choose goes INSIDE the options table.** Not in prose above it, not in an
  earlier message, not in a summary that assumes the reader still has the options in mind. If a path
  turns on a term the reader may not hold — a Jira project key, a clause number, a mechanism — the
  table carries the expansion. Worked failure, 2026-08-24: a run summarised its recommendation while
  leaving the three paths described two messages earlier, then asked the user to pick. They could
  not, and said so. A path the reader cannot evaluate is not an option, it is a stall.
- **Offer the pragmatic option alongside the procedurally correct ones.** Where the work is small
  enough to simply do, "just do it — no ticket, no risk entry, no document change" is a legitimate
  path and often the best one. Same worked failure: three paths were offered for roughly one day of
  configuration work, all three carrying register entries or document amendments, and none saying
  the obvious thing. Presenting only formal routes for trivial work reads as over-engineering and
  invites the user to reject the whole frame.
- **"Auditor's view" is a verdict, not a vibe.** Name the clause and the probable question. If the
  honest verdict is "this is a nonconformity", write that.
- **Never make a path artificially unattractive** to steer the choice. If amending the document is
  cheap and legitimate, say so plainly even when the alternative feels more diligent.

### The most common path set

Turning up repeatedly for Step 3 outcome 4 (green in Drata, our own document declares the gap):

| | What it says | When it's right |
|---|---|---|
| **Requirement already met — correct the document** | The standard's bar is lower than our document's; amend ours to state the real basis, retire the plan | The clause text is disjunctive or hedged and the evidence satisfies it |
| **Requirement met + keep the task as an objective** | Amend the document *and* retain the planned work as a clause 6.2 improvement objective rather than a gap closure | The work is wanted anyway; a slip shouldn't read as a nonconformity |
| **Not met — re-plan with live dates** | Keep the declared gap, re-date it honestly **in the controlled document**, minute the prior lapse under 10.2. The IRT ticket stays undated until the prioritisation pass; its body states the lapse | The evidence genuinely doesn't meet the clause |

The middle one is easy to miss and often the best answer: it keeps a commitment funded and tracked
without the organisation declaring itself non-competent in a controlled document.

---

## 8 — ISO facts that keep coming up

Established from the clause text via `Drata_listRequirements(expand=["controls"])` and recorded here
so they are not re-derived, or worse, guessed. Quotes are verbatim `longDescription`.

### Approval — what ISO actually requires, and what it doesn't

Three different things get conflated. They have three different answers:

| Object | Does ISO require approval? |
|---|---|
| **A control** | **No.** No clause and no Annex A control requires a control to be approved or attested by a second person. A compliance tool offering a control-approval toggle is offering a product feature, not a requirement. Declining to use it is not a gap. |
| **A risk** | **Yes — by its owner.** Clause **6.1.3(f)**: *"obtain risk owners' approval of the information security risk treatment plan and acceptance of the residual information security risks."* It requires the **risk owner**, not an independent second party. Where the owner also performed the assessment, their recorded acceptance still satisfies the clause. A reviewer field is the tool's construct. Bitpool decided on 2026-08-24 not to populate Drata's — see `drata-fields.md` §7; independent challenge is the periodic risk assessment review under `DCF-16`, not a per-entry field. |
| **Documented information** | **Yes.** Clause **7.5.2(c)** requires *"review and approval for suitability and adequacy"* when creating and updating documented information. This is the obligation people mean when they say approval is mandatory — and it lands on policies, not on controls or risk entries. |

**The trap:** a self-approval that is *conforming* can still be indefensible on the one risk whose
subject is concentration of authority. Say that out loud rather than resting on the clause.

### A fix that satisfies the clause is compliance, not mitigation

When the proposed action makes a mandatory clause **met**, do not let it be framed as mitigating a
risk — there is no residual to accept and no register entry to make. Name the clause and say it is
satisfied.

Worked example, 2026-08-24: a one-role ISMS cannot achieve internal-audit impartiality internally.
Clause **9.2.2 b)** requires the organisation to *"select auditors and conduct audits that ensure
objectivity and the impartiality of the audit process"* — so engaging an external party **satisfies
9.2**, and the instrument is a dated corrective action, not a mitigate-and-accept. The same fix
described as a mitigation would have manufactured a risk entry a clause cannot legally take.

### Check the controlled document already permits it before proposing an amendment

Read the controlled text before drafting a change. Documents are routinely more permissive than the
current practice, and the honest fix is then to **select an option already written down** and make it
true — far cheaper than an amendment, and it removes a false claim instead of adding a new clause.

Worked example, 2026-08-24: the production ISMS Plan already offered *"Third party internal
auditor"* as one of three Audit Entity options, and the Statement of Applicability already justified
A.5.35 as *"Regular independent reviews conducted by third-party auditors"*. Nothing needed
rewriting to permit the decision. What needed fixing was narrower and would have been missed: an
independence mechanism the same document could not achieve, and an `Implemented = Y` on a control
with no evidence.

### The residual score is the post-treatment position — don't inflate it to today's

When measures sit in `PLANNED`, the residual describes where the risk lands once they operate. Leave
it, and state in `treatmentDetails` that the residual is the post-treatment position, relied on once
the `PLANNED` items operate — each carrying its outcome, condition and IRT pointer, never its
progress. Do **not** raise it to reflect today.

The reason is mechanical, not cosmetic: raising it can push the residual back above the acceptance
threshold in the Risk Assessment Policy, at which point the risk may not be retained at all and
demands treatment already assessed as disproportionate. A labelled target is defensible; an inflated
residual invalidates its own acceptance.

### Internal audit → policy update → management review, in that order

Clause **9.3.2** makes seven inputs mandatory to the management review, including **d) 3) "audit
results"**. Scheduling the review before the first internal audit leaves that input empty by
construction. Where a user proposes the reverse order, say why it needs swapping.

And clause **9.3.1**: *"**Top management** shall review the organization's information security
management system at planned intervals…"* — so an external contractor may prepare inputs and attend
but can never *be* the reviewer. Check who the ISMS Plan defines as top management; at Bitpool it is
the CEO alone, which also means auditing the ISMS and then reviewing it would concentrate a fresh
pair of duties in one person.
