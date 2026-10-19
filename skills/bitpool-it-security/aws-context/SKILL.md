---
name: aws-context
description: "Use when about to run AWS CLI or an AWS session fails."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, aws, sso, iam-identity-center, security, read-only]
    category: bitpool
    related_skills: [aws-query, azure-context, network-segmentation-evidence]
---

# aws-context

Environment-readiness checklist for AWS work against Bitpool's AWS Organization (IAM Identity Center SSO, no static keys). Run it once per session before the first AWS CLI call, not before every call.

The commands ship with this skill in `references/`. For query technique, see `/aws-query` — this skill only covers "is the environment ready", not "how do I ask for X". Full architecture, setup procedure and troubleshooting live in `it-documentation/aws/aws-mcp-server-readonly-access.md`; this skill is the quick pre-flight check, not a replacement for that page.

## When to Use

- Proactively before your first `aws` CLI command in a session.
- Whenever an AWS command fails with a session or credentials error (`The specified sso-session does not exist`, `ForbiddenException`, expired token, `aws` not recognised).
- On the slash command `/aws-context`.

Don't use for:
- Re-checking before every later AWS command once a session is confirmed live — stop checking.
- Constructing or debugging an actual query: use `/aws-query`.
- Azure sign-in: use `/azure-context` (the two are not symmetric).

## Prerequisites

- AWS CLI v2 (cross-platform). Commands run through the Hermes `terminal` tool, which is bash on every host — git-bash on Windows. The reference shows PowerShell forms; the bash equivalents are given in the Procedure.
- `~/.aws/config` carrying the one `bitpool` `sso-session` and its 7 named profiles (setup is in the `it-documentation` page above).

## Procedure

1. **Read the reference.** `read_file` `references/aws-environment-readiness.md` in full. Skimming for the line you expect is how a flag gets missed. Done when you have read the sign-in warning and the identity section.
2. **Check the CLI resolves.** `command -v aws` (PowerShell: `Get-Command aws`). On Windows, if it doesn't resolve after a recent install, a GUI-launched process may not have inherited the new `PATH` — try the full path `"/c/Program Files/Amazon/AWSCLIV2/aws.exe"` (PowerShell: `C:\Program Files\Amazon\AWSCLIV2\aws.exe`) before concluding it isn't installed. Install only if genuinely absent (`winget install Amazon.AWSCLI` on Windows). Done when `aws --version` prints v2.
3. **Check for a live session.** `aws sts get-caller-identity --profile aws-it`. Interpret the result with the table in the reference. Done when it succeeds, or you know which failure it is.
4. **If a login is needed, apply rule 1 first**, then `aws sso login --sso-session bitpool`. The user completes the browser step in the dedicated browser profile. Done when the login command returns successfully.
5. **Confirm the identity.** Re-run `aws sts get-caller-identity --profile aws-it` and check the ARN's trailing UPN is the dedicated identity. If it is a personal admin account: stop, `aws sso logout`, fix the browser profile, sign in again. Done when the UPN is the dedicated identity — then proceed to `/aws-query` and don't re-run this skill this session.

## Load-bearing rules

Restated here because getting these wrong authenticates as the wrong person, or misstates what the identity can do.

1. **Never sign in from a browser profile that has a personal admin or M365 session active.** The dedicated identity shares an Entra tenant with real admin accounts, so the SSO handshake can complete as the **wrong identity with no visible error**. Use a separate, dedicated browser profile.
2. **After any sign-in, confirm the identity** — `aws sts get-caller-identity --profile aws-it` and check the trailing UPN is the dedicated identity. If it isn't, stop: `aws sso logout`, fix the browser profile, sign in again.
3. **This identity is `ViewOnlyAccess`** — list/describe/get-metadata only. It cannot read resource data: no `S3:GetObject`, no `SecretsManager:GetSecretValue`. This is **stricter** than AWS's `ReadOnlyAccess`; don't conflate the two when describing what it can do.
4. **A freshly installed `aws` may not resolve** in a GUI-launched process — invoke the full path rather than assuming it isn't installed.
5. **Run this once per session**, not per command.

## Pitfalls

- **Driving the SSO sign-in with Hermes browser tools.** The agent's browser is not the dedicated profile, and credentials are never typed by the agent. Let `aws sso login` hand the page to the user's dedicated browser profile (forcing the Edge profile via `BROWSER` is covered in the `it-documentation` page) and let the user complete it.
- **Trusting a successful login without step 5.** Silent wrong-identity sign-in is Microsoft's persistent sign-in behaviour, not a bug — the only signal is the UPN.
- **Describing the identity as "read-only" in the `ReadOnlyAccess` sense.** It cannot read data content; an access-denied on a data read is by design.
- **Re-running the checks every command.** Wasteful, and it suggests a problem where there isn't one.

## Verification

- `aws sts get-caller-identity --profile aws-it` succeeded this session.
- The returned ARN's trailing UPN is the dedicated sign-in identity, not a personal admin account.
- Any statement about what the identity can do says `ViewOnlyAccess`, not `ReadOnlyAccess`.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/aws-environment-readiness.md` | The once-per-session pre-flight check before running AWS CLI commands against Bitpool's AWS Organization — CLI tooling, SSO session, and the browser-profile trap that can silently authenticate as the wrong identity. |

Commands, sign-in procedure and permission notes are edited in `references/aws-environment-readiness.md`. The full architecture and setup stay authoritative in `it-documentation/aws/aws-mcp-server-readonly-access.md`.
