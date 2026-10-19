# Golden examples

Three descriptions from CSIP, one per shape. Read them before drafting and check your draft against
the one that matches your control's shape. They are the specification for **shape and voice** —
where this file and prose guidance on structure disagree, these win. They are not a licence for
content: where an example conflicts with the prohibitions in `description-format.md` §6 or with
`/bitpool-writing-standard`, the prohibition wins and the example is the thing to fix.

Copied from Jira on 2026-08-20, then edited to the writing standard: products in use are named by
capability, Shape B's dated rollout target is replaced by a pointer to its tracking ticket, and each
Drata quote's lead-in carries the date it was read (a placeholder here). The
live tickets predate the standard, are not rewritten here, and no longer match this file word for
word — never copy wording from a live ticket that this file has changed. For what over-specific
text looks like, read the calibration pairs in the standard's Security Jira profile (§4).

---

## Shape A — Automated infrastructure

**[CSIP-653](https://bitpool.atlassian.net/browse/CSIP-653)** · `Drata | Bitpool | DCF-54 | Encryption at Rest`

Note the two stream sub-headings each with their own table, the account-level enforcement block
carrying both the security and the evidence-effort argument, the cross-reference to DCF-75, and the
RDS gotcha placed in the table cell where someone will actually hit it.

```markdown
### DCF-54 — Encryption at Rest

**What it is**

A control requiring that data stored across in-scope systems is encrypted using strong cryptographic
algorithms — protecting data from exposure if underlying storage is accessed or removed.

---

**What it actually requires**

Per Drata's description, as read <YYYY-MM-DD>:

> _Data at rest is encrypted using strong cryptographic algorithms._

Primarily automatically monitored by Drata via its AWS integration — Autopilot checks resource
configurations for encryption at rest across AWS services.

---

**In practice for Bitpool**

**AWS Infrastructure**

| Resource | What to demonstrate |
| --- | --- |
| **S3 buckets** | Default encryption enabled — SSE-S3 minimum, SSE-KMS preferred for sensitive buckets |
| **RDS instances** | Encryption at rest enabled on the instance — note this must be set at creation time, it cannot be enabled on an existing unencrypted instance without a snapshot/restore |
| **EBS volumes** | Encryption enabled — can be enforced account-wide via the "Always encrypt new EBS volumes" account setting |
| **Aurora / RDS clusters** | Cluster-level encryption enabled via KMS |
| **Secrets Manager** | Encrypted by default using KMS |
| **CloudTrail logs in S3** | Covered by S3 default encryption |
| **Backups** | RDS automated backups and snapshots inherit encryption from the source instance |

**Account-level enforcement**

Similar to DCF-75, the strongest posture is enforcing encryption at the account or organisation
level:

* **EBS default encryption** — a single account setting that ensures all new EBS volumes are
  encrypted automatically, no per-volume configuration needed
* **S3 default encryption** — set at the bucket level but can be enforced via SCP/RCP preventing
  creation of unencrypted buckets
* **AWS Config rule** `encrypted-volumes` and `rds-storage-encrypted` — automatically flags any
  unencrypted resources and feeds directly into Drata

**Employee & Endpoints**

| Area | What to demonstrate |
| --- | --- |
| **Windows devices** | BitLocker enabled via an MDM configuration profile |
| **macOS devices** | FileVault enabled via an MDM configuration profile |

Device encryption status is monitored by Drata automatically via its device-management
integration — devices without encryption enabled will surface as non-compliant.

---

**Evidence Drata will look for**

Automatically monitored via Drata's AWS and device-management integrations. Key Autopilot checks
include S3 default encryption, RDS storage encryption, EBS volume encryption, and device encryption
compliance. Ensure the AWS and device-management integrations are connected and Autopilot tests are
passing. The account-level EBS encryption setting and AWS Config rules provide the strongest and
cleanest evidence posture.
```

**Also worth reading:** [CSIP-651](https://bitpool.atlassian.net/browse/CSIP-651) (`DCF-73`,
remote admin ports) for the `| Port | Requirement |` table variant and the SSM Session Manager
posture argument, and [CSIP-659](https://bitpool.atlassian.net/browse/CSIP-659) (`DCF-75`,
restricted public access) for the shortest clean instance of the shape.

---

## Shape B — Tooling / endpoint

**[CSIP-646](https://bitpool.atlassian.net/browse/CSIP-646)** · `Drata | Bitpool | DCF-558 | Restrictions on Software Installation`

Note the `Per Drata's evidence guidance, as read <YYYY-MM-DD>:` lead-in (Drata's `description` was
the weaker text here), the capability table, the honest-tension block, and evidence as bullets naming
specific kinds of artefact. The mechanism is named by capability throughout: the live ticket named
the platform then in use, its own module names, the tools in tension with it, and a dated rollout
target — each of which goes false on its own schedule.

```markdown
### DCF-558 — Restrictions on Software Installation

**What it is**

A control requiring that mechanisms are in place to prevent unauthorised software from being
installed or executed on company-managed devices — ensuring only approved applications can run.

---

**What it actually requires**

Per Drata's evidence guidance, as read <YYYY-MM-DD>:

> _Screenshots from MDM or endpoint management tools showing enforced rules that block unauthorized
> software installation, or access controls that restrict the ability to run executables on company
> devices._

---

**In practice for Bitpool**

This control is satisfied by **application control** on company-managed devices, operating a
default-deny model where nothing runs unless explicitly permitted.

| Capability | What it demonstrates |
| --- | --- |
| **Application whitelisting** | Only approved applications are permitted to execute — everything else is blocked by default |
| **Application containment** | Approved applications are restricted in what they can access, limiting lateral movement even from permitted software |
| **Privilege elevation control** | Users cannot self-elevate to install software without approval |
| **Audit log** | Full record of blocked and permitted execution attempts |
| **Central enforcement view** | The platform's dashboard provides a centralised view of enrolled devices and their enforcement status |

**Known tension with AI and developer tooling**

There is deliberate tension between hash-based whitelisting and AI and developer applications that
update frequently and change their hashes with each release. This is a known operational
challenge — the control intent is still satisfied, but the operational process for managing
developer tooling exceptions needs to be documented in the policy or procedure that governs the
whitelist.

---

**Evidence Drata will look for**

* Screenshot of the application-control dashboard showing whitelisting is enabled and enforced
  across enrolled devices
* Screenshot of blocked application attempts — demonstrating the default-deny model is active
* Evidence that enforcement covers every company-managed device — until it does, the rollout plan
  and its tracking ticket (`<tracking ticket key>`)
* A documented policy or process for how new software is requested, approved, and added to the
  whitelist
```

---

## Shape C — Governance / clause

**[CSIP-760](https://bitpool.atlassian.net/browse/CSIP-760)** · `Drata | Bitpool | DCF-164 | Management System Management Review`

Note the `You need to demonstrate that:`-style bullet groups instead of a quote, the
`| Stream | What this looks like |` table with Bitpool's two streams, and the **Concretely:**
paragraph that deflates the requirement to its minimum viable artefact.

This is a **mandatory clause** control (clause 9.3) — no acceptance route, no risk-treatment
language. See golden rule 8 in `SKILL.md`.

In the live ticket, Drata's original one-liner is **preserved above** the explainer rather than
being folded into a quote block. That's the *human-authored content present* write mode in action —
either treatment is acceptable; preserving is never wrong.

```markdown
### DCF-164 — Management System Management Review

**What it is**

A formal, scheduled review by leadership of the entire ISMS (Information Security Management System)
to confirm it remains suitable, adequate, and effective. It's one of the core "top management"
obligations in ISO 27001 — the standard explicitly requires that this isn't delegated away; someone
with authority needs to sign off.

---

**What it actually requires**

You need to run a documented review meeting at planned intervals — the standard leaves the interval
for Bitpool to set — that covers a defined agenda and produces recorded outputs.

**Mandatory inputs the review must address:**

* Status of actions from previous reviews
* Changes in external/internal issues relevant to the ISMS (new threats, reg changes, business
  changes)
* Feedback on security performance — incidents, nonconformities, monitoring results, audit findings
* Feedback from interested parties (customers, auditors, regulators)
* Results of risk assessments and status of the risk treatment plan
* Opportunities for continual improvement

**Outputs that must be documented:**

* Decisions on continual improvement opportunities
* Any changes needed to the ISMS
* Resource needs

---

**In practice for Bitpool**

| Stream | What this looks like |
| --- | --- |
| **Employee & endpoints** | Review MDM compliance rates, security training completion, phishing/incident stats, any endpoint policy changes needed |
| **SaaS infra** | Review AWS posture findings (Drata Autopilot), access review outcomes, vendor/SaaS changes, open risks from the risk register |

**Concretely:** you need a calendar invite, an agenda that maps to the required inputs above, someone
from leadership present, and minutes/notes saved as evidence in Drata. A one-page doc with the date,
attendees, what was reviewed, and what was decided is sufficient — it doesn't need to be elaborate.

Drata will typically want to see the review document itself uploaded as evidence, along with the
meeting date and sign-off.
```

**Also worth reading:** [CSIP-687](https://bitpool.atlassian.net/browse/CSIP-687) (`DCF-760`,
control of audit activities) — same shape, and the one example that closes with the optional
**The audit question** line:

```markdown
**The audit question** is: _"How do you ensure audit and testing activities are coordinated so they
don't cause unplanned disruptions to Bitpool's systems or operations?"_
```

---

## Counter-example — what an un-described ticket looks like

For contrast, this is the stock Drata stub these tickets arrive with, and the thing this skill
exists to replace. [CSIP-626](https://bitpool.atlassian.net/browse/CSIP-626) (`DCF-406`, audit
logging) still carries only:

> Audit logs are enabled and active for all system components and sensitive data in accordance with
> company policies.

One sentence, no Bitpool context, no evidence guidance, nothing actionable. Under the *stub* write
mode this gets replaced outright — and that sentence reappears verbatim as the blockquote in
*What it actually requires*, so nothing is lost.
