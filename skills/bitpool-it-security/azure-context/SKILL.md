---
name: azure-context
description: "Use when about to run az or an Azure sign-in fails."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, azure, entra, az-cli, wsl, security, read-only]
    category: bitpool
    related_skills: [azure-query, aws-context]
---

# azure-context

Environment-readiness checklist for Azure work against Bitpool's three Entra tenants: is `az` reachable, is there a live session, and if not, how to sign in without the traps that make an Azure login look successful when it isn't. Run it once per session before the first `az` call, not before every call.

The tenant map, sign-in procedure and diagnostic tree ship in `references/`. This is the Azure counterpart to `/aws-context`, and the two are **not** symmetric: AWS SSO sessions self-expire and are bounded by the permission set, Azure sessions are long-lived and bounded only by what you do about it. Do not carry AWS assumptions across.

## When to Use

- Proactively before your first `az` command in a session.
- When an Azure command fails with a session, `Subscription ... not found`, `No subscriptions found` or credentials error.
- Checking that an empty test tenant is still empty.
- On the slash command `/azure-context`.

Don't use for:
- Re-checking on every later `az` command once a session is confirmed live.
- Queries, Sentinel searches or the quarterly asset dump: use `/azure-query`.
- AWS sign-in: use `/aws-context`.

## Prerequisites

- **Bitpool's Windows workstation:** `az` lives only in WSL. From the Hermes `terminal` (git-bash) invoke it as `wsl -e bash -lc '...'` — single quotes keep `$HOME` for WSL to expand. Opening the sign-in link happens on the Windows side through `powershell.exe`.
- **Linux / macOS host:** run the same `az` commands directly, dropping the `wsl -e bash -lc` wrapper; keep `AZURE_CONFIG_DIR` under `$HOME` and `BROWSER=echo`, and have the user open the link in their dedicated browser profile.

## Procedure

1. **Read the reference before attempting any login.** `read_file` `references/azure-environment-readiness.md` in full — five separate things make an Azure sign-in fail silently, and four of them look identical from the outside. Done when you have read sections 1-3 and the decision tree in section 6.
2. **Check for a live session.** `wsl -e bash -lc 'export AZURE_CONFIG_DIR="$HOME/.az-bitpool"; az account show --only-show-errors -o json'`. Done when it shows an `eric-mcp@` UPN in the intended tenant (skip to step 6), or you know a login is needed.
3. **Start the OAuth sign-in in the background.** Create `$HOME/.az-bitpool`, then run the Step 2 command from the reference with `BROWSER=echo`, output redirected to `$HOME/az-login.out`, using `terminal` with `background=true`. Done when `$HOME/az-login.out` contains the `https://login.microsoftonline.com/...` line.
4. **Open the link from Windows in Edge Profile 5.** `write_file` the reference's two-line `Start-Process` snippet (section 3, Step 3) to a `.ps1` in the scratch dir and run `powershell -NoProfile -ExecutionPolicy Bypass -File <file>` — never paste the ~600-character link by hand, and never open it with Hermes browser tools. The user picks the `eric-mcp@` account for the tenant. Done when the background `az login` exits 0 (`process_manage` poll); then delete `$HOME/az-login.out`.
5. **If the browser shows `localhost refused to connect`**, stop the waiting login and use the device-code fallback in the reference; read the code from the background process output and reissue rather than nurse a stale one. Done when the login completes.
6. **Verify the identity.** `az account show` (never `az account list --all`). Done when the UPN is an `eric-mcp@` identity and the tenant is the one intended. Then proceed to `/azure-query` and don't re-run this skill this session.
7. **Diagnose failures with the decision tree** (reference section 6), working down in order. Done when the symptom maps to a row and its fix.

## Load-bearing rules

Restated here because each one produces a failure that looks like a different failure.

1. **`az` exists only in WSL on Bitpool's Windows workstation.** Azure CLI is not on the Windows PATH and the `Az` PowerShell module is not installed. Invoke it as `wsl -e bash -lc '...'`. Verified 2026-08-27: `az` 2.84.0 in WSL, absent on Windows.
2. **`AZURE_CONFIG_DIR` must be under `$HOME`, never `/tmp`.** WSL restarts between tool invocations and `/tmp` is cleared on boot, so a token cache written there is gone before the next command runs — and it presents as an expired session, a revoked token, or a propagation delay, none of which it is. Use `$HOME/.az-bitpool`.
3. **OAuth sign-in, with `BROWSER=echo`.** `az login` runs the authorization-code flow with PKCE: it prints a sign-in link and waits on `http://localhost:<port>` for the redirect, which WSL's localhost forwarding carries back from Windows (verified 2026-10-16). `BROWSER=echo` is what makes it print the link rather than open it — left unset, `az` in WSL opens it in Windows' default browser and whatever profile that last used, which is how a sign-in silently lands as the wrong identity. Never let `az` choose the browser.
4. **Open the link from Windows, in Profile 5.** `Start-Process` from PowerShell against the dedicated Edge profile works; launching the same binary from WSL only works when Edge is already running, and dies with the shell otherwise. The link is bound to the `az` process waiting for it — if that process dies, start a new login rather than reopening the old link.
5. **Device code is the fallback, not the default.** Use `az login --use-device-code` only when the redirect can't get back to WSL — the browser shows `localhost refused to connect` after sign-in. Device codes expire in about 15 minutes; a lapsed code reports `AADSTS70016 Authorization is pending` or `AADSTS70020 expired`, not "wrong password".
6. **An Entra directory role is not an Azure RBAC role.** Global Reader grants directory read and confers **nothing** on Azure resources. Resource discovery needs `Reader` assigned on the subscription's **Access control (IAM)** blade. Both are wanted; one does not substitute for the other.
7. **A PIM *eligible* assignment is dormant.** It is visible to an admin and invisible to ARM until activated, and a non-interactive identity cannot activate itself. Query identities need **active** assignments.
8. **ARM says "not found", not "forbidden".** `Subscription '<id>' not found` plus `/subscriptions` returning `count: 0` means the principal has no effective RBAC — not a wrong subscription ID. Never re-check the ID first; check the assignment.
9. **Never run `az account list --all` as a health check.** When it finds no subscriptions it **clears the cached account**, destroying the session you were diagnosing. Use `az account show`.
10. **One login per tenant.** The three tenants share no management group, so a single session cannot span them. Confirm the signed-in UPN is an `eric-mcp@` identity in the tenant you intended — the risk is authenticating as a personal admin account, not confusing one read-only identity for another.

## Pitfalls

- **Running `az login` in the foreground.** It blocks waiting for the redirect; run it with `background=true` and poll.
- **Inline PowerShell through bash.** The link is full of `&`; write the snippet to a `.ps1` file rather than nesting quotes.
- **Leaving the session open.** Nothing expires an Azure session for you — use the teardown in reference section 5 when the work is done.
- **Reading "subscription not found" as a typo.** It is an authorisation signature (rule 8).

## Verification

- `az account show` returned an `eric-mcp@` UPN in the intended tenant this session.
- `AZURE_CONFIG_DIR` points under `$HOME`, not `/tmp`.
- `az account list --all` was not run.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/azure-environment-readiness.md` | The once-per-session pre-flight check — where `az` lives, the tenant and subscription map, the OAuth sign-in procedure and its device-code fallback, the empty-tenant check that needs no RBAC, teardown, and the decision tree that separates an authentication failure from an authorisation one. |

Tenant map, subscription IDs, sign-in procedure, diagnostic tree and teardown are edited in `references/azure-environment-readiness.md`. Query technique and the asset dump belong to `/azure-query`, never here.
