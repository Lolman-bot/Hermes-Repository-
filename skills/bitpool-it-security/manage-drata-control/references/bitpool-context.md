# Downstream skills and Bitpool context

> Relocated verbatim from this skill's `SKILL.md` when it was ported to Hermes; `SKILL.md` keeps the
> route and a summary of each rule, and this file is the full text. Bold section names refer to:
> **golden rules** → `references/golden-rules.md`; **Invoke the downstream skills** and **Bitpool
> context** → `references/bitpool-context.md`; **Batched policy changes**, **Writing a queue row** and
> **Rules for the index** → `references/policy-queue.md`; **Step 0–11** → `references/workflow.md`.

## Invoke the downstream skills — do not narrate them at the user

**Bitpool instruction, 2026-08-27, in the risk owner's words: "I don't want to keep getting buried
lines of text telling me to invoke them."**

This skill routes three kinds of output to other skills — documentation to `/bitpool-docs`, ISMS
policy drafting to `/isms-draft`, and non-policy wiki pages to `/bitpool-docs` again. Wherever this
file or its references say *"route via `/bitpool-docs`"* or *"hand it to `/isms-draft`"*, that is an
instruction to **you**, to invoke that skill in the same run. It is **not** a line to print at the
user telling them to go and do it.

**So: invoke `/bitpool-docs` and `/isms-draft` yourself, as part of finishing the work.** Both are
available to this skill and neither needs the user to type the slash command. A run that ends with
"you should now run `/isms-draft`" has not finished; it has handed back a to-do list.

Three limits, which are about *what* gets written rather than *whether* you invoke:

1. **This skill still never writes policy text directly.** `/isms-draft` owns the draft edit — the
   point is that you call it, not that you bypass it. Same for `/isms-prod`, which this skill never
   invokes at all: promotion is the bulk event, tracked by the policy queue ticket.
2. **The approval gates are unchanged.** A Drata risk still needs the §4 block approved. A Jira write
   is still staged first. Invoking a downstream skill inherits *that* skill's own gates too — if
   `/bitpool-docs` asks about diagrams before writing, answer it and carry on rather than stopping
   to relay the question.
3. **Report what was written, not what should be.** In the Step 11 summary, name the repo and path
   `/bitpool-docs` actually wrote, what `/isms-draft` actually wrote, and the queue row actually
   added. "Handed to `/isms-draft`" is only a truthful summary line if you invoked it.

The same applies to `/ask-drata`: it is a prerequisite to read, not a suggestion to pass on.

---

## Bitpool context

**Never hardcode counts or statuses in this skill.** Control readiness, risk totals, treatment
splits and evidence gaps all change continuously and are one MCP call away — read them live every
run. Counts and statuses are welcome in the chat and the Step 11 summary, which sit outside the
writing standard's register; whether one may go into Drata, `IRT` or `ICR` is that standard's call
(see the golden rules). What follows is *structure* (stable configuration), not measurement.

**Paths — verified 2026-09-28 on Bitpool's standard workstation layout. Never pattern-match a repo name.**

| | |
|---|---|
| This skill and its references | The installed Hermes skill — `skill_view(name='manage-drata-control')`; source in the `Lolman-bot/Hermes-Repository-` repo at `skills/bitpool-it-security/manage-drata-control/` |
| Security documentation | The main local working copy of `security-documentation` — on Bitpool's standard layout, `security-documentation` under the `BitpoolDev\Github-Bitpool` folder at the root of the system drive |

Confirm the working copy exists before the first edit (`terminal`: `git -C <path> rev-parse --show-toplevel`); if it is
not at the standard location, ask the user for the path with `clarify` rather than guessing.
The parent is `Github-Bitpool` — **no spaces**. `Github - Bitpool` (with spaces) **does not exist** on
Bitpool machines, yet the project `CLAUDE.md` and `/isms-draft` both hardcoded that form at the time of
verification. Every path written that way is broken and only works because the right one gets
inferred each time. Flag it when you see it; never copy it.

Look-alike repos sit under the same parent, and a wrong guess writes to the wrong repo:
`security-documentation` vs `security-documentation-restricted`, `ai-skills` vs the retired
`ai-skills-beta` (an old local clone can still be there; neither is where this Hermes skill lives), `it-documentation` vs
`it-documentation-restricted`.

**This skill is self-contained — it fetches nothing from GitBook, and neither does any other
skill in this repo.** The live-fetch pattern was unwound: `/isms-draft`, `/bitpool-docs`,
`/update-hermes-skill` and `/ask-drata` all used to pull their detail from the Bitpool Private Wiki
and now ship it in their own `references/`. Everything this skill needs is in `references/`. There
is no manage-drata-control page in GitBook — do not go looking for one, and do not create one, or the
skill acquires a second source that will drift from these files.

**Bitpool's estate — three separate things, and evidence for one never covers another.**
Confirmed with the user 2026-08-24:

| Estate | What it is | Where its evidence comes from |
|---|---|---|
| **Infrastructure** | **All of it is AWS**, across every account in the Organization — enumerate them at run time via `/aws-query`; never assume a count. **No application workloads run in Azure** — it holds security and tooling resources only (Sentinel, code signing, Veeam, Power BI); see `/azure-query`'s asset register. | AWS APIs, and `SSM Run Command` for in-instance state |
| **Endpoints** | Staff laptops, Intune/Entra managed. **Not** infrastructure | Intune. `SSM Run Command` cannot reach them |
| **OT / edge devices** | A third estate again | The Edge Device Security papers — **never** inferred from the ISMS or Drata |

Two traps this closes. Bitpool's own SoA exclusion text for **A.7.8** reads *"managed by the AWS
and Azure data centres respectively"*, which sounds like an Azure estate — it is about
provider-managed facilities, not Bitpool workloads, so never scope work to cover Azure compute.
And where a control's wording reaches "systems used by the organization", **laptops are in scope
and infrastructure-scoped evidence does not cover them** — that exact gap became risk `CR-06` on
2026-08-24, after an AWS-wide clock-sync sweep was mistaken for whole-estate coverage.

The endpoint estate **can be sized from Drata** — corrected 2026-08-25. Editions of this line
before that date said personnel lookups were blocked account-wide and sent the reader to Intune;
that was true on 2026-08-07 and is not true now. The `read:personnel` and `read:device` scopes were
granted in between, and the whole Personnel/Devices domain works — see `/ask-drata` rule 5, which
owns this fact.

- `Drata_searchDeviceCompliance(facets: […])` sizes the estate **without naming anyone** — read the
  device count and the pass/fail split live each run; never carry one over from an earlier run.
- `Drata_listDevices(person: …)` returns one person's devices and their five monitor checks.
- `Drata_listPersonnel(employment_status: […])` sizes the population. **It defaults to ACTIVE
  personnel only** (`CURRENT_EMPLOYEE` + `CURRENT_CONTRACTOR`), so pass the statuses explicitly
  when service accounts or leavers matter — the default silently leaves them out.

Still cross-check against Intune where the number is load-bearing: Drata sees only what its
connections report, and a device absent from Drata is not evidence of a device that does not exist.

- **Risk register:** id `1`, name `Risk Management`.
- **`treatmentPlan` enum:** `UNTREATED` · `ACCEPT` · `TRANSFER` · `AVOID` · `MITIGATE`.
- **Scoring:** `impact` 1–5 × `likelihood` 1–5 = `score` 1–25, with a parallel
  `residualImpact` / `residualLikelihood` / `residualScore` triplet.
- **Framework tag:** `ISO270012022`.
- **Governing policy:** `Risk Assessment Policy` — resolve live with
  `Drata_listPolicies(name="risk")`. Defines the methodology and the acceptable level of risk.
  **Read its content before scoring anything.** Ignore its `renewalDate` and `approvedAt` — see the
  golden rule on renewal lapse.
- **Risk ID prefixes observed:** `SD-`, `CR-`, `AI-`, `IN-`. Follow the existing prefix for the
  domain rather than inventing a new one; if none fits, ask.
- **Governance controls worth knowing by code:** `DCF-162` Statement of Applicability · `DCF-164`
  Management System Management Review · `DCF-179` Competence Records (clause 7.2 — mandatory,
  no acceptance route) · `DCF-566` Management of Nonconformities.
- **Jira:** cloud id `bitpool.atlassian.net`. Control work is tracked in `CSIP` with the control
  encoded in the title: `Drata | Bitpool | DCF-xxx | [Control Name]`. Find it with
  `project = CSIP AND text ~ "DCF-xxx"`. Drata's `flags.hasTicket` tells you whether one exists.
  **Read-only from this skill** — it is Drata's integration lane and two other skills own its
  writes.
- **Two confirmed Drata limits that shape this skill** (detail in `references/drata-fields.md`):
  1. **A control's `rationale` field is a dead end — never stage text for it.** Verified 2026-08-21:
     `null` on all 250 controls (199 enabled and all 51 disabled), no UI surface found, and not
     writable via MCP — `Drata_updateControl` omits the field. Whether it can be **set at
     creation** is unverified: `Drata_createControl` is exposed but its scope is unprobed, and
     control creation is outside this skill's write model (see `/ask-drata`). The field that
     *does* work is on the framework **requirement**, it holds the
     **SoA exclusion justification only**, and it renders solely where an Annex A requirement is
     marked out of scope (`A.7.8` and `A.7.11` when verified on 2026-08-21 — read the current set
     live with `Drata_listRequirements`). Inclusion justification and decision
     rationale have **no home in Drata** — they go in the `Rationale` column of
     `compliance/drata-controls-register.md`.
  2. **Drata's *risk object* has no date-based trigger.** Confirmed with Drata support 2026-08-18:
     nothing fires when `anticipatedCompletionDate` passes without `completionDate` set. Those fields
     are record keeping only. **This is not a claim that Drata cannot alert on any date** — the
     Evidence Library's `renewalSchema` does fire, but it re-attests an artefact rather than chasing
     a deliverable (`DCF-179` carries evidence `184` renewing 2027-07-17 while the commitment under
     it has been lapsed since end 2024, and the control reads green). Detail in
     `references/irt-tickets.md` §1.
- **`IRT` — ISO27001 Plans** (project id `13535`) is where tracked ISO 27001 commitments live.
  It has no wiki page, and **a Jira `duedate` is a field, not a trigger** — it buys a changelog audit
  trail of date changes, not alerting. Never say a ticket makes a date "chased".
  **Tickets are created undated**, with a mandatory Original Estimate in hours and the default
  assignee (next bullet), and the backlog is found by the field's *absence*:
  `project = IRT AND duedate IS EMPTY AND statusCategory != Done AND labels in (RTP, Clause)`.
  Dates are assigned board-wide in the prioritisation pass, tracked by the standing
  `IRT prioritisation pass` ticket — `project = IRT AND labels = PrioritisationPass`; its own
  `duedate` is the pass date. See `references/irt-tickets.md` §1.
- **The default person for structured fields: Eric Sharp** — named here and nowhere else in this
  skill; its `references/` point here. He is the `assignee` on every `IRT` `Task` and `Sub-task`
  (Bitpool decision, 2026-09-15; `references/irt-tickets.md` §5) and the default Drata risk
  `owners` unless the user says otherwise (`references/drata-fields.md` §7). Everywhere else this
  skill says *the default assignee* or *the default risk owner*. The name is a structured value
  only: durable text names the role, never the person (the writing standard's core rule 5).
- **Two other ISO 27001 Jira projects exist. Query them before creating anything, or you add
  a fourth copy of one commitment:**
  - **`ICR` — ISO27001 Control review** (id `13602`): one `Workstream` per control, titled
    `DCF-xxx | [Control Name]`, generated from the Drata Controls Register wiki page.
    **This skill ends the run on the `ICR` ticket for the control it just reviewed: it closes the
    ticket when the control passes the audit-ready gate, and otherwise holds it with a comment
    saying what closes it** — see Step 10. It never creates one and never edits a description.
  - **`CYB` — Cyber Security Recurring Tasks** (id `13173`): Bitpool's **only** scheduled generator
    of recurring ISO tasks (Automation for Jira, including `"Annual Risk review"`). Recurring work
    belongs here, not in IRT — recommend the automation rule, never write to `CYB`.

Consult `/ask-drata` before concluding a Drata record doesn't exist — search-mode `query` params
are unreliable on this account; use structured list mode and follow `cursor` to `null`.
