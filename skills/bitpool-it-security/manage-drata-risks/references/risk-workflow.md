# Manage Drata Risks — the four-phase workflow in full

The complete Phase 1–4 procedure summarised in `SKILL.md`. Drata tool names are the Drata MCP
server's own (find the live `mcp_<server>_…` names with `tool_search`); Jira queries run through the
Atlassian MCP server's tools. **Phase 2 is a hard stop** — nothing in Phase 3 runs before the user
has answered the discrepancy table.

### Phase 1 — Verify

1. **Resolve the risk.** `Drata_searchRisks` with `q=<riskId>` and
   `expand=["owners","reviewers","controls","categories","documents","notes","tickets","tasks"]`.
   Capture every field. If `query` mode returns empty, that is the documented account quirk — use
   structured mode and paginate.
2. **Resolve its RTP.** `project = IRT AND text ~ "<riskId>"`, and read the full description, its
   comments — an earlier run's verification record is there — and every subtask. Also run
   `project in (CSIP, ICR, IRT, CYB) AND text ~ "<riskId>"` so a second copy of the same commitment
   is visible. Then read, read-only, the latest outcome comment on each linked control's `ICR`
   ticket, and any hold comment posted after it (`project = ICR AND text ~ "DCF-xxx"`):
   `/manage-drata-control` records its verifications and Observed values in those comments, so they
   are the other place an earlier verification of the same control can
   sit, and the latest one is judged across both.
3. **Read the governing policy's content** for the scales and the acceptable level.
4. **Read the linked controls** and, for each, the real evidence list — not the flag.
5. **Test every claim.** Walk `references/risk-verification.md` §1–§4. Produce the discrepancy
   table in §5.

State plainly what the entry asserts and what you could confirm, as a table, before proposing
anything.

### Phase 2 — Gate

Put the discrepancy table to the user. For each row: the claim, what contradicts it or why it could
not be verified, and what it would take to settle it.

Then ask. Recommend a disposition per row — **operating**, **planned**, **accepted exposure**,
**generalise**, or **delete** — but do not apply any of them yet. Anything the user cannot confirm
stays unverified; an unverifiable claim is not promoted to true by the user's silence.

If the table is empty, say so in one line and stop. **Do not manufacture findings** — a skill that
reports drift every run trains people to ignore it.

### Phase 3 — Repair

Only after the gate:

1. **Rewrite the risk statement** if it reads as a missing control rather than a consequence to
   information — see `references/risk-verification.md` §6. Get agreement on the statement before
   touching scores; the wording determines the score.
2. **Reassess the scores** against the policy scales, following `references/risk-scoring.md`.
   Propose, with reasoning. Always set the residual triplet, including for `ACCEPT` where residual
   equals inherent — a blank residual reads as an omission, an explicit equal one reads as a
   decision.
3. **Redraft `treatmentDetails`** under the Security Drata profile — the bucket headings where the
   entry has a coverage story to disambiguate, otherwise a short paragraph
   (`references/risk-verification.md` §4). Number the items continuously only on an entry that does
   not declare its item numbers stable; on one that does, each surviving item keeps its number, a
   removed number is retired and a new item takes the next unused number
   (`references/drata-risk-fields.md` §3, repair rule 6). Specifics Phase 1 verified go to the
   verification record, not the entry.
4. **Run the durability check** on every durable span staged for Drata or `IRT`, per
   `/bitpool-writing-standard` `references/durability-check.md`: flag, dispose of each flag, re-run
   on the final wording.
5. **Render the approval block** and get an explicit yes.
6. **Write** with `Drata_updateRisk`, then **quote what the API returned** — not what you sent. The
   two differ more often than you would expect, and non-admin owners are dropped silently.
7. **Close the loop outside Drata:** the dated verification-record comment on the RTP ticket, which
   also records what changed in the risk, why and on whose decision — or, where the risk has no RTP
   ticket, the same record staged for the user to file on the linked control's `ICR` review ticket,
   which this skill does not write (`references/drata-risk-fields.md` §3, *Where the risk has no RTP
   ticket*). Where the change removes an acceptance, that record states that the changed position
   awaits acceptance at the next management review (`references/risk-scoring.md` §2). Then: RTP
   ticket corrections — a description edit is durable Security Jira text, and its reason goes in a
   comment beside Jira's changelog; a policy queue row for any drift — claimed on the queue page,
   then its detail comment, then the link; and
   the evidence the user still has to upload — split into what exists today and what a planned
   subtask will create.

### Phase 4 — Summarise

State the decision, what was written, **what the returned record actually says**, the discrepancies
resolved and the ones still open, the RTP changes and the link to the verification-record comment —
or, where there is no RTP ticket, that the record is staged and is the user's to file on the `ICR`
review ticket — any policy queue row added — with the link to its comment, and the queue page file
left for the user to commit and push — and what remains
unverified. Where the change removed an acceptance, list the risk as awaiting management review and
tell the user to table it there. Reconcile every date: list each place the commitment now appears
and confirm they agree.

**Never report a policy as updated** — this skill hands drafts to `/isms-draft`. It does write
Drata risks and Jira, so report those as done, quoting the response.
