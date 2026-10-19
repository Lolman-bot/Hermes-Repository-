---
name: quarterly-configuration-and-asset-review
description: "Use when running the quarterly asset or config review."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, iso27001, drata, asset-register, configuration-baseline, intune, aws, azure, github, grc]
    category: bitpool
    related_skills: [aws-context, aws-query, azure-context, azure-query, manage-drata-control, manage-drata-risks, drive-iso27001]
---

# Quarterly Configuration and Asset Review

Bitpool's quarterly cycle: asset registers reconciled against live state, and running configuration
diffed against approved hardening baselines. Satisfies ISO/IEC 27001 `A.5.9` and Drata `DCF-20`
(assets), and `A.8.9` and Drata `DCF-12` / `DCF-785` (configuration).

AWS, Azure and GitHub tags ARE the register, snapshotted each cycle so cycles can be diffed. The wiki
hardware register is the inventory; Intune reconciles against it. Drata is the vendor register. The
same Intune run files a dated configuration dump in `security-documentation-restricted`, diffed by
object id against ratified standards.

## When to Use

- `/quarterly-configuration-and-asset-review`, or the user asks to run the quarterly review.
- Working a CYB sub-task of the *Quarterly Asset Register Review*.
- Diffing a register snapshot or a configuration baseline, ratifying a hardening standard, building
  the configuration evidence pack.
- Reconciling Intune against the hardware register.

Don't use for:
- Sign-in checks: use `/aws-context` or `/azure-context`.
- A one-off estate query: use `/aws-query` or `/azure-query`.
- Treating a control: `/manage-drata-control`. Verifying a risk: `/manage-drata-risks`.
- Driving ISO 27001 work generally: `/drive-iso27001`.

## Prerequisites

- **Read `references/model-and-rules.md` first on any run where the model is not already in
  context.** Everything below is mechanics, and the mechanics make no sense without it: three kinds
  of register (cloud tags, the wiki hardware register reconciled by Intune, Drata for vendors) plus
  the configuration baselines, which are *not* a fourth register.
- Jira access to project `CYB` and read-only Drata access, both through MCP servers added to Hermes
  (`hermes mcp add ...` or `manage_connections`). Find their tools with `tool_search` if names differ.
- `/aws-context` and `/azure-context` sign-ins for the cloud dumps; collection itself is delegated
  to `/aws-query` and `/azure-query` — never duplicate their query libraries here.
- The Intune configuration exporter in `it-tools/MS/IntuneConfigExport/` needs an interactive admin
  device-code sign-in, so **the user runs it**; it places raw files, setting definitions and the
  collection manifest into the dated folder itself.
- A `security-documentation-restricted` checkout. From an installed skill copy the default does not
  resolve: set `STANDARDS_REPO`. Python scripts are pure stdlib and run through WSL (`wsl -e bash -lc
  "python3 <scripts>/..."`); `Export-GhRepoProperties.ps1` runs on the Windows side.

## Procedure

Two streams, one cycle: **asset register** (sub-tasks 1-6, `A.5.9`) and **configuration hardening**
(sub-tasks 2, 7, 8, `A.8.9`). They share one Intune collection run but keep separate dispositions,
evidence artefacts and evidence stores. Run via `terminal`; read references with `read_file`.

**Before any phase**

1. **Find the cycle's tickets** with the Atlassian MCP server's tools:
   `project = CYB AND summary ~ "Quarterly Asset Register Review"`, then its sub-tasks. Work whichever
   the user names; if none, report the status of all and ask with `clarify`. Done when the sub-task
   in scope is named.
2. **Establish which phase the cycle is in** — is every dump filed or not? That decides what can be
   worked at all; it is not a per-sub-task question. Done when the phase is stated.
3. **For any cloud register read `references/snapshot-and-diff.md` first**, then the one reference
   for that register — not all of them. Done when both are read this run.

**Phase 1 — dump**

4. **Collect, snapshot (`scripts/snapshot.py`) and diff against last cycle
   (`scripts/diff_snapshots.py`).** Every added and removed item needs a disposition; an unexplained
   addition is the finding. This diff is *within* one register, against its own previous snapshot.
   Check `scope.excluded_types_seen` — a new entry is a scope decision, not noise. Done when every
   add/remove has a disposition.
5. **File the extracts and the snapshot** in the cycle's evidence folder, and stop. **Nothing is
   reconciled across registers yet.** The Intune configuration dump is the exception: the exporter
   already placed it in the standards repo, and phase 3 owns it. Done when file names and target
   folder are given to the user.
6. **Repeat for every sub-task.** Dumps are independent; a finding in one blocks none of the others.
   The Intune device export from the Microsoft dump is what the manual register reconciles against
   (`scripts/reconcile_intune.py`, `references/intune-endpoint-reconciliation.md`). Done when every
   dump is filed.

**Phase 2 — reconcile (sub-task 6, `Reconciliation and tag review`, alone)**

7. **Confirm every dump exists, then build the workbook** with `scripts/build_reconciliation.py`
   over all of them at once. Read `references/reconciliation-workbook.md` before reading its output.
   Done when one consolidated CSV exists, built after the last dump.
8. **Disposition every flagged row** — all of it; a blank flag is not a pass. `SCOPE` rows (a type
   the allow-list excluded) and `Entra` rows (non-human identities, which Drata excludes) belong to
   no dump sub-task and are the most likely to be skipped. `Entra` rows reconcile both ways against
   `## Non-human identities` on the register's *Digital assets* page; purpose `Unrecorded` is a
   finding with an owner. Done when no flagged row is blank.
9. **Apply any scope change where scope lives**: the allow-list in `scripts/snapshot.py` *and* the
   relevant wiki page, same pass. Done when both are changed (or no scope change arose).
10. **Correct the register, then retain evidence, then the user closes the ticket**
    (`references/evidence-contract.md`). Done when the user has the file list and the order.

**Phase 3 — configuration** (independent of phase 2, gated only on the Intune dump). Read
`references/configuration-baseline.md` first. `scripts/run_config_cycle.py` (`status`, `generate`,
`diff`, `ratify`, `pack`) is the way to run it; everything it writes lands in the standards repo's
working tree for the user to commit.

11. **Run `status`, then the acceptance test, before comparing anything.** `status` checks every
    dated folder's raw files against `collection-manifest.json` hashes and exits `1` on a mismatch or
    incidents. Then: every policy's `settingCount` equals `length(settings)`, `isAssigned` is on every
    object, and manifest `incidents` are empty or each one dispositioned. The exporter, `generate` and
    `ratify` gates enforce parts of this; none replaces reading it. **A diff against a truncated
    export reports no change** — the most dangerous output available. Done when the acceptance test
    is recorded with counts.
12. **`generate` the cycle's folder, then `diff` it, and disposition every difference.** `diff`
    compares the newest folder against the one `RATIFIED` names. Cycle 1 for a platform is a
    **ratification**, run only on the named approver's word, `--dry-run` first, on a folder with both
    `collection-manifest.json` and `setting-definitions.json` (**cycle 1 ratifies 2026-09-27**; the
    2026-09-24 dump was retired 2026-09-28). `ratify` refuses anything weaker with exit `2`; the
    override flags are the approver's informed choice, never Hermes's way past a refusal. Done when
    every difference has a disposition.
13. **`pack` the cycle, then hand the zipped dated folder over for upload** as a new version of the
    Drata bucket `Endpoint Configuration Hardening`. **Check the exported scripts for embedded secrets
    before zipping.** Hermes cannot upload: the Drata evidence write scopes are not granted
    (`Drata_updateEvidenceArtifacts` returns 403). **Never hand over a pack with a high finding
    against a standard's approval.** See `references/configuration-evidence-pack.md`. Done when the
    pack exists with no high approval finding and the user has the zip path.

## Load-bearing rules

One line each; the full text and reasoning are in `references/model-and-rules.md` — read it before
arguing with any of them.

1. **The snapshot is not the register — the tags are.** Fix the tag, then re-snapshot.
2. **Never diff against a snapshot built from the same dump** — a self-comparison is always clean.
3. **Stable ids, never names** (ARN, Azure resource id, GitHub repo id, Intune object id).
4. **Every added and removed item gets a disposition.**
5. **Never reconcile before every dump is complete.**
6. **A scope change is not a disposition** — edit `scripts/snapshot.py` and the wiki page together.
7. **Record clean results with counts**; a no-change cycle gets the full write-up.
8. **Correct the register before retaining evidence; close the ticket last.**
9. **Never delete a register row because live state does not show it.** Mark it and confirm.
10. **Read-only against Drata.** Only `/manage-drata-control` and `/manage-drata-risks` write.
11. **The user saves the evidence, commits, and closes the tickets.** Never claim a file is retained.
12. **An unassigned policy is not a baseline**; list every exclusion with its reason.
13. **A configuration object is its Intune object id; its name is a setting** (`@displayName` row).
14. **A deviation goes in the ISMS exemption register**; the `Deviation` cell holds `none` or `EXM-nnn`.
15. **Diff the raw value; show the label. Never invent a label.**
16. **Never ratify on your own initiative**, nor a folder missing its manifest or definitions.
17. **Never hand-edit a dated folder or the id map.**

Never write a `cis:` citation that has not been read out of the benchmark. Never delete the Drata AWS
connection (~35 monitoring tests read from it). AWS has no configuration baseline yet (`IRT-75`, risk
`CR-14`) — do not stub one.

## Pitfalls

- **Dropping the snapshot diff because the tags look right.** A live query shows only today; the diff
  answers "what appeared since last quarter, and did anybody notice" — that question is the control.
- **Building the workbook early.** A missing dump makes every row that should have matched it flag as
  missing, indistinguishable from real findings.
- **EKS worker nodes** must be excluded on `kubernetes.io/cluster/<name>`, not a provisioner's key —
  three provisioners tag differently (`references/aws-tag-coverage.md`).
- **Quoting the old AWS scope figure.** Use 257 of 46,505 (2026-09-18), not 300 of 46,487.
- **A GitHub export run as a member** gives a meaningless coverage figure
  (`references/github-repository-properties.md`).
- **Azure case-folding** invents phantom resource groups (`references/azure-dump-and-compare.md`).
- **Treating Intune vs wiki laptop gaps as inventory defects.** Intune wins on which devices exist;
  the wiki wins on dates.
- **Staging or committing** the files phase 3 wrote. Say which files changed and stop.

## Verification

- Every sub-task worked has a disposition for every added/removed item, with counts.
- The workbook was built only after all dumps existed, and no flagged row is blank.
- Phase 3: `status` exit `0` (or each problem dispositioned), acceptance test recorded, every diff
  event dispositioned, pack has no high approval finding, `ratify` ran only on a named approver's word.
- The user was given file names, cycle folders and the correct-retain-close order; nothing was claimed
  as retained or uploaded.
- When editing the skill's scripts: `python3 -m unittest discover` in `scripts/`
  passes (run through WSL; four tests rely on POSIX `sha256sum`/permissions and fail natively on Windows).

## Reference files

Read the file itself — this table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/model-and-rules.md` | **Read first.** The model (three registers plus configuration), what this skill owns vs delegates, the full load-bearing rules, and how to edit this skill without drift. |
| `references/snapshot-and-diff.md` | **Read first for any cloud register.** Snapshot format, why it exists alongside the live tags, running both scripts, reading a diff, failure modes. |
| `references/reconciliation-workbook.md` | **Read before phase 2.** Workbook columns, inconsistency flags, the Notes column and why scope changes go elsewhere. |
| `references/evidence-contract.md` | What every sub-task leaves behind, where extracts are retained, comment shape, no-change results, order of the last three steps. Read on every run. |
| `references/aws-tag-coverage.md` | AWS required keys, ephemeral exclusion rule, untagged in-scope resources. |
| `references/azure-dump-and-compare.md` | Azure dump, resource-group tagging unit, empty-tenant confirmations, case-folding trap. |
| `references/github-repository-properties.md` | GitHub admin-only export, member-token trap, two API traps. |
| `references/intune-endpoint-reconciliation.md` | Intune half of the physical reconciliation: two exports, four traps, running the script. |
| `references/manual-registers.md` | Wiki hardware register: physical walk, desk-scoped ownership, label schemes, lifecycle statuses. |
| `references/drata-vendor-register.md` | Vendor register tidy, done by hand in the platform. |
| `references/configuration-baseline.md` | **Read before phase 3.** Normative standards, dated folders, `RATIFIED`, `run_config_cycle.py` and its refusals, ratify-then-freeze, acceptance test, object-id identity, id map, diff events, schema and `Deviation` cell, disposition rubric. |
| `references/configuration-evidence-pack.md` | Evidence pack: building it, its five mechanical properties, no-network and escaping rules, retention and Drata upload, renewal tripwire, which controls it attaches to. |

## Scripts

Run, never retyped. All Python is pure stdlib.

| File | What it does |
|---|---|
| `scripts/snapshot.py` | Normalises an AWS, Azure or GitHub dump into one snapshot shape, applying the AWS allow-list; records `scope.excluded_types_seen`. |
| `scripts/diff_snapshots.py` | Diffs two snapshots: Added / Removed / Changed / Regressed; recomputes coverage from items. `--format markdown`. |
| `scripts/build_reconciliation.py` | Builds the single consolidated reconciliation CSV from every dump at once. |
| `scripts/bpw_register_labels.py` | Extracts endpoint labels from the BPW hardware asset inventory page (handsets rewritten to their Intune form) for `reconcile_intune.py --register-labels`. |
| `scripts/Export-GhRepoProperties.ps1` | Exports repo names, descriptions and custom properties; refuses to run as an org member unless `-AllowPartial`; never persists the token. Windows side. |
| `scripts/reconcile_intune.py` | Intune "Export all data" CSV + Entra users CSV → full endpoint reconciliation. |
| `scripts/run_config_cycle.py` | **The way to run phase 3.** `status`, `generate <date>`, `diff`, `ratify <date> --approved-by "<name>"`, `pack <date>`. Paths: argument, then env (`STANDARDS_REPO`, `CONFIG_CYCLE_*`), then default. Exit `0` ok, `1` differences/integrity, `2` refusal (writes nothing). |
| `scripts/generate_baseline.py` | Raw Intune dump + `setting-definitions.json` → `baseline-rows.json` (generator `2.0`), permanent `BP-` ids from `id-map.json`; refuses a truncated dump unless `--allow-truncated`. |
| `scripts/diff_baseline.py` | Diffs two `baseline-rows.json` on `row_key`, raw value only: `RENAMED`, `REASSIGNED`, `OBJECT ADDED/REMOVED`, `CHANGED`, `ADDED`, `REMOVED`, `INTEGRITY`. |
| `scripts/build_evidence_pack.py` | Builds the self-contained, byte-reproducible `evidence-pack.html` an auditor reads. |
| `scripts/test_generate_baseline.py`, `scripts/test_diff_baseline.py`, `scripts/test_run_config_cycle.py`, `scripts/test_build_evidence_pack.py`, `scripts/fixtures/synthetic-setting-definitions.json` | Unit tests for the four configuration scripts and their synthetic fixture. |

The configuration row contract is shared by `generate_baseline.py`, `diff_baseline.py`,
`run_config_cycle.py` and `build_evidence_pack.py`; change it in all four and
`references/configuration-baseline.md` together (see `references/model-and-rules.md`).
