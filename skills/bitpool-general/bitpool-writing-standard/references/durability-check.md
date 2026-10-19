# The durability check

Two uses: **before** durable text is approved, as a visible block in the approval prompt; and
**after**, as an audit sweep over records that already exist. Same flags, same dispositions.

**Both apply only inside a registered target** — the target gate in `SKILL.md` Step 1 runs first.
Text headed anywhere else gets no check, and none is shown.

---

## §1 The check in an approval block

Show **one** check per approval block, directly under the staged text, as a markdown table with a
`Field` column — never one table per field, and never a fenced code block. The person approving is
confirming the text is true; the check shows them which spans could stop being true, what was done
about each, and what was removed, so a specific that belonged can be restored.

*Example — placeholders, not real values:*

**Durability check**

| Field | Span | Why flagged | Disposition |
|---|---|---|---|
| `treatmentDetails` | `time synchronisation was verified on <date> by <method> …; the result is the evidence on the linked controls` | Date | Kept — anchored fact; the compensating-control claim rests on it, and it is the latest |
| `treatmentDetails` | `across every account in the AWS Organization` | Universal claim | Kept — population; checked against the scope record, no account excluded for this claim |
| `treatmentDetails` | `on the cadence the <policy> sets` | Pointer | Kept — pointer verified against the version in force |
| all | `DCF`, risk and clause codes; `IRT-n` with its recovery query; policy and register titles; Drata, Jira and the AWS Organization as pointers | Handles | Kept — durable handles |

**Removed before staging** — `the <n> AWS accounts` → *"every account in the AWS Organization"*;
`owner <person>` → Drata `owners`; `Corrected <date> …` → dated ICR comment, staged alongside.

When nothing is flagged, one line replaces the table: **Durability check — no current-state values,
people, copied facts or record history.**

Rules for the block:

- **Flag the draft, dispose of each flag, then re-run on the final wording.** The table lists what
  remains in the final text; *Removed before staging* lists what the draft had and where it went.
- **Rows only for judgement calls** — each kept anchored fact, boundary, home value, verified
  pointer, published contact and named product. Collapse every handle, structured value and
  system-of-record name into one row.
- **Budget.** More than about eight judgement rows, or a single field running past a page, means the
  text is carrying a log: shorten it and re-run before staging, rather than asking the reviewer to
  audit forty spans.
- **On a long page or a policy draft, check the text you changed**, not the whole document. Values
  the page is the declared home of, per its profile, take one row — *"hostnames and commands —
  kept, this page is their home per its profile"*.
- **Every flag gets a disposition.** An unexplained *kept* is a skipped check.
- **No approval block in the chat** — a skill that writes then reports, approval in a staging file,
  a draft offered for pasting, a handoff: `SKILL.md` Step 4 says where the check goes.
- **Snapshots are not checked** — comments, minutes and evidence packs are meant to be specific.
  Only a hand-typed value inside a *generator* is checked, because it is durable text shipped in a
  snapshot.

---

## §2 What to flag

Flag every span in durable text that matches one of these. The list is deliberately wider than the
defects, because most flags are kept and the point is that each one is looked at.

| Pattern | Examples | Usually |
|---|---|---|
| A number attached to things, in digits or words | *"seven accounts"*, *"24 of 25"*, *"one business day"*, *"three photos"* — not list or item numbering | Generalise to the criterion or population |
| A date, month, quarter, year or cadence word | *"31 July 2025"*, *"September cycle"*, *"end Q3"*, *"annually"*, *"quarterly"* | Keep only if an anchored fact needed here, or a value this record is the home of; otherwise point at the home |
| Relative time | *"ago"*, *"last month"*, *"recently"*, *"for eight months"* | Replace with the date, or drop |
| Status or progress | *pending, currently, at present, not yet, to date, so far, at this time, as of, newly, still, now, completed, underway, begun, provisioned, rolled out, phased, remaining* | State the standing position; planned measures as outcome + condition + IRT pointer; progress lives in the ticket |
| A person's name or a job title | Any name — check against Drata personnel if unsure; any title | Replace a name with the role; a title only where this record assigns the accountability, exactly as the RACI tables name it |
| An email address or mailbox | *"…@bitpool.com"* | Name the channel and the document that publishes it; the address appears only inside that document |
| A place | a suburb, street address, building, floor or room; *"one office in …"* | Name the site's role (*"the office"*) and point at the record that holds the address |
| An account, host or network identifier | 12-digit AWS account IDs, profile names, hostnames, IPs and CIDRs, resource IDs, bucket names | Describe the population or the role of the account |
| A product, vendor, organisation, plan or version | a security product, an AMI, a professional body, a contracted service, *"v1.1"*, a licence tier | Name the capability or category; keep the name only where it is a pointer, the subject, a relied-on provider, or named by a control or policy as the requirement |
| A configuration value | Retention periods, session lifetimes, thresholds, ports | Point at the system or baseline that holds it — unless this record is its home |
| A policy-owned parameter | SLAs, cadences, scales, tiers, required lists | Cite the policy by name, once the version in force is confirmed to set it |
| An exclusive, negative or universal claim | *only, sole, no, none, never, all, every, does not* — *"Bitpool does not store personal data"*, *"only one door"* | Keep when it states a criterion or requirement with its source, checked against the true boundary; generalise when it reports an observation — state the requirement and point at where exceptions are recorded |
| A pointer phrase | *"the period the X Policy sets"*, *"as recorded in the Y Register"* | Confirm the version in force holds it (core rule 1, `references/core-rules.md`) |
| A positional reference into another record | *"CR-01 item 9"*, *"row 42"* | Name the item by what it is, unless that record declares its numbering permanent |
| A control code in risk prose | *"treated under DCF-50"* | Cut if the control is in `control_ids`; keep only for a deliberately unlinked control that owns part of the risk |
| Another record's content | Another risk's items, another control's description, a ticket's status or due date, an evidence-bucket or monitoring-test name | Reference it by code or key, and stop |
| Record history or session voice | *"Corrected …"*, *"supersedes"*, *"previously read"*, *"likelihood raised from…"*, *"another session"*, *"Claude proposed"*, *"Hermes proposed"* | Move to a dated comment or the changelog, created in the same change |

---

## §3 Dispositions

| Disposition | When | Say |
|---|---|---|
| **Kept — handle** | A `DCF` code, risk ID, clause number, IRT key with its recovery query, a policy, page or register title, a system of record named as a pointer | Which handle |
| **Kept — structured** | Only in a structured field, never in prose | The field |
| **Kept — home** | This record is the system of record for the value — the policy that sets the parameter, an inventory register row, a runbook or configuration page its profile declares its home, a vendor record's own contact fields | Which record's job it is (for a docs page, that it carries `last_reviewed`) |
| **Kept — pointer verified** | A pointer to the home of a value | The home, and that the version in force holds the value |
| **Kept — population** | A universal claim describing the whole of a population (*"every account in the AWS Organization"*) | That it was checked against the scope record, and that nothing is excluded for this claim |
| **Kept — boundary** | A scope statement where the boundary is the decision, stated as a criterion | The criterion, and the policy or register that sets it |
| **Kept — anchored fact** | A past-tense event this record's claim rests on, with date, method (or deciding role and forum) and pointer, and no counts, lists, settings or progress inside it | Which claim rests on it, that it is the latest, and — if relied on as present assurance — what re-performs it |
| **Kept — published contact** | Only inside the document that publishes it, or a procedure whose reader must act on it | Which document, and that this text is that document |
| **Kept — subject** | The vendor, product or object the record is about, or a provider whose assurance is relied on | Why the name is the subject, not current state |
| **Generalised** | The value has a home elsewhere, or will change — to the true boundary, never past it | The new wording, quoted |
| **Moved** | The value belongs in a snapshot or a structured field | Where it went |
| **Cut** | It adds nothing the record needs — often history, status or session voice | Nothing more |

---

## §4 False positives — do not generalise these

- `DCF-xxx`, `CR-xx`, `SD-xx`, clause numbers like `6.1.3(f)`, `A.8.22`, ISO/IEC standard numbers —
  **except** a `DCF` code in a risk's text that is already in that risk's `control_ids`: flag it as
  another record's content, and cut it.
- `IRT-n` in a risk's `treatmentDetails` when it is the tracking pointer and carries its recovery
  query.
- The date inside an anchored fact, a document's own identification date, or a `Date constraint:`
  quote.
- Policy, page and register titles, including a product name inside such a title. Drata
  evidence-bucket and monitoring-test names are **not** titles — Drata owns and renames them. A
  product or system named to say where something runs is not a title either.
- A system of record named as a pointer, or the vendor or product a record is about.
- The name of the record the text is **about**, as its system titles it — the control a CSIP
  explainer describes, the vendor a vendor record describes. Kept as the subject. Anywhere else, a
  control is named by its `DCF` code, not its title.
- A value in the record that is its home — the timeout in the policy that sets it, the asset in the
  inventory register row, the hostname in the runbook its profile declares its home.
- Stock Drata text — leave it, including Drata's integration title format on CSIP tickets.
- Numbers that are part of a requirement Bitpool quotes verbatim, with its source named.
- Requirement-level identifiers stated as what must be true — the resource type, rule name, port or
  setting a control requires — rather than as an observation of the estate.
- A verbatim quote of another record, anchored with its source and the date it was read.
- An operating system's own feature named as the mechanism a control requires (full-disk encryption
  through the platform's built-in feature) — it is the requirement, not this year's product choice.

---

## §5 The audit sweep — checking records that already exist

A skill with an audit mode runs the same flags over existing durable fields and reports the result;
it never rewrites a record without the approval block its own workflow requires.

1. **Read the durable fields in full** — risk `description` and `treatmentDetails`, evidence `name`
   and `description` for each control in scope, control descriptions Bitpool has customised (any that
   name Bitpool, its platforms, registers, policies, people or risk IDs, or carry Bitpool's spelling),
   vendor free text, IRT `summary` and `description`. Use structured list mode and follow pagination to the
   end, per `/ask-drata`.
2. **Flag spans** per §2. Also flag the two things spans miss: a **long entry** (length is the
   earliest warning — the entries that drift most are the longest) and **status text that has
   already flipped** (a *"not yet scheduled"* line on a ticket that now has a date).
3. **Check what can be checked.** Where a flagged value has a live home, read it: an account count
   against the AWS Organization, a quoted document date against the version in force of the
   controlled document (not a draft awaiting promotion), a named owner against the structured field,
   a pointer against the version in force. A value that
   already disagrees with its home is a **confirmed** defect; one that still agrees is a **latent**
   defect. Report both, separately.
4. **Report a summary table first** — one row per record: its length, confirmed defects and latent
   defects, with the longest and confirmed-defect records first. Draft rewrites, each with its
   durability check, only for the records the user picks, a few at a time.
5. **Report, do not write**, unless the skill's own workflow authorises a batched fix after one
   approval block.
