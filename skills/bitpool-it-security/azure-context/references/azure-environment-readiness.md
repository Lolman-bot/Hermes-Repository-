# Azure environment readiness — the once-per-session pre-flight

Everything here was verified live on 2026-08-27 against Bitpool's tenants, except the OAuth sign-in
in section 3, which replaced device code and was verified end to end on 2026-10-16 against
`bitpool.com`. Where a fact was established by observation rather than documentation, it says so.

Run this once per session before the first `az` call. Do not re-run it per command.

---

## 1 — Where the tooling lives

| Tool | State on this machine |
|---|---|
| Azure CLI (`az`) | **WSL only**, version 2.84.0. Invoke as `wsl -e bash -lc '...'` |
| `az` on Windows PATH | **Absent** |
| `Az` PowerShell module | **Not installed** |

```bash
wsl -e bash -lc 'az version'
```

There is no Windows-side fallback. Anything Azure runs through WSL.

---

## 2 — The tenant and subscription map

Three separate Entra tenants. They share no management group, so **one login per tenant** and no
cross-tenant visibility.

| Tenant domain | Tenant ID | Azure subscription | Identity |
|---|---|---|---|
| `bitpool.com` | `820737d5-aa31-442a-8140-9a22577361dc` | `3e13a29f-90c5-40a8-abb9-8d25f5911d82` — "Bitpool - Default" | `eric-mcp@bitpool.com` |
| `bp-it-testing.com` | `51c92ffb-2754-4e4d-9d9c-82f8c0b60928` | **none** | `eric-mcp@bp-it-testing.com` |
| `BitpoolExternal.onmicrosoft.com` | `f74c44ba-fbfd-438e-81da-2f2ef123ed8c` | **none** | `eric-mcp@BitpoolExternal.onmicrosoft.com` |

`eric-mcp@bitpool.com` object ID: `efd6176d-bb81-4832-9845-a618ee7b9d8d`.

**Only `bitpool.com` holds Azure infrastructure.** The other two are Entra-only test tenants used
mainly for identity testing, and are expected to stay empty. `bp-it-testing.com` carries an M365
commercial subscription for a couple of Exchange licences — that is a licence subscription, not an
Azure resource subscription, and ARM will never return it.

### Permissions model — two separate systems

| System | Role held | Grants | Assigned at |
|---|---|---|---|
| Microsoft Entra | **Global Reader** — all three tenants | Directory read: users, groups, app registrations, Conditional Access, sign-in config | Entra ID, Roles and administrators |
| Azure RBAC | **Reader** — `bitpool.com` subscription only | Subscriptions, resource groups, resources, tags | Subscription, Access control (IAM) |

Global Reader confers **nothing** on Azure resources. Both roles are wanted; neither substitutes
for the other. This distinction cost an entire debugging session on 2026-08-27 — see section 6.

---

## 3 — Sign-in procedure

### Step 1 — set a persistent config dir

```bash
wsl -e bash -lc 'mkdir -p "$HOME/.az-bitpool"'
```

**Never use `/tmp`.** WSL restarts between tool invocations and `/tmp` is cleared on boot, so a
token cache written there is gone before the next command. It presents as an expired session — it
is not. `$HOME` is on the persistent ext4 volume.

### Step 2 — start the OAuth sign-in

```bash
wsl -e bash -lc 'export AZURE_CONFIG_DIR="$HOME/.az-bitpool"; BROWSER=echo az login --tenant bitpool.com --only-show-errors > "$HOME/az-login.out" 2>&1'
```

Run it in the background (Hermes `terminal` with `background=true`). `az login` runs the OAuth authorization-code flow with PKCE: it builds a
sign-in link, then waits on a one-shot listener at `http://localhost:<port>` for Microsoft to
redirect back with the code. `BROWSER=echo` makes it **print** that link instead of opening it, and
the redirect sends it to `$HOME/az-login.out`, where Step 3 reads it — the line starting
`https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/authorize?`, about 600 characters.

Why `echo`, observed 2026-10-16:

- **Left unset**, `az` inside WSL opens the link itself through `powershell.exe Start-Process` —
  Windows' **default** browser, in whatever profile it last used. That is the silent wrong-identity
  trap, so never let `az` choose the browser.
- **Pointed at `msedge.exe`**, the launch happens from WSL and dies with the shell when Edge isn't
  already running (Step 3).

The redirect itself does get back: a Windows browser reaches a listener inside WSL on `localhost`
through WSL's localhost forwarding — both a `127.0.0.1` and a `0.0.0.0` bind answered HTTP 200 from
Windows on 2026-10-16, with `.wslconfig` in the default NAT networking mode. So the indefinite hang
seen on 2026-08-27, with `BROWSER` pointed at a Windows browser, was not the redirect failing; the
browser launch from WSL is the likely cause.

The link is bound to the `az` process waiting for it — its PKCE verifier and `state` exist only
there. If that process is killed or exits, the link is dead: start a new `az login`, never reopen an
old link.

For a tenant with no subscription, or to diagnose why a subscription is invisible, add
`--allow-no-subscriptions` — otherwise `az` exits non-zero with `No subscriptions found for <upn>`
and persists nothing.

### Step 3 — open the link in the dedicated Edge profile

From **Windows**, not WSL. Read the link straight out of the file rather than pasting it — it is
about 600 characters and full of `&` characters, which makes a hand-copied link easy to truncate.
This is the exact command verified on 2026-10-16:

```powershell
$url = wsl -e bash -lc 'grep -m1 "^https://login.microsoftonline.com/" "$HOME/az-login.out"'
Start-Process -FilePath "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" -ArgumentList '--profile-directory="Profile 5"',$url
```

If `$url` comes back empty, `az` hasn't printed the link yet — wait a second and read it again.

Note Edge is under `Program Files (x86)` on this machine, not `Program Files`. Profile 5 is the
dedicated-identity profile; all three `eric-mcp@` accounts are signed into it. Pick the `eric-mcp@`
account for the tenant you asked for. Once the page reports that authentication is complete, the
background `az login` exits on its own with exit code 0. Then delete `$HOME/az-login.out` — the link
in it is dead once used, but there is no reason to keep it.

Launching the same binary from WSL only works when Edge is **already running** — with Edge closed
the process detaches and dies with the shell, and nothing appears.

### Step 4 — verify the identity before running anything

```bash
wsl -e bash -lc 'export AZURE_CONFIG_DIR="$HOME/.az-bitpool"; az account show --only-show-errors -o json'
```

The check that matters is that the UPN is an `eric-mcp@` identity and the tenant is the one you
intended. The three read-only identities are interchangeable in blast radius; **the risk is
authenticating as a personal admin account**, which the tenant ID and email domain make obvious.

**Do not use `az account list --all` for this.** When it finds no subscriptions it clears the
cached account and destroys the session.

### Fallback — device code

Use this only when the redirect cannot get back to WSL — the browser shows `localhost refused to
connect` (or `ERR_CONNECTION_REFUSED`) after sign-in while `az login` keeps waiting. A VPN client, a
change to WSL's `networkingMode`, or `localhostForwarding=false` in `.wslconfig` can each cause it.
Stop the waiting `az login`, then:

```bash
wsl -e bash -lc 'export AZURE_CONFIG_DIR="$HOME/.az-bitpool"; az login --use-device-code --tenant bitpool.com --only-show-errors'
```

Read the code from the background process's output (Hermes `process_manage` poll) and open `https://login.microsoft.com/device` in Profile 5
with the same `Start-Process` command as Step 3, the device URL in place of `$url`. Device codes
expire in about 15 minutes: issue one immediately before it is needed and reissue rather than
nursing a stale one. The device page stays open, so on a retry reissue only the code — don't
relaunch the browser. Then verify the identity exactly as in Step 4.

---

## 4 — Checking an empty tenant is still empty

This needs **no Azure RBAC at all** — Entra Global Reader alone is enough, because a tenant with no
subscriptions returns an empty ARM result regardless of role.

```bash
wsl -e bash -lc 'export AZURE_CONFIG_DIR="$HOME/.az-check"; BROWSER=echo az login --tenant bp-it-testing.com --allow-no-subscriptions --only-show-errors > "$HOME/az-login.out" 2>&1'
```

in the background, open the link in Profile 5 exactly as in section 3, Step 3, then

```bash
wsl -e bash -lc 'export AZURE_CONFIG_DIR="$HOME/.az-check"; az rest --method get --url "https://management.azure.com/subscriptions?api-version=2022-12-01" -o json'
```

A result of `count.value: 0` with an empty `value` array confirms the tenant holds no Azure
subscription. Anything else means a subscription appeared and the tenant is no longer out of scope.

---

## 5 — Teardown

Sessions are long-lived by default. Azure access tokens last about an hour but are silently
refreshed from a cached refresh token whose lifetime depends on tenant Conditional Access — in the
absence of a policy, expect weeks, not hours. Unlike AWS SSO, **nothing expires the session for
you**, so bound it explicitly:

```bash
wsl -e bash -lc 'export AZURE_CONFIG_DIR="$HOME/.az-bitpool"; az logout; rm -rf "$HOME/.az-bitpool"'
```

For read-only discovery, scope is the more valuable restriction than duration. `Reader` is
sufficient for everything in `/azure-query`.

---

## 6 — Diagnostic decision tree

Several distinct failures present almost identically. Work down the list in order.

| Symptom | Cause | Fix |
|---|---|---|
| `az login` waits with no sign-in link in its output | `BROWSER` wasn't `echo`, so `az` tried to open the link itself — in the default browser, or through an Edge launch from WSL that died | Stop it and rerun with `BROWSER=echo`, then open the printed link from Windows |
| No browser window appears | Edge was fully closed; the WSL launch detached and died | Launch from Windows via `Start-Process` |
| `az account show` reports a UPN that isn't `eric-mcp@` | The link opened in the default browser or another profile, not Profile 5 | `az logout`, then sign in again with the link opened in Profile 5 |
| After sign-in the browser shows `localhost refused to connect`, and `az login` keeps waiting | The redirect can't reach WSL — a VPN client, a `networkingMode` change, or `localhostForwarding=false` | Use the device-code fallback in section 3 |
| `AADSTS70020 ... device code has expired` (fallback only) | Code older than about 15 minutes | Reissue the code. Do not relaunch the browser |
| `AADSTS70016 Authorization is pending` at exit (fallback only) | The poll window closed before sign-in completed | Reissue and complete promptly, or run the login from a terminal with no time pressure |
| Session vanishes between commands | `AZURE_CONFIG_DIR` was under `/tmp`; WSL restarted and cleared it | Move it under `$HOME` |
| `No subscriptions found for <upn>` **and** the grant was made | Entra directory role assigned instead of Azure RBAC, **or** a PIM *eligible* rather than *active* assignment | Assign `Reader` on Subscription, Access control (IAM), as an **active** assignment |
| `Subscription '<id>' not found` while Graph calls succeed | No effective RBAC for this principal | Check the assignment, not the subscription ID — see below |

### The authn-versus-authz signature

This pair is decisive and worth committing to memory:

- **Microsoft Graph calls succeed** (e.g. `az ad signed-in-user show` returns the object) — authentication is fine.
- **ARM returns `Subscription '<id>' not found` and `/subscriptions` returns `count: 0`** — authorisation is missing.

ARM deliberately reports *not found* rather than *forbidden* for a subscription the principal
cannot see. So "not found" never means a mistyped ID. Verify with:

```bash
wsl -e bash -lc 'export AZURE_CONFIG_DIR="$HOME/.az-bitpool"; az rest --method get --url "https://management.azure.com/subscriptions?api-version=2022-12-01" -o json'
```

### Confirming a grant, as an admin

Run by someone with Owner or User Access Administrator, authenticated to that tenant:

```bash
az role assignment list --all --scope /subscriptions/3e13a29f-90c5-40a8-abb9-8d25f5911d82 -o table
```

Expect a row with `principalType: User` and `roleDefinitionName: Reader`. Granting by object ID
removes all principal ambiguity:

```bash
az role assignment create --assignee-object-id efd6176d-bb81-4832-9845-a618ee7b9d8d --assignee-principal-type User --role Reader --scope /subscriptions/3e13a29f-90c5-40a8-abb9-8d25f5911d82
```

Beware the role-name collisions in the portal picker: **Directory Readers** and **Global Reader**
are Entra roles, and **Reader and Data Access** is storage-specific. The one you want is plain
**Reader**, described *"View all resources, but does not allow you to make any changes."*
