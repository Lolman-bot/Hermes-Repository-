# Writing profile — Security Drata

| | |
|---|---|
| **Writing profile** | Security Drata |
| **Platform** | Drata — Bitpool's workspace |
| **In scope** | Risk register · Evidence library · Controls · Vendors · Framework requirements (SoA exclusion rationale) · Custom Tests |
| **Out of scope** | Every other Drata area — personnel and devices, the policy center, background checks, and anything not listed above |
| **Readers** | ISO 27001 auditors testing evidence against the records; the risk owner; the next Hermes session reading the register |
| **Tone** | Auditor-facing statements of position and mechanism. Exact about pointers, general about contents |
| **Split from** | — |

The core rules (`references/core-rules.md`) apply to every in-scope field, whether a skill writes it through the
MCP or drafts it for a person to paste into the UI. **Who presses save does not change the
profile** — most over-specific text reaches Drata by being drafted in chat and pasted.

Workflow rules that are not about wording stay with the skill that owns the workflow: *which* fields
a skill may write and the trap in each verb (`/ask-drata`); the IRT pointer form, the blank
`anticipatedCompletionDate` and the empty `reviewers` (`/manage-drata-control`); the vendor field
dispositions (`/manage-drata-vendors`). This profile governs *what the text says*, and where a
workflow skill's template puts a copied value into one of these fields, this profile wins.

---

## §1 Sections

One profile covers every in-scope section today. Any section can be split into its own profile by
the five-step process in `references/maintaining-the-register.md`; the section keeps its row here, pointing at the new profile.

| Section | In scope? | Profile | Rules |
|---|---|---|---|
| Risk register | Yes | Security Drata | §3.2 |
| Evidence library | Yes | Security Drata | §3.1 |
| Controls | Yes | Security Drata | §3.3 |
| Vendors | Yes | Security Drata | §3.4 |
| Framework requirements — SoA exclusion rationale | Yes | Security Drata | §3.5 |
| Custom Tests | Yes | Security Drata | §3.6 |
| Personnel, devices, policy center, background checks | No | — | Not a target |

---

## §2 Record kinds in this target

| Section | Field | Kind | Note |
|---|---|---|---|
| Evidence | `name` | Durable | Names the artefact **kind** — one bucket per recurring artefact, not one per occurrence |
| Evidence | `description` | Durable | Persists across every future version of the bucket — §3.1 |
| Evidence | `implementation_guidance` | Durable | How the artefact is produced, at method level |
| Evidence | artefact files, with `filedAt`; `artifact_name`, `ticket_url` | Snapshot | Versioned with the artefact. The specifics live here |
| Evidence | URL | Pointer | Points at a living record that is the home of its values; nothing in Drata versions it — §3.1 |
| Risk | `title`, `description` | Durable | Risk language. Length caps and verb traps are connection facts — `/ask-drata`'s writable-fields inventory |
| Risk | `treatmentDetails` | Durable | The position and its mechanism — §3.2 |
| Risk | `owners`, `control_ids`, scores, `treatmentPlan`, `completionDate` | Structured | The home of each value; prose never restates them. `anticipatedCompletionDate` and `reviewers` are deliberately left empty (`/manage-drata-control`) — an empty field is correct, and never a prompt to state a date or name a reviewer in prose instead |
| Control | `name`, `description`, `activity`, `question` | Durable | The statement an auditor tests evidence **against** — §3.3 |
| Framework requirement | `rationale` | Durable | SoA exclusion justification — §3.5. Written through the Drata UI where no MCP verb covers it — `/ask-drata`'s writable-fields inventory says which |
| Vendor | `services_provided`, `data_stored`, `location`, `notes`, `environment_access`, `operational_impact`, `password_policy` | Durable | §3.4 |
| Vendor | `contact_at_vendor`, `contacts_email`, `cost` | Structured | The contact record and the vendor's own figure — §3.4 |
| Vendor | security review observations and conditions | Snapshot | A dated review; specifics belong here |
| Custom Test | name and description | Durable | §3.6 |
| Any in-scope object | `custom_fields[].value` (text) | Durable | Same rules as the object's other text |

**Stock text.** Drata's generic template wording — its own control statements and its automatically
seeded test-result evidence (*"Drata inspected… and confirmed…"*) — is not Bitpool's drift and not
Bitpool's to rewrite. Text naming Bitpool's platforms, registers, policies, people or risk IDs is
Bitpool's, whatever the object.

---

## §3 Rules beyond the core

### §3.1 Evidence — the description

An evidence bucket outlives every file in it. A file bucket keeps one description while a new
artefact is uploaded each time, so anything describing *this* upload — the photo count, the
attendees, the tool the screenshot came from — goes false at the next renewal. A URL bucket is
worse: the page it points at changes with no new version in Drata at all, so every value copied from
the page drifts continuously.

So the description is written to be true of **every** version the bucket will ever hold. It carries
the five parts of core rule 2, usually as four sentences — the artefact and where it lives go
together:

1. **The artefact and where it lives.** *"URL points at the RACI Designated Roles and Teams page on
   Bitpool's internal wiki."* Describe a page by its **title and location**, never its URL slug —
   the slug moves (the `DCF-527` bucket's first link was replaced the same day by a new slug).
2. **What it is.** *"The page is the controlled record of the roles Bitpool designates for a
   specific duty."*
3. **How it evidences the control, by category.** *"It evidences DCF-527 by recording the
   appointment of the Data Protection Officer, the role through which it is held, the
   responsibilities assigned to it, and the contact mailbox…"*
4. **What keeps it trustworthy — integrity and currency.** *"The page is version-controlled, so its
   change history records each appointment and change."* Version control is integrity. Say what
   re-checks it too, by pointer, unless the record changes only on an event (an appointment, a
   designation) — then its change history is its currency and the bucket's renewal is the periodic
   re-check.

**Templates.**

*A link to a living page:*

> URL points at the `<page title>` page on `<location>`. The page is `<what it is>`. It evidences
> `DCF-xxx` by recording `<categories>`. The page is version-controlled, so its history records every
> change`<, and it is reviewed <on the cycle the policy sets / at each recurring task>, each review
> recorded in <the page history / last_reviewed / the review ticket>>`.

*A file added each time:*

> `<Artefact kind>` from `<system or process>`, `<what it shows, by category>`, covering
> `<the in-scope population, by pointer>`. It evidences `DCF-xxx` by showing `<how the categories
> meet the control>`. Each `<occurrence — review, run, attestation>`, on the cycle the `<policy>`
> sets, is added as a new version; `<what varies per version — the review period, the run date>` is
> in the file itself.

*A generated evidence pack:*

> `<Artefact kind>` for `<estate, as a population, with its scope record>`, generated by
> `<process>` from live state. Each version records `<the provenance the generator actually
> emits — collection time, collecting identity, source digest>`. It evidences `DCF-xxx` by showing
> `<categories>`. Findings, scope and counts are in the attached files and change with each version.

**Rules specific to evidence.**

- **`name` is the artefact kind, never a dated filename.** *"Periodic User Access Review"*, one
  bucket, a new version per review — not one bucket per review, each named for its date and each
  lapsing on its own.
- **Name where the population is defined.** Evidence covering a population — platforms, accounts,
  devices, people — says where the in-scope population is recorded: the policy criterion, the asset
  register, the ISMS scope. An auditor can then reconcile what the artefact shows against what it
  should show. By pointer; never a list of members. The pointer must resolve (core rule 1).
- **Name the capability, not the tool.** A screenshot of a platform shows the platform. The
  description names the kind of platform (*"the infrastructure monitoring platform"*, *"the device
  sanitisation tool"*) and what the artefact demonstrates. A product name stays only where a control
  or policy names that product as the requirement, or where it is the platform the estate is defined
  by and naming it lists nothing (*"every account in the AWS Organization"*).
- **No "at this time", "to date" or "has not been subject to".** *"Bitpool has not been subject to a
  notifiable breach"* goes false the day one occurs. Describe the prepared mechanism and point at
  where occurrences are recorded — *"any notification sent is recorded on the incident ticket"*.
- **Meeting outcomes belong to the minute.** Attendees, the risks challenged and the decisions taken
  are recorded in the attached record — *"the record lists the attendees, the risks questioned and
  the decision taken on each"*.
- **Guidance goes in `implementation_guidance`, at method level** — which system, which export,
  which query — never a named person's account as the test subject.

### §3.2 Risks — title, description and `treatmentDetails`

**Title and description** are written in risk language — a consequence to information, not a
missing control:

| Not risk language — a restated gap | Risk language — a consequence to information |
|---|---|
| *"Code review is not performed."* | *"Unreviewed code changes could introduce vulnerabilities or unintended behaviour into the customer-facing platform before release."* |
| *"No SIEM alerting on the office network."* | *"Malicious activity on the office network could go undetected long enough to reach systems holding customer data."* |

More pairs live with the workflow that writes risks (`/manage-drata-control`'s
`references/treatment-decisions.md`). What this profile adds: the description never names the
systems affected by account, host or product — *"the platforms holding customer data"*, not a list.

**`treatmentDetails` states the position and the mechanism, and points.** It says what Bitpool does
about the risk, why that is proportionate, which measures are relied on and which are planned, where
the operating evidence sits, and where outstanding work is tracked. It does not restate anything
with another home:

- **Scores, owner and treatment option** are structured fields. A `SCORING` paragraph or an
  *"accepted by `<name>`"* line is the same fact twice on one record.
- **Linked controls are carried by `control_ids`.** Any mention in prose — single or listed — of a
  control already linked is cut. Describe a linked control's capability only where the risk's
  position depends on it (*"antimalware software is installed on company-managed devices"*);
  otherwise the link carries it and the entry says nothing — capability sentences for every linked
  control turn a position into a disclaimer list. A `DCF` code appears in risk prose only to point at a control that
  is deliberately **not** linked because it owns something this risk does not (*"code review — not
  performed; treated under DCF-5"*). Before cutting a code, confirm it is in `control_ids`; if it is
  not, link it first. Never quote an evidence-bucket or monitoring-test name — Drata owns them and
  renames them; write *"the evidence on the linked controls"*.
- **Policy-owned parameters** — thresholds, SLAs, cadences, review intervals, required lists — are
  cited by policy name, once the version in force is confirmed to set them (core rule 1). A
  treatment item's own recurring activity cites its policy: *"access is reviewed on the cadence the
  System Access Control Policy sets"*, never *"reviewed quarterly"*. The risk entry's **own**
  re-examination is not stated at all — it belongs to the periodic risk review control and its
  recurring task.
- **Another record's content** — another risk's numbered items, another control's scope — is
  referenced by its code and never restated. Restatement is how one risk came to describe a plan that
  another had already changed. Refer to another record's item by what it is, not its number, unless
  that record declares its numbering permanent — a line in the entry stating that its item numbers
  are stable identifiers and are not renumbered on amendment.
- **An acceptance awaiting management review** is never written as *"pending"* in the entry. The
  owning workflow skill names where it is tracked until the minute exists.
- **Status that flips at a known event** — *"holds no evidence"*, *"newly identified"*, *"is
  provisioned"* — goes false for every entry carrying it at once. State the position; the ticket
  carries the status. One exception: a pointer whose target is still a draft — *"(pending promotion,
  `<ticket>`)"* keeps the pointer true until the policy is in force, and the promotion change removes
  it from every entry in one sweep.
- **Planned measures** are stated as the outcome, the condition on which they will be relied on, and
  the IRT pointer — never their progress (core rule 3).
- **Correction history** — *"CORRECTION `<date>`"*, *"supersedes"*, *"item numbering updated"*, a
  score change — is kept out of the body and recorded in a dated IRT or ICR comment **posted in the
  same change** (core rule 6). Drata keeps no readable history of the entry.
- **Exposure is a boundary, not an inventory.** Define the protected set by the criterion that
  decides membership. *"Platforms that meet the Vulnerability Management Policy's criteria for
  penetration testing are tested; platforms outside them are not"* stays true; a list of the hosts
  that are not tested is wrong the moment one is deployed or retired.

**Anchored verifications** (core rule 4): keep one per relied-on compensating control — the latest —
written as a past-tense event with its method and pointer, with no counts, lists or progress inside
it, and with what re-performs it where it is relied on as present assurance. Earlier verifications of
the same control move to the verification record the owning skill defines — an ICR or IRT comment;
they are not appended. A verification line on every item is a log, and the log belongs in those
comments.

**Length is a warning, not a limit.** Each treatment item is a sentence or two; the number of items
is whatever the treatment needs. An entry that runs to pages almost always carries logs, history or
restated records — cut those, never a treatment item.

**Exemplar — `CR-11`**, which stays true because it names the register and the kind of fact it
holds: *"Platforms that enforce multi-factor authentication natively, with no bypass available to
the user, are recorded as enforced in the Access Path Register together with the basis for that
grade."*

### §3.3 Control descriptions

A control description is what an auditor tests the evidence against, so rewriting it changes what
Bitpool asserts about itself. `/manage-drata-control` gates *whether* to rewrite one. When it is
rewritten, the new text must be durable as well as true:

- **The capability, not the product** — and claimed only once it covers the whole population the
  sentence names. *"Application allow-listing is enforced on managed Windows endpoints"* is the
  durable form of a completed rollout; while enforcement is partial, state by criterion the scope
  that is enforced, and that the remainder is carried on the risk register. `DCF-558` was corrected
  from one allow-listing product to its replacement, which set up the next identical correction.
- **Scope by reference, not by enumeration.** *"In-scope systems as defined in the Logging and
  Monitoring Policy"*, not *"AWS and Office365"* — once the policy is confirmed to define them.
- **No project state.** *"Being completed as a phased implementation"* is status. Where the control
  under-performs, say that the residual exposure is carried on the risk register, and stop.
- **No record IDs duplicating a structural link.** *"The residual exposure is carried on Bitpool's
  risk register"*, not *"accepted as risk CR-16"* — and confirm the risk is linked.
- **Every other copy moves with it.** A control description is mirrored into the controlled register
  and sometimes into a CSIP ticket. A durable description is what makes that mirror cheap: it does
  not go stale on its own.
- **The rewrite is recorded** in a dated ICR or IRT comment in the same change (core rule 6).

**Exemplars.** `DCF-56`: *"Vendors that meet the review criteria defined in the Vendor Management
Policy are subject to a security review at least annually. That policy defines the review criteria,
the classification scheme and the rating scales."* `DCF-67`: *"The level applied to each access
path — technically enforced, monitored for enrolment, or required by policy — is recorded in the
Access Path Register, with an approved exemption where none is achievable."* A later control review
recorded the payoff: `DCF-56` survived a correction unchanged *because* it pointed at the policy,
while the prose summary beside it did not.

### §3.4 Vendor fields

| Field | Write | Not |
|---|---|---|
| `services_provided` | The function and its category — *"source code hosting and CI/CD for the engineering team"* | Plan tier, seat or licence counts, named users, integrations, cost |
| `data_stored` | Data categories, in the terms of Bitpool's data classification scheme — *"Bitpool internal documentation and public product documentation"*; *"no stored data"* is a valid answer | Volumes, record counts, named customers, retention periods |
| `location` | Where the service is delivered, at the granularity the contract states, with the source named | Legal entity, governing law, or a "not publicly stated" research finding — those are dated review observations |
| `notes`, `environment_access`, `operational_impact` | The standing position, in categories and roles | Counts, dates, named people, current configuration |
| `contact_at_vendor`, `contacts_email` | A role mailbox where the vendor offers one | Bitpool's own addresses, URLs, or a person where a role address exists |

Verification dates, citations and review findings go in the **security review** (a dated snapshot)
or the skill's staging note, never in the field. Where the delivery location is not published, leave
`location` empty and name the document that would establish it in the staging note — never write
the negative finding into the field. Security review **conditions** are re-tested at the next review
and carry the residual score, so write them as testable criteria in role or category terms, never as
current counts, names or settings. The good existing examples are the terse ones:
*"stores electronic contact lists for email distribution"*; *"does not store any of Bitpool's data
or have access to any of Bitpool's systems"*.

### §3.5 SoA exclusion rationale

The requirement's `rationale` holds the justification for excluding an Annex A control, and renders
only where a requirement is marked out of scope. Clause 6.1.3(d) needs the justification to follow
from the risk assessment and the ISMS scope, so state it in those terms: which activity or asset
class the control governs, and either why no risk in the register requires it or why that activity
is outside the scope. By category, not by provider or product.

- **Outsourced is not excluded.** Where a provider operates the control on Bitpool's behalf, the
  control applies and is met through supplier management — mark it in scope and evidence the supplier
  assurance, naming the provider whose attestation is relied on.
- **Test the boundary against everything Bitpool runs itself** — the office, its network equipment
  and endpoints, not only production infrastructure. An exclusion that ignores equipment evidenced
  elsewhere in Drata will be tested against that evidence.
- **Inclusion justification** has no Drata field. It lives in the `Rationale` column of the controls
  register in `security-documentation`, under that repo's profile.

### §3.6 Custom Test name and description

Say what the test checks, which control it serves and where its logic is documented. Never resource
IDs, counts, current results or named accounts — the results live in Drata's test history, the logic
in the test's documentation page, and the literals inside the rule itself. Naming the `DCF` code a
test evidences is a durable handle here; §3.2's rule against naming linked controls is specific to
risk prose.

---

## §4 Calibration pairs — observed 2026-09-24

| Section | Before (copies values) | After (describes shape) |
|---|---|---|
| Evidence | *"For each running instance across all five AWS accounts, the script dispatches… All Linux instances are synchronising to 169.254.169.123… the Windows instance (bitpool-ftp)…"* — the account count was already wrong when read back | *"Generated report from Bitpool's time-synchronisation check, collected with AWS Systems Manager Run Command across every running instance in every AWS account in scope. For each instance it records the time service, its reference source and whether the clock is synchronised. It evidences DCF-421 to DCF-424 by showing every instance takes time from a common approved source. Each run is dated, and that run's results are in the report."* |
| Evidence | *"…reviewed between `<three named people>` during a meeting on `<date>`… Questions were raised about the following risks…"* | *"Risk assessment report and risk treatment exported from Drata for Bitpool's periodic risk review. The attached record captures the attendees, the date, the risks questioned and the decision taken on each. It evidences DCF-16 by showing the register is reviewed against the Risk Assessment Policy. Each review is added as a new version."* |
| Evidence | *"Backup monitoring is performed for SharePoint, BitBucket, Jira, and Chargebee. Notifications are sent to it@bitpool.com."* | *"Screenshots of the backup monitoring configured for the business SaaS platforms in backup scope, as recorded in `<the register or policy that defines that scope>`, showing which platforms are covered, that failures alert the IT mailbox, and that a ticket is raised for each failure. It evidences DCF-99 by showing backup failures are detected and acted on."* |
| Risk | *"…across all seven AWS accounts and both regions…"* | *"…across every account in the AWS Organization and every enabled region…"* — or, where an account is excluded by decision, *"…within `<the scope record>`"* |
| Risk | *"Accepted by Eric Sharp, risk owner. Review annually — recurrence generated by CYB."* | Where the acceptance needs stating: *"accepted by the risk owner at management review on `<date>`; minuted"* — the minute names the person and the residual level accepted; `owners` holds only the current owner. Drop the cadence: it belongs to the periodic risk review control and its recurring task. |
| Risk | *"…the platforms subject to review are Microsoft 365/Entra ID, AWS (all accounts), MongoDB, GitHub… Telstra is out of scope… Bitbucket is retired"* | *"Scope: the platforms that meet the selection criteria in the System Access Control Policy; the current list is held in the access review record."* |
| Control | *"…Windows Defender Application Control on all Windows devices…"*, later corrected to its replacement product | *"Application allow-listing is enforced on `<the managed Windows population the scope record defines>`; the remainder is carried on the risk register."* |
| SoA | *"managed by the AWS and Azure data centres respectively"* — names providers, implies an Azure workload estate, while office network equipment Bitpool sites itself is evidenced under `DCF-369` | A scope decision through `/manage-drata-control` first; then the basis in terms of the ISMS scope and the risk assessment, naming only a provider whose attestation is relied on |
