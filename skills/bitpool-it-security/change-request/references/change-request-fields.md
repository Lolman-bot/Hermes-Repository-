# Change Request Fields & Flow

## Atlassian Config (hardcoded — do not look these up)
- **Cloud ID**: `d7442fe0-cadf-44e1-9313-6b27e16f3fbc`
- **Project key**: `CHAN`
- **Issue type name**: `(Basic) Service request with approvals`
- **Request type ID**: `633` (Basic Change Management — must always be set)
- **Portal**: `https://bitpool.atlassian.net/servicedesk/customer/portal/14`

---

## Custom Field Reference

| Field | Key | Type | Allowed values |
|---|---|---|---|
| Summary | `summary` | text | (required) |
| Description | `description` | text | free text |
| Customer Request Type | `customfield_10100` | string | always `"633"` — set via `editJiraIssue` after creation |
| Change type | `customfield_11402` | select | `Common`, `Normal`, `Emergency` — always default to `Common` unless context says otherwise |
| Standard change? | `customfield_11645` | radio | `Yes` (Common) / `No` (Normal/Emergency) |
| Risk rating | `customfield_11888` | select | `Low`, `Medium`, `High` |
| Impact | `customfield_11401` | select | `Significant / Large`, `Moderate / Limited`, `Minor / Localized` |
| Urgency | `customfield_11407` | select | `Critical`, `High`, `Medium`, `Low` |
| Change start date/time | `customfield_11405` | datetime | ISO8601 e.g. `2026-05-21T09:00:00.000+1000` |
| Estimated duration | `customfield_11885` | text | e.g. `2 hours` |
| Backout plan | `customfield_11529` | ADF | must use ADF format (see below) |
| Affected hardware | `customfield_11525` | text | free text |
| Components | `components` | array | use component IDs (see list below) |
| Department | `customfield_11646` | select | `Information Technology`, `Development`, `Other` |
| Link to related Jira ticket | `customfield_11884` | URL | ticket URL |
| Approvers | `customfield_11400` | multi-user | Jira account IDs |
| People required at change | `customfield_11886` | multi-user | Jira account IDs |
| Affected people | `customfield_11647` | multi-user | Jira account IDs |
| Priority | `priority` | select | `Critical`, `Major`, `Minor` |
| Labels | `labels` | array | free text |
| Due date | `duedate` | date | `YYYY-MM-DD` |

### Backout plan ADF format
```json
{
  "type": "doc",
  "version": 1,
  "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "BACKOUT_TEXT_HERE" }] }]
}
```

### Components
| Name | ID |
|---|---|
| Active Directory | 18007 |
| Analytics and Reporting Service | 18008 |
| Billing Services | 18009 |
| Cloud Storage Services | 18010 |
| Data Center Services | 18011 |
| Email and Collaboration Services | 18012 |
| Financial Services | 18013 |
| HR Services | 18014 |
| Intranet | 18015 |
| Jira | 18016 |
| Office Network | 18017 |
| Payroll Services | 18018 |
| Printers | 18019 |
| Public Website | 18020 |
| VPN Server | 18021 |
| Webstore Purchasing Services | 18022 |

---

## Step 1 — Infer from conversation context FIRST

Before asking the user anything, scan the entire conversation history and extract:

| Field | What to look for in context |
|---|---|
| `summary` | The thing being changed — e.g. "deploying the GraphDB update", "enabling MFA for dev team" |
| `description` | Any detail the user has already described about what the change involves |
| `components` | Systems mentioned — map to component IDs (e.g. "AWS" → Cloud Storage Services / Data Center Services, "M365/Outlook/Teams" → Email and Collaboration Services, "Jira" → Jira, "GitHub" → no match, leave blank, etc.) |
| `customfield_11888` (risk) | Words like "low risk", "routine", "risky", "prod deployment" etc. |
| `customfield_11401` (impact) | Mentions of downtime, user impact, blast radius |
| `customfield_11405` (start) | Any date/time mentioned — convert to `YYYY-MM-DDTHH:MM:SS.000+1000` |
| `customfield_11885` (duration) | Estimated time mentioned |
| `customfield_11529` (backout) | Any rollback/revert plan mentioned |
| `customfield_11646` (department) | Who is asking — dev team → `Development`; IT/infra context → `Information Technology` |
| `customfield_11884` (linked ticket) | Any Jira ticket key mentioned (e.g. BT-123, CSIP-456) — use full URL |
| `customfield_11402` (change type) | Always default to `Common` — do NOT ask the user. Override to `Normal` or `Emergency` only if explicit context says so |

**Auto-set without asking (ever):**
- Change type → `Common` (default, unless context clearly says emergency/normal)
- Standard change? → `Yes` (Common) / `No` (Normal/Emergency)
- Priority → Risk Low = `Minor`, Medium = `Major`, High = `Critical`
- Urgency → Common = `Low`, Normal = `High`, Emergency = `Critical`
- Due date → same date as start date

---

## Step 2 — Ask only for what is still missing

After inferring from context, identify which required fields are still unknown.
Only ask for those. Group questions naturally — do not ask one at a time if
multiple are missing.

**Required fields that must be filled (prompt if not inferrable):**
1. Summary (one-line title)
2. Description (what the change involves)
3. Risk rating (Low / Medium / High)
4. Start date and time (AEST)
5. Backout plan
6. Department (IT / Development / Other)

**Optional — only ask if relevant or if user mentions it:**
- Components (which systems)
- Estimated duration
- Linked Jira ticket
- Affected hardware
- Approvers / people required (Normal/Emergency only)

Never ask about change type. Never ask about standard change, urgency, or priority
— these are all derived automatically.

---

## Step 3 — Confirm before creating

Show a summary and ask **"Shall I create this ticket?"**

```
📋 Change Request Summary
──────────────────────────────────────────
Title:       [summary]
Department:  [department]
Components:  [component names or "None"]
Risk:        [Low / Medium / High]
Impact:      [impact]
Start:       [date/time AEST]
Duration:    [duration or "N/A"]
Priority:    [derived priority]

Description:
[description]

Backout plan:
[backout plan]
──────────────────────────────────────────
```

Do not create until confirmed.

---

## Step 4 — Create the ticket (two steps)

### 4a. Create the issue with `createJiraIssue`

```json
{
  "cloudId": "d7442fe0-cadf-44e1-9313-6b27e16f3fbc",
  "projectKey": "CHAN",
  "issueTypeName": "(Basic) Service request with approvals",
  "summary": "<summary>",
  "description": "<description>",
  "contentFormat": "markdown",
  "additional_fields": {
    "priority": { "name": "<Critical|Major|Minor>" },
    "customfield_11402": { "value": "Common" },
    "customfield_11645": { "value": "Yes" },
    "customfield_11888": { "value": "<Low|Medium|High>" },
    "customfield_11401": { "value": "<impact>" },
    "customfield_11407": { "value": "<Critical|High|Medium|Low>" },
    "customfield_11405": "<ISO8601 datetime>",
    "customfield_11885": "<duration>",
    "customfield_11529": {
      "type": "doc",
      "version": 1,
      "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "<backout plan>" }] }]
    },
    "customfield_11646": { "value": "<department>" },
    "components": [{ "id": "<component id>" }],
    "duedate": "<YYYY-MM-DD>"
  }
}
```

Only include optional fields if values are available.

### 4b. Immediately patch request type with `editJiraIssue`

After creation succeeds, call `editJiraIssue` to set the request type:

```json
{
  "cloudId": "d7442fe0-cadf-44e1-9313-6b27e16f3fbc",
  "issueIdOrKey": "<new issue key e.g. CHAN-86>",
  "fields": {
    "customfield_10100": "633"
  }
}
```

This ensures the ticket appears under the correct "Basic Change Management"
request type in the portal. This step is mandatory — always do it.

---

## Step 5 — Post-creation

Share the ticket URL: `https://bitpool.atlassian.net/browse/CHAN-XXX`
