# Drata Control Insights Matrix

Produces a structured visual matrix for any Drata control (DCF) or CSIP Jira issue, joining the
real Drata control record, live Jira data, a GitBook documentation check, and — for controls that
touch infrastructure — the **actual current state of Bitpool's AWS accounts** into one status
matrix and keyword tag cloud. Read-only across all four systems — this skill never writes
anywhere. For multi-control work, staged Jira writes, and a persistent worklog, that's
`/drive-iso27001` — this skill is just the single-control snapshot it (or the user) can render
on demand.

**Why the AWS check matters here:** when Drata's `isMonitored` flag is `false` there is no automated
test behind the control, so the only other input is someone's recollection of how the environment is
configured. A bounded read-only query replaces that with an observation.

---

## Workflow

### Step 1 — Resolve the identifier

**If given a DCF number (e.g. DCF-164):**
- Search Jira with the Atlassian MCP server's search tool, query `DCF-xxx`, to find the linked CSIP issue.
- Then fetch the full issue with its `getJiraIssue` tool using `cloudId: bitpool.atlassian.net`.
  (In Hermes these carry an `mcp_<server>_` prefix — find the live names with `tool_search`.)

**If given a CSIP key directly (e.g. CSIP-760):**
- Fetch directly with the Atlassian MCP server's `getJiraIssue` tool. Read the title/description for the `DCF-xxx` code
  (title format: `Drata | Bitpool | DCF-xxx | [Control Name]`) so Step 1b can look it up.

Extract from the issue:
- `summary` — title/control name
- `status.name` — current CSIP stage
- `assignee.displayName`
- `description` — contains the full control explanation, requirements, and Bitpool-specific context
- `issuetype.name`
- `key` — CSIP issue key

**Step 1b — Pull the real Drata record (read-only).** Once you have a DCF code, call
`Drata_searchControls` (the Drata MCP server's tool; find its live name with `tool_search`) to fetch
the actual control. Search mode (`query: "DCF-xxx"`) is broken on this account — `/ask-drata`
rules 1–3: use list mode with no `query`, seeking by cursor or paginating to `cursor: null`, and
check the returned `code`. Capture:
- `flags` — `isReady`, `hasEvidence`, `hasPolicy`, `hasOwner`, `isMonitored`, `hasTicket`
- `name`, `description`, `updatedAt`

This is a single lightweight call — never call `Drata_listEvidence`, `Drata_updateControl`, or any
other Drata write/detail tool from this skill; `flags` alone is a fast, sufficient gap signal. If
no Drata match is found, note "no Drata record found for DCF-xxx" and fall back to Jira-only for
the fields below — don't block the render on it.

---

### Step 2 — Derive metadata

Prefer real data over inference wherever it's available; fall back to reading the CSIP
description + your knowledge of ISO 27001 only for the fields Drata doesn't carry:

- **ISO 27001 clause** — e.g. "9.3", "A.9.2.1" — from the CSIP description if referenced, else infer
- **Control category** — e.g. "Access Control", "Risk Management", "Audit & Compliance" — infer
- **Frequency** — e.g. "Annual", "At planned intervals", "Continuous", "Per incident" — infer from description
- **Mandatory inputs** — what the control requires as inputs (list, drawn from description)
- **Required outputs** — what must be produced/evidenced (list, drawn from description)
- **Drata status flags** — the real `flags` from Step 1b (isReady/hasEvidence/hasPolicy/hasOwner/isMonitored) —
  do **not** guess these, render exactly what Drata returned
- **Bitpool context** — specific systems, processes, or people at Bitpool relevant to this control
- **Keywords** — 12–20 tags covering the control domain, ISO clause, key concepts, and tools

**Step 2b — Documentation check (local index).** Look the control's domain up in
[Documentation Index](documentation-index.md) to see whether a supporting policy or procedure is
recorded. Capture the best-matching page path, or if the domain has no entry, record it as a
**candidate documentation gap** (consistent with how `/drive-iso27001` flags missing docs as an
action item).

Render the distinction honestly, because the index is a snapshot and the matrix is read as a
compliance artefact:

- A page in the index → *"documented: `/isms/...`"*.
- No entry → *"no documentation found in index (snapshot 2026-08-21)"* — **not** *"undocumented"*.
  The index cannot see a page added since it was built, so the stronger claim isn't yours to make.

A policy and a procedure are different things. If the domain has a policy but no runbook, say that
rather than marking it documented and moving on.

**Step 2c — Infrastructure current-state check (read-only, automatic when relevant).**

Read [AWS Evidence Map](aws-evidence-map.md) and apply it. That file is the single source
of truth for *which* AWS calls evidence *which* control domain, shared with `/drive-iso27001`.

1. **Apply the relevance test** in section 2 of the map. Physical, HR, policy-existence and training
   controls are **not AWS questions** — skip the check entirely and render the row as "not an AWS
   question". Don't fish.
2. **If relevant, run it automatically** — no need to ask first at this scale. Session handling and
   query construction are not this skill's job:
   - No confirmed `aws sts get-caller-identity` yet this session → run **`/aws-context`** first.
   - Then use **`/aws-query`** to build and run the calls (it owns the account list, profile names,
     the multi-account loop, and the JMESPath gotchas). **Never inline CLI commands, profile names,
     or account IDs into this skill.**
3. **Stay inside the snapshot budget: ≤2 domains, ≤6 calls** (section 4 of the map). This is a
   single-control snapshot, not an audit — one account unless the control is inherently org-wide
   (CloudTrail, Organizations, Identity Center, SCPs). If a control needs more than that to assess
   properly, say so and point at `/drive-iso27001 DCF-xxx`.
4. **Capture, per check:** what was asked, the observed result, the observation date, and which of
   three states it lands in — **in place** / **gap** / **not checked**.
5. **Degrade cleanly.** No SSO session and the user doesn't want to sign in, or the query fails on
   session grounds → render "not checked", never block the widget. AWS is enrichment; the matrix
   must still render from Drata + Jira + GitBook alone.

**An AWS result is an observation, not evidence and not a verdict** (section 5 of the map). Report
"CloudTrail logging in `<n>` of `<m>` accounts, observed `<date>`", never "control satisfied". Drata stays
read-only — a human attaches evidence in the Drata UI; this check tells them what's worth attaching.

---

### Step 3 — Render the matrix widget

Hermes has no inline widget surface, so the matrix is one self-contained HTML file. Write it with
`write_file` to the Hermes scratch directory (`$TMPDIR`, or `$HERMES_HOME/cache/`) as
`drata-insights-<DCF-xxx>.html`, open it with the browser tools so the user sees it rendered, and
give the user the file path.

- **Declare the palette once, in a `:root` block at the top of the file** — `--color-text-primary`,
  `--color-text-secondary`, `--color-text-success`, `--color-text-warning`,
  `--color-background-primary`, `--color-background-secondary`, `--color-border-tertiary`,
  `--border-radius-md`, `--border-radius-lg`. Take the values from `/bitpool-design-system` when it
  is installed. That block is the only place a colour value appears; everything below uses
  `var(--…)`.
- Load Tabler icons from their CDN stylesheet in the `<head>` for the Row 5 icons.

#### Layout structure

**Row 1 — metric cards (6 cards, 3-column grid):**
- Control ID (DCF-xxx)
- Jira issue (CSIP-xxx)
- Status — CSIP stage (with muted colour if Planned/Blocked); if no Drata match was found in
  Step 1b, append "(Drata: not found)" in muted text
- ISO 27001 clause
- Assignee
- Frequency

**Row 2 — full-width card: Drata status flags (5-across icon/label strip):**
- One small tile per flag — `isReady`, `hasEvidence`, `hasPolicy`, `hasOwner`, `isMonitored` —
  each a label + a coloured dot/check: `var(--color-text-success)` when `true`,
  `var(--color-text-secondary)` (muted) when `false`. This is the row that makes Drata's real
  gap signal visible at a glance instead of guessed evidence text.
- If Step 1b found no Drata record, replace this row with a single muted note instead of
  fabricating flag values.

**Row 3 — full-width card: Infrastructure reality (from Step 2c):**

Deliberately placed directly under the Drata flags — the juxtaposition of "Drata has no monitor for
this" against "here is what AWS actually returned" is the point of this row.

- Header: `INFRASTRUCTURE (AWS — OBSERVED [date])`, in the standard section-header style.
- One row per check performed: the question in `var(--color-text-primary)`, the observed result
  beside it, and a state indicator using the same colour language as Row 2 —
  `var(--color-text-success)` for **in place**, `var(--color-text-secondary)` for **not checked**.
  For a **gap**: use `var(--color-text-warning)` from the `:root` palette if it is declared; otherwise use `var(--color-text-primary)` and rely on the "gap" label. Never
  hardcode a hex colour to get a warning tone.
- **Order gaps first.** They're the reason the row exists.
- **If the control isn't infrastructure-relevant**, render one muted line: "Not an AWS question —
  [reason, e.g. physical/people control]." Do **not** omit the row silently.
- **If relevant but not checked** (no session, or the user declined sign-in), render one muted line
  naming the reason: "Not checked — no active AWS SSO session this session." Never let this read as
  a pass.
- Cap it at what fits: **≤6 lines**. If more was queried, show the gaps plus a muted "+N further
  checks in place".

**Row 4 — two-column card grid:**
- Left: Mandatory inputs (bulleted list)
- Right: Required outputs (bulleted list, drawn from the CSIP description)

**Row 5 — two-column card grid:**
- Left: Bitpool context (icon list using Tabler icons — choose contextually from:
  ti-device-laptop, ti-cloud, ti-users, ti-alert-triangle, ti-file-text, ti-shield, ti-lock,
  ti-server, ti-mail, ti-key, ti-building, ti-chart-bar)
- Right: Documentation — the GitBook page title + link from Step 2b, styled as a normal card
  row; if it's a gap, render one line in `var(--color-text-secondary)`: "No matching GitBook
  procedure found — documentation gap."

**Row 6 — full-width card:**
- Keywords tag cloud — ALWAYS render via JavaScript (see implementation note below)

#### Keyword rendering — critical implementation note

**Never use template literals or `${}` interpolation to generate keyword tags inline in HTML.**
This breaks rendering. Instead, always use a `<div id="kw"></div>` placeholder and populate
it via a `<script>` block using `document.getElementById` and `appendChild`:

```html
<div style="display: flex; flex-wrap: wrap; gap: 8px;" id="kw"></div>

<script>
var keywords = ['Keyword One', 'Keyword Two', ...];
var container = document.getElementById('kw');
keywords.forEach(function(k) {
  var span = document.createElement('span');
  span.textContent = k;
  span.style.cssText = 'background: var(--color-background-secondary); border: 0.5px solid var(--color-border-tertiary); border-radius: var(--border-radius-md); padding: 4px 10px; font-size: 12px; color: var(--color-text-primary);';
  container.appendChild(span);
});
</script>
```

#### Design rules
- All text via CSS variables — never hardcode colours
- Status value: use `color: var(--color-text-secondary)` for Planned/Blocked/Ready;
  use `color: var(--color-text-success)` for Done/In Progress
- Section headers: 12px, font-weight 500, uppercase, letter-spacing 0.04em,
  `color: var(--color-text-secondary)`
- Cards: `background: var(--color-background-primary)`, `border: 0.5px solid var(--color-border-tertiary)`, `border-radius: var(--border-radius-lg)`
- Metric cards: `background: var(--color-background-secondary)`, no border, `border-radius: var(--border-radius-md)`
- No gradients, shadows, or emoji

---

### Step 4 — Follow-up

After rendering, offer 1–2 sentence commentary on the most actionable insight for the control.
Prioritise in this order, because it's the order of how well-grounded each signal is:

1. **An AWS gap** — a queried, observed shortfall in the live environment. Most concrete thing on
   the matrix.
2. **A `false` Drata flag** — a real record from Drata.
3. **A documentation gap** — a real GitBook search result.
4. Guessed/inferred detail — last, and only if nothing above applies.

If the control looks like it needs real work (not just a quick look), mention `/drive-iso27001
DCF-xxx` can drive it to completion.

**If the user then asks "what would it take to fix this?"** — risk, cost, or effort of closing the
gap — answer using the advisory shape in section 6 of [AWS Evidence Map](aws-evidence-map.md): T-shirt effort from real
resource counts, named blast radius (flag production explicitly), risk in *both* directions, and
directional cost. Dollar figures only if they ask for dollars, and say plainly if Cost Explorer is
denied rather than estimating. Commit to one recommended course. If closing the gap needs a
production change, note that `/change-request` raises the ticket. Keep the whole thing to a few
lines — anything longer belongs in `/drive-iso27001`.

---

## Improving this skill over time

This skill is designed to be iteratively improved, but stay lightweight — this is a single-control
snapshot, not a driver. Anything that needs staged Jira writes, a worklog, or batch/multi-control
scanning belongs in `/drive-iso27001` instead. Areas to extend within that constraint:

- **Additional metadata fields** — priority, due date, linked issues, parent task
- **Cross-control linking** — surface related DCF controls or CSIP sub-tasks
- **Audit readiness indicator** — a single ready/not-ready badge derived from the Drata flags
- **Evidence detail on request** — only if the user explicitly asks "what evidence is attached" for
  one control, a follow-up `Drata_listEvidence` call is reasonable; don't pull it by default
- **AWS checks** — extend the shared [AWS Evidence Map](aws-evidence-map.md) (owned by `/drive-iso27001`), never this
  file. Adding CLI recipes, profile names, or account IDs here is the specific duplication the split
  exists to prevent. Deeper multi-account infrastructure work belongs in `/drive-iso27001` too — this
  skill's AWS budget stays at ≤2 domains / ≤6 calls.
