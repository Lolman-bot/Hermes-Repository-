# Writing profile — ISMS Policy

| | |
|---|---|
| **Writing profile** | ISMS Policy |
| **Platform** | ISMS policy drafts — Markdown in `security-documentation/ISMS/ISMS - Draft/` and `ISMS/ISMS - Draft (New)/` |
| **In scope** | Policy text written through `/isms-draft`: the body and the front matter of each draft |
| **Out of scope** | The controlled production set in the `isms` repo, which `/isms-prod` builds from an approved draft rather than authors; CYB promotion tickets; every other page in `security-documentation` (that is the Security Documentation profile) |
| **Readers** | Every Bitpool employee bound by the policy; auditors testing practice against it; the approver at each promotion |
| **Tone** | Requirements, roles, criteria and systems of record. Normative, not descriptive |
| **Split from** | — |

Policy text is the most durable record Bitpool writes and the most expensive to correct. Every fix is
a controlled-document revision and an approval event under clause 7.5.2, so a single copied value
turns every future change to that value into a policy revision.

Workflow — seeding, versioning, the policy queue, promotion — stays with `/isms-draft` and
`/isms-prod`. This profile governs *what the policy text says*.

---

## §1 Sections

| Section | In scope? | Profile | Rules |
|---|---|---|---|
| Policy body | Yes | ISMS Policy | §3.1 |
| Front matter (title, subtitle, date, owner) | Yes | ISMS Policy | §3.2 |
| Document Version Control table | Yes — as a snapshot | ISMS Policy | §2 |
| Generated extracts (e.g. the published Privacy Policy website extract) | No | — | Generated from the draft |

---

## §2 Record kinds in this target

| Part | Kind | Note |
|---|---|---|
| Policy body | Durable | §3.1 |
| Front matter `owner` | Durable | Names the owning **role**; the named owner's single home is Drata's policy owner — §3.2 |
| Front matter `date` | Structured | The document's own identification (clause 7.5.2(a)). A version number is assigned at promotion in the `isms` repo, not in the draft |
| Document Version Control rows | Snapshot | One change per row: the date and what changed, with why and the originating control and clause. Specific is correct. The **approver** is recorded in the `isms` promotion commit and Drata's Policy Center approval, not in this table |
| A threshold, SLA, cadence or scale this policy defines | Home | The policy that sets a parameter states it; other policies cite it by name |

---

## §3 Rules beyond the core

### §3.1 The policy body

- **Roles, never people** — *"the Head of Information Security approves…"* — using the title exactly
  as Bitpool's RACI tables name it.
- **Criteria, never inventories.** *"Every account in the AWS Organization"*, *"platforms holding
  customer data"* — not a list of accounts, platforms or vendors.
- **The system of record, never its contents.** *"Current holders of each role are recorded on the
  RACI Role Holders page"*, *"hardening settings are defined in the configuration baselines"* — not
  the holders or the settings.
- **A parameter is set in one policy — the policy is its home.** Where this policy defines a
  threshold, SLA, cadence or scale, it states the value; where another policy defines it, cite that
  policy by name rather than repeating the number.
- **No internal mailboxes, counts, hostnames, account names or configuration values** that a
  register, baseline or system owns. **Exception:** a contact point the policy exists to publish, or
  that its reader must act on — the Privacy Policy's contact mailbox, the incident-reporting channel
  in an incident procedure.
- **Commitment dates only where the ISMS requires the document to carry one** — an information
  security objective's completion date (clause 6.2(k)), or a corrective action's committed date
  recorded under clause 10.2. The document is then the authoritative home of that date. This governs
  dates in the policy's requirements; it does not touch the document's own identification date, the
  front-matter `date` the cover renders, the Version Control rows, or a *Last updated* line a control
  requires (as `DCF-120` does of the published Privacy Policy).

### §3.2 The cover's Document Owner

The cover names the **owning role**. That a named person owns the policy is a fact, and its single
home is Drata's policy owner field — a second copy on the cover is a second point of truth. Existing
drafts that name a person convert to the owning role; when, and in what batch, is `/isms-draft`'s
workflow decision, confirmed with the user. **Before converting a draft, confirm Drata's policy owner
holds the name** (core rule 1): where it is blank, it is filled first, so the conversion never
removes the only record of who owns the policy.

### §3.2a Text brought in unchanged

Wording seeded from an existing controlled document, or carried forward untouched, is not rewritten
unasked. Reshape only what the change requires, and list what this profile would change in the rest
so the user can choose. The same restraint applies as to Drata's stock text.

### §3.2b Queue text

Policy-queue text `/isms-draft` hands on is not policy text. The row's detail comment is IRT text,
under the Security Jira profile; its row on the queue page in `security-documentation` is register
content, under the Security Documentation profile.

### §3.3 Drafting from a finding

When a control review hands `/isms-draft` a correction, the handoff's evidence — the account names,
the observed configuration, the counts — is what *proves* the old text wrong. It stays in the handoff
and the policy queue comment. The proposed policy wording states the requirement and its basis in
categories.

---

## §4 Calibration pairs

| Before | After |
|---|---|
| Front matter `owner: "<person>"` | `owner: "<owning role>"` — the person is Drata's policy owner |
| *"…across the `<n>` AWS accounts…"* | *"…across every account in the AWS Organization…"* |
| *"…contact `<person>` at `<internal address>`…"* | *"…contact the `<role>` through the channel published in `<document>`…"* |
