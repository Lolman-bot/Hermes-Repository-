# The model, ownership and full rules — Quarterly Configuration and Asset Review

The parts of the skill that must not drift, kept verbatim from the original skill. `SKILL.md` carries
the route and a one-line form of each rule; this file carries the reasoning. Read the model before
anything else on a first run.

Satisfies ISO/IEC 27001 `A.5.9` and Drata `DCF-20` (assets), and `A.8.9` and Drata `DCF-12` /
`DCF-785` (configuration).

## Two streams, one cycle

| Stream | The question | Annex A | Sub-tasks |
|---|---|---|---|
| **Asset register** | Do we know what we own? | `A.5.9` | 1-6 |
| **Configuration hardening** | Is it configured as approved? | `A.8.9` | 2, 7, 8 |

They share a cycle because they share a collection step: **one Intune run yields both** the device
export the asset register reconciles against and the policy export the configuration baseline is
diffed against. One authentication, one calendar.

**What stays separate is the disposition and the evidence artefact**, because they attach to
different controls with different renewal clocks and answer different questions. One artefact
covering both gives an auditor a worse answer than two artefacts each doing one job.

**And the evidence store.** The asset extracts go to the GRC cycle folder. The configuration dump is
placed by the exporter itself into a dated folder in `security-documentation-restricted`, which is
the retention store. Each cycle that whole folder, evidence pack included, is zipped and uploaded to
Drata — see *4 — Configuration* below.

## The model

Read this before anything else. Everything below is mechanics, and the mechanics make no sense
without it.

**Three kinds of register, three different jobs.**

### 1 — Cloud: AWS, Azure, GitHub

**The tags and properties ARE the register.** There is no separate list of cloud assets to
maintain. A resource that exists carries its own ownership metadata; a resource that is deleted
takes its row with it.

**And each one is also snapshotted to a file every cycle.** Not instead of the tags — *as well
as*. The snapshot exists for one reason: so this cycle can be **diffed against the last one**, and
anything added or removed without being accounted for shows up.

That second half is the part that is easy to drop, and dropping it removes the whole point of a
quarterly cadence. A live tag query only ever shows **today**. It cannot answer *"what appeared
since June, and did anybody notice"* — and that question is the control. The tags give an accurate
register; the diff gives assurance that nothing changed behind your back.

**AWS tracks primary assets only.** Bitpool decision, 2026-09-17: an **allow-list of 13 resource
types** — compute, storage, data stores, code artefacts and secrets. Measured on the day the
decision was made, that was 300 of 46,487 tagged. **Re-measured 2026-09-18 across all accounts and
every permitted region, and with EKS worker nodes correctly excluded: 257 of 46,505.** Quote the
later figure; the earlier one counted worker nodes and one region.

Two separate reasons to drop something, and collapsing them into one loses the second:

- **Ephemeral** — pods, spot requests, **EKS worker nodes**, CSI volume churn. A row with a
  lifetime measured in hours supports no accountability. **45,401** of the 46,505.
- **Not primary** — snapshots and AMIs (copies of something already in the register), parameter
  and subnet groups (settings, not assets), plumbing, load balancers, API Gateway, SQS, SNS,
  VPCs, certificates, Cognito user pools. **847** more.

**EKS worker nodes are matched on `kubernetes.io/cluster/<name>`, not on a provisioner's own key.**
Bitpool runs three node provisioners and each tags differently; excluding one of them left the other
two churning in the register — 46 removals and 20 additions over a 17-hour gap, all phantom. Cluster
membership is the property worth testing, because a fourth provisioner would tag differently again.
Details and the verification in `references/aws-tag-coverage.md`.

Backup copies are the ones worth naming explicitly: RDS and ElastiCache snapshots turn over on a
schedule, so including them opens every quarterly diff with dozens of additions and removals that
mean nothing — and buries the one that does.

An allow-list is the safer shape, because a type nobody has decided on stays out of the register
rather than being swept in with no owner. Its one cost is that a genuinely new primary type would
be dropped unnoticed, so `snapshot.py` records **every excluded type it saw** under
`scope.excluded_types_seen`. **A new entry there is a scope decision to make, not noise to skim.**

### 2 — Physical: the wiki hardware register, reconciled by Intune

**The wiki register IS the inventory — for everything except laptops and desktops.** Nothing else
records that a monitor, a handset, a printer or an access card exists. There is no live system
behind it, so a wrong row can sit there for years looking exactly like a right one.

**Laptops and desktops are the exception, and it runs the other way: Intune is their register of
record.** The wiki's Windows and MacBook tables *support* it by holding purchase dates Intune has no
field for. Where the two disagree about which devices exist, **Intune wins**; on dates, the wiki
wins. A gap between them is not an inventory defect.

**The Intune export exists to reconcile against it** — to find endpoints lost, or present and not
accounted for. That is one job, not two. Intune is not a separate register running its own
independent cycle; it is the live counterpart that gives the manual register something to be
checked against.

### 3 — Vendors: Drata

**Drata is the register of record for SaaS vendors and third parties.** That is the whole of its
inventory role. Tidied **by hand, in the platform** — this skill is read-only against Drata.

Drata's *device* list is not a register: it is personnel-scoped and includes contractor-owned
equipment Bitpool does not own, so it answers "what accesses our data", not "what do we own", and
`A.5.9` asks the second. Its cloud resource list is not cited either. **Do not delete the Drata
AWS connection** — roughly 35 enabled monitoring tests read from it.

### 4 — Configuration: the approved baselines

**Not a fourth register.** The first three answer *what do we own*; this one answers *is what we own
configured the way we approved*. Same estate, different question.

**A standard is normative; a dump is descriptive.** A standard states what the configuration ought
to be — approved, versioned, changed only by deliberate act. A dump states what it is, right now.

Conflating them is the defect this stream exists to fix. Until 2026-09-18 Bitpool's only baselines
were descriptive dumps of current Intune settings, with no approval, no version, no authority per
setting and no review cadence. **A snapshot regenerated each cycle cannot be deviated from, because
it IS the configuration.**

**Ratify once, then freeze.** Bitpool decision, 2026-09-18, refined 2026-09-25: the first corrected
dump of a platform is ratified as the approved baseline. From then on every difference must be
authorised, rationalised or recorded as a gap. A later dump reaches a standard only through another
ratification — a deliberate, reviewed act with a named approver, which bumps the version — and
**never as an automatic step of a cycle**. That is what makes a frozen snapshot normative, and it is a
genuinely different thing from regenerating it.

The `Authority` on rows established this way reads `bitpool:ratified <date>` — not a benchmark
section. **Never write a `cis:` citation that has not been read out of the benchmark.** A fabricated
citation is worse than an honest internal one, because it survives review.

**The accepted residual, which must be stated and not implied:** nobody verified that the day-one
configuration was itself correct against an external benchmark. The recurring review mitigates that;
it does not remove it.

**The standards and the dumps both live in `security-documentation-restricted/configuration-hardening/`.**
Changed 2026-09-24, by user decision; until then the dumps were kept out of that repo. The standards
are the three `hardening-standard-*.md` pages. The dumps sit under `dumps/YYYY-MM-DD/`, one folder per
cycle — the raw Graph files byte for byte, a `collection-manifest.json` recording when, by whom and
with which hashes, and beside them the rows, the cycle record `README.md` and the diff report
generated from them. `dumps/RATIFIED` names the folder the standards were ratified from. **The repo
is the retention store, and Drata receives a copy of each cycle's folder**: the whole dated folder,
pack included, zipped into one upload (user decision, 2026-09-28; until then only the pack went).
The pack is what an auditor reads. It prints the sha256 of every input it read, and the files beside
it in the zip let anyone recompute those hashes.

Physical separation used to be the guarantee that a commit to a standard is a human act rather than
a regenerated file. **That guarantee is now mechanical**: generated content on a standard page sits
only between `<!-- GENERATED:START -->` and `<!-- GENERATED:END -->`, and only a ratification with a
named approver writes there. Generating rows, diffing and building the pack never touch a standard.

**Identity is the Intune object id, and the name is a setting.** Each object carries one synthetic
`@displayName` row, so a rename is one visible change and no other row moves. **Values are shown
human-readable and diffed raw** — labels resolved from the Settings Catalog definitions are for
display only, so a Microsoft relabel never creates a difference.

**AWS is not in this stream yet.** No AWS configuration baseline exists; it is tracked on `IRT-75`
under risk `CR-14`. Do not stub one — an empty placeholder is exactly what let the previous cloud
hardening gap persist unnoticed.


## What this skill owns, and what it delegates

| | |
|---|---|
| **Delegated — collection** | `/aws-query` and `/azure-query` own the account list, query mechanics and the AWS exclusion rule. `/aws-context` and `/azure-context` own sign-in. **Never duplicate their query libraries here** — two copies drift, and the stale one is indistinguishable from the live one |
| **Delegated — Intune configuration collection** | The exporter in `it-tools/MS/IntuneConfigExport/`. It needs an interactive admin device-code sign-in, so **the user runs it**; it places the raw files, the setting definitions and the collection manifest into the dated folder itself |
| **This skill** | The snapshot format, the diff engine, the consolidated reconciliation workbook, the Intune reconciliation, the configuration baseline generator, differ, cycle wrapper and evidence pack, the evidence contract, and the disposition of whatever the diffs and the workbook find |

Anything that would overflow a skill — heavy dependencies, a scheduled runtime, a real test
matrix — belongs in `security-tools`. Nothing here overflows: every Python script is pure stdlib
over JSON.

## The load-bearing rules (full text)

1. **The snapshot is not the register — the tags are.** Never correct an estate by editing a
   snapshot. Fix the tag, then re-snapshot.
2. **Never diff against a snapshot built from the same dump.** It will always come back clean, and
   a clean diff from a self-comparison is the most convincing wrong answer this cycle can produce.
   `run_config_cycle.py diff` refuses a baseline folder equal to the current one for this reason.
3. **Stable ids, never names.** A renamed resource must read as *changed*, not as a delete plus an
   add. `snapshot.py` keys on ARN, Azure resource id and numeric GitHub repository id; the
   configuration baseline keys on the Intune object id.
4. **Every added and removed item gets a disposition.** "3 resources appeared" is not a result;
   "3 appeared, all Terraform-managed and tagged, accounted for" is.
5. **Never reconcile before every dump is complete.** The workbook flags inconsistencies by
   comparing the registers against one another, so a register that has not been dumped makes
   everything that should have matched a row in it flag as missing — and a flag caused by a missing
   dump is indistinguishable from a real finding. Building it early does not save the later build;
   it buys a page of artefacts to disposition. Check every dump is present, then build.
6. **A scope change is not a disposition, and the workbook cannot hold it.** *"Retired and wiped"*
   closes a row. *"This resource type should not be in the register at all"* does not — closing
   that means editing the allow-list in `scripts/snapshot.py` **and** the relevant wiki page, in
   the same pass. **A scope change recorded only in the workbook is lost the moment the next cycle
   regenerates it**, and gets rediscovered and re-argued next quarter by someone who does not know
   it was settled.
7. **Record the clean results, with counts.** "28 of 28 enrolled devices have a primary user" is
   the evidence the check ran. A no-change cycle gets the same full write-up as one with findings
   — "no change" alone is indistinguishable from nobody having looked.
8. **Correct the register before retaining evidence, and close the ticket last.** A closed ticket
   over a register that still disagrees with live state asserts a check passed when it did not.
9. **Never delete a register row because live state does not show it.** It may be an asset never
   enrolled, or one retired with no evidence of disposal. Mark it and confirm — deleting destroys
   the only record Bitpool ever owned the thing.
10. **Read-only against Drata.** The write verbs exist on the connection and it will not refuse
    them, because OAuth scope is account-level. Only `/manage-drata-control` and
    `/manage-drata-risks` may use them. List what needs changing; let a human change it.
11. **The user saves the evidence and closes the tickets.** Hermes cannot write to SharePoint, and
    the user handles their own git and ticket transitions. Name the files and the cycle folder they
    belong in, then stop. Never claim a file has been retained. The phase 3 scripts do write into
    the standards repo's working tree — that is not retention until the user commits it, so say
    which files changed and stop short of staging or committing.
12. **An unassigned policy enforces nothing, so it is not a baseline.** Scope the configuration
    diff to assigned objects only, and list every exclusion with its reason rather than dropping it
    silently — an exclusion nobody can see reads as an oversight.
13. **A configuration object is its Intune object id; its name is a setting.** Every row keys on
    `row_key = collection|object_id|setting_id`, lowercased — no name and no platform in it — and
    every object carries one synthetic `@displayName` row whose value is its display name. A rename
    is therefore one `RENAMED` event on one row, and no other row's identity moves. **Superseded
    2026-09-25:** the rule used to key on `(collection, @odata.type or platform, normalised name)`,
    because the name is ambiguous in this tenant — `deviceConfigurations` holds *"Default Device
    Restrictions Configuration"* twice, once macOS and once iOS, and two typo spellings are live,
    `Defualt` and `Defult`. Those facts still stand; under an object-id key they no longer matter
    for identity, and they are the reason a name can never be the key.
14. **A deviation from a standard goes in the ISMS exemption register, not in the standard.** Every
    Bitpool exemption belongs in the one register at
    `security-documentation-restricted/isms-exemptions/exemption-register.md` so they can be
    reviewed together once a year, and **its rationale lives there only.** A standard row's
    `Deviation` cell holds `none` or an `EXM-nnn` reference into that register — nothing else. It is
    the one cell between the generated markers a human writes, and `ratify` carries an existing
    `EXM-nnn` forward by BP id while that id still names the same object and setting; one it cannot
    carry is printed as a `WARNING`, never dropped silently. Where the honest answer is a
    consciously retained exposure rather than an exemption, the instrument is the Drata risk
    register — not either document.
15. **Diff the raw value; show the label.** `required_value` is the raw Graph value and, with row
    presence, the only thing the differ compares. `setting_name` and `display_value` are resolved
    from the Settings Catalog definitions for readers only, so a Microsoft relabel never creates a
    difference. Where a label cannot be resolved, show the raw value — **never invent a label**.
16. **Never ratify on your own initiative.** `ratify` writes a named person's approval into a
    normative document and repoints `RATIFIED`. Run it only when that person has said to, with their
    name, after showing them `--dry-run`. A cycle that re-ratifies automatically has turned the
    standard back into a snapshot. **Nor ratify a folder without `collection-manifest.json` and
    `setting-definitions.json`.** The wrapper refuses one (exit `2`) unless `--allow-missing-manifest`
    and `--allow-raw-labels` are passed; those overrides record an approver's informed choice, and
    are never Hermes's way past a refusal.
17. **Never hand-edit a dated folder or the id map.** The raw files are evidence, hashed in two
    places; the generated files are rewritten byte-identically on every run; `id-map.json` ids are
    permanent — reused, never renumbered, a vanished key's number reserved forever. A v1 map is
    refused, not migrated: delete it and regenerate.

## Editing this skill

**The model at the top is the part that must not drift.** If a change contradicts it, change the
model deliberately and say so, rather than letting a reference file disagree with it quietly.

**The configuration row contract is shared by four scripts** — `generate_baseline.py`,
`diff_baseline.py`, `run_config_cycle.py` and `build_evidence_pack.py` — and specified in
`references/configuration-baseline.md`. Change `row_key`, the name row or the id-map schema in all of
them and that reference together, and bump the generator's major version whenever a key changes
shape: the differ refuses to compare across major versions precisely so that a reshaped key cannot
pass as a wall of changes.

Collection technique belongs to `/aws-query` and `/azure-query` — never copy it here. The snapshot
shape is shared by all three cloud registers, so change it in `references/snapshot-and-diff.md` and
`scripts/snapshot.py` together. **Scope lives in two places** — the allow-list in
`scripts/snapshot.py` and the wiki page documenting it — so a scope change applied to only one of
them is undone by the next cycle. The decisions about *which* register owns an asset class live on
the wiki hub and in `security-documentation/compliance/asset-library.md`; if a register changes
hands, change the wiki first, then this skill in the same pass.
