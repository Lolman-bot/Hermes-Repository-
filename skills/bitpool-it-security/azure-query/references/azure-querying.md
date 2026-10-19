# Querying Bitpool's Azure estate

Every command here was run successfully on 2026-08-27 against subscription
`3e13a29f-90c5-40a8-abb9-8d25f5911d82` ("Bitpool - Default") as `eric-mcp@bitpool.com` holding
Azure RBAC `Reader`. Counts quoted are from that run and will drift — re-read them, never restate
them from here.

Assumes a live session. If `az account show` hasn't been verified this session, run
`/azure-context` first.

---

## 1 — The invocation shape

```bash
wsl -e bash -lc 'export AZURE_CONFIG_DIR="$HOME/.az-bitpool"; az <command>'
```

`AZURE_CONFIG_DIR` must be exported in **every** invocation — each `wsl -e bash -lc` is a fresh
shell and inherits nothing from the last one.

---

## 2 — Collect first, parse second

**Do not pipe `az` straight into an inline parser.** Nested quoting inside
`wsl -e bash -lc '... python3 -c "..."'` breaks in ways that produce a confusing `SyntaxError`
rather than a clear failure. Write JSON to disk under `$HOME`, then run a script file against it.

### The collection block

```bash
wsl -e bash -lc 'export AZURE_CONFIG_DIR="$HOME/.az-bitpool"
D="$HOME/azdisc"; mkdir -p "$D"
az group list --only-show-errors -o json > "$D/groups.json" 2>"$D/groups.err"
az resource list --only-show-errors -o json > "$D/resources.json" 2>"$D/resources.err"
az monitor log-analytics workspace list --only-show-errors -o json > "$D/law.json" 2>"$D/law.err"
az role assignment list --all --only-show-errors -o json > "$D/roles.json" 2>"$D/roles.err"
for f in groups resources law roles; do printf "%-11s json=%8s err=%s\n" "$f" "$(stat -c%s $D/$f.json)" "$(stat -c%s $D/$f.err)"; done
grep -h . $D/*.err | head'
```

A non-zero `.err` size with a zero-size `.json` is almost always a session or RBAC failure — go
back to `/azure-context` section 6 rather than retrying.

### Then write the analysis as a file

```bash
wsl -e bash -lc 'cat > "$HOME/azan.py" <<PYEOF
... python ...
PYEOF
python3 "$HOME/azan.py"'
```

Use an **unquoted** heredoc delimiter only if you intend shell expansion inside the script; for
Python, quote it (`<<"PYEOF"`) so `$` and backticks pass through untouched.

---

## 3 — What each collection returns

| Command | Returns | Register relevance |
|---|---|---|
| `az group list` | Resource groups: name, location, tags | **The tagging unit.** 15 groups, 14 populated as at 2026-08-27 |
| `az resource list` | Every taggable resource: id, name, type, location, resourceGroup, tags | **The register itself.** 43 resources |
| `az monitor log-analytics workspace list` | Workspaces: name, resourceGroup, sku, retentionInDays | Sentinel and its retention period |
| `az role assignment list --all` | Assignments: principalName, principalType, roleDefinitionName, scope | Privileged-access review |

`Reader` includes `Microsoft.Authorization/roleAssignments/read`, so the access review comes free.

The workspace list says a workspace exists and how long it keeps data. To search what is *in* the
Sentinel workspace — incidents, alerts, sign-ins, Graph activity — see `sentinel-log-querying.md`.

---

## 4 — Analysis patterns worth having

### Composition

Group `az resource list` by `resourceGroup`, by `type`, and by `location`. Split `type` on the
first `/` to separate provider from resource kind — `Microsoft.KeyVault/vaults` becomes
`KeyVault` + `vaults`, which makes the security-relevant rows obvious.

### Tag coverage

Count resources with a non-empty `tags` object, then count occurrences per tag key. Check
explicitly for owner-style keys — `owner`, `managedby`, `contact`, `criticality`, `environment`,
`classification`.

As at 2026-08-27: **1 of 43 resources carried any tag, and that key was `hidden-title`** — an
Azure-internal display field, not a governance tag. No owner, criticality, environment or
classification tag existed anywhere, and every resource group was untagged. This is the finding
that makes Azure a point-in-time dump rather than a tag-derived live register.

### Case-variant resource groups

`az resource list` returns `resourceGroup` with inconsistent casing against `az group list` —
`Sentinel` versus `sentinel` for the same group. **Normalise to lowercase before grouping**, or a
single group appears twice and the count is wrong.

### Privileged access

Filter `roleDefinitionName` to `Owner`, `Contributor` and `User Access Administrator`, and check
the `scope` string. A scope of `/` is **tenant root**, above subscription — materially broader than
a subscription-scoped assignment and worth calling out separately.

---

## 5 — Querying the two empty tenants

`bp-it-testing.com` and `BitpoolExternal.onmicrosoft.com` hold no Azure subscriptions, so none of
the commands above return anything. The only meaningful query is the emptiness check, and it needs
no Azure RBAC — see `/azure-context` section 4.

Do not attempt `az resource list` against them; the failure is expected and tells you nothing.

---

## 6 — Traps

1. **`--output text` collapses structure.** Use `-o json` and parse when shape matters.
2. **`--query 'length(...)'` under CLI auto-pagination prints one length per page**, not a total. Project the ARNs or IDs and count lines instead.
3. **`az account list --all` clears the cached account** when no subscriptions are found. Never a health check; use `az account show`.
4. **`az rest` against ARM returns "not found" for unauthorised subscriptions**, not "forbidden". A not-found never means a mistyped ID.
5. **Resource IDs are the stable key, not names.** Several unrelated resources in this estate share the name `onepasswordftdn33ek` across four different types. Deduplicate on `id`.
6. **`Microsoft.SaaS/resources` entries are third-party subscriptions surfaced as Azure resources** — Veeam and Impartner, in this estate. They belong in the vendor lane of the asset library, not the infrastructure lane, even though ARM returns them here.
