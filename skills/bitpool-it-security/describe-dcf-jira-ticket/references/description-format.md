# The DCF ticket description format

Derived from six descriptions written in production between June and August 2026 (DCF-54, DCF-73,
DCF-75, DCF-164, DCF-558, DCF-760). The skeleton is constant across all six; sections 3 and 4 flex
by control shape. Those six predate `/bitpool-writing-standard`; where one carries a product name or
a dated target, this file follows the standard instead (§6).

---

## 1 — The constant skeleton

Always these four sections, always in this order, separated by `---` horizontal rules:

```markdown
### DCF-[nn] — [Control Name]

**What it is**

[One paragraph. Plain English. What the control requires *and* the exposure it prevents.]

---

**What it actually requires**

Per Drata's description, as read <YYYY-MM-DD>:

> _[Drata's control text, verbatim.]_

[One or two sentences: how it is monitored — automatically via an integration, or manually.]

---

**In practice for Bitpool**

[Shape-specific — see section 3 below. Always contains at least one two-column table.]

---

**Evidence Drata will look for**

[Prose or bullets — see section 3.]
```

### Rules that hold for every one of them

- **`###` is the only heading level used.** Section labels are **bold paragraphs**, not headings.
  This matters: Jira renders `###` as a visible heading, and using `##` or `#` makes the ticket
  shout. Sub-blocks inside *In practice* are also bold paragraphs.
- **`---` separates the four major sections only** — never between sub-blocks inside a section.
- **The Drata quote is verbatim and italicised** inside a blockquote. Never paraphrased, never
  trimmed to fit. Its lead-in names the source and the date it was read (§2).
- **Tables are two columns**, left column bolded, header naming what the row *is* and what must be
  shown: `| Resource | What to demonstrate |`, `| Area | What to demonstrate |`,
  `| Port | Requirement |`, `| Capability | What it demonstrates |`, `| Stream | What this looks like |`.
- **Inline code for identifiers only** — `0.0.0.0/0`, `encrypted-volumes`, `rds-storage-encrypted`,
  port numbers, setting names. Not for emphasis.
- **No emoji. No task lists. No status claims.** The description says what the control needs, not
  what state it's in. Work items belong in sub-tasks or `/create-devsecops-ticket`.
- **Australian/British spelling** throughout: organisation, minimise, unauthorised, centralised,
  recognise, prioritise.
- **Second person for Bitpool** — "your application-control approval process", "you need a calendar
  invite".
  These are read by Bitpool staff, not by an external auditor.

### The opening line of *What it is*

Every one of the six opens the same way, and it works — keep it:

> A control requiring that [subject] is [required state] — [the exposure it prevents].

Examples from production:

- *"A control requiring that data stored across in-scope systems is encrypted using strong
  cryptographic algorithms — protecting data from exposure if underlying storage is accessed or
  removed."*
- *"A control requiring that cloud resources are configured to deny public access by default —
  nothing should be publicly accessible unless there is an explicit, deliberate decision to make
  it so."*

The clause em-dash carrying the *why* is the part that makes these readable. Don't drop it.

---

## 2 — The quote lead-in

Three lead-ins are in use. Pick by what Drata actually holds:

| Drata field | Lead-in |
|---|---|
| `description` is substantive | `Per Drata's description, as read <YYYY-MM-DD>:` |
| `activity` (evidence guidance) is the more useful text | `Per Drata's evidence guidance, as read <YYYY-MM-DD>:` |
| Drata's text is thin or absent | `You need to demonstrate that:` followed by a **bullet list** — no blockquote |

The date is the day you read the control in Drata (SKILL.md step 2). A verbatim quote of another
record stays true only as what that record said on a stated date, so the first two lead-ins always
carry it; a refresh re-reads the control and updates the date with the quote.

The third form is how DCF-760 and DCF-164 handle governance controls where Drata's one-liner carries
almost nothing. The bullets there enumerate the standard's actual requirements, which is more useful
than quoting a stub.

---

## 3 — The three shapes

### Shape A — Automated infrastructure

*(`isMonitored: true`, satisfied by AWS/M365 configuration. DCF-54, DCF-73, DCF-75.)*

**In practice** contains:

1. Optionally, stream sub-headings as bold paragraphs — `**AWS Infrastructure**`,
   `**Employee & Endpoints**` — each with its own table.
2. A `| Resource | What to demonstrate |` table. Rows name the concrete AWS resource type and what
   must be true of it — where a policy sets the value (an algorithm, a retention period, a
   timeout), cite the policy, not the number (§6). Include the gotcha in the cell where one
   exists — e.g. RDS encryption *"must be set at creation time, it cannot be enabled on an existing
   unencrypted instance without a snapshot/restore"*. That sentence saves someone a day.
3. **The opinionated posture block** — bold-paragraph titled `**Account-level enforcement**` or
   `**The preferred posture for Bitpool**`. This is the most valuable part of the whole description
   and the easiest to skip.

**What the posture block argues:** enforcing at account or organisation level beats per-resource
configuration, *and the evidence is cleaner too*. Make both halves of that argument explicitly —
the security case and the audit-effort case. Production examples:

> "A single screenshot of this account-level setting enabled covers all S3 buckets at once."

> "Rather than restricting SSH/RDP to specific IPs, the stronger and cleaner approach — which Drata
> will recognise positively — is eliminating the need for open SSH/RDP entirely… security groups can
> have **no inbound SSH/RDP rules at all** rather than restricted ones — a stronger control and
> easier to evidence."

Name the concrete mechanism: an account setting, an SCP/RCP, an AWS Config rule (`encrypted-volumes`,
`rds-storage-encrypted`), SSM Session Manager.

**Evidence section:** a **prose paragraph**. Name the Autopilot checks, state which integrations must
be connected, and close on which posture gives the cleanest evidence.

### Shape B — Tooling / endpoint

*(Satisfied by a platform: application control, device management, a SaaS product. DCF-558.)*

**In practice** contains:

1. A sentence naming the mechanism that satisfies the control and how its model works
   (e.g. default-deny application control) — the capability, not the product in use this year.
   Name a product only where the control itself names it; otherwise the sentence goes false the day
   the platform is replaced.
2. A `| Capability | What it demonstrates |` table — one row per platform capability that maps to
   part of the control.
3. **The honest-tension block** where one exists — bold-paragraph titled e.g.
   `**Known tension with AI and developer tooling**`. Name the real operational friction — by kind
   of tooling, not by product — say the control intent is still satisfied, and say what needs
   documenting as a result.

That third block is a deliberate house choice: these descriptions are honest about friction rather
than presenting a clean story. Include it whenever a real tension is known — it's what makes the
ticket trustworthy.

**Evidence section:** a **bullet list** of specific kinds of artefact — a screenshot of the
platform's enforcement dashboard, a screenshot of the blocked-attempt view, the rollout plan and its
tracking ticket, a documented approval process. The target date lives on the tracking ticket, never
in the description.

### Shape C — Governance / clause

*(Management review, competence, audit coordination. DCF-164, DCF-760. Frequently mandatory
clauses 4–10 — check rule 8 in SKILL.md before writing a word of this shape.)*

**What it actually requires** uses the `You need to demonstrate that:` bullet form, and for
clause controls splits into two labelled bullet groups:

```markdown
**Mandatory inputs the review must address:**

* [...]

**Outputs that must be documented:**

* [...]
```

**In practice** uses a `| Stream | What this looks like |` table with the two Bitpool streams —
**Employee & endpoints** and **SaaS infra** — followed by a **`**Concretely:**`** paragraph that
deflates the requirement to its minimum viable artefact:

> "**Concretely:** you need a calendar invite, an agenda that maps to the required inputs above,
> someone from leadership present, and minutes/notes saved as evidence in Drata. A one-page doc with
> the date, attendees, what was reviewed, and what was decided is sufficient — it doesn't need to be
> elaborate."

That deflation is the point of the shape. Governance controls read as enormous and are usually
satisfied by one modest document; saying so is what stops them sitting untouched for a year.

**Evidence section:** a **bullet list** of documents.

**Optional closer**, used by DCF-760 — a final `---` and one line:

```markdown
**The audit question** is: _"[the question an auditor will actually ask, in their words]"_
```

Use it when the control's whole point compresses into a single question. It's the sharpest thing in
that description; don't force it where it doesn't fit.

---

## 4 — Cross-references

Reference sibling controls in prose where a shared posture applies:

> "Similar to DCF-75, the strongest posture is enforcing encryption at the account or organisation
> level"

Find them with `project = CSIP AND text ~ "DCF-xxx"`. Bare code plus context — no formal Jira issue
links, and no hyperlink needed inside a description that lives in the same project.

---

## 5 — Write mode

| Existing description | Action |
|---|---|
| **Stub** — Drata's stock one-liner only | **Replace.** The one-liner survives as the verbatim quote in section 2, so nothing is lost. |
| **Human-authored content present** | **Preserve it in full at the top**, blank line, then the explainer. Never edit or trim it. DCF-760 and DCF-164 both keep Drata's text above the explainer this way. |
| **Already carries an explainer** | **Refresh in place.** Say what changes and why. Never append a second copy. |

When in doubt, preserve. A duplicated paragraph is untidy; a deleted decision note is unrecoverable.

---

## 6 — What these descriptions never contain

The description is durable text under the **Security Jira** writing profile of
`/bitpool-writing-standard` (profile §3.7, CSIP descriptions; SKILL.md rule 11) — a standing
statement of a requirement, read long after it was written. The standard is the authority: load it
and apply its core rules. This list is the CSIP shortlist, each item with where the value lives
instead. **These prohibitions take precedence over the golden examples** — where an example carries
one of them, the example is the defect to fix.

- **Status claims** — "encryption is enabled on all buckets" — and the gaps observed today.
  Requirements only; observations go in the report to the user (SKILL.md step 5), however well
  verified and however dated.
- **Task lists / action items** — those go to sub-tasks or `/create-devsecops-ticket`.
- **Risk scores, treatment decisions, or acceptance language** — `/manage-drata-control` owns those, and on
  a mandatory clause acceptance language is actively wrong.
- **ISMS policy text** — reference a policy, never draft one.
- **Owners, due dates, or assignees** in prose — they're Jira fields and they drift. So is a rollout
  target or any other commitment date: write *"the rollout plan and its tracking ticket"*; the date
  lives on that ticket.
- **Live Drata counts or readiness flags** — they change continuously and go stale in a static
  description. `/drata-control-insights` renders those live.
- **Named individuals and role-holders** — name the role or function the requirement assigns
  (*"top management"*, *"the risk owner"*), never the person holding it. Who holds a role is the
  RACI Role Holders page; the control's owner is Drata's `owners`.
- **Email addresses and mailboxes** — name the channel and the document that publishes it.
- **Appointment and approval dates** — the appointment or approval record holds them; describe what
  that record holds, by category.
- **AWS account names, IDs and counts, and resource names** — describe the population (*"every
  account in the AWS Organization"*, *"the account holding production workloads"*). Resource *types*
  stated as requirements (`S3 buckets`, `RDS instances`) and AWS Config rule names are fine: they
  describe the requirement, not the estate.
- **Products and versions in use** — name the capability (*"application control"*, *"device
  management"*), unless the control itself names the product, or it is a platform the text points
  at rather than reports on (AWS, Drata, Jira), or an operating system's own built-in feature named
  as the mechanism the control requires (durability-check §4 — e.g. BitLocker, FileVault for
  full-disk encryption).
- **Configuration values** — retention periods, session lifetimes, observed settings: point at the
  system or baseline that holds them.
- **Numbers a policy owns** — SLAs, cadences, timeouts, thresholds: cite the policy by name, once the
  version in force is confirmed to set the value.
- **Values copied from a comment** — state the requirement the comment settles and point at the
  comment by its date (SKILL.md step 1).
- **The description's own history, or session voice** — *"updated on"*, *"previously said"*,
  *"Claude found"*, *"Hermes found"*. Jira's changelog holds the edit.
