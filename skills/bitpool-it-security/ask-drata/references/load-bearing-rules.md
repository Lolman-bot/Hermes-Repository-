# Ask Drata — the load-bearing rules in full

The complete text of the numbered rules summarised in `SKILL.md`. Numbers match the summary and are
cited by other skills (e.g. "`/ask-drata` rule 10"), so never renumber — append. Tool names are the
Drata MCP server's own (`Drata_searchControls`, …); in Hermes they carry an `mcp_<server>_` prefix,
so find the live names with `tool_search`.

Each rule changes what you're entitled to conclude from a Drata response, or what you may send to one.

Restated here because each one changes what you're entitled to conclude from a Drata response, or what you may send to one.

1. **Never conclude a record doesn't exist from an empty search-mode result.** On this account, `query`-mode search across the `Drata_search*` tools is broken account-wide in **two distinct ways** — and the difference matters, because one is diagnosable and the other is indistinguishable from a genuine "no results":

   | Failure mode | Tools |
   |---|---|
   | **Silent empty** — HTTP 200, `data: []` | `Drata_searchControls`, `Drata_searchPolicies` |
   | **Hard 500** | `Drata_searchMonitoringTests`, `Drata_searchRisks` |

   Confirmed 2026-08-20 with generic single-word queries (`"encryption"`), in both `semantic` and `keyword` modes, with and without `workspace_id`, at sizes 5–50. It is not caused by any specific record or query text. **Default to list/filter mode.**

2. **Passing `query` silently discards your filters.** `Drata_searchControls(query="encryption", is_ready=False)` returns `[]` — the `is_ready` filter is dropped rather than applied, because any `query` value routes the call down the broken AI path. So `query` is not harmless-if-ignored: adding it turns a working list call into an empty one. **Omit `query` entirely** when you want results; never pass it "just in case".

3. **Follow list-mode pagination to `cursor: null`.** A single page is never enough to say "X isn't in the results". Results sort by internal `id`, not by `DCF-xxx` code, so a code's number gives no clue which page it lands on. If you only need a count, read `pagination.totalCount` off the first page — but a count is not the same as having seen every row. Say so explicitly when reporting mid-pagination. **For one known control, seek instead of paginating:** the cursor is base64 of `id|<n>`, so `cursor` = base64 of `id|<id + 1>` with `size: 1` returns that control in one call — then check the returned `code`, because an archived or disabled target silently yields its neighbour. And completeness is only ever **within a filter set**: archived controls appear under no `is_enabled` value. Both in `references/drata-mcp-gotchas.md`, gotchas #2 and #11.

4. **Server-side `name` filters match a PREFIX, not a substring.** A mid-name word returns zero for a record that plainly exists, which reads exactly like absence. Confirmed 2026-08-20:

   | Call | Result |
   |---|---|
   | `Drata_listPolicies(name="Data")` | 3 results, including **Data Classification Policy** |
   | `Drata_listPolicies(name="classification")` | **0** — the same policy, invisible |
   | `Drata_listEvidence(name="Web")` | 2, including **Web Filtering** |
   | `Drata_listEvidence(name="Filtering")` | **0** |

   Match on the **first word** of the name, or list unfiltered and filter client-side. Note that `Drata_listPolicies`' own parameter docs claim "partial match supported" — that is wrong; don't trust it over this.

   **The client-side "augmented" filters behave differently — those really are contains-matched:** `Drata_listRequirements(code_or_name="5.13")` finds `A.5.13`, and `Drata_listEvidence(control_code="DCF-780")` resolves correctly. So: server-side `name` = prefix, augmented filter = contains.

5. **Prefer a tool's own non-AI fuzzy param over `query`** where one exists — `Drata_searchRisks(q: …)` (confirmed working 2026-08-20, returned 11 matches with `totalCount`), `Drata_listPersonnel(q: …)`, `Drata_listEvidence(name: …)`. For policies, use `Drata_listPolicies(name: …)` rather than `Drata_searchPolicies` — subject to the prefix caveat in rule 4.

6. **`test_source` and `check_type` are different filters.** Both have a value called `CUSTOM`, but they answer different questions. To find user-authored tests, filter `test_source: CUSTOM` — `check_type: CUSTOM` returns something else entirely.

7. **A missing-scope 403 will not yield to different parameters.** The 403 body names the scope it wants — quote it, because fixing it is a Bitpool admin action in Drata under **Settings → MCP OAuth Configuration**, not something to retry around. Adding a scope to a connection that already exists requires the *Add new scopes to an existing connection* step — the connection does not pick it up on its own. **The 2026-08-20 blocked list is superseded:** `read:personnel`, `read:device` and `Drata_getCompany` were all re-probed live on **2026-08-25** and now work. The probed matrix — as of 2026-08-25, 14 read scopes granted, 4 write scopes granted and 3 confirmed **not** granted; every other write scope, including those behind the write tools exposed since (rule 8), is unknown — is in `references/drata-mcp-gotchas.md`. Re-probe rather than trusting any list; scopes change, and this one already has.

8. **Drata is no longer read-only — but only for specific verbs.** Changed **2026-08-21**, when
   Bitpool granted write scopes. ✅ means the verb was exercised live and its traps recorded; the
   ⛔ rows, and the scope on the `Drata_updateVendor` row, were verified by probing or by reading
   the connection's configuration. None of it is inferred from the tool list:

   | Verb | Status |
   |---|---|
   | `Drata_createRisk` | ✅ **Works** — created `CR-05`. Traps in rule 9. |
   | `Drata_updateRisk` | ✅ **Works** — amended `owners`, `reviewers`, scores, `treatment_details`, `control_ids`. *(A capability probe only. Bitpool sets no reviewers — decision 2026-08-24; see `/manage-drata-control` `references/drata-fields.md` §7.)* |
   | `Drata_updateControl` | ✅ **Works** — attached a policy via `policy_names`. Relation fields **replace**; see rule 9. |
   | `Drata_updateVendor` | ❓ **Scope granted, verb not yet exercised** — `update:vendor` answered the impossible-identifier probe with `404` (2026-08-25), but no live update is recorded here, so its traps are unknown. Read the returned record back after every call. |
   | `Drata_createVendor` | ❓ **Scope unknown** — `create:vendor` is not safely probeable, and no creation is recorded here. |
   | `Drata_updateEvidenceArtifacts` | ⛔ **Exposed but 403s — `update:evidence` is NOT granted.** Probed 2026-08-25: `403 Missing required OAuth scope(s). Required one of: update:evidence`. This settles the open question in earlier editions: the claim *"evidence upload is a human action"* — in `/manage-drata-control` and this skill — is **correct** for this connection. Evidence *text* is a separate matter — rule 16. |
   | `Drata_deleteEvidenceArtifact` | ⛔ **Exposed, but `delete:evidence` is NOT granted** — of Drata's four evidence scopes, the configuration read on 2026-08-25 enabled only `read:evidence`. Permanently deletes one file if ever enabled. Destructive — never call it merely to test the scope. |
   | Every other write verb | ❓ **Unverified.** Observed exposed on 2026-09-24, scopes unprobed: `Drata_createControl`, `Drata_createEvidence`, `Drata_updateEvidence`, `Drata_updatePersonnel`, `Drata_deleteRisk`, `Drata_deleteVendor`, `Drata_deleteEvidence`, `Drata_createBackgroundCheck`, `Drata_uploadPersonnelDocument`. `Drata_createEvidence` and `Drata_deleteEvidence` sit behind scopes the 2026-08-25 configuration did not grant. An earlier edition of this rule called four of these verbs "not implemented by this MCP server"; they appeared later. |

   **Never conclude from this table, or from memory, that a verb is absent or available.** The
   tool list changes between sessions. Before relying on any write verb not marked ✅: confirm it
   is in this session's live tool list, then settle an `update:*` scope with the
   impossible-identifier probe (rule 13) and record the result in the scope matrix. A `create:*`
   or `delete:*` scope is never probed; it stays unknown until a real, approved use settles it.

   **A verb being authorised is not permission to use it unprompted.** Scope is account-level, so
   every skill is handed the same verbs — which skill may actually use them is a policy decision,
   and it is recorded in one place: **"Drata write policy by skill"** below. Read that table before
   any write; do not infer permission from this one.

9. **Every write verb tested so far has a trap that either fails silently or rejects late.**
   Confirmed 2026-08-21, each by hitting it, except where a line says otherwise:

   - **`Drata_createRisk` caps `description` at 768 characters.** Returns `400 … maxLength:
     description must be shorter than or equal to 768 characters`. It **rejects**; it does not
     truncate. Count the string before calling.
   - **`Drata_createRisk` has no `riskId` parameter.** The register assigns its own. A `GV-33`
     agreed with the user in advance came back as **`CR-05`**. Treat any pre-agreed id as
     advisory, report the one Drata actually gave, and fix every downstream reference.
   - **`control_ids` takes numeric control ids, not DCF codes.** `DCF-745` is `217`, `DCF-5` is
     `169`, `DCF-69` is `88`. Read them from `Drata_listRequirements(expand=["controls"])` or
     from the `control-details/<id>/overview` URL.
   - **`owners` / `reviewers` silently drop non-admin users.** A resolved user without an
     admin / risk-management role is dropped with **no error**. Always compare the returned
     arrays against what you asked for, and say so when reporting.
   - **`Drata_updateRisk` cannot clear a date.** Omitting a field means "unchanged" and the
     parameter's default is `null`, so there is no way to express "set
     `anticipatedCompletionDate` back to empty". Clearing a date is a UI action.
   - **`Drata_updateControl` relation fields REPLACE, they do not append** — `owners`,
     `policy_ids` / `policy_names`, `report_ids`, `requirement_ids`, `test_ids`. Read the
     control's current values and send them all, or you silently unlink everything else.
   - **`treatment_details`, both completion dates, the residual pair and `reviewers` are silently
     dropped unless `treatment_plan` is set to something other than `UNTREATED`** — on both
     `Drata_createRisk` and `Drata_updateRisk`. Recorded from the tools' own text (2026-09-24), not
     yet hit live. Send `treatment_plan` in the same call and read the returned record back.

   Every writable free-text field, with its length cap and its trap, is inventoried in the
   *Writable free-text fields* section of `references/drata-mcp-gotchas.md`.

10. **Three control status flags are unreliable as gap signals — resolve each from its own list.**

    - **`hasEvidence` lies in both directions.** Confirmed 2026-08-21 on `DCF-745`: the control
      reported `hasEvidence: true` while `Drata_listEvidence(control_code="DCF-745")` returned
      **nothing**. The flag was true because of `evidenceIds.invalidExternalEvidenceIds: [54]`,
      and evidence `54` is *"Independent Board of Directors"* — which belongs to **`DCF-41`**.
      The flag counted an invalid pointer at another control's artefact as evidence. A populated
      `invalidExternalEvidenceIds` or `invalidReportIds` on a control response is itself a finding
      worth raising.

      **But do not conclude from that case that the list is authoritative — corrected 2026-08-28.**
      The two signals count **different populations**, so neither settles the question alone.
      `flags.hasEvidence` (identical to the server-side `has_evidence` filter — one field, not two)
      tracks **manually attached external evidence** and deliberately ignores Drata's auto-seeded
      buckets. `Drata_listEvidence` covers **Evidence Library buckets only**. Measured across the
      account on 2026-08-28 — a dated snapshot of the gap's size, not a baseline to match:
      **79 of 199 enabled controls disagreed** — 21 flagged `true` with no bucket, 58 held a
      bucket while flagging `false`.

      **An empty `Drata_listEvidence` result means "no bucket". It NEVER means "no evidence."** The
      external-evidence layer is **unreachable on this connection**: `expand=["evidenceIds"]`,
      `["evidence"]`, `["externalEvidence"]` and `["reports"]` are all **silently dropped** by
      `Drata_searchControls`, and `Drata_getEvidence` and `Drata_listEvidenceArtifacts` both return
      `multi_artifact_not_enabled` account-wide. Confirmed the hard way on 2026-08-28: a control
      flagged `true` with an empty bucket list was written into the risk register as having no
      evidence, and the control owner then confirmed the artefact was there all along. Whatever
      you conclude about evidence state is a reading on the day: report it as one, and before any
      of it goes into a Drata text field, rule 16 applies.

      So report **"evidenced"** only when the control filter returns a bucket. Flag `true` beside an
      empty list is **"external evidence indicated, not readable via API — verify in the Drata UI"**,
      never a gap.
    - **Evidence age is `versions[].createdAt`, never the bucket's `updatedAt`.** Pass
      `expand=["renewalSchemaAndVersions"]`: `renewalSchema.renewalDate` is the lapse date and
      equals newest `versions[].createdAt` plus the schedule interval — confirmed on 2026-08-28 for
      49 of 49 buckets carrying both, zero exceptions. `updatedAt` is a **bulk system touch**: that
      day 104 of 151 buckets shared one date and 109 of 151 sat more than 180 days ahead of their
      own newest artefact, so ageing by it made 553-day-old evidence look like it was filed
      yesterday.
    - **`hasTicket` and `ticket_status`** report Drata's own Jira-integration provenance, not
      coverage. Resolve ticket existence with a Jira query on the control code across `CSIP`,
      `ICR` and `IRT`.
    - **`isReady` is real, but the `flags` object cannot tell you why it is `false`.** A pending
      **control approval** holds a control at `isReady: false` on its own, and approval state is
      **not exposed anywhere in `flags`**. Confirmed 2026-08-26 on `DCF-17`, which sat
      `isReady: false` with `hasEvidence: true`, `hasPolicy: true`, `hasOwner: true` and
      `isMonitored: false` — a flag profile **identical** to ready controls `DCF-86`, `DCF-571`,
      `DCF-59` and `DCF-107`. Removing the approval requirement flipped it to `true` with no other
      change. So `isReady: false` beside a complete-looking flag set is neither a contradiction nor
      a bug: check the control's approval state in the Drata UI before diagnosing anything else, and
      never report the cause as unknown without having looked there. Bitpool decided on 2026-08-24
      not to use Drata's control approval function, so a control still carrying one is a leftover
      rather than a deliberate gate.
    - The general shape: a boolean summarising a relation is only as trustworthy as that
      relation's integrity. Where a list endpoint exists, read the list.

11. **`code_or_name` is a SUBSTRING match — the opposite of rule 4.** Two filters that look alike
    behave differently, and the difference will hand you the wrong requirement. Server-side `name`
    filters are prefix-anchored (rule 4); the client-side augmented `code_or_name` on
    `Drata_listRequirements` matches anywhere in the code or name. Confirmed 2026-08-24:

    ```
    Drata_listRequirements(framework_tag=["ISO270012022"], code_or_name="5.3")
    → A.5.30, A.5.31, A.5.32, A.5.33, A.5.34, A.5.35, A.5.36, A.5.37,
      A.5.3, 7.5.3 and clause 5.3 — eleven requirements, one of which was wanted
    ```

    **Always read `name` on each returned item before using it.** `"9.2"` likewise returns 9.2.1
    and 9.2.2 (both wanted, as it happens) and `"6.1.3"` returns exactly one. The filter is useful —
    just never assume a single hit.

12. **The risk register is fully available — and a Bitpool wiki page says it is not.** Confirmed
    2026-08-24: `Drata_listRiskRegisters` returns register id `1` ("Risk Management") and
    `Drata_searchRisks` returns the active register (47 active risks that day — a dated count, not
    a baseline), with `facets`, score-range filters and
    `Drata_updateRisk` all working. The Private Wiki page
    `/security/compliance/rto-rpo-objectives` claims *"Drata's Risk Register module is not
    available on Bitpool's current plan (`Drata_searchRisks`/`Drata_listRiskRegisters` return HTTP
    402)"*. **That page is wrong.** It is the kind of stale claim that sends the next reader to
    build a workaround for a problem that does not exist — if you meet it, say so rather than
    believing it.

    Related, and **unresolved**: `approvedAt` was `null` on **every active policy** — 56 of them
    (`Drata_listPolicies(size=100)`, 2026-08-24) — while `security-documentation`'s own
    `md-standardisation-log.md` rule 2 deliberately relocated approver records *into* the Drata
    Policy Centre. So either the field is unused by the UI or no policy is recorded as approved —
    the API cannot tell you which. **Do not assert either.** The Policy Centre UI is the only check.

13. **Tool exposure tells you nothing about scope — probe with an impossible identifier.** **Corrected 2026-08-25; an earlier edition of this rule claimed the opposite.** An exposed tool can still 403: `Drata_updateEvidenceArtifacts` sits in the toolset and `update:evidence` is **not** granted. An absent tool means only that this session's tool list lacks it — and that list has grown since this rule was first written (rule 8), so absence is a dated observation, never a standing fact, and it says nothing about scope either. Check the live tool list. **The only reliable test:** call the *update* verb against an identifier that cannot exist. `403 Missing required OAuth scope(s)` = not granted; `404` record-not-found = granted; nothing is mutated either way. `create:*` cannot be probed like this (no impossible target, and a well-formed call would actually create something) — leave it unknown unless a real creation already happened. Never probe `delete:*` at all. Full probed matrix in `references/drata-mcp-gotchas.md`.

14. **`framework_tag: "ISO27001"` returns zero — Bitpool’s tag is `ISO270012022`.** Confirmed 2026-08-25. The wrong tag is listed in the tool’s own parameter docs as a common value, so it looks correct and fails silently, exactly like rule 1. Bitpool’s framework is **ISO 27001:2022** (123 requirements when probed 2026-08-25). Never trust a zero-result framework filter — re-run without `framework_tag` and read `frameworkTag` off a returned row before concluding a framework has no requirements.

15. **Drata product documentation is not in the MCP — and does not need to be requested from Drata.** The connection is a data plane only: no documentation tool, no documentation scope. The help centre is public and already published in LLM form. **`https://help.drata.com/llms.txt`** indexes the help centre's articles (845 when read on 2026-08-26) with descriptions and `.md` links, and appending **`.md`** to any article URL returns clean markdown. **Never fetch the plain HTML article URL** — the site renders its entire global navigation into every page, which swamps the body and makes a real article read as empty. That is a false negative, not a missing article.

16. **Text for a Drata field in the Security Drata register is drafted under
    `/bitpool-writing-standard`.** The register is the risk register, the evidence library,
    controls, vendors, framework requirements (the SoA exclusion rationale) and Custom Tests — the
    **Security Drata** writing profile. It covers every free-text field in those sections, whether
    the text is sent through the MCP or drafted for a person to paste into the Drata UI: evidence
    *upload* stays a human action (rule 8), but the bucket `name`, `description` and
    `implementation_guidance` drafted for it are under the profile. Before drafting, load the
    standard's `SKILL.md` — the target gate and the six core rules — then its
    `references/profile-security-drata.md`. Every approval block that stages durable text for one
    of those fields shows the durability check (`references/durability-check.md` §1) directly under
    the staged text. Snapshots in the target — versioned evidence artefacts, a vendor security
    review — stay specific.

    **Not in the register:** personnel, devices, the policy center and background checks — and
    everything this skill itself produces: reports to the user, this skill's reference file, and
    probe payloads aimed at an impossible identifier. The standard does not apply there, and no
    check is shown. Which fields the connection can write, with their caps and traps, is this
    skill's job (*Writable free-text fields* in `references/drata-mcp-gotchas.md`); what the words
    say is the standard's, and this skill never restates it.

    **Requires `/bitpool-writing-standard` (section `bitpool-general`).** Before drafting text for
    a Drata field in the Security Drata register, load it with `skill_view`. If it is not installed,
    **stop and ask the user once per chat** (`clarify`): *"`/bitpool-writing-standard` isn't
    installed, so the Security Drata writing profile can't be applied. Installing it
    (`hermes skills install Lolman-bot/Hermes-Repository-/skills/bitpool-general/bitpool-writing-standard --category bitpool`)
    is recommended. Proceed without it?"* Continue only on a yes, and do not ask again in the same chat.
