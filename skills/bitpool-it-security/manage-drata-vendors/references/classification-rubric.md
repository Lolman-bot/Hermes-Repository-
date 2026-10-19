# Vendor classification rubric

How Bitpool classifies and scores a vendor, and what follows from it. Settled with the risk owner
2026-09-03 during the A.5.19–A.5.23 control review.

**The Vendor Management Policy is the parent of record for everything in this file.** It lives at
`security-documentation/ISMS/ISMS - Draft/Vendor Management Policy.md`. Where the policy and this
file disagree, **the policy wins and this file is stale** — fix it here, and never resolve it the
other way by editing the policy from this skill.

---

## 1. Relationship type — split on standing access

`type` is decided by **whether the third party holds standing access to Bitpool systems or data**,
not by what kind of organisation it is. A law firm engaged from time to time with no Bitpool login
is a different control problem from a DevOps contractor holding standing AWS credentials, even
though both are "professional services".

| `type` | Definition | Induction required? | Examples |
|---|---|---|---|
| `VENDOR` | A platform or product Bitpool holds an account with. At least one service-model flag true | No — access is Bitpool-side, governed by MFA and the periodic access review | Chargebee, Xero, Microsoft, AWS, Atlassian, GitHub, ThreatLocker, Telstra |
| `SUPPLIER` | Supplies goods, premises, or professional services engaged from time to time. **No standing access, no Bitpool identity** | No | Law firms, accountants, auditors, insurance brokers, hardware resellers, the landlord, building-automation subcontractors |
| `CONTRACTOR` | Performs work for Bitpool **with standing access to Bitpool systems or data** | **Yes** | Perun, Rise Building Technology, CLK Bookkeeping, Zoe & Co |
| `PARTNER` | Reseller or joint-delivery relationship; may hold a delegated administrative role | Case by case — flag where a role is held | Alliance Business Technologies, which held a least-privilege admin role in the O365 tenancy |
| `OTHER` | Genuinely none of the above. **Requires the reason, recorded in the staging note's `Basis` column** — `notes` is IGNORE (`field-contract.md`) | — | Should end up empty |

The named examples are as classified on 2026-09-03 — illustrations of each definition, not a record
of any relationship's current state. Re-derive from the definition.

**Why professional services are not `CONTRACTOR`.** The instinct is to group by profession, and it
is wrong. Splitting by access is what makes the field do work: a `CONTRACTOR` carries an induction
obligation and a `SUPPLIER` does not, so mixing a law firm in with a DevOps contractor either
over-obligates the firm or under-obligates the contractor.

### The contractor identity mechanism

Not a task this skill performs — a control it must not misreport.

Contractor personnel hold **individually named `@bitpool.com` identities**, provisioned into a
dynamic Entra group for contractors. They do not use shared accounts and they do not use
vendor-managed credentials. Those identities sync into Drata Personnel as `CURRENT_CONTRACTOR`
(`syncStatus: SYNCED`), so the personnel controls — policy acceptance, security awareness, access
review, offboarding — reach them automatically.

> **Drata Personnel does not record which vendor a contractor belongs to.** There is no field
> linking a person to the vendor-register row for their firm. **Never infer that a contractor firm
> has no personnel records from the fact that you cannot match the names — ask.**
>
> Worked failure, 2026-09-03: a review reported that Perun's engineers held no Drata Personnel
> record and were therefore covered by no personnel control. Both of the firm's engineers held
> `CURRENT_CONTRACTOR` records with `@bitpool.com` identities, **both present in the very list that
> had just been read.** The claim was one step from a Drata risk entry and an ISO control
> review comment, where it would have been a false statement about a named third party's compliance
> posture.

**No recurring register-to-personnel reconciliation exists, deliberately.** The Entra dynamic group
does it automatically, so a manual quarterly cross-check would duplicate a working automated
control — and a control performed for form's sake implies coverage it does not add. The residual
risk it would supposedly catch is *access through a route with no Bitpool identity at all* — a
shared account, a vendor-managed credential, a direct IAM key — which a register cross-check cannot
see and the periodic access review can.

---

## 2. Service model — four independent flags

A vendor can be several at once, so this is **four booleans, not one value**. Microsoft is SaaS +
IaaS + IdP across M365 and Azure; no single-value field can carry that.

| Flag | Custom field | Means |
|---|---|---|
| Is SaaS? | `7` | Bitpool consumes a hosted application |
| Is IdP? | `8` | The vendor provides identity or authentication for Bitpool |
| Is IaaS? | `9` | Bitpool runs its own workloads on the vendor's infrastructure |
| Is PaaS? | `10` | Bitpool builds on a managed platform, runtime or database the vendor operates |

**Set all four on every vendor.** A law firm is `false, false, false, false` — which is a
classification. All-null is not.

> **Any vendor flagged SaaS, IaaS or PaaS is a *cloud service* for policy purposes.** This is what
> makes ISO 27001 **A.5.23** (Information security for use of cloud services) answerable from the
> register at all, and it is what selects the Cloud Service Provider contract clause set. Before
> these flags existed nothing in the register said which vendors were cloud services.

**Direction of trust matters for `Is IdP?`.** AWS has IAM Identity Center, but Entra federates
*into* it — so Microsoft is the IdP and AWS is the relying party. `Is IdP?` is `false` on AWS. Do
not set it true just because an identity feature exists.

---

## 3. Scoring — inherent versus residual

Two separate scales, both recorded, and the distinction is load-bearing.

**`impact_level` — inherent impact.** How serious the consequences would be if the vendor were
breached or failed, assessed **without reference to Bitpool's own compensating controls**.

> **⚠️ Known defect in this field, recorded 2026-09-03. Read before scoring anything.**
>
> "Breached **or** failed" asks one field to carry **two orthogonal axes**, and the register proves
> they diverge:
>
> | Vendor | If it **fails** | If it is **breached** |
> |---|---|---|
> | Telstra | expensive — carrier outage | little reach |
> | 1Password | little direct cost | **total** — every Bitpool credential |
>
> Both score around `MAJOR`/`MODERATE`, and the field cannot tell you which kind of exposure it is
> describing. Four more make the same point, all `MODERATE` when recorded and four of the five with
> `passwordMfaEnabled: false`: **GitProtect** (all source-code backups), **Veeam** (all of O365),
> **Drata** (the ISMS record itself) and **ZeroTier** (a network path into production).
>
> **Consequence for scoring:** when the two readings disagree, score the **breach reach**, because
> that is what the review threshold and every access control question actually turn on — and say in
> the note that you did. Availability impact then needs recording separately if Bitpool wants it.
>
> **Consequence for control scoping:** never scope an access control by business criticality.
> *Criticality measures how much it hurts if the platform fails; control scope needs how far a
> stolen login reaches.* A criticality rule puts the ISP in scope and leaves the credential vault
> out — Telstra in, 1Password out, which is exactly backwards. Bitpool created a custom field for
> business criticality on this basis and deleted it the next day.

| Value | Means |
|---|---|
| `CRITICAL` | Holds Bitpool or customer production data, source code, credentials or billing records; or its failure halts delivery of Bitpool services |
| `MAJOR` | Holds significant confidential information, or holds standing privileged access to production |
| `MODERATE` | Holds internal, non-sensitive information, or has limited access |
| `MINOR` | Holds little or no Bitpool information, no access, readily replaced |
| `INSIGNIFICANT` | No Bitpool information and no access |

**`risk` — residual risk.** That same exposure reassessed **after** Bitpool's controls (enforced
MFA, SSO, least privilege) and after any conditions imposed at security review. `NONE` · `LOW` ·
`MODERATE` · `HIGH`.

> **Bitpool's controls reduce residual risk; they do not reduce inherent impact.** A vendor's
> inherent impact changes only when what it holds, or what it can reach, changes.

### The scoring bias warning

A parallel AI classification pass over all 35 vendors on 2026-09-03 proposed re-scoring **23 of
them, with 20 of the 23 moving inherent impact upward** — Team Viewer `INSIGNIFICANT`→`MAJOR`,
Mullins Lawyers `MINOR`→`MAJOR`. When that many independent judgements move the same direction it
is rubric or model bias, not that many findings.

Two proposals moved residual risk *downward* from `HIGH`, which under the threshold below would
have silently removed those vendors from review altogether.

**So: propose scores, never apply them in a completeness pass.** Score changes get their own
labelled block and their own approval, per SKILL.md rule 5.

---

## 4. The security review threshold

A vendor is subject to a periodic security review, conducted **at least annually**, where **any** of
these applies:

1. its **residual risk** is `MODERATE` or `HIGH`;
2. it is a **sub-processor** of personal information, irrespective of residual risk;
3. a security review has been **approved subject to conditions** and those conditions have not since
   been evidenced as met at a subsequent review.

Otherwise `renewal_schedule_type = NONE`.

**Inherent impact level does not by itself trigger a review.** "Critical vendor" means inherent
`MAJOR` or `CRITICAL` — it describes the consequence of failure, and it is not the trigger.

### Residual `HIGH` requires an exception

Residual `HIGH` means Bitpool's controls *and* any review conditions have **not** brought exposure
below the acceptable level. Continuing to rely on the vendor is a **risk acceptance, not a routine
approval**: it needs a documented exception, recorded against the vendor and raised in the risk
register. A vendor may not be recorded as approved at residual `HIGH` without one.

**The 2026-09-03 review found vendors at residual `HIGH` with no recorded exception of any kind** —
seven on that day's read of the register. That is a finding to raise, not something this skill
resolves; read the live register for the current position rather than quoting that count.

### Why the review is the lever, not just a record

The chain is **inherent risk → security review → decision → residual risk.** The review is the
instrument that moves inherent to residual, and the conditions attached to an
`APPROVED_WITH_CONDITIONS` decision *are* the controls doing the reduction.

AWS demonstrates it: its 2024 review closed `APPROVED_WITH_CONDITIONS` with five named conditions —
backups of all critical data, MFA on all user accounts, tightly restricted admin accounts,
POLP/RBAC, and data protection, retention and deletion controls.

An earlier draft of the threshold argued that keying review frequency off residual risk is
**circular**, since residual risk reflects Bitpool's controls rather than the vendor's security.
**That objection was rejected, and rightly.** It is not a circularity defect but a designed feedback
loop, and the review is what closes it — a vendor leaves the cycle only by being assessed and
mitigated.

**Criterion 3 exists to close the one real hole in that loop.** If residual `LOW` exits the cycle,
the conditions that produced `LOW` are never re-verified. That failure is already in the data: AWS's
2024 review imposed five conditions and its 2025 review (id `30`, `APPROVED`) carries an **empty
note** — no record that any of the five were re-tested. **A condition that is never re-tested is not
a control.**

> Criterion 3 is worded as *"conditions not since evidenced as met"* rather than *"the most recent
> review was with-conditions"*, because the latter misses AWS exactly — its most recent decision is
> plain `APPROVED`. Evaluating it needs `Drata_listVendorSecurityReviews` per vendor and a judgement
> about whether the note evidences closure. There is no field for it.

### The sub-processor criterion is not negotiable here

Criterion 2 is **not a risk-appetite matter.** The published Privacy Policy commits to customers,
without qualification by score, to assess each sub-processor and review that assessment annually.
A sub-processor can sit at residual `LOW` — Chargebee and Pandadoc did when the threshold was
settled on 2026-09-03 — and without criterion 2 the ISMS would contradict a public privacy notice.

**If it is ever to be removed, the Privacy Policy must be edited in the same change.** That is a
customer-facing commitment and therefore the risk owner's decision, never a drafting one.

### Re-scoring upward creates the obligation

A vendor reassessed such that any criterion becomes true **acquires a review obligation from that
point**, and its next review due date is set at the time of the reassessment.

This closes a real observed failure: 1Password was re-scored to inherent `MAJOR` / residual
`MODERATE` and **the schedule did not follow** — it held every Bitpool credential, was flagged
`hasPii: true`, and had no review and none scheduled.

---

## 5. Worked classifications

Reference points, not a lookup table. Re-derive from the rubric. **As classified on 2026-09-03** —
a dated record of the reasoning, never any vendor's current score, which is on its Drata record.

| Vendor | `type` | Service model | Inherent | Residual | Review? |
|---|---|---|---|---|---|
| Microsoft | `VENDOR` | SaaS + IdP (+IaaS/PaaS if Azure compute is in use) | `CRITICAL` | `HIGH` | Yes — residual, **plus an exception** |
| AWS | `VENDOR` | IaaS + PaaS, **not** IdP | `CRITICAL` | `HIGH` | Yes — residual, **plus an exception** |
| Chargebee | `VENDOR` | SaaS | `CRITICAL` | `LOW` | **Yes — sub-processor** |
| Perun | `CONTRACTOR` | none | `MAJOR` | `LOW` | No under the threshold |
| 1Password | `VENDOR` | SaaS | `MAJOR` | `MODERATE` | Yes — residual |
| A law firm | `SUPPLIER` | all four `false` | `MINOR` | `LOW` | No |

Perun was the entry worth arguing about: a DevOps contractor with access to the whole AWS estate at
inherent `MAJOR`, exempted because its residual risk was `LOW`. That is the deliberate consequence of
keying the threshold off residual risk, and it was the risk owner's decision. If it is revisited,
this file and the policy change together.
