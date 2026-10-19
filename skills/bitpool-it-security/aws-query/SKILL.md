---
name: aws-query
description: "Use when looking up or auditing Bitpool's AWS accounts."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, aws, cli, jmespath, asset-register, tagging, security, read-only]
    category: bitpool
    related_skills: [aws-context, drive-iso27001, drata-control-insights, network-segmentation-evidence, azure-query]
---

# aws-query

Functional reference for querying Bitpool's AWS accounts with direct AWS CLI calls: example queries, the multi-account loop, JMESPath gotchas, the asset-register tag check, and how to use the AWS Knowledge MCP server to work out what to query before constructing a call. Assumes a live SSO session — if `aws sts get-caller-identity` hasn't been verified this session, run `/aws-context` first.

**Called by the compliance skills.** `/drive-iso27001` and `/drata-control-insights` delegate all AWS calls here rather than carrying their own. This skill stays framework-agnostic: it owns the account list, profiles, loop pattern and query mechanics — not compliance mappings, which live in `references/aws-evidence-map.md`.

**Direct AWS CLI, not a registered MCP server.** `awslabs.aws-api-mcp-server` was built, debugged and confirmed working, then evaluated against direct CLI and not adopted — no material capability gain for solo use, real setup fragility.

## When to Use

- Proactively whenever the user asks to look up, check, list, count or audit something in Bitpool's AWS accounts.
- Running the asset-register tag-coverage check for an account.
- When a compliance skill needs a live AWS answer.
- On the slash command `/aws-query`.

Don't use for:
- Purely conceptual AWS questions with no actual account lookup.
- Session, SSO or credential failures: use `/aws-context`.
- Producing the A.8.22 segmentation evidence pack: use `/network-segmentation-evidence`.
- Azure: use `/azure-query`.

## Prerequisites

- A live session confirmed by `/aws-context` this session.
- The **AWS Knowledge MCP server** added to Hermes (public, unauthenticated, read-only — e.g. `hermes mcp add aws-knowledge --url https://knowledge-mcp.global.api.aws`). Find its tools (`search_documentation`, `read_documentation`, `list_regions`, `get_regional_availability`) with `tool_search` if names differ. If it isn't connected, use `web_search` / `web_extract` against `docs.aws.amazon.com` instead — never guess.
- Commands run through the Hermes `terminal` tool, which is bash on every host (git-bash on Windows). The reference shows PowerShell; see step 3 for the bash form.

## Procedure

1. **Read the references.** `read_file` `references/aws-querying.md` in full before any query, plus `references/aws-asset-tag-coverage.md` for register work and `references/aws-evidence-map.md` when the question is framed as a control. Done when you know the profile(s) and loop shape you'll use.
2. **Check current AWS documentation** through the AWS Knowledge MCP server before constructing an unfamiliar call or claiming a runtime is deprecated, a flag doesn't exist, or a service isn't in a region (rule 1). Done when the subcommand and parameter names come from the docs, not memory.
3. **Run the query against an explicit `--profile`.** For an org-wide question, loop once and build one table. Bash form of the reference's loop (the account IDs and names are in `references/aws-querying.md`):
   ```bash
   for p in aws-aggregator aws-deployments aws-it aws-master aws-prod aws-test aws-cloudtrail-admin; do
     printf '%s\t%s\n' "$p" "$(aws <service> <operation> --profile "$p" --query '<jmespath>' --output json 2>&1 | tr -d '\n')"
   done
   ```
   To run a PowerShell snippet from the reference as written, `write_file` it to a `.ps1` in the scratch dir and run `powershell -NoProfile -File <file>` (Windows) or `pwsh -File <file>`. Done when every in-scope account returned a result or a classified error.
4. **For the asset-register tag check**, run `bash scripts/aws-tag-coverage.sh <profile> [region]` from this skill's folder (region defaults to `ap-southeast-2`). It is read-only and applies the Kubernetes exclusions. Done when it prints the exclusion, coverage and ownership sections.
5. **Diagnose any failure before retrying** (rule 6). Session/credential errors go back to `/aws-context`; `ParamValidation`, `AccessDenied` on a specific action and wrong parameter names are fixed here. Done when each failure is labelled environment or query-construction.
6. **Answer from what the CLI returned**, naming the accounts and profiles queried. Done when every number in the answer traces to a command run this session.

## Load-bearing rules

Restated here because each one prevents a confidently wrong answer.

1. **Check the AWS Knowledge MCP before claiming a runtime is deprecated, a flag doesn't exist, or a service isn't available in a region.** API surfaces and deprecation dates move faster than training data, and getting this wrong in a security-adjacent answer is a real cost.
2. **Always target an explicit `--profile`.** Never assume a default. **Never guess an account ID or profile name** — they're in the reference, and a wrong profile silently queries the wrong account.
3. **Loop once across accounts, don't run seven one-off commands** for an org-wide question. The account map records the Organization as last confirmed — before an org-wide claim rests on it, confirm it against `aws organizations list-accounts` from the management account.
4. **Parenthesized JMESPath boolean logic reliably fails to parse.** Filter broadly with `--query` and narrow afterwards (PowerShell `ConvertFrom-Json` + `Where-Object`, or Python on saved JSON) instead of fighting the grammar.
5. **`--output text` collapses structure** — use `--output json` and parse when the shape matters.
6. **Diagnose the failure class before retrying.** Don't retry the same failing command twice without deciding which class it is.
7. **Everything runs under `ViewOnlyAccess`** — a query that assumes broader access fails by design, not as a bug to work around.
8. **Tags are the asset register.** There is no separate list to maintain. The register check is `scripts/aws-tag-coverage.sh`; the exclusion rule and its reasoning are in `references/aws-asset-tag-coverage.md`.
9. **Exclude ephemeral Kubernetes objects by resource TYPE first, not by tag.** `eks:pod` alone is the overwhelming majority of tagged resources in the production account. A tag-only rule misses the bulk entirely. **The cluster is the asset; its pods, nodes, fleets and CSI volumes are not.**
10. **Tag keys are PascalCase**, no separators — `Owner`, `OwnerGroup`, `Criticality`, `Environment`, `WorkloadType`. Established from the estate, not from a wiki page: no tagging-convention page exists on the Bitpool Private Wiki. Azure mirrors this convention.

## Pitfalls

- **Treating an expired 12h SSO session as a query bug.** A query that worked earlier can fail later for this reason alone — back to `/aws-context`.
- **Quoting a compliance mapping from here.** Mappings live in `references/aws-evidence-map.md`; this skill never carries them in its procedure.
- **Inline PowerShell through bash.** `$` and quotes get mangled; write a `.ps1` file and run it, or use the bash form.
- **Reading a large scoped count from the tag script as a failure.** It means the register scope hasn't been narrowed yet — that narrowing is DCF-777's decision.

## Verification

- Every account and profile queried was named explicitly; none was assumed.
- Any claim about deprecation, flag existence or regional availability was checked against current AWS documentation this session.
- Each failure encountered was classified (environment vs query construction) before any retry.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/aws-evidence-map.md` | Which read-only AWS checks evidence which control domain, the relevance test, per-control call budgets, and the risk/cost/effort advisory shape. Shared by /drive-iso27001 and /drata-control-insights. |
| `references/aws-asset-tag-coverage.md` | The asset-register tag check — the exclusion rule that keeps ephemeral Kubernetes objects out, the PascalCase tag-key convention, and the open scoping decision. Paired with `scripts/aws-tag-coverage.sh`. |
| `references/aws-querying.md` | How to query Bitpool's AWS accounts efficiently — the AWS Knowledge MCP, example queries, the account map and multi-account loop, JMESPath gotchas, and how to tell an environment failure from a query failure. |
| `scripts/aws-tag-coverage.sh` | Read-only per-account tag-coverage report (bash; runs in the Hermes terminal on all hosts). |

Account list, loop pattern, example queries and gotchas are edited in `references/aws-querying.md`. The register exclusion rule, tag convention and scoping decision go in `references/aws-asset-tag-coverage.md`, with the runnable check in `scripts/`. Compliance mappings go in `references/aws-evidence-map.md` — byte-identical copies ship in other skills, so edit every copy.
