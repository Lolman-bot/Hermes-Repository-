# AWS Environment Readiness

Environment-readiness checklist for AWS work against Bitpool's AWS Organization — IAM Identity
Center SSO, no static keys.

Run this **once per session** before the first AWS CLI call, not before every call. For query
technique and AWS Knowledge MCP usage see AWS Querying (see the `/aws-query` skill) — this page only covers
*is the environment ready*, not *how do I ask for X*.

> **Note**
> Full architecture, setup procedure and troubleshooting live in
> `it-documentation/aws/aws-mcp-server-readonly-access.md`. This is the quick pre-flight check, not
> a replacement for that page.


## Check the CLI tooling is installed

```powershell
Get-Command aws -ErrorAction SilentlyContinue
```

If nothing resolves, don't assume a fresh terminal will pick up a new install immediately — a
GUI-launched process (including this one) doesn't always inherit a just-updated `PATH`. If `aws`
was recently installed and still doesn't resolve, locate the binary directly rather than retrying
the bare command:

```powershell
Get-ChildItem "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
```

and invoke that full path instead. If AWS CLI v2 genuinely isn't installed:

```powershell
winget install Amazon.AWSCLI
```

## Check for a current SSO session

```powershell
aws sts get-caller-identity --profile aws-it
```

| Result | Meaning |
|---|---|
| **Succeeds** | Session is live — proceed to AWS Querying (see the `/aws-query` skill) |
| `The specified sso-session does not exist` | `~/.aws/config` isn't set up on this machine yet. See "Configure the local AWS CLI" in `it-documentation/aws/aws-mcp-server-readonly-access.md` for the exact `sso-session` + profile blocks — one `bitpool` session, 7 named profiles |
| `ForbiddenException` / expired token | Needs a fresh login |

```bash
aws sso login --sso-session bitpool
```

## Before signing in — read this first

> **Important**
> **The dedicated sign-in identity (e.g. `aws-mcp-<name>@bitpool.com`) shares an Entra tenant with
> real admin accounts.** Signing in from a browser profile that's already silently signed in with a
> personal admin/M365 session can complete the SSO handshake as the **wrong identity, with no
> visible error**.
>
> This is silent by design — Microsoft's persistent sign-in behaviour — not a bug. Which is exactly
> why it's dangerous here.


- Sign in from a **separate, dedicated browser profile** — never the profile with your own
  admin/M365 session active.
- To force `aws sso login` to use a specific Edge profile, set `$env:BROWSER` to the
  profile-directory-qualified `msedge.exe` path before running the login command. The exact
  command, and how to find a profile's directory name via `edge://version`, are under "Browser
  sign-in profile" in `it-documentation/aws/aws-mcp-server-readonly-access.md`.
- **After any sign-in**, confirm the identity in the response UPN matches the dedicated identity,
  before trusting anything that follows:

```bash
aws sts get-caller-identity --profile aws-it
```

If the returned ARN's trailing UPN is your own admin account instead of the dedicated identity,
**stop** — `aws sso logout`, fix the browser profile, and sign in again.

## What this identity can actually do

Bitpool's permission set (`aws-mcp-access`) uses AWS's **`ViewOnlyAccess`** managed policy —
list/describe/get-metadata only. It cannot read actual resource data: no `S3:GetObject`, no
`SecretsManager:GetSecretValue`.

> **Warning**
> This is stricter than AWS's separate `ReadOnlyAccess` policy, which *can* read data content.
> Don't conflate the two when describing what this identity can do. A query that assumes broader
> access will fail with an access-denied error, not silently succeed.
