# Writing profile — Security Jira

| | |
|---|---|
| **Writing profile** | Security Jira |
| **Platform** | Jira — `bitpool.atlassian.net` |
| **In scope** | Projects `IRT` (ISO27001 Plans), `ICR` (ISO27001 Control review) and `CSIP`. **No other project.** |
| **Out of scope** | Every other Jira project, whatever its subject — finance, sales, `OP`, `BT`, `CYB`, `CHAN` and the rest. Most of the business runs on Jira, and those boards may need exactly the point-in-time numbers, names and approvals this profile keeps out of its three projects |
| **Readers** | The risk owner and the prioritisation pass reading the IRT board; auditors reading ticket bodies as standing statements; the next Hermes session |
| **Tone** | Short outcome statements and pointers in descriptions; specific, dated snapshots in comments |
| **Split from** | — |

**The single most useful fact in this profile: a Jira ticket is not one kind of record.** Its
`summary` and `description` are durable. Its comments are snapshots. Its fields are structured.
Almost every over-specific ticket body on these boards came from treating the whole ticket as a
snapshot, so measurements that belonged in a comment were pasted into the description, where they
read as standing fact long after they stopped being true.

Workflow rules — which skill writes which project, labels, which boards a skill may comment on,
when a date is set, the exact `Date constraint:` forms — stay with the skill that owns the project.
This profile governs *what the text says*, and where a workflow skill's template puts a copied value
into a durable field of these projects, this profile wins.

---

## §1 Sections

| Section | In scope? | Profile | Rules |
|---|---|---|---|
| `IRT` — ISO27001 Plans | Yes | Security Jira | §3.1–§3.4, §3.6 |
| `ICR` — ISO27001 Control review | Yes | Security Jira | §3.5, §3.6 |
| `CSIP` | Yes | Security Jira | §3.1, §3.2 (work tasks), §3.3, §3.7 (explainers) |
| Every other project | No | — | Not a target |

---

## §2 Record kinds in this target

| Part | Kind | Carries |
|---|---|---|
| `summary` | Durable | The commitment or requirement, named by its outcome — or by the object the ticket exists to act on (§3.2) |
| `description` | Durable | What the ticket is for, the gap it closes stated qualitatively, the definition of done including its closing step, and pointers — to the control, the risk, the controlled document, the skill that runs it |
| Comments | Snapshot | Everything dated: what was observed, measured, decided or changed, and why; who confirmed it; the state at creation |
| `assignee`, `duedate`, Original Estimate, labels, links | Structured | Their own values. The description never restates them |
| An `ICR` description that is a self-labelled, dated dump of the control record (*"point-in-time dump … pulled `<date>`"*) | Snapshot | Never rewritten |

---

## §3 Rules beyond the core

### §3.1 Creation-time state and corrections

**Creation-time measurements go in a dated comment, never the description.** The description may
state the gap the commitment closes, qualitatively and as the problem — *"environments are separated
at the network layer, not the account boundary"* — because that stays true for the ticket's open
life. The measurements, names, counts and resource lists behind the gap, and anything else true at
creation and expected to change, belong in a comment headed with the date. Where the owning skill
records that state, it stages the comment **with the create, in the same approval**. The cost of an
undated IRT ticket, which `/manage-drata-control` requires to be said out loud, is said in the
approval block and in that comment. It does not go in the description, where *"not yet scheduled"*
goes false for every ticket at once when the prioritisation pass runs.

**Changing a description is not how history is recorded.** When a description is corrected, the
correction replaces the old text. The reason goes in a comment beside Jira's own changelog entry —
never as a *"Corrected `<date>`: this line read…"* paragraph inside the description. Where the owning
skill posts no comments on that project, the reason goes in its report to the user instead.

A Sub-task gets its own creation comment only where it has creation-time state to record.

### §3.2 IRT Task and CSIP work task — summary and description

This section governs IRT Tasks and the CSIP work tasks and sub-tasks a skill raises (the explainer
`/describe-dcf-jira-ticket` writes is §3.7). **Drata's integration title format** —
`Drata | Bitpool | DCF-xxx | [Control Name]` — is Drata's stock text and the join key between the
two systems: leave it as Drata wrote it, and a skill may mirror it for a new parent.

**A summary may carry a durable handle** — a risk ID, a clause, a `DCF` code — with the commitment.
Copying another record's *title* into it is a copy that goes stale when that record is renamed;
name the commitment instead.

**The summary names the durable commitment, not the instance.** *"ISMS lead competence
development"*, not the vendor course currently chosen to deliver it — if the route changes, the title
is wrong. *"Environment separation at the account boundary"*, not the account names.

**Name the object where the ticket exists to act on it.** A ticket to assess a named vendor, retire a
named platform or remove a named network names it: that name is the scope of the commitment and its
definition of done, and it cannot drift, because the ticket closes when the object is dealt with.
What stays out is the object's current state — its counts, configuration, users, or the accounts it
sits in beyond what identifies it.

**The description states the outcome and points.** A risk-driven Task says what the commitment
delivers, which control it serves, and where everything else lives:

- **The risk** — its ID. Scores, treatment, owner and linked controls are Drata's fields: *"Risk:
  `<riskId>` — scores, owner and linked controls in Drata."* Copying them means every re-score or
  owner change silently falsifies the ticket.
- **The controls** — only the `DCF` codes this commitment's deliverable directly evidences, by code.
- **The accountable role**, where the ticket assigns one — *"the infrastructure owner"*. The person
  is the assignee or Drata's `owners` field.
- **Scheduling** — a pointer to the mechanism, never its date or its current state: *"Scheduled by
  the standing IRT prioritisation pass (`project = IRT AND labels = PrioritisationPass`)."* A pass
  date copied into every ticket body is one date in many places.
- **A controlled document's date**, where the document carries one — an objective's completion date
  under clause 6.2(k), or a corrective action's committed date under clause 10.2 — is quoted under
  `Date constraint:` in the forms `/manage-drata-control` defines, including its `NONE KNOWN` and
  `LAPSED` forms. This profile does not define another. What it adds is the anchor: the quote names
  the document's **version** — or, where the document has none, the date it was quoted — so it reads
  as what the document said then, not what it says now. Mechanism narrative attached to the form
  (*"deliberately not written to `duedate`"*) is not part of it: it goes false once the pass dates the
  ticket.
- **A lapse** is stated with absolute dates — what was committed, in which document, and the date it
  passed — never an elapsed time (*"20 months ago"*, or an `<elapsed> ago` slot in an older
  template).
- **The closing step** — which records to update when the ticket closes: the risk's
  `completionDate`, the source document, the evidence — is part of the definition of done. Keep it.
- **Another record's item by what it is**, not its number — *"the application-control item on
  CR-01"*, not *"CR-01 item 11"* — unless that record declares its item numbers permanent.

**No mechanism narrative or capability explanations.** Why the date field is empty, what the Drata
OAuth scope allows, how an automation behaves — that belongs to the skill that knows it. **A recurring
process splits three ways:** the executable procedure lives in a skill; the scope and the decisions
that must survive between cycles live on its hub page in the Bitpool Private Wiki; and the ticket
carries the task summary, how to run it (the skill), the hub link and where evidence goes — never the
procedure text.

**Exemplars from the IRT board.** *"Environment separation is at the virtual-network layer, not the
account boundary."* *"Provisioning alone creates no separation — that arrives only once the workloads
sit behind the account boundary."* *"Scope is set by criteria in the Vulnerability Management Policy,
not by a fixed system list."*

### §3.3 Sub-tasks and evidence sub-tasks

- **The summary and description name the remaining deliverable as an outcome** — *"deploy to every
  account and capture the configuration export for DCF-xxx"*. The item's current state (*"config
  written but not deployed"*) goes in a comment and moves as the work moves.
- **An evidence sub-task names the artefact kind, where it will land and the control it attaches
  to** — *"the configuration export, filed in the GRC evidence library against DCF-xxx"* — never a
  filename, a date, a resource list or the person who will upload it.
- **Progress counts go in comments.** *"Three of the subtasks were already Done when the estimate was
  set"* is a comment.

### §3.4 Standing IRT tickets

A standing ticket — the ISMS policy queue, the IRT prioritisation pass — keeps a durable description
holding **its standing rules, the skill that runs it and its hub link**, and puts everything that
grows or is dated in comments or on its hub page. The policy queue is the model. Its description
holds only the standing rules, the link to its page, and its due-date and superseded-tickets
sections. The row index, the Status notes and the At promotion steps live on the queue page in
`security-documentation`, under that repo's Security Documentation profile. Each row's detail is a
comment on the ticket, a snapshot under §3.5. Nothing that grows with each row is description text:
a standing ticket that accumulates rows, narrative bullets, incident timelines or per-row reasoning
in its description has turned into a log.

### §3.5 Comments — snapshots, so be specific

Comments on these three projects are where the specifics belong: the counts, the accounts, the named
confirmer, the evidence IDs, the verbatim quote, the date. Give the snapshot the shape that makes it
a snapshot:

- **Head it with the date** — *"Review outcome — `<date>`"*, *"Held open — `<date>`"*,
  *"Reopened — `<date>`"*, *"Review in progress — `<date>`"*, *"Queue row N — `<Policy>`"*.
- **An ICR outcome comment**, posted when the ticket closes, records the position reached, the
  basis, what was recorded where, and any limitation an auditor should see stated. A **Gate**
  section sets each remaining gap against the open IRT ticket carrying it, and lists each
  auditor-facing record checked. An **"Observed `<YYYY-MM-DD>`"** section holds the measurements,
  names and configuration values seen during the review. Having a sanctioned place for them is what
  keeps them out of the durable fields.
- **An ICR hold comment** is headed *"Held open — `<date>`"*, or *"Reopened — `<date>`"* when the
  ticket was Done. It states what is carried and by which IRT ticket, so no reader mistakes it for
  the blocker; each thing holding the ticket open — the record or gap, what is true, and where that
  is recorded; and **what closes it**, as a condition a later reader can check — never a date or a
  forecast. Anything measured in that run goes in its own **"Observed `<YYYY-MM-DD>`"** section, as in
  an outcome comment. When the blocker clears, the outcome comment says so and points back to the hold; the
  hold is never edited. A hold the user directed says it is their decision, not a departure from a
  convention.
- **Correct a snapshot by adding a comment**, never by editing the old one. The old one was true when
  it was written.
- **Quoting another record's mutable field in a snapshot** — *"IRT-45, due `<date>`"* — is tolerable,
  because the comment is dated, but a pointer ages better: *"tracked in IRT-45"*.
- **Specific is not unrestricted.** Security-sensitive identifiers — public addresses, exposed ports
  on named hosts, administrator and break-glass account names — go to a restricted home and the
  comment points there.

A comment records a decision *as of its date*. It never presents a policy-owned number, or a
control's state, as a standing fact.

### §3.6 Drata-side changes recorded on IRT or ICR

Because Drata risks and controls keep no readable history, a change to a risk's scores, treatment or
`treatmentDetails`, or a rewrite of a control description, is recorded as a dated comment on the ICR
or IRT ticket in the same change: what changed, why, and on whose decision (core rule 6).

### §3.7 CSIP descriptions

The house-format explainer `/describe-dcf-jira-ticket` writes is a durable description of a
**requirement**. It says what the control requires and what evidence would show it — not its current
status, the gaps observed today, a rollout target and its date, or the product currently deployed.
Observations, including AWS observations and gaps, go in a dated comment where that skill's workflow
permits one, and otherwise in the report to the user. Where a comment has settled a fact, state the
requirement it implies and point at the comment; never copy its values.

---

## §4 Calibration pairs — observed 2026-09-24

| Project | Before | After |
|---|---|---|
| IRT | A measured table pasted from an ICR closing comment — in-scope resource totals, tagged and untagged counts — into the durable description | *"Every in-scope resource type carries the required ownership tags, per the tagging standard."* The table stays in the ICR comment; the ticket points at it — by the `DCF` code and a query where the owning skill forbids naming the ICR key. |
| IRT | *"…deploy to the five AWS accounts…"* (another ticket on the same board said seven) | *"…deploy to every account in the AWS Organization…"* — within the scope record, where one excludes an account |
| IRT | The office's public IP addresses written into the description | *"The office's public address is an authorised source in cloud access controls for remote administration."* The addresses live in the security group configuration. |
| IRT | *"Owner: `<name>`"*, *"Risk owner: `<name>`"* in the header block | Drop it. The assignee is the field; the risk owner is on the risk. |
| IRT | *"Proposed by Claude on `<date>`"* (or *"…by Hermes…"*), *"edit made earlier the same day by another session"* | Drop it. Session narrative is never durable text. |
| CSIP | *"…target rollout by end Q3 2026 per your current plan…"* | *"The rollout plan is recorded on `<tracking ticket key>`."* |
| CSIP | An AWS observation from a sweep or meeting — account names, resource counts — pasted into a new work task's description | The description states what must be true when done, the `DCF` code and where the evidence will live; the observation goes in a dated creation comment. |
