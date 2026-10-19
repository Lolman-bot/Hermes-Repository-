# Meeting-notes page

Read this **only** when comments have already been posted to the OP board **and** the user has
accepted the offer of a meeting-notes markdown file. It specifies that one deliverable and nothing
else.

The file is a **record of what was posted** — not a second deliverable to be invented, and not a
second pass at the analysis. If no comments were posted, there are no notes to write: say so and
stop. Never write a ticket section for a comment that was previewed but not approved, and never
introduce a decision, action or nuance here that is not in a posted comment.

---

## Filename and location

`<transcript filename without its extension> - meeting notes.md`

- **Named after the transcript, not after the date.** Take the transcript's filename, drop the
  extension, append ` - meeting notes.md`. The real example: transcript `Meeting in _DevSecOps_
  1.vtt` → notes `Meeting in _DevSecOps_ 1 - meeting notes.md`. The two files then sort together
  in the folder, which is the point — the convention exists because the first one was written as
  `2026-08-24 DevSecOps meeting notes.md` and immediately renamed to sit beside its transcript.
- **The meeting date is still everywhere in the file** — it opens the H1 and it opens every posted
  comment reproduced below. It is simply not in the filename, so don't reinstate it there.
- Written **next to the transcript** — literally the folder the transcript file was read from,
  whatever that is. If the input was pasted text, or has no on-disk location, **ask where to write
  it**; never default to the SharePoint transcripts folder.
- **Ask before writing anywhere else.** A different SharePoint folder, a repo, the desktop — each
  needs a yes first. **Never Confluence**, whatever the answer: a wiki or Confluence page is
  `/bitpool-docs`' or `/drive-iso27001`'s job, and the Confluence write verbs are banned in this
  skill.
- **This is a single record of what was posted — not notes distribution.** Distributing meeting
  notes into a documentation repo is `/notes`.

---

## Section order

Exactly this order, every time. Do not add sections and do not reorder.

**1. H1** — `# DevSecOps meeting notes — YYYY-MM-DD`. Em-dash, ISO date, nothing else on the line.

**2. Header block** — four bolded labels, then a `---` rule:

- **Source:** the transcript filename in backticks, plus where it lives (`(this folder)` is
  enough).
- **Calendar entry:** the entry title and its start time with timezone — this records *how the
  date was established*, so name the real entry, e.g. `"Dev Meeting - Dmytro in", 2026-08-24 10:00
  AEST`.
- **Participants:** the attendee list from the calendar entry. If no calendar entry was matched,
  write *"Not established — the .vtt attributes every cue to a single speaker and no calendar
  entry was matched"* and stop there. **Never infer a participant list from the transcript, from
  ticket assignees, or from who usually attends.** A guessed attendee list is the same failure as
  a guessed decision, and it is the thing this skill's strongest rule forbids. Where a list *is*
  established from the calendar, follow it immediately with the honest attribution caveat: Teams
  .vtt files routinely tag every cue to a single speaker, so per-speaker attribution is not
  reliable — statements are recorded as decisions of the meeting rather than quotes from named
  people, except where a name is used explicitly in the audio. Do not dress that up and do not
  omit it; it is the reason the notes read the way they do.
- **Outcome:** how many comments were posted, to which board, on what date — and the explicit
  negative: none of them changed a ticket's status, assignee, or description. Say it even though
  it is obvious; it is the sentence that makes the file safe to circulate.

**3. `## Contents` table** — four columns, `# | Ticket | Subject | Direction`. `#` matches the H2
numbering below. `Ticket` is a markdown link, `[OP-9](https://bitpool.atlassian.net/browse/OP-9)`.
`Subject` is the short ticket title, keeping any DCF reference (`DCF-88 Re-enable WAF`).
`Direction` is the decision in six to ten words (`Decommission, not harden`, `Keep, but relocate`)
— that column is the point of the table and should read on its own as the meeting's outcome. Row
order is the order the comments were posted; the H2 sections follow the same order and the same
numbers.

**4. One H2 per ticket** — `## N. OP-XX — <Subject>`, numbered to match Contents, separated by
`---`. The body carries the comment **verbatim as posted**: the exact markdown string handed to
`addCommentToJiraIssue`. Not a paraphrase, not a tidied version, not a re-wrap, not a merge of two
comments. Where a comment carried cross-cutting ground rules written once on a parent, say so in
the heading — `## 1. OP-9 — DCF-18 Vulnerability scans (parent of the legacy-VM sub-tasks)`.

**5. `## Named actions arising`** — a table, `Owner | Action | Ticket`. One row per named person
per action. Owner is a real name as used in the meeting; the action is imperative and specific
enough to act on without reading the section above it; Ticket is the bare key (`OP-6`), since the
links already live in Contents. Only actions that appear in a posted comment — do not harvest
extra to-dos out of the transcript here.

**6. `## Discussed but deliberately not written to the OP board`** — bullets. Each bullet: a bold
lead-in naming the topic, the substance in a sentence or two carrying the real figures and names
so the reader never has to go back to the audio, and — mandatory — **why it was excluded**. The
why is a short clause, not an apology: "This is ISMS/commercial, not devsecops"; "A working
preference, not a ticket change".

**7. `## Not recorded — transcript too fragmentary to attribute safely`** — prose, not a table.
Name the **exact timestamp range**, the services or topics that went past, what specifically is
unclear (who did what, what is still outstanding), and the **ticket keys left untouched** as
markdown links. Close with what would unblock it — usually that these need confirming verbally
before anything is recorded against them. Omit the section entirely if nothing was dropped, rather
than writing "N/A".

---

## Verbatim, including where Jira altered the rendering

The .md carries the **original wording as sent**, even where Jira's markdown converter rewrote the
rendered comment — typically emphasis collapsing where a bold run ends immediately before a code
span. That is deliberate, and worth one line to the user when handing the file over: the .md is
the clean record, the Jira comment may render slightly differently. Do not "correct" the .md to
match Jira's mangled output, and do not go back and rewrite the Jira comment to chase it.

---

## Skeleton

````markdown
# DevSecOps meeting notes — 2026-08-24

**Source:** `Meeting in _DevSecOps_ 1.vtt` (this folder)
**Calendar entry:** "Dev Meeting - Dmytro in", 2026-08-24 10:00 AEST
**Participants:** <names from the calendar entry, or the not-established sentence>. The .vtt attributes every cue to a single speaker, so per-speaker attribution is not reliable — statements below are recorded as decisions of the meeting rather than quotes from named people, except where a name is used explicitly in the audio.

**Outcome:** <N> update comments posted to the OP board (Perun) on 2026-08-24 — reproduced verbatim below, one section per ticket. These are direction updates only; none of them changed a ticket's status, assignee, or description.

---

## Contents

| # | Ticket | Subject | Direction |
|---|---|---|---|
| 1 | [OP-9](https://bitpool.atlassian.net/browse/OP-9) | DCF-18 Vulnerability scans (parent) | <six-to-ten-word outcome> |

---

## 1. OP-9 — DCF-18 Vulnerability scans (parent of the legacy-VM sub-tasks)

<the posted comment, verbatim>

---

## Named actions arising

| Owner | Action | Ticket |
|---|---|---|
| <Name> | <imperative action> | OP-6 |

---

## Discussed but deliberately not written to the OP board

* **<Topic>.** <Substance, with the real names and figures.> <Why it was excluded.>

## Not recorded — transcript too fragmentary to attribute safely

Around <hh:mm–hh:mm> there is a rapid pass over <topics>. The audio does not make clear <what is unclear>. Nothing was written to [OP-103](https://bitpool.atlassian.net/browse/OP-103) or [OP-92](https://bitpool.atlassian.net/browse/OP-92) as a result — these need confirming verbally before anything is recorded against them.
````
