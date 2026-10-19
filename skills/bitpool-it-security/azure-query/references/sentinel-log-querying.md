# Searching Sentinel logs — incidents, alerts and the activity behind them

Every query here was run successfully on 2026-10-13 against the `Microsoft-Sentinel-LAWS` workspace
as `eric-mcp@bitpool.com` holding Azure RBAC `Reader` and nothing else. Table lists and counts are
from that run and will drift — re-read them, never restate them from here.

Assumes a live session. If `az account show` hasn't been verified this session, run
`/azure-context` first.

---

## 1 — What the workspace holds, and why it is the place to look

| Fact | Value as at 2026-10-13 |
|---|---|
| Workspace | `Microsoft-Sentinel-LAWS`, resource group `Sentinel`, 90-day retention |
| Workspace ID — the `-w` value | `1c606301-9ad7-4714-8f6a-7c5f26b6f505` |
| Access needed | Subscription `Reader`. No Log Analytics or Sentinel role on top |
| CLI extension | `log-analytics` (preview, `1.0.0b1`), already installed in WSL |

The `-w` value is the workspace's `customerId` from `az monitor log-analytics workspace list` — not
its `id` or `name`. Re-read it there if a query reports the workspace missing. The second workspace,
`managed-onepasswordftdn33ek-ws`, is a 1Password-managed sink, not Sentinel.

**Defender is already in here.** The Microsoft Defender XDR connector syncs into this workspace, so
Sentinel and Defender incidents and alerts are searched in one place:

- **`SecurityIncident`** — every incident carries `ProviderName = Microsoft XDR`. These *are* the
  Defender portal's incidents: `ProviderIncidentId` is the Defender incident number, and
  `AdditionalData.providerIncidentUrl` links to it.
- **`SecurityAlert`** — Defender for Endpoint (`MDATP`), Defender for Office 365 (`OATP`), Defender
  for Cloud Apps (`MCAS`), Entra ID Protection (`IPC`) and Sentinel's own near-real-time rules
  (`ASI NRT Alerts`).
- **Defender advanced-hunting tables** — `Device*`, `Email*`, `UrlClickEvents`, `CloudAppEvents`,
  `AlertInfo`, `AlertEvidence`.
- **Entra and Azure logs** — `SigninLogs`, `AADNonInteractiveUserSignInLogs`, the service-principal
  and managed-identity sign-in tables, `AuditLogs`, `MicrosoftGraphActivityLogs`, `AzureActivity`,
  `AADRiskyUsers`, `AADUserRiskEvents`.
- **`OnePasswordEventLogs_CL`.**

No Defender for Identity source appeared. Before saying a source is or isn't connected, run the
table inventory in section 3 — this list is a snapshot.

---

## 2 — The invocation shape

KQL is full of `|`, quotes and `$`, none of which survive being typed inline inside
`wsl -e bash -lc '...'`. Write each query to a file with a **quoted** heredoc, pass it with
`"$(cat file)"`, and write the result to disk:

```bash
wsl -e bash -lc 'export AZURE_CONFIG_DIR="$HOME/.az-bitpool"
D="$HOME/azsentinel"; mkdir -p "$D"; WS=1c606301-9ad7-4714-8f6a-7c5f26b6f505
cat > "$D/q_incidents.kql" <<"KQL"
SecurityIncident
| where TimeGenerated > ago(30d)
| summarize arg_max(TimeGenerated, *) by IncidentNumber
| summarize Incidents = count() by Status, Severity, ProviderName
KQL
az monitor log-analytics query -w "$WS" --analytics-query "$(cat $D/q_incidents.kql)" --only-show-errors -o json > "$D/r_incidents.json" 2>"$D/r_incidents.err"
printf "json=%s err=%s\n" "$(stat -c%s $D/r_incidents.json)" "$(stat -c%s $D/r_incidents.err)"'
```

Then parse `r_*.json` with a script file, as in `azure-querying.md` section 2.

**Log results are personal data** — who signed in where, which files they opened. Keep working files
under `$HOME` in WSL, never in OneDrive or a repo, and offer to delete the folder once the
investigation is done.

---

## 3 — Query library

Each was run on 2026-10-13. Change the literals on the `let` lines.

### Table inventory — what is actually flowing

```kusto
Usage
| where TimeGenerated > ago(30d)
| summarize MB = round(sum(Quantity), 1), LastSeen = max(TimeGenerated) by DataType, Solution
| order by MB desc
```

### Open incidents

```kusto
SecurityIncident
| where TimeGenerated > ago(90d)
| summarize arg_max(TimeGenerated, *) by IncidentNumber
| where Status != "Closed"
| project IncidentNumber, ProviderIncidentId, Title, Severity, Status, CreatedTime, LastModifiedTime,
          Owner = tostring(Owner.assignedTo), AlertCount = array_length(AlertIds)
```

### Alerts by source product

```kusto
SecurityAlert
| where TimeGenerated > ago(30d)
| summarize Alerts = dcount(SystemAlertId) by ProductName, ProviderName, AlertSeverity
| order by Alerts desc
```

### Is the feed quiet, or broken?

```kusto
union withsource=T SecurityIncident, SecurityAlert, AlertInfo
| summarize Latest = max(TimeGenerated) by T
```

Compare with a raw Defender table such as `DeviceFileEvents` in the inventory. Raw data still
arriving with no new alerts is a quiet period, not a dead connector.

### One incident — its alerts, entities and description

```kusto
let inc = 1410;
SecurityIncident
| where IncidentNumber == inc
| summarize arg_max(TimeGenerated, AlertIds) by IncidentNumber
| mv-expand AlertId = AlertIds to typeof(string)
| join kind=inner (SecurityAlert | where TimeGenerated > ago(30d) | summarize arg_max(TimeGenerated, *) by SystemAlertId)
    on $left.AlertId == $right.SystemAlertId
| project SystemAlertId, AlertName, Description, ProductName, AlertSeverity, Status, StartTime, EndTime,
          Tactics, Techniques, Entities, ExtendedProperties, AlertLink
```

`Entities` carries the account (with `AadUserId`), every IP with its role — `Attacker` or
`Contextual` — the cloud apps, and a verdict per entity. `ExtendedProperties.DetectorId` names the
detection rule.

### One incident — its evidence rows

```kusto
let inc = 1410;
SecurityIncident
| where IncidentNumber == inc
| summarize arg_max(TimeGenerated, AlertIds) by IncidentNumber
| mv-expand AlertId = AlertIds to typeof(string)
| join kind=inner (SecurityAlert | where TimeGenerated > ago(30d) | summarize arg_max(TimeGenerated, AlertLink, AlertName) by SystemAlertId)
    on $left.AlertId == $right.SystemAlertId
| extend EvidenceAlertId = tostring(split(parse_url(AlertLink).Path, "/")[2])
| join kind=inner (AlertEvidence | where TimeGenerated > ago(30d)) on $left.EvidenceAlertId == $right.AlertId
| project Timestamp, AlertName, EntityType, EvidenceRole, AccountUpn, DeviceName, RemoteIP, RemoteUrl,
          FileName, Application, AdditionalFields
```

### Which app was it? — attributing a user's Graph calls

This is the step that turns "suspicious IP" into "which integration". `MicrosoftGraphActivityLogs`
records every Graph call with the calling app's `AppId`, the IP and the user agent. Set the window
around the alert's `StartTime` and `EndTime`:

```kusto
let uid = "<AadUserId from the alert's Entities>";
MicrosoftGraphActivityLogs
| where TimeGenerated between (datetime(2026-10-06 01:30) .. datetime(2026-10-06 02:20))
| where UserId == uid
| summarize Calls = count(), First = min(TimeGenerated), Last = max(TimeGenerated), IPs = make_set(IPAddress, 5)
    by AppId, UA = substring(UserAgent, 0, 80)
| order by First asc
```

Then name each app. `az ad sp show` takes an app ID directly and works under Global Reader:

```bash
wsl -e bash -lc 'export AZURE_CONFIG_DIR="$HOME/.az-bitpool"; az ad sp show --id <appId> --query "{name:displayName, verified:verifiedPublisher.displayName, ownerTenant:appOwnerOrganizationId}" -o json --only-show-errors'
```

### What happened from an IP range

```kusto
CloudAppEvents
| where TimeGenerated > ago(30d)
| where ipv4_is_in_range(IPAddress, "136.124.0.0/16")
| summarize Events = count(), First = min(TimeGenerated), Last = max(TimeGenerated), Actions = make_set(ActionType, 8)
    by Application, ISP, CountryCode, AccountDisplayName, UA = substring(UserAgent, 0, 100)
```

And whether anything **signed in** from it. Check both sign-in tables — token refreshes land in the
non-interactive one:

```kusto
union withsource=T SigninLogs, AADNonInteractiveUserSignInLogs
| where TimeGenerated > ago(30d)
| where ipv4_is_in_range(IPAddress, "136.124.0.0/16")
| summarize Events = count(), First = min(TimeGenerated), Last = max(TimeGenerated)
    by T, UserPrincipalName, AppDisplayName, AppId, ResultType
```

For who owns an address, ARIN's registry record — `https://rdap.arin.net/registry/ip/<ip>` — is
authoritative for ARIN-allocated ranges. `CloudAppEvents.ISP` is a quicker hint.

---

## 4 — Direct Defender access is held, not missing

Graph's Defender endpoints — `/security/incidents`, `/security/alerts_v2`,
`/security/runHuntingQuery` — return **Forbidden** to `az rest`: *missing application scopes
`SecurityIncident.Read.All`, `SecurityAlert.Read.All`*. The Azure CLI's own app registration can't
request those scopes, so no role assignment fixes it. Reaching them needs a dedicated app
registration with admin consent.

**Decided 2026-10-13: held — use Sentinel.** What the Graph API would add is modest: the incident
`summary` text, `recommendedActions`, `priorityScore` and the automated-investigation state. The
Defender portal's **attack-story graph has no API at all.** Don't propose the app registration as
the fix for a failed call — it's a decision already taken, and changing it is the user's call.

---

## 5 — Known benign signatures

A match still needs the user to confirm the activity was theirs. A signature proves which app
acted, not which person drove it.

### Claude's Microsoft 365 connector

| Signal | Value |
|---|---|
| App | `07c030f6-5743-41b7-ba00-0a6e85f37c17` — "M365 MCP Server for Claude", verified publisher Anthropic PBC |
| Source IPs | Google Cloud — `136.124.0.0/16`, inside Google's `136.112.0.0/12` (network `GOOGL-46`), and `34.96.x` |
| User agent | `node`; `kiota-typescript/...` for search calls |
| Pattern | Graph calls, then file downloads through pre-authorised links — `CloudAppEvents.ActionType` `PreAuthTokenUsed` then `FileDownloaded` |
| What it trips | Defender for Cloud Apps "Impossible travel activity" and "Activity from infrequent country" |
| What it doesn't leave | **No sign-in rows** for those IPs in either sign-in table — the connector already holds a delegated token |

First diagnosed on incident 1410 (Defender 1725), 2026-10-06. Confirm with the Graph-attribution
query in section 3 rather than matching on IP alone — attackers rent Google Cloud too.

---

## 6 — Traps

1. **`SecurityIncident` has one row per update.** Always
   `summarize arg_max(TimeGenerated, *) by IncidentNumber` before counting or filtering on `Status`,
   or each incident counts several times and closed ones show as open.
2. **`AlertIds` is dynamic.** `mv-expand AlertId = AlertIds to typeof(string)` before joining to
   `SecurityAlert.SystemAlertId`.
3. **`AlertEvidence.AlertId` is not `SecurityAlert.VendorOriginalId`.** It is the last path segment
   of `SecurityAlert.AlertLink` — for Defender for Cloud Apps, `ca` followed by the vendor ID.
   Joining on `VendorOriginalId` returns nothing, with no error.
4. **Every value comes back as a string** from `az monitor log-analytics query` — numbers, and
   dynamic columns as JSON-encoded strings. Parse with `json.loads` and cast numbers before
   comparing.
5. **`az ad sp list --filter "appId eq '...'"` breaks on quoting** through WSL and reports a type
   mismatch. Use `az ad sp show --id <appId>`.
6. **Times are UTC.** Convert to the person's local time before asking "was that you at …?", and
   check their zone rather than assume one — Queensland has no daylight saving, the southern states
   do.
7. **`Usage` is hourly buckets.** A `LastSeen` of `14:00` means the last data landed in that hour,
   not at that minute.
