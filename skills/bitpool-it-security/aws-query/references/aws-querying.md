# AWS Querying

Functional reference for actually querying Bitpool's AWS accounts. Assumes a live SSO session
already exists — if `aws sts get-caller-identity` hasn't been verified this session, do
AWS Environment Readiness (see the `/aws-context` skill) first.

This page is about **how to ask AWS the right question efficiently**, not environment setup.

> **Note**
> **Called by the compliance skills.** `/drive-iso27001` and `/drata-control-insights` delegate all
> AWS calls here rather than carrying their own. If the question is framed as an ISO 27001 / Drata
> control, the map of control domain → which read-only checks evidence it lives in the
> [AWS Evidence Map](aws-evidence-map.md). This page stays framework-agnostic: it owns the account
> list, profiles, loop pattern and query mechanics — not compliance mappings.


**Direct AWS CLI, not a registered MCP server.** `awslabs.aws-api-mcp-server` was built, debugged
and confirmed working, then evaluated against direct CLI and not adopted — no material capability
gain for solo use, real setup fragility. Use the CLI directly.

## Use the AWS Knowledge MCP to figure out what and how to query

Before constructing a call involving anything that shifts over time, or that you haven't queried
before, check the **AWS Knowledge MCP** rather than guessing from training data or trial-and-error
against the real account. It's a public, unauthenticated, read-only documentation connection — no
Bitpool data, always safe to use.

| Tool | Use it for |
|---|---|
| `search_documentation` | Keyword search returning verbatim page chunks — usually enough on its own. Find the exact CLI subcommand or parameter name, current API behaviour, or a deprecation table before writing the call. |
| `read_documentation` | Full page fetch, only when the search chunks are missing something — e.g. a truncated enumeration like a full runtime-deprecation table. |
| `list_regions` / `get_regional_availability` | Whether a service or feature is available in a given region, before assuming a call will work there. |

> **Warning**
> Before telling the user a Lambda runtime is "deprecated", a CLI flag "doesn't exist", or a service
> "isn't available in ap-southeast-2" — check current AWS documentation first. Getting this wrong in
> a security-adjacent answer is a real cost, and API surfaces and deprecation dates move faster than
> training data.


## Example queries — single account

Always target a specific profile. Never assume a default.

```powershell
$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"

# S3 bucket count and names
& $aws s3api list-buckets --profile aws-it --query "length(Buckets)"
& $aws s3api list-buckets --profile aws-it --query "Buckets[].Name" --output table

# Lambda functions and runtimes (check deprecation status against AWS Knowledge MCP)
& $aws lambda list-functions --profile aws-it --query "Functions[].[FunctionName,Runtime,LastModified]" --output table

# VPCs
& $aws ec2 describe-vpcs --profile aws-it --query "Vpcs[].[VpcId,CidrBlock,IsDefault]" --output table

# Security groups open to 0.0.0.0/0 (list broadly, then filter — see the JMESPath note below)
& $aws ec2 describe-security-groups --profile aws-it --query "SecurityGroups[].{GroupId:GroupId,GroupName:GroupName,Open:IpPermissions[?contains(IpRanges[].CidrIp, '0.0.0.0/0')].{From:FromPort,To:ToPort}}" --output json
```

## Querying across multiple accounts

Every account in Bitpool's AWS Organization has its own SSO profile, and the map below is this
skill's working configuration for them. For "check this across all our accounts" questions, don't
run one-off commands per account — loop once and build a single table. The map records the
Organization as it was last confirmed, not a count to quote: before an org-wide claim rests on it,
confirm it still matches `aws organizations list-accounts` run from the management account.

```powershell
$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$accounts = @(
  @{ Name = "Aggregator account";       Id = "343980059340"; Profile = "aws-aggregator" },
  @{ Name = "Bitpool Deployments";      Id = "231614141364"; Profile = "aws-deployments" },
  @{ Name = "Bitpool IT";               Id = "119257711996"; Profile = "aws-it" },
  @{ Name = "Bitpool Master";           Id = "749502997173"; Profile = "aws-master" },
  @{ Name = "Bitpool Prod";             Id = "603214229740"; Profile = "aws-prod" },
  @{ Name = "Bitpool Test";             Id = "118218616624"; Profile = "aws-test" },
  @{ Name = "CloudTrail administrator"; Id = "909176970895"; Profile = "aws-cloudtrail-admin" }
)

$results = foreach ($a in $accounts) {
  $value = & $aws <service> <operation> --profile $a.Profile --query "<jmespath>" --output text 2>&1
  [PSCustomObject]@{ Account = $a.Name; AccountId = $a.Id; Result = $value }
}
$results | Format-Table -AutoSize
```

Swap the `<service> <operation> --query "<jmespath>"` line for whatever the question needs — the
loop shape stays the same regardless. If the account list needs re-confirming, it's documented in
`it-documentation/aws/aws-mcp-server-readonly-access.md`.

## `--query` (JMESPath) gotchas

- **Parenthesized boolean logic reliably fails to parse.** `[?(FromPort<=22 && ToPort>=22) || (...)]`
  throws a `ParamValidation` error, and not a helpful one. Prefer simpler filter functions
  (`contains(...)`, single comparisons), or filter broadly with `--query` and narrow further in
  PowerShell (`ConvertFrom-Json` + `Where-Object`) rather than fighting JMESPath's grammar.
- **`--output text` collapses structure.** Fine for a single scalar — a count, a single ID — risky
  for anything with nested lists where you need to know which value came from where. Use
  `--output json` and parse in PowerShell when the shape matters.
- **Use the full absolute path to `aws.exe`.** More reliable than the bare `aws` command in any
  tool or session where `PATH` may not have refreshed since install.

## Diagnose which kind of failure it is first

Not every failure means "fix the query". Two classes need two different responses.

### Environment / session failures

Go back to AWS Environment Readiness (see the `/aws-context` skill) — don't just retry.

- `The specified sso-session does not exist`
- `ForbiddenException` / expired or invalid token — the 12h SSO session can expire mid-conversation,
  so a query that worked earlier can fail later for this reason alone
- `aws` not recognized, or a command that resolved a moment ago suddenly doesn't
- Results that don't match the expected account — wrong identity signed in

### Query-construction failures

Fix these here; the readiness check won't help.

- `ParamValidation` / JMESPath parse errors — see the gotchas above
- `AccessDeniedException` on a specific action — not a session problem, it's `ViewOnlyAccess`
  correctly blocking a call that needed broader permissions
- Wrong parameter or subcommand name — check the AWS Knowledge MCP rather than guessing again

> **Warning**
> Don't retry the same failing command more than once without first identifying which category it
> falls into.


## Remember

Every call runs under `ViewOnlyAccess` — list/describe/get-metadata only, no reading of actual
resource data content. A query that assumes broader access (reading an S3 object's contents, or a
secret's value) will fail with an access-denied error **by design**, not as a bug to work around.
