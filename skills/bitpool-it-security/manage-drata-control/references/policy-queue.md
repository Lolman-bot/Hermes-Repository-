# Batched policy changes — the policy queue

> Relocated verbatim from this skill's `SKILL.md` when it was ported to Hermes; `SKILL.md` keeps the
> route and a summary of each rule, and this file is the full text. Bold section names refer to:
> **golden rules** → `references/golden-rules.md`; **Invoke the downstream skills** and **Bitpool
> context** → `references/bitpool-context.md`; **Batched policy changes**, **Writing a queue row** and
> **Rules for the index** → `references/policy-queue.md`; **Step 0–11** → `references/workflow.md`.

**Bitpool decision, 2026-08-24.** A control review that finds policy drift does **not** create its
own "promote policy X" ticket. Many controls touch the same few policies, so promoting per control
means the same `.docx` gets rebuilt, re-uploaded and re-approved a dozen times — and every one of
those is a clause 7.5.2 approval event someone has to actually perform. Instead:

> **Draft edits land continuously. One bulk promotion happens at the end.**

This also means a lapsed `renewalDate` is the expected state of every policy between bulk events,
which is why the golden rule forbids reporting it.

> ### ⛔ The queue tracks promotion, never the drafting — corrected 2026-08-27
>
> **Make the draft edit during the run. Do not queue a draft edit as work to be done later.**
>
> The distinction the earlier wording lost: `/isms-draft` edits Markdown in the ISMS draft
> folders (`ISMS/ISMS - Draft/` and `ISMS/ISMS - Draft (New)/`). That is cheap, reversible, needs
> no approval, and **is not a controlled change** — so there is nothing to schedule and no reason to
> defer it. What genuinely has to be
> batched is `/isms-prod`: the `.docx` build, the Drata upload and the clause 7.5.2 approval round,
> which is expensive and which is the *only* reason a queue exists at all.
>
> So a control review that finds drift **invokes `/isms-draft` there and then** and the queue row
> records a change that is already in the Markdown, waiting on promotion. A row whose
> `Draft edited` field reads `pending` is a run that stopped halfway: it left the correction
> unmade *and* consumed the queue slot that would have flagged it.
>
> **Corollary — do not raise a promotion subtask that already exists.** The policy queue ticket
> *is* the outstanding promotion ticket for every policy in it. Before creating anything under a
> control's own IRT parent, check whether the policy is already queued; if it is, the promotion is
> tracked and a second artefact is a duplicate.
>
> Rejected by the risk owner, 2026-08-27: *"you shouldn't queue policy changes, you should apply
> policy changes and queue that the policy needs to be /isms-prod and uploaded to drata."*

### The two phases

| Phase | When | Tracked by |
|---|---|---|
| **1 — Draft edit** | **During the control review that finds the drift.** Cheap, reversible, uncontrolled, no approval needed — so there is nothing to defer. Invoke `/isms-draft` and make the change | Nothing. It is done. The queue row then *records* it |
| **2 — Bulk promotion** | Once, after the control review programme resolves: `.docx` build, Drata upload, approval, renewal | The policy queue ticket's own `duedate` — **this is what the queue is for** |

### The policy queue — one ticket, one page

One standing `Task` in `IRT`, labelled `PolicyQueue`, titled:

`ISMS policy queue | draft edits pending bulk promotion`

Find it with `project = IRT AND labels = PolicyQueue`. **There is exactly one.** Never create a
second — a search returning none is the only case for creating one.

The queue keeps its parts in three places, each with one job:

| Part | Where | Holds |
|---|---|---|
| The description | The queue ticket | **Only the standing rules** — there is exactly one queue; it tracks promotion, not drafting; a past `renewalDate` and a null `approvedAt` are the expected state between bulk events, not a finding — plus a link to the queue page, the **Due date** section and the **Superseded tickets** section |
| One comment per row | The queue ticket | The row's detail, in the format below — a Security Jira snapshot |
| The queue page | `compliance/isms-policy-queue.md` in the main `security-documentation` working copy (path in **Bitpool context**), published as **ISMS Policy Queue** at `https://private-wiki.bitpool.com/security/compliance/isms-policy-queue` once the user pushes | Everything that grows with each row: the **Pending changes** index, the per-row **Status** notes — drafting status, and which rows promote together — and the ordered **At promotion** steps. Its **History** section keeps the superseded description-era procedure |

**Nothing row-related is ever written to the description, and no per-row step touches it.** It
changes only when a standing rule, the due date or a superseded ticket changes. `editJiraIssue`
still replaces the whole field with no conflict detection, so that rare edit re-reads the ticket
immediately before it and sends `description` alone (golden rules).

**The page is the one file in `security-documentation` this skill edits** — its index rows, Status
notes and At promotion steps, by the procedure below, and the marking of rows promoted in the bulk
promotion (**Rules for the index**). Those edits change no front matter, so they need no index
regenerate. Anything else on the page, its front matter included, goes through `/bitpool-docs`,
which regenerates.

> ### ⛔ One row, one comment, one line on the page
>
> **Write the row's detail as a comment on the queue ticket. Index it with one line on the queue
> page.** One comment carries exactly one row; one row is indexed exactly once. Neither half is
> optional — **a comment whose number has no line in the page file has not claimed it**, and the
> next run will take that number.
>
> The index lived in the description until 2026-10-01, and every row grew that field towards Jira's
> cap; the page's **History** section keeps that procedure and the incidents behind it.

### Writing a queue row

The queue page's **How to add a row** states these steps for people, and this section carries the
same steps plus the edge cases an AI session needs; the two are kept in step, so a change to one is
made to the other.

**Stage it like every Jira write:** the detail comment, the page row and any Status note or At
promotion step, in one approval. On the yes, write them in this order — the page row first,
because it claims the number; the comment second; the link last.

**Make the claim, the link and every other page edit with the file tools — `read_file`, then `patch`.**
Never a `terminal` append or redirect, `sed`, a heredoc or a blind whole-file `write_file`: none of them
gives the conflict check the claim relies on, so two runs could take the same number without either
noticing. **Anchor every `patch` on the current text it changes** — for a new row, `old_string` is the
table's current last row *plus the line after it* — so a concurrent append makes the match fail
instead of landing your row in the wrong place. **Treat a `patch` failure or a staleness warning in its
result as a refusal.** (A `write_file` over the page refuses outright when the file changed since your
read; it is acceptable only after a fresh full `read_file`, and never as the default.) The file is the
one in the main `security-documentation` working copy (path in **Bitpool context**) — never a git
worktree or a second clone, and never the published page.

#### 1 — Claim the number on the page

1. **Re-read the page file from disk** immediately before the edit.
2. **`N` is the highest `#` in the Pending changes table plus one.** Withdrawn rows count — a
   number is never reused.
3. **Append the row, with `Detail` reading `pending`:**

   | # | Policy | Detail |
   |---|---|---|
   | N | Network Security Policy | pending |

**The failed or stale-warned `patch` is the conflict check.** Anchored on the table's current end, it
fails when another run changed the page since you read it, so your claim fails instead of overwriting theirs.
Re-read and take the next free number. **If the number you claim differs from the one in the
staged, approved comment, change the comment's heading to the claimed number before posting it.** A
number change alone needs no fresh approval; say so in the Step 11 summary.

#### 2 — The detail comment

One comment per change, headed with the row number so it can be found by search:

```
## Queue row N — <Policy name>

| Field | Value |
| --- | --- |
| **Policy** | <exact document name as it appears in `security-documentation`> |
| **Origin** | `DCF-xxx` · `CR-xx` · `IRT-nn` or `ICR-nnn` |
| **Draft edited** | YYYY-MM-DD |
| **Clause** | the clause(s) the change is *for* |

**Change.** <what changed, in as much detail as the change actually warrants>
```

**Post it as plain headings, text, tables and lists — never a blockquote — and read back what Jira
returns** (**Rules for the index**).

**The comment is the place to be expansive** — it is not size-rationed. A change that *withdraws* a
requirement rather than correcting a false claim should say so, and say why, at length; so should
anything an auditor would want the reasoning for.

Where the reasoning already exists in another comment on the ticket, link to that comment instead of
restating it.

**One comment carries exactly one row** — a comment covering several rows leaves the row-to-comment
mapping ambiguous and points several rows on the page at one target. **A coupled change set is
still one comment per document** — restate the coupling in each of them (`Promote with rows N–M`,
and what breaks if one is left behind). The words carry the coupling; a shared comment body does
not.

Three fields in that header table earn their own rules:

- **`Origin` names the control code first**, then the risk id, then the ticket that produced the
  row — the `IRT` commitment where one exists, otherwise the `ICR` control review that found the
  drift. Control code because it is the durable handle; the rest because they are how a human
  reaches the reasoning. Citing an `ICR` key here is a reference, not a cross-project write, so it
  does not breach the limit on `ICR` writes at Step 10. This field is the answer to
  "why does this policy say this?" six months from now.
- **`Draft edited` is a date. Never `pending`** — and never a prose status. Corrected 2026-08-27:
  `pending` was previously allowed, and it is precisely the state this section forbids. A row
  reaches the queue *because* the Markdown was edited, so the date always exists. If you cannot fill
  it in, you have not finished the run. The `pending` in the page's `Detail` cell is a different
  thing: a claimed number waiting for its comment, and it lasts only until step 3.
- **`Clause` is what the change is *for*.** At promotion this becomes the change rationale the
  `isms` repo's commit convention requires, so filling it in is work done early, not decoration.

#### 3 — Link the row

Re-read the page file, then replace `pending` with the link to the comment:

`[row N](https://bitpool.atlassian.net/browse/IRT-17?focusedCommentId=<comment id>)`

The id comes back in the `addCommentToJiraIssue` response; take it from there rather than
constructing it.

**If a later edit in this run — the link, a Status note or an At promotion step — is refused as
stale, re-read the page and apply it again.** The number is already this run's; never take a new
one for it.

#### 4 — Status and At promotion, on the page

Where the row must promote together with other rows, or needs a step at promotion, add a **Status**
note, an **At promotion** step, or both, on the page in the same run — never in the description. They
are register content: structured, and dated where they record an event.

- **A new At promotion step goes immediately before the last one**, *Only then close the queue
  rows*, and that last step is renumbered.
- **Keep the drafting status true.** When a row is added undrafted, or an undrafted row is later
  drafted, update the Status headline (*everything is drafted except rows …*), At promotion
  step 1's list of rows still to draft, and the row's `— **needs drafting**` suffix in its `Detail`
  cell: add it for an undrafted row, remove it once the row is drafted.

#### 5 — Leave the page edit for the user

**Never commit or push the page.** List the file in the run's changed-files report and in the
Step 11 summary; the user commits and pushes.

#### Rules for the index

Each exists because dropping it loses something at promotion time:

- **Three cells, nothing more.** **The index is a pointer list, not a summary of the queue** — if
  you find yourself wanting to describe the change on the page, that belongs in the comment.
- **One row per *change*, not per policy.** Two controls editing the same policy for different
  reasons are two rows, or the second reason is invisible to whoever promotes it.
- **A row whose `Detail` still reads `pending` is unfinished.** Where its comment exists, link it.
  Where it has none, it is a claimed number whose comment was never posted — act on it only once
  the run that claimed it has ended: the next run that finds it either posts the comment and links
  it, or withdraws the row. A run that cannot tell whether the claiming run is still going leaves
  the row and reports it in the Step 11 summary.
- **One withdrawal convention.** Strike the `Policy` cell through and write `withdrawn YYYY-MM-DD`
  after the policy name — `~~<Policy>~~ withdrawn YYYY-MM-DD`. Where no comment was ever posted,
  the `Detail` cell reads `withdrawn, no comment`. A withdrawn row stays in the table and keeps its
  number forever.
- **Row numbers are permanent, and `N` comes from the page file.** Comments and earlier runs refer
  to rows by number, so never renumber to close a gap, and never reuse a number.
- **The page file is the register of record for row numbers** — the one main working copy of
  `security-documentation` (path in **Bitpool context**), read from disk. Never a git worktree or a
  second clone, whose claims other runs cannot see, and never the published page: it lags until the
  user pushes, and the wiki's own reads are known to serve stale content. **A comment that claims a
  number without a row in the file has not claimed it.** The `ICR` gate, and the hygiene sweep's
  re-test of closed `ICR` tickets (check 13), read `origin/main`'s copy instead, because they ask
  what has landed (Step 10).
- **The comment is always the side that moves.** An indexed row's number never changes. Where a
  comment claims a number the page gives to another row, claim a new number for it by step 1, link
  the new row to that original comment, and post a short correction comment naming the new number.
- **Mark the promoted rows after the bulk promotion.** `/isms-prod` hands the page update to this
  skill and says so in its promotion report. For each row that landed, write `promoted YYYY-MM-DD`
  after the policy name in its `Policy` cell, then update the Status headline. That is what the
  page's last At promotion step, *Only then close the queue rows*, means; a promoted row keeps its
  number too.
- **Never wrap queue text in a blockquote in Jira, and read back what you wrote.** Jira's
  Markdown-to-ADF conversion **silently discards** a `>` block containing a heading and a numbered
  list. The write returns success and the content is simply absent. Keep comments to plain
  headings, text and lists — and **compare what Jira returns against what you sent.** A `200` is not
  evidence the content landed.

**A write that fails part-way, and that this run cannot finish, leaves the row reading `pending`,
and that is the record.** A claim whose comment could not be posted, or a comment whose link could
not be written, is finished by the next run once this one has ended (above). Say so in the Step 11
summary — `references/hygiene-sweep.md` check 8 looks for exactly this state.

### What a control review does

At Step 8, when drift is found:

1. Produce the `/isms-draft` handoff exactly as `policy-alignment.md` §4 specifies — unchanged.
2. **Invoke `/isms-draft` and apply the edit now.** Do not defer it, and do not describe it as
   queued — the queue is for promotion, not for drafting. See the corrected block above.
3. **Claim the row on the page, post the detail comment, then link the row** — the writes above —
   recording the change as drafted with the date it was edited, and report the row number, *its
   comment link* and the page file left for the user to commit and push in the Step 11 summary.
4. **Do not** create a "promote policy X" subtask under the control's own IRT parent. The queue
   ticket already *is* that policy's outstanding promotion ticket — check before creating anything.
5. Reference the queue ticket by key from the control's IRT ticket if useful — permitted, because
   this skill owns `IRT` and can keep that reference true.

**Only invoke `/isms-draft` where the drift is what *this* control evidences.** A policy section a
control review happens to read past is not this run's business — raise it and move on. Confirmed
with the risk owner 2026-08-27: *"only use /isms-draft if it related to DCF-19 directly. then for
sure use it."*

At Step 10, a policy change already sitting in the queue is **covered** once its row on the queue
page links a detail comment that names this control, the row is in `origin/main`'s copy of the
page, and the draft edit it records is on `security-documentation` `main` — whichever run left the
row. Do not raise it again, and never read its presence in the queue as an untracked gap. **Read
the comments, not just the page** — the index carries only the row number, the policy name and a
link, so it cannot tell you whether a queued change already covers your control. Find the row by
content, never by a row number an earlier comment cites (`references/icr-closure.md` §2, check 5).

### Folding in pre-existing promotion subtasks

Where a control's IRT parent already carries individual "promote policy X" subtasks predating this
decision: claim their rows on the page and post their content as queue comments **first**, then
close them as superseded with a comment naming the queue ticket. Document-before-ticket still holds
— here the queue row *is* the document, so it goes in before the subtask closes.
