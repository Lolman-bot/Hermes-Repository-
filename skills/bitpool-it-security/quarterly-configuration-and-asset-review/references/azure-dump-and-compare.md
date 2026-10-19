# Azure dump and compare

> **Read `references/snapshot-and-diff.md` first.** The tags are the live register; the
> snapshot is what lets this cycle be diffed against the last one. Both halves are the job,
> and the diff is the half a live query can never do for you afterwards.

**Snapshot and diff:**

```bash
wsl -e bash -lc 'python3 scripts/snapshot.py azure --resources resources.json --groups groups.json \
  --cycle 2026-09 --source "az resource list + az group list" -o azure_2026-09.json'
wsl -e bash -lc 'python3 scripts/diff_snapshots.py azure_2026-06.json azure_2026-09.json --format markdown'
```

Azure tags at **resource-group** level, so the snapshot expects governance keys on groups and
tracks resources for existence only. An untagged Azure *resource* is not a finding; an untagged
resource **group** is.

**Azure resource tags are the asset register.** There is no separate list. A resource group that
exists carries its own ownership metadata; one that is deleted takes its row with it.

Tagging is at **resource-group** level, not individual resources — there are far fewer groups, their
names already carry meaning, and group-level tags survive resource churn inside the group.

## Scope

| | |
|---|---|
| Tenant with Azure infrastructure | `bitpool.com` |
| Tenants confirmed empty each cycle | `bp-it-testing.com`, `BitpoolExternal.onmicrosoft.com` |
| Access required | Azure RBAC `Reader` on the subscription; Entra Global Reader for the empty-tenant checks |

### The required tags

| Tag | Required | Holds |
|---|---|---|
| `Owner` | Yes | The accountable **team**, not an individual |
| `Purpose` | Yes | What the group is for, in a few words |
| `Criticality` | Yes | `critical`, `high` or `standard` — same vocabulary as AWS |
| `OwnerContact` | Recommended | Current human contact; may go stale without breaking the register |
| `DataClassification` | Yes | `Restricted` · `Confidential` · `InternalUse` · `Public` |
| `IsPersonalData` | Yes | `True` · `False` |

The last two are how **information** is inventoried — `A.5.9` covers information first, and Bitpool
does not keep a separate data catalogue. The vocabulary comes from the Data Classification Policy, so
it is already approved.

The authority for keys, values and casing is the *Cloud resource tagging standard* on the wiki, not
this file. If they disagree, the standard wins and this file needs updating.

## The cycle

### 1. Confirm the session

**Delegate to `/azure-context`.** Azure CLI lives only in WSL on the admin workstation, sign-in is per
tenant through a browser in the dedicated Edge profile, and the sign-in has several ways to fail
quietly — wrong permission system, dormant role assignment, a token cache in a directory that does
not survive. `/azure-context` carries the full diagnostic tree; do not reimplement it here.

### 2. Produce the dump

**Delegate to `/azure-query`**, which owns the collection commands and already produces this dump.

Collect resource groups, every resource with type, location and tags, the Log Analytics workspaces,
and the role assignments. **Write each to a file, then analyse** — do not pipe the CLI straight into a
parser. Record the subscription, the identity used, and the date alongside the output.

### 3. Confirm the two Entra-only tenants are still empty

Sign in to each with `--allow-no-subscriptions` and read the ARM subscriptions endpoint. A count of
zero confirms the tenant holds no Azure subscription.

This needs **no Azure RBAC** — Entra Global Reader is sufficient, because a tenant with no
subscriptions returns an empty result regardless of role.

A non-zero result means a subscription has appeared and the register's **scope** has changed. That is
a finding in its own right, not a routine update.

### 4. Compare against the previous cycle

Report three sets explicitly:

- **New** — present now, absent last cycle.
- **Removed** — present last cycle, absent now. These are decommissioned assets: record the removal
  rather than letting the row quietly disappear.
- **Changed** — same resource in a different group or location, or with different tags.

> **Case-fold resource group names before comparing.** Azure preserves the case a group was created
> with, but a resource can report its parent group in different case — observed 2026-08-28, where the
> Sentinel solution reported `sentinel` while the group itself is `Sentinel`. Grouping on the raw
> string splits one group in two and reports a **phantom resource group that does not exist**, which
> reads as a new asset and wastes the cycle chasing it.

### 5. Update tags

Apply the required tags to any resource group untagged or mis-tagged against the table above.
**Empty resource groups are cleanup candidates** — raise them rather than tagging them.

### 6. Evidence

Per `references/evidence-contract.md`. Retain the dump in the cycle folder.

## What this does not rely on

**Drata's Azure connection is not a source of truth for this estate** and must not be used to
reconcile the dump. When this cycle was established it was reporting a single asset out of the full
estate and had not updated in over eighteen months. A connection that stops reporting does not raise
an error — it simply goes quiet, which is why the register is derived from tags rather than a synced
copy.
