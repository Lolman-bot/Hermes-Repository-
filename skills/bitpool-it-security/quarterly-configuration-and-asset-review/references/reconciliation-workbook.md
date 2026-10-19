# The reconciliation workbook

One CSV, one row per asset, built from every dump in the cycle folder at once. It is the last
thing the cycle produces and the only thing a human works through by hand.

## Why one workbook rather than five reconciliations

The registers do not overlap neatly, and the findings that matter live in the gaps between them.

| Finding | Needs |
|---|---|
| A device enrolled in Intune with no row on the wiki register | Intune **and** the wiki page |
| A holder with two endpoints, one of them a replacement nobody retired | The whole Intune export, grouped |
| A live endpoint belonging to a leaver | Intune **and** the directory |
| An account in no register at all | The directory **and** the Drata Sync Group |
| A resource type dropped from scope without a decision | The AWS snapshot's own `scope` block |

None of those can be produced by a register looking at itself. Reconciling each register
separately produces five reports, in five shapes, at five moments — and then a human holding
five documents, with no single place to write a decision and no way to see that the same person
appears in three of them.

There is a second reason, and it is the stronger one. **Every register's output has to be
dispositioned by a person**, and a person working one list at a time makes different calls than
a person seeing all of it. `LAPTOP-D3321J8L` flagged in the Intune list is a device to chase; the
same device sitting two rows from its wiki entry — which carries the purchase date that says
which of the pair is being retired — is a decision that takes ten seconds and is right.

> **A workbook is not a report.** Nothing in it is a conclusion. It is a worklist with a column
> for the conclusions, and the cycle is not finished until that column is filled in.

## When to build it

**After every dump is in the cycle folder. Never before.**

A workbook built from four of seven dumps is not four-sevenths of a workbook. It reports a clean
estate for the three registers it never read, and it does so in exactly the same shape as a
complete one. Nothing about the file says which registers were absent.

`build_reconciliation.py` will still build a partial workbook — a crash helps nobody, and a
partial pass over the dumps that exist is genuinely useful mid-cycle. But it prints every input it
could not find, under a heading that says those registers were **not reviewed**, and it suppresses
the checks that would produce false findings without their counterpart. Read that block before
reading the counts.

| Missing dump | What is suppressed |
|---|---|
| Intune export | `ON_REGISTER_NOT_IN_INTUNE` — without it, the whole wiki register flags |
| Wiki page | `IN_INTUNE_NOT_ON_REGISTER`, in both directions |
| Entra users | `PRIMARY_USER_DISABLED` — the Intune export has no account-state column and no variant of it does |
| Sync group members | `OUTSIDE_DRATA_SYNC_GROUP` |

## Running it

```bash
wsl -e bash -lc 'python3 "<skill>/scripts/build_reconciliation.py" \
  --cycle-folder "/mnt/c/Users/<you>/Bitpool Pty Ltd/GRC - Bitpool - Documents/General/Drata/Evidence/Asset register review/Asset register review - 2026 09" \
  -o "<same folder>/reconciliation_2026-09.csv"'
```

Windows paths become `/mnt/c/...` inside WSL. Native Windows `python`/`python3` are the broken
Microsoft Store stubs and exit without running.

`--as-of YYYY-MM-DD` overrides the date used for the vendor review-due test; it defaults to today.

### Inputs, discovered by filename pattern

Nothing is passed by hand. The script globs the cycle folder, which is why the evidence contract's
rule that **files keep the name the source gave them** matters operationally and not just as
provenance — rename an export and it stops being found.

| Pattern | Register |
|---|---|
| `aws-snapshot_*.json` | AWS |
| `azure-snapshot_*.json` | Azure |
| `github-snapshot_*.json` | GitHub |
| `bpw-hardware-asset-inventory_*.md` | Wiki (physical) |
| `DevicesWithInventory_*.csv` | Intune |
| `entra-users_*.json` | Entra |
| `entra-drata-sync-group-members_*.json` | Entra |
| `drata-vendors*.json` | Drata vendors — **all pages** |

> **The vendor glob is deliberately loose.** Drata's list endpoint pages at 50, and the second page
> is conventionally saved as `drata-vendors-page2_<date>.json`, which a strict `drata-vendors_*.json`
> pattern does not match. Reading page one alone reviews 50 of 82 vendors and reports a tidy
> register that is a third unread. The script merges every matching file by vendor id and compares
> the total against `pagination.totalCount`, printing a shortfall if one remains.

## What the workbook does not cover

**Desk equipment is in the asset register, but not in the workbook and not diffed.** Monitors,
docking stations and remote-worker kit -- roughly forty items -- live in the wiki register's *Desks,
monitors and docks*, *Remote assets* and *Spare and loan cards* tables and stay there. They are
confirmed by the **physical walk**, not by a comparison.

This is a shape problem, not a judgement that they matter less: those tables are keyed on the
**desk**, and their labels sit inside the cells, several per cell, separated by `<br>`. The parser
reads one label per row from a first column. Nothing about desk equipment changes without somebody
physically moving it, so a walk is the stronger control for this class in any case.

**`build_reconciliation.py` reports every register section it could not parse, by name and row
count, on every run.** That line is the guard -- it is what keeps "not diffed" from quietly becoming
"not checked". If a new register section appears there, decide whether it needs a parser or belongs
to the walk, and write the decision down rather than leaving the next reader to rediscover it.

## The columns

| Column | Holds |
|---|---|
| `Register` | `AWS` · `Azure` · `GitHub` · `Wiki` · `Intune` · `Entra` · `Drata` · `SCOPE` |
| `AssetID` | The stable id — ARN, Azure resource id, GitHub repo id, device name, wiki label, UPN, vendor id |
| `Name` | The human name, as the source spells it |
| `Type` | Resource type, OS class, or the wiki section the row came from |
| `Owner` | `OwnerGroup` for cloud; the recorded owner or holder for physical; the primary user for Intune; the security owner for vendors |
| `Criticality` `DataClassification` `IsPersonalData` | The governance keys, where the register carries them |
| `Status` | Lifecycle state as the source records it — `In service`, `Compliant`, `ARCHIVED`, the snapshot `unit` |
| `Flag` | A short token, **empty when the row is clean**. Several are joined with `;` |
| `FlagDetail` | The specifics — which keys are missing, which device pairs with which, why |
| `Notes` | **Always emitted empty. The human's column.** |

`AssetID` is the id, never the name. A rename must read as a change, not as a delete beside an add
— the same rule the snapshots follow.

### Flags

| Flag | Means | Settles by |
|---|---|---|
| `MISSING_REQUIRED_KEYS` | Some of the five required governance keys are set, some are not | Setting the tags, or recording why the asset is exempt |
| `NO_GOVERNANCE_TAGS` | **None** of the five is set — the register says nothing about this asset beyond that it exists | As above. Separated from the row above because "partly described" and "not described at all" are different sizes of problem |
| `IN_INTUNE_NOT_ON_REGISTER` | Enrolled, no wiki row | Adding the row. **Intune wins on existence** |
| `ON_REGISTER_NOT_IN_INTUNE` | Wiki row, no Intune record | Confirming. **Not** automatically a deletion — it may be a device never enrolled, or one retired with no evidence of disposal |
| `TWO_ENDPOINTS_SAME_HOLDER` | One person holds two laptops or desktops | The wiki register's purchase dates. See the trap below |
| `PRIMARY_USER_DISABLED` | The device's primary user holds a disabled account, or is absent from the directory entirely | HR and IT together — a live, encrypted, compliant endpoint belonging to a leaver |
| `OUTSIDE_DRATA_SYNC_GROUP` | An enabled account outside the dynamic sync group, whose `jobTitle` is not `Service Account` | Correcting the attribute that keeps it out, or recording why it is excluded |
| `VENDOR_NO_OWNER` | No security owner recorded against a live vendor | Setting one. A vendor with no owner has nobody accountable for its review |
| `VENDOR_REVIEW_DUE` | Renewal/review date is past, or never set | A review, or a date |
| `EXCLUDED_TYPE_SEEN` | A `SCOPE` row: an AWS resource type the allow-list dropped | A scope decision — see the feedback loop below |

A row with an empty `Flag` passed every check that applies to it, against a dump taken this cycle.
**That is a result, not an absence of one**, and the clean count is the coverage claim the evidence
rests on. Record it.

### Rows the script emits differently, and why

**Azure `resource` rows never flag for missing keys.** Azure tags at resource-**group** level, so
its resources are tracked for existence only. Flagging them would invent a 34-item shortfall that
does not exist and drown the 8 groups that genuinely are the Azure register.

**Entra rows are exceptions only.** Personnel are not an asset class under `A.5.9` — people are not
assets. The directory earns its place in the workbook for one reason: an account outside the Drata
Sync Group appears in **no** register anywhere, so nothing else in the cycle would surface it.
Service accounts outside the group are emitted unflagged, because the group is a dynamic group that
excludes `jobTitle = "Service Account"` by rule — that is the rule working, not a finding.

**Wiki rows with a blank label are kept.** They appear as `(unlabelled)` and are counted in a line
of their own. A blank label is a real state on that page — an asset Bitpool owns that was never
labelled — and dropping them silently shrinks the register by exactly the rows that most need
attention.

**Unparsed wiki sections are named.** The script parses the headings listed in `WIKI_SECTIONS`. Any other `##`/`###` section
carrying a labelled table is listed after the counts, with its row count, so a renamed heading shows
up as a report rather than as a workbook that quietly got smaller. Some entries in that list are
documentation tables rather than registers; some are not. Read it, do not assume.

## Working the Notes column

Open the CSV in Excel — it is written with a UTF-8 BOM so it opens cleanly, apostrophes and em
dashes intact. Sort or filter on `Flag`, work down, and write a sentence in `Notes`. Leave `Flag`
and `FlagDetail` alone: they are what the script found, and next cycle's comparison depends on them
still saying it.

Every note is one of two things, and telling them apart is the whole job.

### A disposition

Resolves this row, this cycle, and goes no further.

> `LAPTOP-D3321J8L` — wiki purchase date 05/2024, superseded by `LAPTOP-PW0NHYX4`. Wiped, unenrolled
> and disposed of 2026-09-22.

> `IT-MON-MSI-CC8Q233600877` — confirmed physically present in IT stock at the walk on 2026-09-20.

> Vendor 136 GitBook — review completed 2026-09-19, renewal date set to 2027-09-04.

Dispositions are the bulk of the column and they are finished when they are written.

### A scope change

Resolves this row **and changes what the next cycle collects**.

> `ec2:volume` — plumbing for an EC2 instance already in the register, not an asset in its own
> right. Stays excluded.

> `ecs:service` — this is a primary compute unit and should be in the register. Include it.

> `## Desks, monitors and docks` — records equipment against a desk, so the first column is a desk
> and not a label. Needs its own parse rule.

## The feedback loop — a scope change is not finished in the workbook

**This is where the cycle most often leaks.**

A note that says "exclude this type" or "include this type" is a decision about what the register
*is*. Written in the workbook and nowhere else, it survives exactly as long as anyone remembers
reading it. The cycle closes, the folder is not reopened, and next quarter the same type is
collected, flagged and dispositioned again — by someone who was not in the room when it was decided.
The register never changes. The decision evaporates and leaves a recurring finding behind it.

A scope change is only done when **all three** of these have happened:

| # | Where | What |
|---|---|---|
| 1 | The workbook | The note itself, so this cycle's evidence records the decision and who made it |
| 2 | `scripts/snapshot.py` | The `AWS_INCLUDED_TYPES` allow-list edited — add the type to include it, leave it out to exclude it. This is what makes the next cycle behave differently |
| 3 | The wiki page | Where the scope is stated in prose — the cloud resource tagging standard for a cloud type, the asset register's hardware assets page for a physical class. A reader who never opens the script has to be able to learn the same thing |

> **Step 2 without step 3 is the worse failure.** The script and the documentation now disagree, and
> the documentation is what an auditor is shown. Step 3 without step 2 is merely ineffective; step 2
> without step 3 is a page that misstates reality, which is a finding in its own right.

The same applies to a heading rename on the wiki page: the section list in `build_reconciliation.py`
has to move with it, or the next run drops that table and says so in a block nobody reads twice.

### Why `SCOPE` rows exist at all

`snapshot.py` scopes AWS with an **allow-list** of primary asset types. An allow-list cannot drop a
type by accident — a type nobody has decided on is excluded rather than silently swept into the
register with no owner, which is why it was chosen over a deny-list.

But it can drop a genuinely **new** primary type silently. A new managed data store appears, nobody
adds it to the list, and it is simply absent — and absence leaves no trace to notice. The `SCOPE`
rows are that trace: one per distinct excluded type, with the count seen, sitting in the same file
as everything else that needs a decision. An unfamiliar type there is a scope decision to make, not
noise to skim.

## Matching traps

These are not hypothetical. Each one has produced findings that looked real.

> **Curly versus straight apostrophe.** macOS names a device after its owner using U+2019 —
> `David’s MacBook Pro` — and the wiki page is typed with U+0027. Comparing raw strings reports every
> MacBook as missing from the register **and** unaccounted for in Intune at the same time: six
> phantom findings out of one character, in a shape that reads exactly like a register collapse. The
> script normalises U+2019, U+2018, U+02BC and U+00B4 to `'`, collapses whitespace and casefolds —
> and always writes the **original** strings to the CSV, because "your register says X and Intune
> says Y" is only actionable if both are shown.

> **Handset labels use two schemes.** The wiki labels a handset `IT-MOB-APP-<serial>` per the naming
> convention; Intune enrols it as `iPhone-<serial>`. Same device. Without the rewrite every
> legacy-enrolled handset is reported missing from both sides at once — the same double-phantom
> shape, and just as convincing.

> **Never decide which of two devices superseded the other from enrolment date.** A re-enrolled
> device carries a **newer** enrolment date than its own replacement. Observed 2026-09-17:
> `LAPTOP-D3321J8L`, an HP ENVY bought 05/2024 and being retired, was re-enrolled 2026-09-03 —
> against its 2026 replacement `LAPTOP-PW0NHYX4`, enrolled 2026-07-06. Ordering on enrolment names
> the **new** machine as the one to wipe. The script flags the **pair** and says so; **purchase date
> on the wiki register settles it**, and purchase date is not in Intune at all.

> **A Windows laptop and a MacBook held by one person is a two-device issue, not a supersession.**
> Only same-platform devices replace each other. The script pairs within a platform and, where the
> platforms differ, says explicitly that this is not a supersession — reporting it as one sends
> someone to wipe a machine still in daily use.

> **`accountEnabled` is written `True`/`False` with a leading capital.** A lowercase `"true"` test
> matches nothing and reports every device holder as a problem. Compare case-insensitively.

> **The Drata Sync Group is a dynamic group that excludes `jobTitle = "Service Account"`.** A service
> account outside it is the rule working. Flag only enabled accounts whose job title does not
> explain their absence.

> **Drata's `archivedAt` is not a reliable archive signal.** Observed 2026-09-17: 46 vendors carry
> `status: ARCHIVED` and only 27 of them have `archivedAt` set — older archivings never stamped the
> timestamp. Testing `archivedAt` alone flags 19 long-archived vendors as review-overdue and buries
> the ones that genuinely are. Test both. `/ask-drata` is the living reference for status flags that
> lie.

> **A check that cannot be answered says so.** If the vendor dump carries no security-owner field —
> the list endpoint does not return one; `Drata_getVendor` per vendor does — the script reports that
> `VENDOR_NO_OWNER` was **not evaluated**. It does not report that every vendor has an owner, and it
> does not flag all of them. An unevaluated check and a passed check are not the same result and must
> never print the same way.

## Every file is read as `utf-8-sig`

PowerShell redirection writes a UTF-8 BOM. So do the Intune and Entra exports. Plain `utf-8` does
not strip it: `json.load` fails on a stray `﻿` before the opening brace, and `csv.DictReader`
silently names the first column `﻿Device ID`, so every lookup of `Device ID` returns `None` and
the run produces a workbook full of blanks rather than an error. This has cost two runs.
`utf-8-sig` reads BOM and no-BOM files identically, so there is no case where it is the wrong
choice. The workbook is **written** the same way, so Excel opens it as UTF-8.

## Evidence

The workbook is retained in the cycle folder alongside the dumps it was built from, per
`references/evidence-contract.md`. Retain it **with the Notes column filled in** — an empty workbook
evidences that the dumps were taken, not that anyone reviewed them.

Quote its filename exactly in the ticket comment, with the row and flag counts, and state the clean
count. The dumps and the workbook together answer "show me the register as at 30 September, and show
me what you did about it".
