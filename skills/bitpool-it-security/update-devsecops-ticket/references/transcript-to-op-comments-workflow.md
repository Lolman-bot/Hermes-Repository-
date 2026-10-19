# Transcript to OP Comments Workflow

Takes a recorded DevSecOps engineering meeting (a Teams `.vtt` transcript) and turns what was
actually *decided* in the room into short direction updates on the **existing** tickets those
decisions affect — posted as **comments**, on the **OP (Perun)** board, and nowhere else. Nothing
is created, nothing is transitioned, nothing is re-assigned, no description is rewritten. The
output is a set of "here's where this ticket is heading now" notes, so a person opening `OP-90`
next week reads the meeting's verdict on it without hunting for the recording.

This skill is deliberately narrow, and the narrowness is the point. It does **not** map controls,
it does **not** attach a DCF table, it does **not** touch CSIP, and it does **not** create
tickets. Those are `/create-devsecops-ticket`'s and `/drive-iso27001`'s jobs. If a meeting
produced work that has no ticket at all, this skill *reports that gap to the user* and stops — it
never fills it.

**The worked example this skill's design is grounded in:** the DevSecOps engineering meeting of
**2026-08-24** (`Meeting in _DevSecOps_ 1.vtt`), run live with the brief *"add comments, not
tickets — some content in the mid part is not relevant to the OP board — show a preview before
posting — it should just be an update with a small addition on the direction of some of these
tickets."* That run produced **ten comments**, **two deliberate exclusions**, and **one
honestly-reported gap** where the audio could not be attributed. Every step below carries the
specific thing that run got wrong or nearly got wrong. Read those bits — they are not colour, they
are the failure modes.

---

## Bitpool config (hardcoded — do not look these up)

- **Jira Cloud ID:** `d7442fe0-cadf-44e1-9313-6b27e16f3fbc` (host `bitpool.atlassian.net`). Every
  call in this workflow carries it. Don't call `getAccessibleAtlassianResources` to rediscover it.
- **The board — three tiers, and the third one cannot be widened:**
  1. **`OP` (Perun)** is *the* target board — Bitpool's DevSecOps engineering board (board id
     **98**). Everything this skill posts goes here.
  2. **`BT`**, the sibling *product* board, is in scope **only when the user explicitly names it**
     in this run.
  3. **`CSIP` is NEVER in scope.** Not on request, not when the user names it, not when a decision
     obviously belongs there. There is no phrasing of a user instruction that unlocks CSIP for
     this skill. When a decision belongs on CSIP, say so **in the hand-back** and route the user
     to `/drive-iso27001` — that is the whole of this skill's response to a CSIP-shaped decision.
- **Never comment on a ticket whose summary matches `Drata | Bitpool | DCF-xxx`** — those are
  Drata-generated control parents, they all live in CSIP, and they belong to `/drive-iso27001`. If
  a mapping in Step 6 lands on one, that is a mis-map: drop it and hand it back.
- **Issue URL pattern:** `https://bitpool.atlassian.net/browse/<KEY>` — used for every
  cross-reference link in a comment. Plain markdown links only.
- **Transcript folder (the usual home, not an assumption):** the SharePoint folder synced under
  the user's home as `<home>\Bitpool Pty Ltd\Cyber Security - Documents\General\New cyber
  plan\DevSecOps meeting transcripts\`. Files
  land here as `Meeting in _<Channel>_ <n>.vtt` — the real worked-example file is `Meeting in
  _DevSecOps_ 1.vtt`, space and trailing occurrence number included. This is where to *look* and
  where to *offer* — never where to assume the user meant (Step 1).
- **The only Jira write verb this skill may use:** `addCommentToJiraIssue`, always with
  `contentFormat: "markdown"`.
- **Read verbs it may use:** `getJiraIssue`, `searchJiraIssuesUsingJql`. Nothing else.
- **BANNED verbs, no exceptions:** `createJiraIssue`, `editJiraIssue`, `transitionJiraIssue`,
  `addWorklogToJiraIssue`, `createIssueLink` — and, sitting on the same Atlassian connector and
  banned just as hard, `createConfluencePage`, `updateConfluencePage`,
  `createConfluenceFooterComment` and `createConfluenceInlineComment`. This skill writes nothing
  to Confluence, ever; a wiki or Confluence page is `/bitpool-docs`' or `/drive-iso27001`'s job.
  Being one connector away is not a licence — the ban is explicit precisely so it isn't left to
  inference.
- **No Drata calls at all** — not read, not write. This skill never touches `Drata_*`.
- **No wiki calls at all** — the Atlassian MCP server's documentation search, page-read and
  question tools are out. Repo house
  rule for this skill; everything it needs ships in this folder.
- **CSIP is off limits, unconditionally.** CSIP work, DCF-linked compliance writing and control
  tables belong to `/drive-iso27001` and `/create-devsecops-ticket`. If a meeting decision clearly
  belongs on a CSIP ticket, say so in the hand-back and route it to `/drive-iso27001` — don't post
  there. A user asking for it mid-run is not authorisation; it is a request to run the other
  skill, and the correct answer is to name that skill.
- **Scripting runs through a real Python 3, via `terminal`.** Run the shipped script with
  `python3` (or `python`). If the native Windows interpreter is a Microsoft Store stub that prints
  *"Python was not found"*, run it through WSL instead (`wsl -e bash -lc '...'`, Windows paths
  translated to `/mnt/c/...`) — see `references/vtt-parsing.md`.

**Golden rules**

- **Never guess the meeting date.** A `.vtt` carries cue timestamps and nothing else — no date, no
  year, no timezone. The date is the first line of every comment this skill writes, so getting it
  wrong stamps a lie onto ten tickets at once. Establish it from the Outlook calendar and
  cross-check it against any in-audio time reference (Step 2), and **state in the preview how it
  was established** so the user can veto the reasoning, not just the result.
- **Never invent attribution.** Teams routinely collapses every speaker in an exported `.vtt` into
  a single `<v …>` tag. On 2026-08-24, **all 466 cues** were tagged `<v Eric Sharp>` despite three
  people speaking. Per-speaker attribution was therefore *impossible*, and the attendee list could
  not be derived from the file. When that happens: don't name who said what, don't list attendees
  from the transcript, and say plainly in the hand-back that attribution was unavailable. A named
  action only gets a named owner when the **content** of the words makes the owner unambiguous
  ("Armen needs to…"), never because a `<v>` tag said so.
- **Cross-cutting direction goes on the parent, once.** If a rule applies to a whole family of
  sub-tasks, comment the parent and let the children inherit it. On 2026-08-24 the ten legacy-VM
  sub-tasks `OP-89`…`OP-112` all hung off **one** parent, `OP-9` — so the vulnerability cadence
  and the legacy-VM ground rules were written once on `OP-9`, not ten times. Ten near-identical
  comments is noise; the person reading `OP-94` wants *its* verdict, not the boilerplate.
- **Say out loud what you deliberately left out.** The three-way split (Step 7) is not internal
  bookkeeping — the excluded content and the unattributable content both get reported to the user,
  by name, in the preview and again in the hand-back. Silence reads as "the meeting contained
  nothing else," which is a different and false claim.
- **Unattributable content is reported, never written.** If the audio doesn't make clear what was
  done, by whom, or what is still outstanding, the ticket is left untouched and the gap is handed
  back as a question. On 2026-08-24 a rapid `00:14`–`00:16` pass over four systems left `OP-103`,
  `OP-92` and `OP-104` genuinely unresolvable — all three were left alone and the gap was
  reported. **A plausible-sounding reconstruction of a mumbled two minutes is the single worst
  output this skill can produce**, because it is indistinguishable from a real decision once it's
  on the ticket.
- **Keep every comment short.** This is a direction update, not a control mapping and not minutes.
  A bolded lead line, one to three short blocks, and a cross-reference line. If a comment is
  running past roughly a screen, it is trying to be the meeting-notes page — that's Step 12's job.
- **No DCF control table, ever.** Attaching a control table to a ticket is
  `/create-devsecops-ticket`'s job, and it does it on the **description** field, not in comments.
  This skill names a DCF inline, as a plain sentence, **only** where the meeting decision
  genuinely moves that control ("this closes the manual step DCF-xxx was flagging") — and even
  then with no table, no Drata link and no lookup, because Drata calls are banned here.
- **Comments only, and only on tickets that already exist.** No status, no assignee, no labels, no
  description edit, no issue link, no new ticket. If the right home for a decision doesn't exist
  yet, that's a hand-back item routed to `/create-devsecops-ticket`.
- **Render the preview, don't dump its source.** Show all comments as actual rendered markdown in
  the chat — real bold, real links, real structure — never inside a fenced code block. A fence
  shows raw `**` and `|---|---|` instead of the formatting, which defeats the entire point of a
  review step: the user is approving *what it will look like on the ticket*.
- **One approval covers the whole batch, and the batch is shown whole.** Don't post
  ticket-by-ticket as each draft is finished, and don't show three now and seven later. The user's
  judgement about what belongs on the board depends on seeing the set — on 2026-08-24 the "some
  content in the mid part is not relevant" instruction only became actionable once the full spread
  was visible.
- **Verify what came back against what you sent.** Jira's markdown converter is not lossless. On
  2026-08-24 it silently rewrote emphasis on two comments where a bold run ended immediately
  before a code span. Compare the returned `body` to the text you submitted and **report drift
  rather than claiming the text went up verbatim** (Step 11).

---

## Workflow

### Step 1 — Resolve the transcript

- **If the user gave a path or a filename, use it.** Confirm the file exists before parsing; a
  wrong path caught now is cheaper than a parse that silently reads nothing.
- **If they didn't, ask — never assume a folder.** The config block above names where transcripts
  *usually* live. That makes it a good first place to *offer*, not a default to act on. List
  what's there and ask which one, or ask for the path outright. Meetings recur weekly and the
  filenames repeat (`Meeting in _DevSecOps_ 1.vtt` is reused every time), so "the obvious one in
  the obvious folder" is frequently last week's.
- **If more than one candidate is plausible, show the candidates with their file modified times
  and ask.** Don't pick the newest on your own — a transcript can be exported days after the
  meeting, so mtime orders the *exports*, not the *meetings*.
- **Copy the true filename from the directory listing — never retype it from memory or from this
  page.** These files get renamed, and a name that looks right is not the same as the name on
  disk. Paste the exact string, spaces and trailing occurrence number and all, straight into the
  path you hand to Step 3.
- Note the file's full absolute path. Step 3's parser needs it (as a `/mnt/c/...` translation only if you fall back to WSL), and
  Step 12 writes the notes page **next to it**.

### Step 2 — Establish the meeting date (never guess)

The date is load-bearing: it opens every comment as `**DevSecOps meeting update — YYYY-MM-DD**`,
and it is the only thing distinguishing this run's comment from the last three weeks' comments on
the same ticket. **A `.vtt` does not contain it.** Cue timestamps are offsets from the start of
the recording; there is no date, no year and no timezone anywhere in the file. Neither is the
filename reliable — Teams names the export after the *channel*, not the occurrence.

So derive it, from at least two independent signals where possible:

1. **Search the Outlook calendar** with `outlook_calendar_search` — the meeting's channel name,
   the likely participants, or a date window around when the user says it happened. What you're
   looking for is a real calendar occurrence whose title and attendees match the content you're
   about to read.
2. **Cross-check against any in-audio time reference.** Transcripts are full of them and they're
   free corroboration: "the meeting tomorrow at 4:00", "before Friday", "since Monday's outage".
   On 2026-08-24 the in-audio reference *"meeting tomorrow at 4:00"* was matched against a real
   calendar entry the following day, which pinned the recording to **"Dev Meeting - Dmytro in",
   2026-08-24 10:00 AEST**. Neither signal alone would have been conclusive; together they were.
3. **If the two disagree, stop and ask.** A calendar hit that contradicts the audio means you've
   probably found the wrong occurrence of a recurring meeting. Show the user both and let them
   pick.
4. **If the calendar is unavailable or returns nothing, ask the user for the date outright.** That
   is a perfectly good outcome. Guessing from the file's mtime is not — an export timestamp is not
   a meeting date.

**Record how you established it, and say so.** The preview (Step 9) and the hand-back (Step 13)
both state the method in one line — e.g. *"Date established from the Outlook entry 'Dev Meeting -
Dmytro in' (2026-08-24 10:00 AEST), corroborated by the in-audio reference to a meeting 'tomorrow
at 4:00'."* A date the user can't audit is a date they have to take on trust across ten tickets.

Timezone convention: Bitpool meetings are recorded in **AEST/AEDT**. The comment carries the plain
calendar date (`2026-08-24`), not a timestamp — don't over-specify.

### Step 3 — Parse the transcript

**Run the skill's shipped parser — `scripts/vtt_to_text.py` — and never re-implement it.** It is
plain Python 3 standard library, it handles all three traps below, and it prints the attribution
warning for you. Writing a fresh parser in the moment is how every one of these traps got hit in
the first place, so the rule is blunt: the script is *run*, not rewritten, not "adapted", not
pasted into a new file with a tweak.

**The mechanics live in [`references/vtt-parsing.md`](vtt-parsing.md) — read that file, don't
improvise a regex here.** It carries the cue grammar, the two-line-cue trap, the speaker-collapse
detection, the flag reference, and the execution pattern (with its WSL fallback) that this skill's earliest run had
to discover the hard way.

The invocation, in full, through `terminal` — paths quoted, because the transcript folder has
spaces in it. `<skill dir>` is this skill's installed folder (shown by `skill_view`, normally under
`$HERMES_HOME/skills/`); `<transcript folder>` is the synced SharePoint folder *Cyber Security -
Documents/General/New cyber plan/DevSecOps meeting transcripts*:

```bash
python3 "<skill dir>/scripts/vtt_to_text.py" "<transcript folder>/<file>.vtt" > "<scratch dir>/parsed.txt"
```

Fallback where the native Windows Python is a Store stub — the same call through WSL, paths
translated to `/mnt/c/...`:

```bash
wsl -e bash -lc 'python3 "/mnt/c/<skill dir>/scripts/vtt_to_text.py" "/mnt/c/<transcript folder>/<file>.vtt" > "/mnt/c/<scratch dir>/parsed.txt"'
```

The transcript goes to **stdout** and the diagnostics — cue count, distinct speaker tags, the
attribution warning — go to **stderr**, so redirecting the transcript into a file still shows you
the warnings. Read `parsed.txt` from there.

The three things `references/vtt-parsing.md` exists to prevent, named here so you know why not to
skip it:

- **Speaker collapse.** Every cue can carry the same `<v …>` name even when several people spoke.
  Detect it (count distinct `<v>` values against the obvious turn-taking in the text) rather than
  trusting the tags, and set attribution to "unavailable" for the whole run when it's collapsed.
- **Multi-line cues.** A cue's text frequently wraps onto a second line, and **only the first line
  carries the `<v>` tag**. A naive per-line regex that requires the tag silently discards roughly
  half the words — and because the surviving half is still grammatical, the result reads fluently
  and is wrong. This is the most dangerous trap in the whole skill: it fails quietly and produces
  confident nonsense.
- **Quoting hell.** Transcript text is full of apostrophes and em-dashes. Inline bash heredocs
  containing them failed twice on 2026-08-24, which is precisely why the parser is a shipped `.py`
  file rather than something typed into a shell each run. Don't undo that: invoke
  `scripts/vtt_to_text.py` as shown above and read its output file. Never pipe Python source
  through `bash -c`, and if native Windows `python`/`python3` turn out to be Store stubs, use the
  WSL fallback rather than improvising.

Sanity-check the parse before going further: cue count, total word count, first and last cue text.
If the word count looks light against a 40-minute meeting, you've hit the two-line trap.

### Step 4 — Read the whole transcript and extract

**Read all of it.** Not a summary of it, not the first and last thousand words, not a keyword grep
for ticket keys. Direction changes hide in throwaway sentences mid-meeting, and the mapping in
Step 6 depends on recognising a system by its *description* when nobody said its ticket key out
loud (nobody ever says "OP-99").

Extract four distinct things, keeping the cue timestamp against each so you can re-find it:

- **Decisions** — something is now settled that wasn't. "We're not hardening it, we're killing
  it." "Criticality is driven off exposure, not off what the box does."
- **Directions** — a change of heading on work already in flight, without a hard decision. "Keep
  it, but it needs to move off that host eventually."
- **Named actions** — a specific person owes a specific thing. Only take the name from the
  **content** of the words, never from a `<v>` tag (see the golden rule).
- **Open questions** — raised and left unresolved. These are the `⚠️` lines in Step 8, and they're
  often the most valuable thing in the whole output because they're the bit that otherwise
  evaporates when the recording is deleted.

Note against each item **which system or piece of work it's about**, in the meeting's own words
(`edge.bitpool.com`, "the FTP box", "the tagging thing"). That phrasing is what Step 6 matches on.

Also note, separately, anything that is clearly **not engineering-board material** — commercial
discussion, tooling preferences, personnel. Don't discard it here; Step 7 needs it to tell the
user what was left out.

### Step 5 — Pull the OP board

You need the current state of the board to map onto, because a decision about "the FTP box" only
becomes a comment once you know it's `OP-99`.

**The query:**

```jql
project = OP AND issuetype != Sub-task ORDER BY key ASC
```

via `searchJiraIssuesUsingJql`, with the cloud id from the config block.

**The 267 KB overflow trap.** On 2026-08-24 that query — run without a field restriction —
returned **267 KB** and blew past the tool-result limit. The recovery pattern, which is faster
than re-running it:

1. **Always restrict fields.** `fields: ["summary", "status", "parent"]` is all this workflow ever
   needs. Descriptions, comments and changelogs are what make the payload enormous, and none of
   them are used here.
2. **Page deliberately.** Set `maxResults` to something sane (50–100) and follow the pagination
   rather than asking for everything at once.
3. **If it overflows anyway, don't re-run it blind — recover from the persisted output.** When a
   tool result is too large, Hermes writes the full payload to a file and names that path in
   the truncation notice. **Read that file**, with `jq` or a small Python script file run via `terminal`, and
   pull out just the `key`/`summary`/`status`/`parent` triples you need. Re-running the same query
   hoping for a smaller answer wastes a round trip and gets the same 267 KB.

**Discovering sub-task parents.** The non-sub-task query above deliberately excludes sub-tasks, so
run a second, separate query for them:

```jql
project = OP AND issuetype = Sub-task ORDER BY key ASC
```

again with `fields: ["summary", "status", "parent"]`. **The `parent` field is the whole reason for
this second call** — it's what reveals that `OP-89` through `OP-112` are all children of a single
parent, `OP-9`, which is what makes the parent-vs-children rule in Step 6 possible. Without it you
see twenty-four flat tickets and no structure, and you write the same paragraph ten times.

Build a compact working list — key, summary, status, parent — and keep it. Steps 6, 8 and 12 all
read from it.

### Step 6 — Map decisions onto existing tickets

Match each Step 4 item to a ticket **that already exists**, by what the ticket is *about*, not by
keyword collision on its summary. Read the summary and, where the match is uncertain, fetch the
ticket with `getJiraIssue` and read its description before committing.

**The DCF table already in the description is read-only context.** Many OP tickets already carry a
`## DevSecOps / ISO 27001 context` section with a DCF control table in the description, written by
`/create-devsecops-ticket` — `OP-9` and `OP-6` both have one, verified. **Read it for context
only.** Never reproduce it in a comment, never extend or correct it, never cite its Drata or CSIP
links, and never edit the description to bring it up to date — `editJiraIssue` is banned. If it is
out of date, that is a hand-back line for `/create-devsecops-ticket`.

**The parent-vs-children rule.** Before writing anything, ask of each item: *does this apply to
one ticket, or to a family?*

- **One ticket** → comment that ticket.
- **A family** → comment the **parent, once**. The real example: the 2026-08-24 meeting set a
  vulnerability-scanning cadence and a set of ground rules that applied to *every* legacy VM. All
  ten legacy-VM sub-tasks (`OP-89`…`OP-112`) hang off `OP-9`, so the cadence and the ground rules
  were written once on `OP-9`. Each child then got a comment **only if the meeting said something
  specific about that child** — `OP-90` (`edge.bitpool.com`: keep, but relocate), `OP-99` (FTP:
  decommission to S3), `OP-94` (`ts.bitpool.com`: hold hardening), and so on. Generic direction on
  the parent, specific verdicts on the children, and no duplication between them.
- **A family where the parent isn't obvious** → check the `parent` field from Step 5 rather than
  inferring from key adjacency. Consecutive keys do not imply a shared parent.

**Where nothing matches.** Some decisions won't have a home. That is a **hand-back item**, not a
licence to create a ticket — `createJiraIssue` is banned here. Note it, and in Step 13 tell the
user which decisions have nowhere to live and suggest `/create-devsecops-ticket` for them.

**Hand back and stop. Never invoke `/create-devsecops-ticket` yourself in this run — name it as
the user's next step.** If the user asks at the Step 9 approval gate to create the missing
tickets, post the approved comments, then tell them to run `/create-devsecops-ticket` in a fresh
turn; do not chain into it.

**Where several tickets match.** Pick the most specific one and cross-reference the others in the
comment's closing line (Step 8). Don't post the same content twice to cover yourself.

Record the mapping as a table for your own use — decision → ticket → parent-or-child — because
Step 7 partitions exactly this list and Step 9 previews it.

### Step 7 — The three-way split

Every extracted item lands in exactly one of three buckets, and **the user sees all three**. This
split is the skill's honesty mechanism: it makes the difference between "the meeting decided these
ten things" and "the meeting decided these ten things, discussed two more that don't belong here,
and had a stretch I couldn't make out."

**1. In scope — becomes a comment.** Engineering direction that maps to an existing OP ticket. The
2026-08-24 set, as the reference shape of a good run:

| Ticket | What the meeting decided |
|---|---|
| `OP-9` (parent) | Vulnerability-scan cadence + cross-cutting legacy-VM ground rules |
| `OP-82` | The criticality model |
| `OP-6` | WAF scope and rollout |
| `OP-88` | Tagging unblocked; default-VPC exit |
| `OP-99` | FTP decommission to S3 |
| `OP-90` | `edge.bitpool.com` — keep, but relocate |
| `OP-93` | `protect.bitpool.com` — ownership question, unresolved |
| `OP-91` | Email-server upload moves |
| `OP-94` | `ts.bitpool.com` — hold hardening |
| `OP-106` | `ttn.bitpool.com` — migrated |

Ten comments, ten different verdicts, no repetition.

**2. Deliberately excluded — named to the user, posted nowhere.** Real content from the meeting
that is genuinely not engineering-board material. On 2026-08-24 that was: the **certification-body
commercial discussion** (Bolton at roughly A$1,500 against Swiss/BSI at roughly US$3,000, how much
accreditation weight each carries, and where to source internal audit) — that is ISMS and
commercial, belonging to `/drive-iso27001` or a conversation with the user, not to an engineering
board; and a **Jira review-workflow preference** aired in passing, which is a process opinion, not
a ticket direction.

The user's brief on that run was *"some content in the mid part is not relevant to the OP board"*
— which is a licence to exclude, **not** a licence to exclude silently. List what you dropped and
why, in one line each, in the preview. If the user disagrees with an exclusion, they say so before
anything is posted, which is the entire value of showing it.

**3. Unattributable — reported, never written.** Content where the audio genuinely doesn't
establish what happened. On 2026-08-24 a rapid pass between roughly `00:14` and `00:16` covered
**`dev-app-proto`, `node-red`, the `docker-hub-build-deploy-server` and OpenVPN**, and the
recording does not make clear what was already done, by whom, or what still needs Armen. Three
tickets — **`OP-103`, `OP-92`, `OP-104`** — were therefore **left completely untouched**, and the
gap was handed back to the user as a question instead of being papered over.

The test is blunt: *could you defend this sentence to the person who owns the ticket, from the
transcript alone?* If not, it goes in bucket 3. A confident-sounding reconstruction is worse than
nothing, because nobody downstream can tell it apart from a real decision.

### Step 8 — Draft the comments

**The house comment shape**, in order:

1. **A bolded lead line:** `**DevSecOps meeting update — YYYY-MM-DD**`, optionally followed by an
   em-dash and a **short verdict clause** — e.g. `**DevSecOps meeting update — 2026-08-24** —
   direction is decommission, not harden.` The verdict clause earns its place when the meeting
   genuinely flipped or settled the ticket's heading; leave it off when the update is incremental.
   Someone scanning the ticket's comment stream should get the answer from this line alone.
2. **One to three short blocks.** Each is a sentence or two, or a tight three-bullet list. What
   was decided, what changes, what it means for this ticket. Not a narrative of the discussion —
   the *outcome* of it.
3. **A `⚠️` line, when and only when there is one** — a blocking question the meeting left open,
   or a named owner's action. One per comment at most; two `⚠️` lines and neither reads as urgent.
   Examples in shape: `⚠️ Ownership of protect.bitpool.com is unresolved — nobody in the meeting
   could say who runs it. Needs an answer before any hardening work starts.` / `⚠️ Armen to
   confirm the relocation target before this moves.`
4. **A closing cross-reference line**, using **plain markdown links** — e.g. `Ground rules for all
   legacy VMs are on [OP-9](https://bitpool.atlassian.net/browse/OP-9); tagging context on
   [OP-88](https://bitpool.atlassian.net/browse/OP-88).` Never a formal Jira issue link, never a
   bare key without a link, never a raw URL. **Cross-reference OP keys only.** Never link a CSIP
   ticket, a Drata control URL (`app.drata.com`), or a GitBook / private-wiki page from a comment
   — those are compliance cross-references and belong to `/create-devsecops-ticket`'s description
   section, not to a direction update.

**Keep it short.** This is a direction update. If a draft is sprawling, the extra material almost
always belongs in the Step 12 notes page, not on the ticket.

**No DCF control table.** Say it plainly, because the temptation is real when the neighbouring
skill produces exactly such a table: **this skill does not attach control tables to tickets.**
That is `/create-devsecops-ticket`'s job, and it does it on the **description** field. Here, a DCF
is named **inline, in a plain sentence, only where the meeting decision genuinely moves that
control** — for instance where a decision to decommission a host removes the manual process a
control was flagging. No table, no Drata link, no control lookup: `Drata_*` calls are banned in
this skill, so a DCF mentioned here is only ever one the *meeting itself* raised, never one you
went and found.

**The third source of a DCF code — the ticket's own summary.** OP summaries frequently carry one:
`OP-6` is *"DCF-88 Re-enable WAF"*, `OP-9` is *"DCF-18 Vulnerability scans…"*. **A DCF code that
appears in the ticket's own summary may be repeated as part of the ticket's name, but never
treated as a control claim** — do not write that the decision satisfies, closes or advances it
unless the meeting itself said so. Naming the ticket is not asserting anything about the control.

**The DCF table already in the description is read-only context.** Many OP tickets already carry a
`## DevSecOps / ISO 27001 context` section with a DCF control table in the description, written by
`/create-devsecops-ticket` — `OP-9` and `OP-6` both have one, verified. **Read it for context
only.** Never reproduce it in a comment, never extend or correct it, never cite its Drata or CSIP
links, and never edit the description to bring it up to date — `editJiraIssue` is banned. If it is
out of date, that is a hand-back line for `/create-devsecops-ticket`.

**Formatting cautions, learned on 2026-08-24:**

- **Avoid ending a bold run immediately before a code span.** `**Scope:** \`app.bitpool.com\`` and
  `**hook in the** \`bitpool.app\`` both came back from Jira's converter with the emphasis
  silently rewritten. Rephrase so bold and code aren't adjacent (`Scope — \`app.bitpool.com\``)
  and you avoid the drift entirely rather than reporting it later.
- Backticks on every hostname, ticket field, command and identifier. Em-dash for asides.
  Australian spelling — *prioritised*, *recognised*, *behaviour*.
- No headings inside a comment. It's a comment, not a document.

### Step 9 — Preview and approval

**Show every comment, at once, as real rendered markdown in the chat.** Not in a code fence — a
fence displays raw `**` and link syntax instead of the formatting, and the user is being asked to
approve *how it will look on the ticket*. This was an explicit instruction on the 2026-08-24 run
and it is not negotiable.

The preview block contains, in order:

1. **One line on how the meeting date was established** (Step 2).
2. **One line on transcript attribution** — e.g. *"All 466 cues were tagged with a single speaker,
   so per-speaker attribution and an attendee list are unavailable from this file."* — when
   speaker collapse was detected.
3. **Every comment, each under a heading naming its ticket** — `OP-90 — edge.bitpool.com` — with
   the comment body rendered beneath it exactly as it will be posted.
4. **The deliberately-excluded list**, one line each with the reason (Step 7.2).
5. **The unattributable gap**, naming the tickets left untouched and the time range (Step 7.3).
6. **Anything with no ticket home** (Step 6), flagged for `/create-devsecops-ticket`.

Then ask one question: **"Shall I post these N comments?"** Wait for a clear yes.

**If the user edits one, re-show the edited one and re-confirm before posting anything.** Don't
post the nine they approved and hold the tenth — a partially-posted batch is the worst state to be
in, because the user can no longer see at a glance what did and didn't land.

### Step 10 — Post

One `addCommentToJiraIssue` call per ticket. The exact payload shape:

```json
{
  "cloudId": "d7442fe0-cadf-44e1-9313-6b27e16f3fbc",
  "issueIdOrKey": "OP-90",
  "commentBody": "**DevSecOps meeting update — 2026-08-24** — keep it, but it has to move.\n\n…",
  "contentFormat": "markdown"
}
```

- `contentFormat: "markdown"` on **every** call. Without it the body posts as literal asterisks
  and pipes.
- **Nothing else is touched.** No `editJiraIssue` to tidy a description, no `transitionJiraIssue`
  because the meeting said something is done, no `createIssueLink` for the cross-references, no
  assignee change. If the meeting clearly implies a status change or a re-assignment, that is a
  **hand-back line** for the user to action, not a write — record it as you go and report it at
  Step 13, item 6, naming the ticket.
- **Keep the exact submitted text for each ticket** — Step 11 compares against it, so hold it in
  hand rather than reconstructing it from the draft afterwards.
- If a call fails, stop and report which ones landed and which didn't, before retrying. A silent
  retry loop risks double-posting to a ticket that actually succeeded.

### Step 11 — Verify the returned body against what was sent

`addCommentToJiraIssue` returns the created comment. **Compare its `body` against the text you
submitted, per comment.** This is not paranoia — it caught real drift on the very first run.

**The confirmed failure mode (2026-08-24):** Jira's markdown-to-ADF converter silently rewrote
emphasis on **two** comments, in both cases where a **bold run ended immediately before a code
span** — `**Scope:** \`app.bitpool.com\`` and `**hook in the** \`bitpool.app\``. The comments
posted successfully; the formatting was simply not what was approved.

What to do:

- **Report the drift to the user, per comment, naming the ticket and quoting the before/after
  fragment.** Do not report "posted verbatim" when it wasn't — the user approved specific text in
  Step 9 and is entitled to know the platform changed it.
- **Don't auto-repost or auto-edit to fix it.** `editJiraIssue` is banned, and re-posting creates
  a duplicate. Cosmetic emphasis drift is worth reporting and leaving; if the user wants it fixed,
  that's their call and their edit.
- **If the drift is substantive** — a link broken, a `⚠️` line lost, content missing rather than
  merely re-emphasised — say so prominently. That's a different class of problem from a stray
  asterisk.
- The prevention is upstream, in Step 8: don't put bold immediately before a code span in the
  first place.

### Step 12 — Offer the meeting-notes page

On 2026-08-24 the user asked for this **after** the comments were posted, which is why it's now
offered proactively rather than waited for. Ask once: **"Want the same content as a meeting-notes
`.md` file next to the transcript?"**

On a yes, follow [`references/meeting-notes-page.md`](meeting-notes-page.md) — it owns the page's
structure and naming. In outline, the file is written **next to the transcript**, in literally the
folder the transcript file was read from, and it is **named after the transcript, not after the
date**: `<transcript filename without its extension> - meeting notes.md`. The real one: transcript
`Meeting in _DevSecOps_ 1.vtt` → notes `Meeting in _DevSecOps_ 1 - meeting notes.md`. The meeting
date still opens the H1 and every comment; it is just not in the filename. If the input was pasted
text, or has no on-disk location, ask where to write it — never default to the SharePoint
transcripts folder.

It carries **all** of the run's output, not a summary of it: a contents table, every posted
comment **verbatim**, a named-actions table (owner / action / ticket), the deliberately-excluded
content, and the unattributable gap. The notes page is where the length that didn't belong on a
ticket goes.

**This is a single record of what was posted — not notes distribution.** Distributing meeting
notes into a documentation repo is `/notes`.

On a no, drop it — don't write the file anyway "just in case."

### Step 13 — Hand back

Report, in this order:

1. **What was posted** — the count, and each ticket key as a link with a four-or-five-word gloss
   of its verdict. Don't re-paste the comment bodies; the user just read and approved them.
2. **How the meeting date was established** — one line, same wording as the preview.
3. **Attribution status** — if speakers were collapsed, say so and say that the attendee list
   could not be derived from the file.
4. **What was deliberately excluded**, with the reason, and where it should go instead if anywhere
   (`/drive-iso27001` for ISMS/commercial material).
5. **The unattributable gap** — the time range, the systems it covered, and the tickets left
   untouched, framed as a question the user can answer from memory. This is the item most likely
   to be actionable within minutes of the hand-back, because the person who was in the room can
   just *say* what happened.
6. **Any status or assignee change the meeting implied** — named per ticket, framed as *"the
   meeting implies `OP-99` should move to Done; this skill does not transition, so action it
   yourself."* Step 10 refuses to write these on purpose, and this is the only place they surface
   — leave the line out and the implication evaporates with the recording.
7. **Any decision with no ticket home**, named individually. **Hand back and stop. Never invoke
   `/create-devsecops-ticket` yourself in this run — name it as the user's next step.** If the
   user asks at the Step 9 approval gate to create the missing tickets, post the approved
   comments, then tell them to run `/create-devsecops-ticket` in a fresh turn; do not chain into
   it.
8. **Converter drift**, if Step 11 found any.
9. **The notes-page path**, if Step 12 wrote one.

Never end a run without stating items 4 and 5 explicitly, even when both are empty — "nothing
excluded, nothing unattributable" is a meaningful statement about the transcript, and its absence
reads as an omission rather than a clean run.

---

## Improving this skill over time

- **2026-08-24, the speaker-collapse discovery that produced the attribution rule.** The
  transcript's **466 cues were every one of them tagged `<v Eric Sharp>`** despite three people
  speaking — Teams had collapsed the speakers on export. Per-speaker attribution was impossible
  and the attendee list could not be taken from the file at all. The fix is the golden rule above:
  detect collapse rather than trusting the tags, take a named owner only from the *content* of the
  words, and state the limitation in both the preview and the hand-back. If a future run ever
  attributes a decision to a person, check here first — confirm the name came from what was said,
  not from a `<v>` tag.
- **2026-08-24, the two-line-cue trap — the most dangerous bug in the skill.** A cue's text
  frequently wraps onto a second line, and only the first line carries the `<v>` tag. A per-line
  regex that requires the tag drops roughly half the words *and still produces grammatical
  output*, so the failure is invisible on inspection and reads as a coherent meeting. Mechanics
  now live in `references/vtt-parsing.md`, the block-parsing is baked into
  `scripts/vtt_to_text.py`, and Step 3 mandates a post-parse sanity check on word count. If
  extracted decisions ever feel oddly clipped or a topic seems to end mid-thought, re-check the
  parse before re-checking your reading of it.
- **2026-08-24, quoting hell — and why the parser now ships.** A bash heredoc carrying the
  transcript's apostrophes and em-dashes failed **twice** before the parser was written out to a
  `.py` file and executed as a file. That episode is the reason `scripts/vtt_to_text.py` exists
  as a shipped file: Step 3 now **runs** it and never re-implements it. Don't retry inline
  heredocs with clever escaping, and don't write a fresh parser to the scratchpad either — invoke
  the shipped script with `python3 "<skill dir>/scripts/vtt_to_text.py" …` (WSL fallback where the
  native interpreter is a Store stub), per `references/vtt-parsing.md`.
- **2026-08-24, the 267 KB overflow.** `project = OP AND issuetype != Sub-task` with unrestricted
  fields blew the tool-result limit. The recovery — read the persisted output file the tool layer saved with
  `jq`/Python rather than re-running the query — is now Step 5, along with the standing `fields:
  ["summary","status","parent"]` restriction that stops it happening. If a board pull ever
  overflows again, the fix is almost always that the field restriction was dropped.
- **2026-08-24, the `OP-9` discovery that produced the parent-vs-children rule.** All ten
  legacy-VM sub-tasks (`OP-89`…`OP-112`) hang off a single parent. Written naively, the
  cross-cutting vulnerability cadence and ground rules would have been repeated on all ten
  children — ten near-identical comments, and the specific verdict on each host buried in
  boilerplate. Written once on `OP-9`, with only host-specific verdicts on the children, the board
  reads correctly. This only became visible because the sub-task query requested the `parent`
  field; if a future run produces a run of suspiciously similar comments, check whether `parent`
  was pulled at all.
- **2026-08-24, the deliberate exclusion that proved the three-way split.** The certification-body
  commercial discussion (Bolton ~A$1,500 vs Swiss/BSI ~US$3,000, accreditation weight,
  internal-audit sourcing) is real, useful content — and completely wrong for an engineering
  board. So is a Jira review-workflow preference aired in passing. The user's brief said "some
  content in the mid part is not relevant", which authorised **excluding** it, not **hiding** it.
  Bucket 2 of Step 7 exists so the exclusion is a visible decision the user can overturn before
  anything posts.
- **2026-08-24, the unattributable stretch that produced bucket 3.** A rapid `00:14`–`00:16` pass
  over `dev-app-proto`, `node-red`, `docker-hub-build-deploy-server` and OpenVPN left it genuinely
  unclear what had been done, by whom, and what still needed Armen. `OP-103`, `OP-92` and `OP-104`
  were left untouched and the gap was reported. **This is the behaviour to protect hardest.** The
  pressure to produce a comment for every ticket the meeting mentioned is strong and always will
  be; a plausible reconstruction of a mumbled two minutes is indistinguishable from a real
  decision once it's posted, and it is the one output of this skill that can actively mislead the
  team. If a future run ever fills a gap it couldn't hear, the fix is here.
- **2026-08-24, the converter drift that produced Step 11.** Jira's markdown converter silently
  rewrote emphasis on two comments where a bold run ended immediately before a code span. The
  drift was reported rather than glossed over as a verbatim post. Two lasting changes: Step 8
  avoids the bold-then-code adjacency in drafting, and Step 11 compares the returned body against
  the submitted text on every comment. If the converter starts mangling something new — nested
  lists, or links inside bold are the likely next candidates — record the shape here and add it to
  Step 8's cautions.
- **2026-08-24, the notes page that was asked for afterwards.** The user requested a meeting-notes
  `.md` only after the comments had posted. It's now Step 12, offered proactively, because the
  content is already in hand at that moment and reassembling it later costs a second read of the
  transcript. It also gives the length that doesn't belong on a ticket somewhere legitimate to go,
  which is part of what keeps the comments short.
- **The scope boundary is the thing most likely to erode.** This skill comments; it does not
  create, transition, map controls, or touch CSIP. Every one of those is a neighbouring skill's
  job and every one of them will feel tempting mid-run — especially attaching a control table,
  because `/create-devsecops-ticket` produces exactly such a table two folders away. If this skill
  ever starts creating tickets or writing DCF tables, the fix isn't a new rule, it's re-reading
  the config block's banned-verb list and the "no DCF control table" golden rule.
- **If the OP board ever splits, or a dedicated DevSecOps project appears**, Step 5's two queries
  and the config block's board note are the only things that need changing — but re-confirm with
  the user before changing them, since **"OP by default, `BT` only when the user names it, CSIP
  never"** was an explicit scoping decision, not a default. Only the first two tiers are open to
  renegotiation. The CSIP ban is not a scoping default that a board reshuffle can loosen and it is
  not something a user request widens: however the projects are rearranged, CSIP stays out and
  routes to `/drive-iso27001`.
