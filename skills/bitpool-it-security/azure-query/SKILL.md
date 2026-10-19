---
name: azure-query
description: "Use when querying Bitpool Azure, Sentinel or asset dumps."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, azure, sentinel, kql, defender, asset-register, security, read-only]
    category: bitpool
    related_skills: [azure-context, aws-query, bitpool-docs, quarterly-configuration-and-asset-review]
---

# azure-query

Functional reference for querying Bitpool's Azure estate with the Azure CLI, searching its Sentinel workspace with KQL (which carries the Defender incidents and alerts too), and producing the quarterly Azure asset dump behind the Azure Asset Register on the Bitpool Private Wiki. Assumes a live session — if `az account show` hasn't been verified this session, run `/azure-context` first.

**Azure is deliberately not managed the way AWS is.** AWS is a live register derived from resource tags. Azure is a **quarterly point-in-time dump** into a GitBook page, because the Azure estate carries almost no tags and is small enough to enumerate exhaustively. Do not carry the AWS tag-first model across — the reasoning is in `references/azure-asset-register.md`.

**Everything runs read-only.** The identity holds Azure RBAC `Reader` on one subscription and Entra Global Reader across three tenants. A query that assumes write access fails by design, not as a bug.

## When to Use

- Proactively when the user asks to look up, check, list, count, audit or dump something in Bitpool's Azure tenants.
- Searching Sentinel or Defender logs, incidents or alerts; triaging an alert; tracing activity to the app behind it.
- Running the quarterly Azure asset register review, the resource-group tagging compare-and-tag cycle, or the no-RBAC empty-tenant check.
- On the slash command `/azure-query`.

Don't use for:
- Purely conceptual Azure questions with no tenant lookup.
- Session, sign-in or "subscription not found" failures: use `/azure-context`.
- AWS work: use `/aws-query`.

## Prerequisites

- A live session confirmed by `/azure-context` this session.
- On Bitpool's Windows workstation `az` runs only in WSL: from the Hermes `terminal` (git-bash) invoke `wsl -e bash -lc 'export AZURE_CONFIG_DIR="$HOME/.az-bitpool"; az <command>'`. On a Linux/macOS host run `az` directly with the same `AZURE_CONFIG_DIR`.

## Procedure

1. **Read the reference for the job.** `read_file` in full: `references/azure-querying.md` for estate queries, `references/azure-asset-register.md` for the quarterly cycle, `references/sentinel-log-querying.md` for KQL. Skimming for the line you expect is how a flag gets missed. Done when you know the commands and output paths you'll use.
2. **Collect to files under `$HOME`, then analyse** (rule 2). Use the collection block in `references/azure-querying.md` (or the KQL-to-file invocation in `references/sentinel-log-querying.md`); write analysis code as a script file through a quoted heredoc, not an inline `python3 -c`. Done when each `.json` is non-empty and each `.err` is empty — a non-zero `.err` with a zero-size `.json` goes back to `/azure-context` section 6.
3. **Enumerate, don't summarise.** Report what the JSON holds (rule 9), with counts recomputed this run, never restated from the references. Done when every number in the answer traces to a file written this run.
4. **For Sentinel incidents**, deduplicate to the latest row per incident first (rule 11), and trace any unfamiliar IP to its app before calling it an attacker (rule 12). Done when counts come from the `arg_max` view and each suspicious source has an app attribution or an open question for the user.
5. **For the quarterly register**, follow the compare-and-tag procedure and wiki locations in `references/azure-asset-register.md`; check empty tenants with the no-RBAC check (rule 7). Done when the dump, comparison and empty-tenant results are in hand, ready for `/bitpool-docs` to publish.

## Load-bearing rules

Restated here because each one prevents a confidently wrong answer.

1. **`az` is WSL-only on Bitpool's Windows workstation.** Invoke as `wsl -e bash -lc '...'`. There is no Windows fallback.
2. **Write `az` output to a file under `$HOME`, then parse it.** Inline `az ... | python3 -c` breaks on nested quoting, and `/tmp` does not survive between WSL invocations.
3. **`az resource list` is the register.** It returns id, name, type, location, resourceGroup and tags for every taggable resource in the subscription — 43 resources across 14 populated resource groups as at 2026-08-27. Small enough to enumerate in full, which is what makes the point-in-time model defensible.
4. **Resource groups are the tagging unit, not resources.** 14 populated groups against 43 resources, and the group names are already meaningful. Tag ownership at group level.
5. **Azure tag coverage is effectively zero** — 1 of 43 resources carried any tag as at 2026-08-27, and that tag was `hidden-title`, an Azure-internal display field. Never report Azure tags as a working ownership source without re-checking.
6. **Drata's Azure connection is not a source of truth.** It reported **one** asset of 43, last updated 2026-01-30 and untouched since. Do not reconcile the register against it.
7. **Confirming an empty tenant needs no RBAC.** `--allow-no-subscriptions` plus an ARM `/subscriptions` read returning `count: 0` is the whole check, and Entra Global Reader is sufficient.
8. **`az account list --all` clears the cached account** when it finds no subscriptions. Never use it as a health check.
9. **Report what the estate holds, not what you expect it to hold.** The 2026-08-27 dump surfaced a code-signing Key Vault, five Sentinel incident-response playbooks and a break-glass login monitor that no register had recorded. Enumerate; don't summarise from memory.
10. **Sentinel already holds the Defender incidents and alerts.** Search them with `az monitor log-analytics query` against `Microsoft-Sentinel-LAWS` — plain `Reader` is enough. Graph's Defender endpoints refuse the Azure CLI by design, and direct access is held by decision, so never propose it as the fix for a failed call.
11. **Count incidents on their latest row.** `SecurityIncident` holds one row per update. Run `summarize arg_max(TimeGenerated, *) by IncidentNumber` first, or counts and statuses come out wrong.
12. **Find the app behind an unfamiliar IP before treating it as an attacker.** Trace the activity through `MicrosoftGraphActivityLogs` and `az ad sp show` first, then ask the person to confirm it was them. The Microsoft 365 MCP connector used by AI assistants ("M365 MCP Server for Claude") trips impossible-travel alerts from Google Cloud — its signature is in the Sentinel reference.

## Pitfalls

- **Unquoted heredocs for Python.** `$` and backticks get expanded by the shell; quote the delimiter (`<<"PYEOF"`).
- **Forgetting `AZURE_CONFIG_DIR` on one invocation.** Each `wsl -e bash -lc` is a fresh shell and inherits nothing.
- **Matching a benign signature on IP alone.** Attackers rent Google Cloud too; confirm with the Graph-attribution query.
- **Writing the register pages from here.** Wiki pages in `security-documentation` are written via `/bitpool-docs`, which owns that repo's taxonomy, frontmatter and index tooling. Never write them from this skill.
- **Applying tags with the query identity.** It is `Reader`; the tag updates in the quarterly cycle are made by someone with write access, not by this skill.

## Verification

- Every count reported was computed from files written this run.
- Incident counts and statuses come from the latest row per `IncidentNumber`.
- No write command (`az ... create/update/delete`, tag writes) was run by the agent.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/azure-querying.md` | How to query the estate — the collection commands, the JSON-to-markdown analysis pipeline, tag-coverage analysis, role-assignment review, and the quoting traps that break inline parsing. |
| `references/azure-asset-register.md` | The quarterly Azure asset register cycle — why Azure is a point-in-time dump rather than a live register, the resource-group-scoped tagging standard, the compare-and-tag procedure, the empty-tenant check, and where the register and its explainer live on the wiki. |
| `references/sentinel-log-querying.md` | Searching the Sentinel workspace — what it holds (the Defender incidents and alerts included), the KQL-to-file invocation, a tested query library for incidents, alerts, evidence, sign-ins and IP ranges, tracing activity to the app behind it, why direct Defender access is held, known benign alert signatures, and the join traps. |

Collection commands, the analysis pipeline and query gotchas are edited in `references/azure-querying.md`; the quarterly cycle, tagging standard and register locations in `references/azure-asset-register.md`; Sentinel KQL, investigation patterns and benign signatures in `references/sentinel-log-querying.md`. Session and sign-in belong to `/azure-context`, never here.
