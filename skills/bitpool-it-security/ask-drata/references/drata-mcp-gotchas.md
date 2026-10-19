# Drata MCP Gotchas

A living reference for operational quirks of the Drata MCP connection — things that are true
about *how the connection behaves*, confirmed by hitting them live, not things about any one
control or compliance workflow. Add to this file whenever a new Drata MCP gotcha is confirmed;
don't let the same mistake get rediscovered in a future session.

## Confirmed gotchas

### 1. Search mode can return empty even when the record exists

`Drata_searchControls` (and likely the other `Drata_search*` tools — `searchMonitoringTests`,
`searchRisks`, etc. — same underlying pattern) has two modes: **search** (`query` param set, AI
semantic/keyword lookup) and **list** (`query` omitted, structured filter + pagination). Search
mode is not reliable for existence checks — a query for a control that is very much present can
come back `{"data":[],"pagination":{"cursor":null}}`.

**Confirmed live (2026-08-07):** `Drata_searchControls(query: "DCF-92")` returned an empty
result. The control genuinely exists — `id: 25`, `code: "DCF-92"`, name "Encrypted Remote
Production Access" — and was only found by falling back to list mode. **Re-confirmed the same
day with the exact plain-English control name**: `Drata_searchControls(query: "Encrypted Remote
Production Access")` — a literal, exact match of the control's own `name` field — *also* returned
empty (both `search_mode: semantic` and `search_mode: keyword`). So this isn't a fuzzy-matching
weakness or a code-vs-name issue; search mode can miss an exact match of a record's own name.

**Rule:** never conclude "this control/record doesn't exist" from an empty search-mode result
alone. Fall back to list mode (drop `query`) and paginate. See gotcha #3 below — on this account,
prefer list/filter mode by default and treat `query`-mode search as unreliable in general, not
just for existence checks.

### 2. List-mode pagination is easy to under-read — follow the cursor to `null`

List mode returns `pagination.cursor` (a token for the next page) and, **only on the first page**
of a given filter set, `pagination.totalCount`. Results are sorted by internal `id` (descending by
default), **not** by the human-facing code (`DCF-xxx`) — so a code's numeric value gives no clue
which page it will land on, and the codes appear in an order that looks arbitrary. The **internal
`id`**, by contrast, fixes a record's position exactly — see *Seeking directly to one record* below.

**Confirmed live (2026-08-07):** finding `DCF-92` (`id: 25`) among Bitpool's 199 enabled controls
took **4 full pages of 50** — cursor chain `(none) → "aWR8MjA3" → "aWR8MTMx" → "aWR8NjE=" →
(found here, next cursor null)`. It did not appear on page 1, 2, or 3. (It also isn't in the
disabled-controls list — checked separately with `is_enabled: false`, 51 total — since it's an
active, enabled control.)

**Rule:**
- A single page of list-mode results is **never** enough to say "X is not in the results" or to
  report a count/list as complete. Keep calling with the returned `cursor` until the response
  comes back with `cursor: null` (or `pagination.cursor: null`), or apply a narrower filter
  (`is_ready`, `has_evidence`, etc.) that plausibly excludes the rest.
- If you only need a count, read `pagination.totalCount` off the **first page** rather than
  paginating and tallying — it's the authoritative total for that filter set. But a count is not
  the same as "I've seen every row" — don't treat a partial page's contents as the full list just
  because you read the total.
- When reporting results to the user mid-pagination, say so explicitly ("checked 3 of ~4 pages,
  still looking") rather than presenting an incomplete page as the final answer.
- Pagination completeness applies **within a filter set**. It does not mean you have seen every
  control — **archived** controls are returned by no `is_enabled` value at all. See gotcha #11.

**Seeking directly to one record.** The list-mode cursor is not opaque: it is base64 of
`id|<last id on the page>`, and rows sort by internal `id` descending. So when you know a
control's numeric id, fetch it in **one call** by passing `cursor` = base64 of `id|<id + 1>` with
`size: 1`. The cursors in the 2026-08-07 example above decode to `id|207`, `id|131` and `id|61` —
the page boundaries of that run.

```
Drata_searchControls(cursor: "aWR8MjY=", size: 1)     # base64("id|26")
  → id 25, DCF-92 — the control that took four pages above
```

Verified 2026-09-24 twice: `DCF-175` (id 211, via `aWR8MjEy`) and `DCF-92` (id 25, as shown).

Get the numeric id without paginating, from either:

- the control's Drata UI URL, `/compliance/control-details/<id>/overview` — the Drata Controls
  Register (`security-documentation/compliance/drata-controls-register.md`) stores one for every
  enabled control; or
- `Drata_listRequirements(framework_tag: ["ISO270012022"], expand: ["controls"])`, whose
  `controls.data[]` carries `{id, code, isReady, archivedAt}` per mapped control (capped at 10 per
  requirement — gotcha #11).

Rules for the seek:

- **Check `code` on the row that comes back.** If the target id is archived or disabled, the seek
  does not fail — it silently returns the next id down. Confirmed 2026-09-24: seeking archived
  `DCF-572` (id 13) with `aWR8MTQ=` returned `DCF-571` (id 12). A wrong code is a finding about
  the target's state (gotcha #11), not a reason to retry.
- **Default sort only.** Passing `sort` (`createdAt`, `updatedAt`) changes what the cursor means.
  Other tools' cursors use other formats — a `Drata_searchRisks` cursor decoded to
  `os_sort_tuple|%5B9%2C235%5D` — so do not assume the seek works beyond `Drata_searchControls`
  until it has been tested there.
- **Undocumented.** The cursor format is Drata's implementation detail and can change without
  notice. If a seek returns nothing sensible, fall back to paginating to `null`.
- **Seek for one record; paginate to enumerate.** When the question is "how many" or "which
  ones", a seek answers neither.

### 3. AI search mode (`query`) is broadly unreliable on this account — confirmed across tools

This isn't limited to `Drata_searchControls`. Investigating a 500 error hit on
`Drata_searchMonitoringTests(query: "DCF-92")` — initially suspected to be caused by DCF-92's
monitoring test being a newly created Custom Connections & Tests (CCT) test, Bitpool's first —
turned into a broader finding: **the failure has nothing to do with that specific test.**

**Confirmed live (2026-08-07), ruling out the "new custom test" hypothesis:**
- `Drata_searchMonitoringTests(query: "DCF-92")` → `500 Internal Server Error` (`code: 10010`),
  both `search_mode: semantic` (default) and `search_mode: keyword` explicitly.
- `Drata_searchMonitoringTests(query: "multi-factor authentication")` — a completely generic
  query, unrelated to DCF-92 or any custom test — **also 500'd**, identically. This proves the
  500 is a blanket failure of `query`-mode on this tool for this account, not something specific
  to the custom test's content, age, or `testSource: CUSTOM` status.
- Meanwhile, **the custom test itself is completely fine and fully retrievable** via list mode:
  `Drata_searchMonitoringTests(test_source: "CUSTOM", expand: ["controls"])` returned it cleanly
  — `id: 208`, "Encrypted Remote Production Access", `checkResultStatus: FAILED`,
  `testSource: CUSTOM`, `testId: 90000`, correctly linked to control `DCF-92`. So the test data,
  its control mapping, and its failing result are all healthy — only the AI-search *endpoint* is
  broken.
- `Drata_searchRisks(query: "encryption")` also **500'd** the same way, while
  `Drata_searchRisks(q: "encryption")` — the tool's separate, non-AI fuzzy keyword filter param,
  **not** the natural-language `query` param — worked fine (returned `0` results, a legitimate
  answer, not an error).
- `Drata_searchPolicies(query: "encryption")` returned an empty result rather than a 500 — and
  this one is now a **confirmed false negative**, not just a suspected OAuth-only limitation:
  `Drata_listPolicies(name: "encryption")` (the plain catalog browse, no AI search) found exactly
  one real match, "Encryption Policy" (`id: 11`, published, currently active). So the account
  genuinely has a matching policy; `searchPolicies`'s `query` mode simply failed to find it, same
  failure pattern as the other tools above. Use `Drata_listPolicies(name: ...)` instead of
  `Drata_searchPolicies` for policy lookups on this account.

**Summary table (2026-08-07, Bitpool account):**

| Tool | `query` (AI search) mode | Non-AI filter mode |
|---|---|---|
| `Drata_searchControls` | Silently empty (200, `data: []`) | ✅ Works (`is_ready`, `is_enabled`, etc.) |
| `Drata_searchMonitoringTests` | **500 Internal Server Error** | ✅ Works (`test_source`, `check_result_status`, etc.) |
| `Drata_searchRisks` | **500 Internal Server Error** | ✅ Works (`q` fuzzy filter, `status`, `treatment_plan`, etc.) |
| `Drata_searchPolicies` | Silently empty — **confirmed false negative** (real "Encryption Policy" exists) | N/A — no separate list mode on this tool; use `Drata_listPolicies` instead |

**Rule:** default to list/filter mode for every `Drata_search*` tool on this account. Treat the
natural-language `query` parameter as unreliable across the board — not just for one tool, and
not just for one specific record — until Drata/the MCP connection confirms the AI search backend
is fixed for this account. If asked to search Drata content by topic, prefer a tool's own
non-AI fuzzy param when one exists (e.g. `Drata_searchRisks(q: ...)`,
`Drata_listPersonnel(q: ...)`, `Drata_listEvidence(name: ...)`) over the `query` param.

### 4. `test_source` and `check_type` are different filters — don't conflate them

On `Drata_searchMonitoringTests`, `test_source` (who authored the test: `DRATA`, `CUSTOM`,
`EXTERNAL`, `ACORN`, `DRATA_LIBRARY`) and `check_type` (what kind of system it checks: `POLICY`,
`IN_DRATA`, `AGENT`, `INFRASTRUCTURE`, `VERSION_CONTROL`, `IDENTITY`, `TICKETING`, `HRIS`,
`OBSERVABILITY`, `CUSTOM`) both have a value literally called `CUSTOM`, but they answer different
questions and are not interchangeable.

**Confirmed live (2026-08-07):** for the DCF-92 custom test (`id: 208`), `test_source: "CUSTOM"`
correctly found it (1 result). Filtering by `check_type: "CUSTOM"` instead returned **0 results**
— the test's `check_type` is something else (its own field, unrelated to who wrote the test).

**Rule:** to find user-authored/Custom-Connections-and-Tests tests, filter on `test_source:
CUSTOM`, not `check_type: CUSTOM`. If asked "what type of check is this," read the `check_type`
value back from the record rather than assuming it matches authorship.

### 5. Personnel and Devices — scope gap RESOLVED 2026-08-25 (was: blocked account-wide)

**Superseded. Do not act on the original finding.** Between 2026-08-07 and 2026-08-25 the
`read:personnel` and `read:device` scopes were added to Bitpool’s MCP OAuth configuration.
Both domains now work. Re-probed live 2026-08-25:

- `Drata_listPersonnel(size: 1, include_total_count: true)` → 25 active personnel
- `Drata_listDevices(person: "<user-email>")` → device record, all five monitor checks
- `Drata_searchPersonnelCompliance(facets: [...])` → PASS/FAIL facets across 25 personnel
- `Drata_searchDeviceCompliance(facets: [...])` → device-check facets

Original finding, kept so the history stays legible: on 2026-08-07 every personnel/device tool
returned `403 "Missing required OAuth scope(s). Required one of: read:personnel"` (`code: 12330`).

**The durable rule outlives the fix.** A 403 missing-scope error is a connection-configuration
gap, never a badly-formed call. Do not retry with different parameters — it cannot help. Name the
scope and the tool that triggered it, and say it must be added in Drata under **Settings → MCP
OAuth Configuration** (a Bitpool admin action, outside what Hermes can grant). For a connection
that already exists, the relevant help-centre article is *Add new scopes to an existing
connection* — an existing connection does **not** pick up newly granted scopes on its own.

**Expiry.** MCP OAuth configurations carry an expiration date set at creation. If this connection
ever fails wholesale — every domain at once rather than one — check expiry before debugging
anything else.

### 6. `code_or_name` matches a substring, while `name` matches a prefix

Confirmed 2026-08-24. These two filters read as siblings and are not.

```
Drata_listRequirements(framework_tag=["ISO270012022"], code_or_name="5.3")
→ A.5.30 A.5.31 A.5.32 A.5.33 A.5.34 A.5.35 A.5.36 A.5.37 A.5.3 7.5.3 5.3
```

Eleven requirements for a query aimed at one. `code_or_name` is the client-side augmented filter
(it paginates up to 10 pages and matches anywhere in code or name); the server-side `name` filters
covered by gotcha #4 are prefix-anchored instead.

**Rule:** narrow with `framework_tag`, then read `name` on every returned item before using it.
Never treat a `code_or_name` result as a single lookup — and never assume the first element is the
one you asked for, because ordering is by internal id.

### 7. The risk register works; a wiki page claims it returns HTTP 402

Confirmed 2026-08-24 against the live account: `Drata_listRiskRegisters` → register id `1`
("Risk Management"); `Drata_searchRisks` → 47 active risks with working `facets`, `q`,
`controls`, `inherent_score_gte` and `residual_score_gte`; `Drata_updateRisk` applied and returned
the updated record.

The Private Wiki page `/security/compliance/rto-rpo-objectives` states the opposite — that the
module is unavailable on Bitpool's plan and those calls return 402. It is wrong, and it is
load-bearing wrong: a reader who believes it will design a spreadsheet register instead of using
the one that exists.

**Rule:** the API is the authority on what the API does. When a Bitpool document describes a Drata
capability, verify it with a call before relying on it, and report the contradiction rather than
silently working around it.

**Settled, recorded so it is not re-derived:** faceting `Drata_searchRisks` on `reviewerEmails`
returns **empty across every active risk**. Confirmed live 2026-08-26. That is the real and intended
state — a Bitpool decision of 2026-08-24 — not a broken facet, a missing scope, or an under-read
page. Do not report it as a gap, and never "fix" it by populating the field. The governing rule and
its clause reasoning live in `/manage-drata-control` `references/drata-fields.md` §7; do not restate
them here.

**Unresolved, recorded so it is not re-derived:** `approvedAt` was `null` on every active policy
(56 of them, 2026-08-24), while `security-documentation/ISMS/_tools/md-standardisation-log.md`
rule 2 moved approver records into the Drata Policy Centre on purpose. The API cannot distinguish "field unused by the UI" from
"nothing is approved". Do not assert either; the Policy Centre UI is the only check.

### 8. `framework_tag: "ISO27001"` silently returns zero — Bitpool’s tag is `ISO270012022`

Confirmed live 2026-08-25.

```
Drata_listRequirements(framework_tag: "ISO27001", size: 1, include_total_count: true)
  → {"data": [], "pagination": {"totalCount": 0}}     # no error — just empty

Drata_listRequirements(size: 1, include_total_count: true)
  → totalCount: 123, frameworkTag: "ISO270012022"     # the real tag
```

`ISO27001` is listed in the tool’s own `framework_tag` description as a common value, so it looks
correct and fails silently. Same shape as gotcha #1, but caused by a wrong enum value rather than
by search mode. Bitpool’s framework is **ISO 27001:2022** — `frameworkTag: "ISO270012022"`,
`frameworkSlug: "iso2022"`, `frameworkName: "ISO 27001:2022"`, **123 requirements**.

**Rule:** never trust a zero-result framework filter. Re-run without `framework_tag` and read the
`frameworkTag` off a returned row before concluding a framework has no requirements.

### 9. Tool exposure says NOTHING about scope — probe with an impossible identifier instead

**Corrected 2026-08-25.** An earlier edition of this entry asserted the exact opposite — that the
exposed tool list was the granted-scope manifest. **That was wrong, and it was disproved the same
day.** A tool being exposed here does not mean the scope behind it is granted:

```
Drata_updateEvidenceArtifacts(evidence: 999999999, url: "…")
  → 403 "Missing required OAuth scope(s). Required one of: update:evidence"   (code 12330)
```

`Drata_updateEvidenceArtifacts` and `Drata_deleteEvidenceArtifact` are both exposed on this
connection and **neither scope is granted** — of Drata’s four evidence scopes, the configuration
read on 2026-08-25 enabled only `read:evidence`. The tool list reflects what the MCP server
*implements*, not what this account is *entitled to*.

The mirror-image inference is equally invalid — and the tool list is **not static**. On
2026-08-25 `Drata_createControl`, `Drata_updatePersonnel`, `Drata_deleteRisk` and
`Drata_deleteVendor` were absent, and an earlier edition of this entry concluded the server did not
implement them. By 2026-09-24 all four were exposed, alongside `Drata_createEvidence`,
`Drata_updateEvidence`, `Drata_deleteEvidence`, `Drata_createBackgroundCheck` and
`Drata_uploadPersonnelDocument`. So a tool's absence is a dated observation about one session's
tool list, never a standing fact, and it says nothing about scope. Read the live tool list; treat a
verb missing from it as missing *today*. (`Drata_listRequirements`’s description telling you to
call `Drata_createControl` was read in 2026-08 as stale tool text, while the verb was absent. Its
presence now says no more about `create:control` than its absence did.)

**The only reliable test is the impossible-identifier probe.** Call the *update* verb with an
identifier that cannot exist, and read the status code:

| Response | Meaning |
|---|---|
| `403` + `Missing required OAuth scope(s)` | Scope is **not** granted |
| `404` record-not-found | Scope **is** granted — only the record was missing |

Nothing is mutated either way, because the target does not exist. All four verified 2026-08-25:

```
Drata_updateControl(control_code: "ZZZ-NONEXISTENT-PROBE-20260825", name: "probe") → 404 (17001)
Drata_updateRisk(risk_id: "ZZ-99999", title: "probe")                              → 404 (10000)
Drata_updateVendor(vendor_id: 999999999, notes: "probe")                           → 404 (10170)
Drata_updateEvidenceArtifacts(evidence: 999999999, url: "…")                       → 403 (12330)
```

**`create:*` scopes cannot be probed this way** — there is no impossible identifier to aim at, and
a well-formed call would actually create something. Leave them unknown unless a real creation has
already happened (see `SKILL.md` rule 8). Never probe a `delete:*` scope at all.

### 10. External accounts map to people only via `Drata_lookupUserIdentity(expand: ["identities"])`

Confirmed live 2026-08-25. Drata links third-party accounts — GitHub logins, IdP accounts — to a
Drata user through an **identities** collection, and **nothing else in this connection exposes it**.
Personnel tools will not find them: a GitHub login is not a personnel field, so
`Drata_listPersonnel(q: "<github-login>")` returns nothing and that absence means only that you
used the wrong tool.

```
Drata_lookupUserIdentity(email: "<user-email>", expand: ["identities", "roles"])
  → identities[]: each with username, identityId, connectionId, hasMfa,
                  connectedAt, disconnectedAt
```

Each identity carries a **`connectionId`** naming the provider it came from. Resolve the mapping
live — connections are added, removed and reconnected. When probed on 2026-08-25: `connectionId 2`
= Microsoft 365 / IdP, `connectionId 18` = a connection whose identities were all disconnected,
`connectionId 20` = **GitHub**, whose identities were all created `2026-08-24T05:31:19Z`.

**Two things this is the only way to establish:**

1. **Whether one person holds several accounts on one provider.** On 2026-08-25 two Drata users
   each held two GitHub identities. That is precisely what a "unique accounts" monitoring test
   objects to, and it is invisible from the test record itself. The four logins were recorded in
   this entry's earlier editions and remain in this file's git history; they are left out of the
   current text because this skill ships to every Bitpool user (see `SKILL.md`, *Editing this
   skill*). Re-read them live with the call above before acting on them.
2. **When a provider connection was established.** `createdAt` on the identities dates the
   connection. This matters because a monitoring test evaluating a brand-new connection **passes
   before the connection exists and fails once it does** — which reads as a regression and is not
   one. Check identity `createdAt` against the test's `failedSince` before diagnosing a cause.

**`Drata_searchMonitoringTests` does not expose which entities failed a test** — only
`checkResultStatus`, `lastPassedAt` and `failedSince`. So for any identity-shaped test failure, the
identities collection is the diagnosis and the Drata web UI's test page is the confirmation. Do not
report a cause from the test record alone; it does not contain one.

### 11. Controls have three states, and `is_enabled` only reaches two

**Confirmed live 2026-09-24.** `Drata_searchControls(is_enabled: true)` returns 200 controls and
`is_enabled: false` returns 51, both paginated to a null cursor — but **archived** controls are in
neither, however far you paginate. All 51 "disabled" controls carry `archivedAt: null`: disabled
and archived are different states, not synonyms.

Archived controls surface **only** inside a requirement's `controls` expansion:

```
Drata_listRequirements(framework_tag: ["ISO270012022"], code_or_name: "A.7.5", expand: ["controls"])
  → controls.data[]: DCF-571 (archivedAt null), DCF-572, DCF-573, DCF-749 (archivedAt set)
```

That expansion carries `id`, `code`, `controlNumber`, `isReady` and `archivedAt` — **no `name`
and no `description`**. An archived control's text is readable only in the Drata UI. A cursor
seek to its id (gotcha #2) skips it and returns the next id down.

**Rule:** never conclude a control does not exist from the two `is_enabled` lists. Never report a
control list as complete without saying which of the three states it covers.

**The expansion is capped at 10.** `controls.data[]` returns at most 10 entries regardless of
`size` (confirmed by re-querying one requirement with `size: 1` and still receiving 10), sorted
`isReady` ascending, then control number. Archived controls read `isReady: true`, so they sort
into the tail the cap removes. Wherever `controls.totalCount > 10`, reconcile against the enabled
and disabled lists before concluding the requirement hides no archived controls. On 2026-09-24
exactly one ISO 27001:2022 requirement exceeded the cap (`totalCount: 16`); a full sweep of all
123 requirements found four archived controls — `DCF-375`, `DCF-572`, `DCF-573`, `DCF-749`.

## Tools swept and confirmed clean (2026-08-07)

Beyond the gotchas above, a full pass through every other read tool in this MCP came back with
no issues — worth recording so a future session doesn't waste time re-suspecting tools that are
actually fine: `Drata_listWorkspaces`, `Drata_listPolicies`, `Drata_listEvidence`,
`Drata_listRequirements`, `Drata_listRiskRegisters`, `Drata_listVendors`, `Drata_getVendor`,
`Drata_listVendorDocuments`, `Drata_listVendorSecurityReviews`, `Drata_lookupUserIdentity`
(including `expand: ["roles"]`).

**Write tools: superseded 2026-08-21.** This sweep predates Bitpool granting write scopes, and
recorded every `Drata_create*`/`Drata_update*`/`Drata_delete*` tool as deliberately untested. That
is **no longer true for all of them** — `Drata_createRisk`, `Drata_updateRisk` and
`Drata_updateControl` have since been exercised against the live account and work, each with its
own trap. **The authority is `SKILL.md` rules 8–10, not this paragraph.** Read it before any write
call. Every write verb that rule 8 does not mark as working remains untested — including those that
have appeared in the tool list since (observed 2026-09-24).

**Rule (personnel/device 403s):** superseded — see gotcha #5. Those scopes are granted as of
2026-08-25. The general handling of any missing-scope 403 is recorded there.

## Granted scope matrix — probed live 2026-08-25

Every row below was established on 2026-08-25 by an actual call against Bitpool’s account, or by
reading its configuration, not read off documentation — except the rows marked *observed
2026-09-24*, which record only that a tool appeared in the tool list, with the scope its own text
names; nothing was called. The live-result counts are what each probe returned that day, not
figures to match. Re-probe rather than trusting this table if a call behaves unexpectedly — scopes
change (see gotcha #5). Drata publishes 27 scopes in total; this is where Bitpool sits.

**Read scopes — all confirmed working.**

| Scope | Probe | Live result |
|---|---|---|
| `read:workspace` | `Drata_listWorkspaces()` | 1 workspace — “Bitpool” (id 1) |
| `read:framework` | `Drata_listRequirements(size: 1)` | 123 requirements (`ISO270012022`) |
| `read:policy` | `Drata_listPolicies(size: 1)` | 60 policies |
| `read:assigned-policies` | `Drata_listPolicies(assigned_to_user: …)` | 1,496 assignment records |
| `read:risk` | `Drata_searchRisks(size: 1)` | 48 risks |
| `read:risk-registers` | `Drata_listRiskRegisters(size: 1)` | 1 register — “Risk Management” |
| `read:evidence` | `Drata_listEvidence(size: 1)` | 151 evidence buckets |
| `read:vendor` | `Drata_listVendors(size: 1)` | 81 total / 35 current / 46 archived |
| `read:vendor-document` | `Drata_listVendorDocuments(vendor_id: 135)` | `200`, 0 docs on that vendor |
| `read:vendor-security-review` | `Drata_listVendorSecurityReviews(vendor_id: 135)` | 1 review |
| `read:personnel` | `Drata_listPersonnel` / `…searchPersonnelCompliance` | 25 active personnel |
| `read:device` | `Drata_listDevices` / `…searchDeviceCompliance` | device + all 5 checks |
| `read:monitor-test` | `Drata_searchMonitoringTests(size: 1)` | 132 tests |
| `read:users` / `read:user` | `Drata_lookupUserIdentity(email, expand: ["roles"])` | account + 9 roles |

Two things have **no scope of their own** in Drata’s published table yet work fine here:
`Drata_getCompany()` (returns Bitpool PTY LTD and account entitlements) and `Drata_searchControls`
(199 controls). There is no `read:control` scope — control *reads* are not separately gated, even
though `create:control` and `update:control` exist as write scopes.

**Write scopes — each probed, or explicitly marked unknown. Never inferred from the tool list
(gotcha #9).**

| Scope | Evidence | Status |
|---|---|---|
| `update:control` | `404` probe — impossible control code | ✅ granted |
| `update:risk` | `404` probe — `ZZ-99999` | ✅ granted |
| `update:vendor` | `404` probe — vendor `999999999` | ✅ granted |
| `create:risk` | `Drata_createRisk` actually created `CR-05` on 2026-08-21 | ✅ granted (by use) |
| `update:evidence` | **`403` probe** on `Drata_updateEvidenceArtifacts` — `Missing required OAuth scope(s)`. `Drata_updateEvidence` (bucket details) *observed 2026-09-24*; its text names the `evidence-put` permission, and whether the same scope gates it is unprobed | ❌ **not granted** |
| `create:evidence` | Drata config — only `read:evidence` of the four evidence scopes is enabled. `Drata_createEvidence` *observed 2026-09-24*; not safely probeable | ❌ not granted (config) |
| `delete:evidence` | Drata config, as above. Also gates `Drata_deleteEvidence` (whole bucket), *observed 2026-09-24* | ❌ not granted (config) |
| `create:vendor` | `Drata_createVendor` exposed, never exercised, not safely probeable | ❓ **unknown** |
| `create:control` | `Drata_createControl` *observed 2026-09-24* (absent 2026-08-25); not safely probeable | ❓ **unknown** |
| `update:personnel` | `Drata_updatePersonnel` *observed 2026-09-24* (absent 2026-08-25); probeable with an impossible `personnel_id` (gotcha #9), not yet done | ❓ **unknown** |
| `delete:risk` | `Drata_deleteRisk` *observed 2026-09-24* (absent 2026-08-25); never probed | ❓ **unknown** |
| `delete:vendor` | `Drata_deleteVendor` *observed 2026-09-24* (absent 2026-08-25); never probed | ❓ **unknown** |
| `create:background-checks` | `Drata_createBackgroundCheck` *observed 2026-09-24*; its text says the Create ability on Personnel is also required; not safely probeable | ❓ **unknown** |
| `create:user-document` | `Drata_uploadPersonnelDocument` *observed 2026-09-24*; its text says it also needs an Evidence scope (create or update), neither granted at the 2026-08-25 configuration, and `create-restricted:personnel` for offboarding evidence; not safely probeable | ❓ **unknown** |

**Evidence is read-only on this connection, and that is deliberate.** The configuration read on
2026-08-25 enabled exactly one of Drata’s four evidence scopes. `Drata_updateEvidenceArtifacts`
403s when called (probed). The other evidence write tools now in the list split two ways.
`Drata_createEvidence` sits behind `create:evidence`, and `Drata_deleteEvidence` and
`Drata_deleteEvidenceArtifact` behind `delete:evidence` — both scopes not granted per the 2026-08-25
configuration, and never probed (gotcha #9). Only `Drata_updateEvidence`'s gate is genuinely unknown:
its text names the `evidence-put` permission, and an impossible `evidence_id` probe settles whether
`update:evidence` gates it. Evidence upload and deletion remain human actions in the
Drata UI — do not offer to do them. The evidence *text* drafted for the person doing the upload is
still governed — `SKILL.md` rule 16.

**A granted scope is still not a tested verb.** This table records which *scopes* the connection
holds. Whether the verb behind a granted scope works, and what it does wrong, is a separate
question answered by `SKILL.md` rule 8. Read that before any write call.

**Unknown means unknown.** Every ❓ row is neither probed nor configuration-confirmed. Do not
report one as granted or as absent — say it is untested. An `update:*` row can be settled with the
impossible-identifier probe; for a `create:*` or `delete:*` row, if it matters, ask rather than
find out by creating or deleting something.

**Role did not narrow anything for the account that ran these probes** — the Head of Information
Security's. When probed on 2026-08-25, `Drata_lookupUserIdentity` returned that account holding
every role — `ADMIN`, `TECHGOV`, `RISK_MANAGER`, `CONTROL_MANAGER`, `REVIEWER`, `PEOPLE_OPS`,
`TRUST_CENTER_MANAGER`, `TRUST_CENTER_REVIEWER`, `EMPLOYEE`. Access is the intersection of scope and
role, so for that account the configured scope is the only real limit. A less-privileged
colleague on the same connection will see less — a tool working here does not prove it works for
them.

## Writable free-text fields

Every free-text field the connection's write tools accept, read from the live tool schemas on
2026-09-25 — nothing was called. Caps are what the schema declares unless marked as hit live. A
field listed here says nothing about whether its scope is granted (the matrix above) or whether any
skill may write it (`SKILL.md`, *Drata write policy by skill*). **What the text says is not this
file's business:** for a field in the Security Drata register it is `/bitpool-writing-standard`'s
(`SKILL.md` rule 16).

| Verb | Free-text fields (cap) | Trap |
|---|---|---|
| `Drata_createRisk` | `title` (required); `description` (required; **768 — rejects, does not truncate; hit live 2026-08-21**); `treatment_details`; `custom_fields[].value` | `treatment_details` — with both dates, the residual pair and `reviewers` — is **silently dropped** unless `treatment_plan` is set to something other than `UNTREATED`. No `riskId` parameter (`SKILL.md` rule 9) |
| `Drata_updateRisk` | `title`; `description`; `treatment_details`; `custom_fields[].value` (`null` clears) | The same silent drop: send `treatment_plan` in the same call — whether an omitted `treatment_plan` on an already-treated risk is enough is unprobed. The schema declares no cap on `description`; the 768 hit on create is presumably the same field, so count before sending. An omitted field is left unchanged, so omission never clears text |
| `Drata_updateControl` | `name` (191); `description` (30,000); `activity` (768); `question` (768); `code` (20); `custom_fields[].value` (`null` clears) | Relation fields sent in the same call **replace** (`SKILL.md` rule 9) |
| `Drata_createControl` | `name` (191), `description` (30,000), `code` (20) — all required; `activity` (768); `question` (768); `custom_fields[].value` | `code` must be unique — `400 DUPLICATE_CONTROL_CODE`. Evidence is linked afterwards, never at creation |
| `Drata_createEvidence` | `name` (255, required); `description`; `implementation_guidance`; `artifact_name` (a hint — an uploaded file's own name overrides it); `file_name`; `url`; `ticket_url` (Jira format, regex-validated) | The tool text says `owner` and `renewal_schedule_type` are required on every create, though the schema marks only `name`. At most one content source. `upload_files: true` returns a Drata-hosted upload link and creates nothing until the person presses Confirm; a `url`, `ticket_url` or empty create is immediate |
| `Drata_updateEvidence` | `name` (255); `description` (an empty string **clears** it); `implementation_guidance` | Edits the bucket only — no `url`, `ticket_url` or file parameters, and sending one errors. `control_codes` / `control_ids` **replace** the whole mapping. `evidence_name` is documented as a case-insensitive partial match, untested against the prefix behaviour in `SKILL.md` rule 4 — prefer `evidence_id` |
| `Drata_updateEvidenceArtifacts` | `artifact_name`; `url`; `ticket_url`; `add_artifacts[].artifactName` | No metadata-only edit of a file: renaming or re-dating one means supplying its contents again with `replace_file` |
| `Drata_createVendor` / `Drata_updateVendor` | `name` (required on create); `notes`; `services_provided`; `data_stored`; `environment_access`; `operational_impact`; `location`; `password_policy`; `contact_at_vendor`; `contacts_email` (semicolon-separated); `cost` (a string, in cents); `url`, `privacy_url`, `terms_url`, `trust_center_url`; `custom_fields` | No caps declared. `Drata_updateVendor` is a partial update — omitted fields are left unchanged |
| `Drata_updatePersonnel` | `not_human_reason` (30,000; required whenever `employment_status` is `OUT_OF_SCOPE`); `custom_fields[].value` | Setting `started_at` by hand disables IdP/HRIS sync of that field for that person |
| `Drata_createBackgroundCheck` | `url` (required; the only evidence source) | Not idempotent — a retry after a timeout files a second record. `filed_at` is the report's date and is required |
| `Drata_uploadPersonnelDocument`, the delete verbs | None | — |

**Tool text is field guidance written for every Drata customer, not a requirement of the API.** Two
passages shape content and need reading correctly:

- `Drata_createRisk` describes `description` as covering the *"affected systems or processes"* and
  `title` as identifying the risk's *"scope"*. That invites a list of systems; the API does not
  require one. In a Security Drata field the content is governed by `SKILL.md` rule 16, not by the
  tool's wording.
- `Drata_createRisk` (`title`, `description`) and `Drata_createControl` (`name`, `description`,
  `code`) say the text must come from the user and never be invented. Text the user has read and
  approved verbatim in an approval block comes from the user; text they have not seen does not.
  Never call either with unapproved text.

## Drata Help Centre — the documentation the MCP does not carry

The MCP is a **data plane only**. It reads and writes the tenant’s own records; it has no
documentation tool, no equivalent of the Private GitBook MCP server’s `searchDocumentation` /
`getPage` / `askQuestion`, and no documentation scope. Product documentation therefore has to come
from the public help centre.

The help centre is **public, unauthenticated, and already published in an LLM-oriented format** —
there is nothing to request from Drata:

- **`https://help.drata.com/llms.txt`** — the index. When read on 2026-08-26: ~164 KB, 845
  articles across 12 sections, each with a one-line description and a `.md` link. Start here.
- **Append `.md` to any article URL** for clean markdown (`text/markdown`). Example:
  `https://help.drata.com/en/articles/13379899-drata-mcp-setup-usage-guide.md`.
- `https://help.drata.com/sitemap.xml` also exists. `llms-full.txt` does **not** (404).

**Do not fetch the plain HTML article URL.** The help centre renders an enormous global navigation
into every page, which swamps the article body — a `web_extract` of the HTML returns what looks like a
sitemap and reports the article as having no content. This is a false negative, not a missing
article. The `.md` suffix is the correct access path.

Articles that answer questions this skill set actually hits:

| Article | Why it matters |
|---|---|
| `13379899-drata-mcp-setup-usage-guide.md` | The full 27-scope table, roles per scope, and *Add new scopes to an existing connection* — the source for gotcha #5 |
| `9415404-resource-guide-for-custom-tests.md` | Confirms the Resource Guide is **UI-only** — 2.8 KB, no schemas. See the rule below |
| `13403932-advanced-editor-in-the-test-builder.md` | Advanced Editor semantics for `/create-drata-test` |
| `11632648-introduction-to-the-drata-control-framework-dcf.md` | What a DCF code is |
| `6116040-risk-treatment-plan-guidance.md` | Drata’s own treatment-plan framing, for `/manage-drata-control` |
| `13521519-set-up-oauth-for-the-drata-api.md` | OAuth setup underlying every scope question here |

**Checked, and it changes nothing: the help centre does NOT relax `/create-drata-test`’s
paste-the-schema rule.** The “Resource Guide for custom tests” article is 2.8 KB, contains zero
code blocks, and only explains how to open the Resource Guide inside the product UI. It does not
carry per-resource example data structures. That skill’s rule — never fabricate a resource schema,
always have the user paste the real “Example data structure” — stands unchanged.

## Custom fields and formulas — defined in the UI, populated by id

Drata's **Custom Fields & Formulas** feature adds fields to a record type that has no native field
for a value. It is **on** for Bitpool's account: vendor records carry custom fields
(`/manage-drata-vendors`, `references/field-contract.md`). Bitpool's Drata administrator confirmed
the following from the Drata UI on 2026-10-06; none of it was exercised through the MCP.

| | |
|---|---|
| **Where a field can be defined** | Assets, controls, personnel, risks and vendors |
| **Data types** | Short answer, URL and dropdown among them — the UI lists the full set |
| **Custom formulas** | Can be applied to risk fields such as inherent likelihood and residual risk. Bitpool does not use them, and the administrator considers them unlikely to be needed (2026-10-06) |

What the connection does with them:

- **Definitions are a UI action.** No MCP verb creates or edits a custom field definition. When a
  record needs a value that has no field, ask the user to define one in the Drata UI, then capture
  its id — writes address a custom field **by id**, never by its label.
- **Values go through `custom_fields` on the write verbs** — `Drata_createRisk`,
  `Drata_updateRisk`, `Drata_createControl`, `Drata_updateControl`, `Drata_createVendor`,
  `Drata_updateVendor` and `Drata_updatePersonnel` (*Writable free-text fields* above). No asset
  verb was in the tool list when observed on 2026-10-06, so a custom field on an asset is read and
  written in the UI.
- **An empty `customFields` array means no field is defined on that record type — not that the
  feature is missing.** Sampled controls return `customFields: []`; that is the state of the
  definitions, not of the account.
- **A required custom field makes a create a one-call write.** Drata rejects a create that omits a
  required custom field with a `400`, so the values go inline in the create call — confirmed for
  vendors in `/manage-drata-vendors`.

## Where this fits vs. the other Drata skills

- **This skill (`ask-drata`)** — connection-level operational notes only. No workflow, no
  per-control logic.
- **Which skills may write to Drata**, and which verbs each may call, is the *Drata write policy by
  skill* table in `SKILL.md` — not this file, and not any skill's own claim.
- **What the words say** in a Security Drata field is `/bitpool-writing-standard`'s (section
  `bitpool-general`; `SKILL.md` rule 16). This file records only what the connection does with the
  text — see *Writable free-text fields* above.
- `/create-drata-test` already independently documents gotcha #1
  for its own narrower use case (resolving a control before designing a Custom Test) — that's
  expected duplication, not a conflict; this skill is the general home for the pattern across
  *all* Drata MCP tool calls, not just test design.
- `/drata-control-insights`,
  `/drive-iso27001`, and
  `/create-devsecops-ticket` are workflows that consume
  Drata data — they should assume the gotchas here apply, not re-derive them. In particular,
  `create-devsecops-ticket`'s control-mapping step leans on gotcha #1 (don't trust `query`-mode
  search) and gotcha #2 (follow list-mode `cursor` to `null` before treating the code→id lookup
  as complete).

## Improving this skill over time

When a new Drata MCP quirk is confirmed live (an empty result that shouldn't be empty, a filter
that behaves unexpectedly, an undocumented field, a permission error that's actually something
else), add it as a new numbered entry under **Confirmed gotchas** — include the date, the exact
call and response that revealed it, and the rule to follow. Keep entries about the *connection's
behavior*, not about specific controls' content or a specific compliance workflow's steps — those
belong in `create-drata-test`, `drata-control-insights`, or `drive-iso27001` instead.
