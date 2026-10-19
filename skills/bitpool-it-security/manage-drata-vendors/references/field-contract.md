# Vendor field contract

**The authority on what this skill writes to a Drata vendor.** Agreed with the risk owner
2026-09-03, field by field. Do not add a field to the keep list without that decision being
recorded here first.

Three dispositions, plus one field that is neither:

- **KEEP** — the skill sets and maintains it.
- **WIPE** — Bitpool has retired it. Cleared **once**, then never populated again.
- **IGNORE** — left exactly as found, in either direction.
- **`confirmed`** — never written at all. See the note at the end; it is not one of the three.

---

## KEEP — the skill sets these

### Identity and description

| Field | Type | Notes |
|---|---|---|
| `name` | string | Canonical vendor name. No trailing entity noise ("Pty Ltd", "s. r. o.") unless it disambiguates |
| `services_provided` | string | What the vendor does **for Bitpool**. `DCF-56` names this field explicitly. Enough to scope a review from — two words is not — worded per Security Drata §3.4 |
| `data_stored` | string | What data it holds, as categories per Security Drata §3.4. **"No stored data" is a valid answer; `null` is not** |
| `location` | string | Where the service is delivered, per Security Drata §3.4. Feeds the geographic-limits contract clause and every data-residency questionnaire |
| `url` · `privacy_url` · `terms_url` | string | Best effort |
| `trust_center_url` | string | **The most valuable of the four** — it is where the SOC 2 and ISO certificates live, so it is what makes the annual review repeatable instead of a hunt |

**The three free-text fields are durable text in a registered target.** Their wording belongs to
`/bitpool-writing-standard`: load it and its Security Drata profile before proposing a value.
§3.4 of that profile is the authority on what each field says and leaves out, and this file does not
restate it. What this contract adds:

- **The verification date and the citation (the URL and the date read) go in the staging note's
  `Basis` column**, never inside the value. `location` alone names, inside the value, the contract
  document it rests on, per Security Drata §3.4 — *"`<region>`, as stated in the vendor's Data
  Processing Addendum"* — but never a date.
- **What has no field goes in the security review, not the nearest free-text field.** A vendor's
  legal entity, governing law, a "not published" research finding, and a certification's report
  period, auditor and expiry belong in the dated security review text (staging note section 7). A
  `location` that cannot be established stays `null`, with what would establish it in section 4 of
  the note.
- **`notes` is IGNORE, so it is never the fallback** for a reason with no field — a type `OTHER`
  justification goes in the staging note's `Basis` column.
- **Every proposed value passes the durability check** shown under section 1 of the staging note.

### Classification

| Field | Type | Allowed values |
|---|---|---|
| `type` | enum | `VENDOR` · `SUPPLIER` · `CONTRACTOR` · `PARTNER` · `OTHER` · `NONE` |
| `category` | enum | `ENGINEERING` · `PRODUCT` · `MARKETING` · `CS` · `SALES` · `FINANCE` · `HR` · `ADMINISTRATIVE` · `SECURITY` · `LEGAL` · `INFORMATION_TECHNOLOGY` · `NONE` |
| `has_pii` | bool | Explicit. `null` is not an answer |
| `is_sub_processor` | bool | **Triggers a review on its own** — see the rubric. Explicit, never `null` |

**`type` cannot be extended from MCP.** There is no `custom_vendor_type` parameter on create or
update, and no custom vendor type was configured as at 2026-09-03. If custom types are ever defined
in the UI, assume they must be assigned by hand until proven otherwise.

### Risk

| Field | Type | Allowed values |
|---|---|---|
| `impact_level` | enum — **inherent** risk | `INSIGNIFICANT` · `MINOR` · `MODERATE` · `MAJOR` · `CRITICAL` · `UNSCORED` |
| `risk` | enum — **residual** risk | `NONE` · `LOW` · `MODERATE` · `HIGH` |

**Never leave either at `UNSCORED`/`null`, and never write either without explicit approval of that
specific score** (SKILL.md rule 5). Note the scales are different lengths and the words overlap
confusingly: `MODERATE` exists on both, `HIGH` only on residual, `MAJOR`/`CRITICAL` only on
inherent. That mismatch is why the old `DCF-56` wording — *"score 'Moderate" or "High"'* — could
only ever have meant residual.

### Review schedule

| Field | Type | Allowed values |
|---|---|---|
| `renewal_schedule_type` | enum | `ONE_MONTH` · `TWO_MONTHS` · `THREE_MONTHS` · `SIX_MONTHS` · `ONE_YEAR` · `CUSTOM` · `NONE` |
| `renewal_date` | date `YYYY-MM-DD` | Never invented, never moved forward past its due date |

Bitpool uses `ONE_YEAR` or `NONE`. Nothing else.

### Ownership and lifecycle

| Field | Type | Notes |
|---|---|---|
| `owner` | user id / email / name | The **security owner**. Resolved server-side. Must be current personnel — check before writing |
| `status` | enum | `PROSPECTIVE` · `ACTIVE` · `ARCHIVED` · `APPROVED` · `REJECTED` · `FLAGGED` · `ON_HOLD` · `OFFBOARDED` · `UNDER_REVIEW` · `NONE` |

**Bitpool's `status` convention: `ACTIVE` for in use, `ARCHIVED` for retired.** Nothing else, and
in particular **not `APPROVED`** — it was in use on some records (Microsoft, Adobe) while others
used `ACTIVE`, which makes filtering unreliable for no gain. It is also easily confused with a
security review `decision` of `APPROVED`, which is an unrelated thing on a different object.

### Authentication

| Field | Type | Notes |
|---|---|---|
| `password_policy` | string | Observed values: `USERNAME_PASSWORD`, `SSO`. **The only password field Bitpool maintains** — the rest are on the wipe list |

> **A trap worth knowing.** `password_policy: USERNAME_PASSWORD` on **Microsoft** looks like a
> defect and is correct: Microsoft *is* Bitpool's identity provider, so there is nothing upstream to
> single-sign-on into. Every *other* Microsoft-authenticated vendor should read `SSO`. Do not
> "fix" the IdP.

### Custom fields

**Verified present 2026-09-03.** Writes address custom fields **by id**, so the id is the
load-bearing detail, not the name.

> ## ⛔ Custom fields are MANDATORY on create — a create cannot be split from them
>
> **Verified 2026-09-04** by attempting `Drata_createVendor` without them. Drata returned `400`
> naming every required custom field, so the two-call pattern of "create the vendor, then set custom
> fields" **does not work**. It was the documented plan here and it failed on the first real create.
> One call, custom fields inline. If you cannot answer them all for a new vendor, you are not ready
> to create it — which is arguably the point.
>
> **The required set as at 2026-09-04 is expected to be `7`–`10`, but is UNVERIFIED.** The observed
> `400` named six fields, two of which have since been deleted, so the list has certainly changed and
> nobody has re-tested it. **The next create settles it** — read the error, do not assume.
>
> A useful side effect: a `400` for missing custom fields proves `create:vendor` scope is **granted**,
> because a scope failure would have been `403` before validation ran.

| id | Name | Type |
|---|---|---|
| `7` | Is SaaS? | boolean |
| `8` | Is IdP? | boolean |
| `9` | Is IaaS? | boolean |
| `10` | Is PaaS? | boolean |

**These four are the whole set.** Created 2026-09-03, empty on every vendor at that point.

Set **all four** on every vendor. `false` is a value; `null` is not — the whole point of the flags is
that a law firm reading `false, false, false, false` is a classified vendor, while one reading
`null, null, null, null` is an unclassified one.

> **Four other custom fields existed and were deleted on 2026-09-04. Do not recreate them.**
>
> | id | Name | Why it went |
> |---|---|---|
> | `4` | Bitpool authenticates to vendor? | MFA scope moved to a separate register — see the scope boundary in `SKILL.md` |
> | `5` | MFA required? | As above |
> | `6` | MFA note | As above |
> | `11` | Is business critical vendor? | Created for MFA scoping by business criticality; that predicate was ruled out because criticality measures failure impact while control scope needs breach reach |
>
> **Deleting a custom field deletes its values.** AWS's `"MFA enforced"` and `"true"`, and the MFA
> note written onto GitBook at creation, are gone with the fields — not orphaned, not recoverable
> from the vendor record. Worth knowing before deleting a populated field.

---

## WIPE — cleared once, then never populated

| Field | Why |
|---|---|
| `password_requires_min_length` | Password mechanics are not maintained per vendor. Risk owner decision, 2026-09-03 |
| `password_min_length` | Same |
| `password_requires_number` | Same |
| `password_requires_symbol` | Same |
| `password_mfa_enabled` | Same — and more fundamentally, **MFA is not a vendor-register attribute at all.** See the scope boundary in `SKILL.md`. Leave it wiped; do not repurpose it |
| `is_sub_processor_active` | **`[Deprecated]` in the schema.** It also contradicted `is_sub_processor` in the data — Chargebee was `is_sub_processor: true` with `is_sub_processor_active: false` |
| `critical` | **Not readable in practice and not visible in the UI.** See the note below — this was reversed twice; the verified position is that it stays wiped |

> **`critical` — the decision, and the mistake that nearly changed it.** Verified across all 35
> current vendors 2026-09-03: **`true` on zero of them** (31 `false`, 4 `null`), **not visible in
> the Drata UI**, and **`Drata_listVendors` has no `critical` filter parameter at all.** It is a
> dead field, like `rationale` on a control.
>
> Mid-session it was moved to KEEP on the argument that it asks a genuinely different question from
> `impact_level` — *is this vendor critical to a business function* versus *how bad if it were
> breached* — and that Drata's own critical-vendor filtering reads it. **The first half is sound; the
> second half was invented.** No such filter exists. A capability was inferred from a field name and
> asserted as fact, and it nearly displaced a working solution the risk owner had already built.
>
> **Business criticality was then moved to custom field `11`, and that field was deleted the next
> day** once it became clear criticality is the wrong predicate for scoping an access control —
> criticality measures how much it hurts if a platform *fails*, while control scope needs how far a
> stolen login *reaches*. A criticality rule puts the ISP in scope and leaves the credential vault
> out. So **neither field carries business criticality**, because nothing needs it carried.
>
> Two rules survive. *Prefer a native field over a custom one where both carry the same fact* — but
> only after confirming the native field is **readable, writable and visible**, not merely present in
> the schema. And before either: **confirm something actually consumes the fact.** Both fields here
> failed that second test, in opposite ways.
>
> Related, and also corrected: the mismatch between `critical` and `impact_level` on ten vendors
> (AWS, Mongo DB, Xero, Atlassian, Microsoft, Telstra, Bitbucket, Perun, 1Password, Chargebee, all
> `MAJOR`/`CRITICAL` impact with `critical` not `true`) was reported as silently excluding those
> vendors from critical-vendor filtering. **Nothing reads the field**, so it is untidy, not harmful —
> which is a further reason to wipe rather than maintain it.

---

## IGNORE — never touched

`account_id` · `notes` · `contact_at_vendor` · `contacts_email` · `relationship_contact` ·
`integrations` · `environment_access` · `operational_impact` · `data_accessed_or_processed_list`

Three of those deserve their reason recorded, because they look useful:

- **`environment_access`** and **`operational_impact`** are **free-text strings**, not enums, and
  were `null` across the register when this contract was agreed. A free-text field describing
  access privileges drifts the moment two people fill it in differently, and neither is required
  by any control.
- **`data_accessed_or_processed_list`** is an array of **undocumented enum values**. The schema says
  "List of data accessed or processed enum type" and never says what the members are. Populating it
  means guessing at an enum, which either 400s or writes something meaningless.

---

## `confirmed` — never written, in either direction

Not keep, not wipe, not ignore-by-default: **actively excluded.**

- **Setting it stamps the read-only `confirmedAt`.** In a bulk run that marks every vendor as
  "confirmed today", which reads as a human having verified each record. It manufactures assurance
  on exactly the field an auditor treats as human attestation.
- **Clearing it destroys real history.** AWS carried a genuine `confirmedAt` of 2026-09-01, set by
  the risk owner. A wipe pass would erase that.

So it is left alone, and the skill never sends it. Risk owner decision, 2026-09-03.

---

## Write mechanics

### Partial update

`Drata_updateVendor` leaves omitted fields unchanged. **Send only what you are changing.** This is
both the safe behaviour and the sufficient one.

### Clearing a field — PARTIALLY UNVERIFIED

| Field kind | Clear with | Status |
|---|---|---|
| `category` · `status` · `type` | the string `"NONE"` | Each exposes a dedicated `NONE` const in its schema alongside the real values, which is what that const is for. **Not yet exercised** |
| everything else | explicit `null` | The schema accepts `null` on every optional field, and the tool describes *omitted* fields as unchanged — which implies an explicit `null` does something different. **Not yet exercised.** If `null` turns out to be treated as "no change", there is no MCP route to clearing that field and the wipe list becomes a UI task |

**Verify on the first wipe of a session and record the result.** Do not assume, and do not report a
field as wiped without reading it back.

### Custom fields — VERIFIED 2026-09-04

```
custom_fields=[{"id": 7, "value": "true"}, {"id": 8, "value": "false"}, ...]
```

**Address the field by `id`. Send booleans as the strings `"true"` / `"false"`, not JSON booleans** —
which matches how the read returns them, and matches the sibling tools documenting `value` as
`<str|int|null>` with no boolean type. Confirmed working on the `GitBook` create (vendor `136`): all
seven fields sent, all seven persisted and read back.

Two alternatives were prepared and **not needed**: `{"customFieldId": N, ...}` (the read shape) and
`{"name": "Is SaaS?", ...}` (name resolution, documented on the sibling tools). Try those only if
`id` ever stops working.

To clear a value, the sibling tools document `"value": null` — **untested here.**

**Always read the vendor back and confirm the value landed.** A silently-dropped custom field looks
identical to a successful write in the response.

Note also that on the read, a custom field with no value returns the object **without a `value`
key** — `{"customFieldId": 8, "name": "Is IdP?"}` — rather than `"value": null`. Test for key
presence, not for a null value.

### What the API does silently

| Behaviour | Consequence |
|---|---|
| `owner` accepts a name, email or id and resolves server-side | An unresolvable or ambiguous entry aborts the call rather than guessing — that is the safe failure |
| Only `name` is required by `Drata_createVendor` | Which is exactly how an unclassified vendor gets created. The rubric exists to stop that |
| `create:vendor` scope was **untested** as at 2026-09-03 | A 403 on the first create is the answer, and mutates nothing |
| `cost` is in **cents** | Wipe list, but read it correctly when reporting: `"12000000"` is $120,000 |
