---
name: ask-drata
description: "Use when checking Drata MCP quirks, scopes or write rules."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, drata, mcp, compliance, iso27001, security]
    category: bitpool
    related_skills: [manage-drata-control, manage-drata-risks, manage-drata-vendors, create-drata-test, drata-control-insights, drive-iso27001, bitpool-writing-standard]
---

# Ask Drata

A living reference for operational quirks of the Drata MCP connection — things that are true about *how the connection behaves*, confirmed by hitting them live. Not things about any one control or compliance workflow, and not a workflow itself.

The gotchas ship with this skill in `references/`. Nothing here is fetched — the wiki page this skill used to read is retired, and the skills repo is the source of truth. This skill also owns the Drata **write model** and the **write policy by skill** — the table every other Drata skill defers to.

## When to Use

- The user types `/ask-drata`.
- **Proactively**, whenever a Drata MCP call returns an empty or unexpected result, or before concluding a Drata record "doesn't exist".
- Before any Drata write, to check the verb's traps and whether the calling skill may write at all.
- A 403, a scope question, a filter that returns zero, or a status flag that looks contradictory.
- Questions about Drata product behaviour (the MCP carries no documentation — rule 15).

Don't use for:
- Designing a Custom Test: `/create-drata-test`.
- A single-control status visual: `/drata-control-insights`.
- Program-wide ISO 27001 driving: `/drive-iso27001`.
- Raising DevSecOps tickets: `/create-devsecops-ticket`.
This skill holds connection-level notes only, not those workflows.

## Prerequisites

- **The Drata MCP server added to Hermes** (`hermes mcp add …` or the `manage_connections` tool). This skill names tools by the server's own names (`Drata_searchControls`, `Drata_updateRisk`, …). In Hermes they carry an `mcp_<server>_` prefix — find the live names with `tool_search` (e.g. `drata controls`, `drata risks`) and never conclude a tool is absent from a name mismatch.

## Procedure

1. **Apply the load-bearing rules below first** — they change what you conclude from a result and need no fetch. Done when the result in hand has been checked against rules 1–7 and 10–14.
2. **Read the detail** with `read_file` when you need the exact rule text, or the confirmed calls, dates and responses behind a gotcha: `references/load-bearing-rules.md` (full rules), `references/drata-mcp-gotchas.md` (numbered gotchas, scope matrix, writable fields). Read the whole file you reach for — skimming for the line you expect is how a threshold or a flag gets missed. Done when every claim you report traces to a file read this run.
3. **Before any write, check the write-policy table below** for the calling skill. No row granting the verb = no write. Done when the verb is in that skill's May-call list and its gate is satisfied.
4. **When a new quirk is confirmed live, add it** to `references/drata-mcp-gotchas.md` (date, exact call, exact response) and the rule it implies to `references/load-bearing-rules.md` plus a one-line summary below. Done when both files and this summary agree.

## Load-bearing rules

One line each; the full text with its evidence is `references/load-bearing-rules.md` (same numbers — other skills cite them).

1. **Never conclude a record doesn't exist from an empty search-mode result.** `query` mode across the `Drata_search*` tools is broken account-wide: silent `[]` on controls/policies, hard 500 on monitoring tests/risks. Default to list/filter mode.
2. **Passing `query` silently discards your filters.** Omit it entirely; never pass it "just in case".
3. **Follow list-mode pagination to `cursor: null`.** Results sort by internal `id`, not DCF code. For one known control, seek with `cursor` = base64 of `id|<id + 1>`, `size: 1`, and check the returned `code`. Completeness is only within a filter set.
4. **Server-side `name` filters match a PREFIX, not a substring.** Match on the first word, or list unfiltered and filter client-side. The augmented filters (`code_or_name`, `control_code`) are contains-matched.
5. **Prefer a tool's own non-AI fuzzy param over `query`** — `Drata_searchRisks(q:)`, `Drata_listPersonnel(q:)`, `Drata_listEvidence(name:)`, `Drata_listPolicies(name:)`.
6. **`test_source: CUSTOM` finds user-authored tests**; `check_type: CUSTOM` is something else.
7. **A missing-scope 403 will not yield to different parameters.** Quote the scope; adding it is a Bitpool admin action under **Settings → MCP OAuth Configuration**. Re-probe rather than trusting any list.
8. **Drata is writable — only for specific verbs.** ✅ exercised: `Drata_createRisk`, `Drata_updateRisk`, `Drata_updateControl`. `Drata_updateEvidenceArtifacts` 403s (`update:evidence` not granted). Everything else is unverified. Never conclude from memory that a verb is absent or available; and authorised ≠ permitted — the write-policy table decides.
9. **Every write verb tested has a trap that fails silently or rejects late:** `description` ≤768 chars on `createRisk` (rejects); no `riskId` param (Drata assigns); `control_ids` are numeric ids, not DCF codes; non-admin `owners`/`reviewers` silently dropped; `updateRisk` cannot clear a date; `updateControl` relation fields **replace**; treatment fields dropped unless `treatment_plan` ≠ `UNTREATED`. Read every returned record back.
10. **Control status flags are unreliable gap signals.** `hasEvidence` and `Drata_listEvidence` count different populations — empty list means "no bucket", never "no evidence". Evidence age is `versions[].createdAt`, never `updatedAt`. `hasTicket`/`ticket_status` are integration provenance — resolve tickets in Jira (`CSIP`, `ICR`, `IRT`). `isReady: false` beside complete flags → check control approval in the Drata UI.
11. **`code_or_name` is a SUBSTRING match** — `"5.3"` returns eleven requirements. Read `name` on every item.
12. **The risk register is fully available**, despite a stale Private Wiki page claiming HTTP 402. `approvedAt: null` on every policy is unresolved — assert neither reading.
13. **Tool exposure tells you nothing about scope.** Probe `update:*` with an impossible identifier (403 = not granted, 404 = granted). Never probe `create:*` or `delete:*`.
14. **Bitpool's framework tag is `ISO270012022`**, not `ISO27001` (which returns zero silently).
15. **Drata documentation is not in the MCP.** Use `https://help.drata.com/llms.txt` and append `.md` to article URLs (`web_extract`); never fetch the plain HTML article.
16. **Text for a Security Drata field is drafted under `/bitpool-writing-standard`** (section `bitpool-general`), with the durability check under every staged text. If it isn't installed, ask once per chat (`clarify`) whether to proceed — exact wording in the full rule.

## Drata write policy by skill

**This table is the authority on which skill may write to Drata. It lives here and nowhere else.**

The reason it has to be central: **OAuth scope is account-level.** There is no per-skill token and no
per-skill scope. Every skill in a session is handed the *same* granted verbs — `/drive-iso27001` can
physically call `Drata_createRisk` exactly as easily as `/manage-drata-control` can. The MCP will not
stop it.

So a skill being "read-only" is a **policy this repo enforces, not a capability the connection
withholds**. It holds only because the skill says so and Hermes obeys it. State it that way to the
user; never tell them a skill *cannot* write when it simply *must not*.

> **Never express a read-only posture as an enumerated list of forbidden verbs.** A list is only
> complete on the day it is written, and it fails silently the day a scope is granted — which has
> already happened here. `/drive-iso27001` named four verbs, all of them control and evidence verbs,
> because it was written before `create:risk` and `update:risk` existed. Those two were therefore
> never forbidden by its own rule. **Default-deny is the only durable form:** no Drata write verb,
> named or unnamed, existing or future.

| Skill | Drata posture | May call | Gate |
|---|---|---|---|
| `/manage-drata-control` | **WRITE** | `Drata_createRisk`, `Drata_updateRisk`, `Drata_updateControl` | Approval block rendered in full, explicit user yes, per write. Never sets `reviewers` — its drata-fields reference §7. Staged text follows rule 16, with the durability check in the approval block |
| `/manage-drata-risks` | **WRITE, risks only** | `Drata_updateRisk` | Same approval gate. Does not create risks — register-wide work is delegated to `/manage-drata-control audit`. Never sets `reviewers`. Staged text follows rule 16 |
| `/manage-drata-vendors` | **WRITE, vendors only** | `Drata_createVendor`, `Drata_updateVendor` | Approval happens in a per-vendor Markdown staging note the risk owner reads and annotates — one vendor per approval, never a batch, never in the chat. Staged text follows rule 16, with the durability check in the staging note. Security reviews and vendor documents are read-only — outside its May-call list, whatever verbs the tool list offers |
| `/drive-iso27001` | **READ-ONLY** | No write verb, named or unnamed | Absolute. Reports gaps; writes to Jira and the worklog only. Drata edits are a human action in the UI. Evidence text it drafts for the upload follows rule 16 |
| `/drata-control-insights` | **READ-ONLY** | No write verb | Absolute |
| `/create-drata-test` | **READ-ONLY** | No write verb | Absolute. Authors test JSON for a human to paste into Test Builder; the test name and description it drafts follow rule 16 |
| `/describe-dcf-jira-ticket` | **READ-ONLY** | No write verb | Absolute. Writes the Jira `description` field only |
| `/create-devsecops-ticket` | **READ-ONLY** | No write verb | Absolute |
| `/network-segmentation-evidence` | **READ-ONLY** | No write verb | Absolute. Generates the evidence pack; a person uploads it |
| `/quarterly-configuration-and-asset-review` | **READ-ONLY** | No write verb | Absolute. Lists vendor and evidence changes for a person to make |
| `/ask-drata` (this skill) | **READ-ONLY** | No write verb | Absolute. Probing a scope is permitted **only** against an impossible identifier (rule 13), which mutates nothing. Never probe `create:*` or `delete:*` |

**Read-only is about calls, not drafts.** A read-only skill that drafts text for a person to paste
into a Security Drata field — a Custom Test description, an evidence description — is under rule 16
exactly as a writing skill is.

**Evidence upload is a human action for every skill on this list.** No row grants an evidence verb,
so default-deny forbids them all. As far as has been checked it is also a capability limit, not only
policy: `update:evidence` 403s (probed 2026-08-25, re-probed 2026-08-28), and the configuration read
on 2026-08-25 enabled only `read:evidence`. Of the evidence verbs that have appeared in the tool list
since (observed 2026-09-24), `Drata_createEvidence` sits behind `create:evidence` and
`Drata_deleteEvidence` behind `delete:evidence` — neither granted in that configuration, and neither
ever probed (rule 13). Only `Drata_updateEvidence`'s gate is genuinely open: whether `update:evidence`
gates it is unprobed, and an impossible `evidence_id` probe settles it (rule 13). Until that is
settled in the scope matrix, never tell anyone evidence text *cannot* be written through the
connection. **The upload is human; the text is not exempt** — the bucket `name`, `description` and
`implementation_guidance` a skill drafts for the person uploading follow rule 16.

Changing a skill's posture is a decision that gets recorded **in this table first**, then reflected
as a one-line pointer in that skill. A skill must never be the place where its own write permission
is defined — that is how two skills end up disagreeing about what is allowed.

## Pitfalls

- **Reading an empty result as absence** — rules 1–4 and 11 are each a different way that happens.
- **Treating the tool list as a scope manifest** — an exposed tool can 403; a missing tool may just be named differently in Hermes (`tool_search` first).
- **Trusting what you sent instead of what came back** — owners drop, relations replace, treatment fields vanish (rule 9).
- **Stating a dated count as a baseline.** Every count in the references is what a call returned on a date.
- **Telling the user a read-only skill *cannot* write.** It *must not*; the connection would let it.

## Verification

- Every conclusion about absence was reached in list mode, paginated or seeked, with the filter set named.
- Every write was permitted by the policy table, approved per its gate, and its returned record quoted.
- Any new quirk is dated, with the exact call and response, in `references/drata-mcp-gotchas.md`.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/load-bearing-rules.md` | Full text of rules 1–16 with the confirmed calls, dates and responses behind each. |
| `references/drata-mcp-gotchas.md` | A living reference of confirmed, operational quirks of the Drata MCP connection — unreliable AI search mode, list-mode pagination that is easy to under-read, filter distinctions, the live-probed scope matrix, why the tool list is not a scope manifest, the writable free-text fields with their caps and traps, the Drata Help Centre access path, custom fields and formulas (defined in the Drata UI, populated by id), and the confirmed write model. |
| `references/confirmed-working-baseline.md` | The positive baseline of calls confirmed working (2026-08-20, extended 2026-08-24) — if one fails, the problem is new. |
| `references/maintaining-ask-drata.md` | Where this skill fits against the other Drata skills, and the rules for editing it (what belongs here, dating, placeholders). |
