---
name: update-devsecops-ticket
description: "Use when a DevSecOps transcript should update OP tickets."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, devsecops, jira, transcript, meeting, vtt]
    category: bitpool
    related_skills: [create-devsecops-ticket, drive-iso27001, notes, change-request]
---

# Update DevSecOps Ticket

Takes the recording of a DevSecOps engineering meeting and feeds what was actually decided back onto the tickets that already exist on the OP (Perun) board — one short comment per ticket, saying where that piece of work is now heading. It is a direction update, not a control mapping and not a status change.

The output is deliberately light. A comment says what changed in the thinking since the ticket was written; the ticket itself, its description, its status and its assignee are all left exactly as they were. It dates the meeting from the calendar, renders every comment for approval before one is posted, says what it left off the board, and offers a markdown write-up after.

## When to Use

- The user invokes `/update-devsecops-ticket`.
- Proactively, when a DevSecOps meeting transcript or `.vtt` is supplied with a request to update existing OP board tickets.

Don't use for:
- An ISO 27001 / CSIP transcript, or anything that would create compliance work: `/drive-iso27001`.
- Filing a transcript into a docs repo's `notes/` folder: `/notes`.
- Control context on a ticket's description: `/create-devsecops-ticket`.
- A decision that needs a controlled production change: flag it, and raise it with `/change-request`.

## Prerequisites

- **Atlassian (Jira) MCP server** added to Hermes (`hermes mcp add ...` or the `manage_connections` tool). The workflow names its tools by their connector names (`addCommentToJiraIssue`, `getJiraIssue`, `searchJiraIssuesUsingJql`); if the names differ, find them with `tool_search`.
- **Microsoft 365 MCP server** for the calendar lookup that dates the meeting (`outlook_calendar_search` in the workflow).
- **Python 3** reachable from `terminal` for `scripts/vtt_to_text.py` (WSL fallback on Windows where the native interpreter is a Store stub — `references/vtt-parsing.md`).
- No Drata server, no SharePoint state folder, no worklog — never stop because one is missing.

## Procedure

**Check rule 1 before writing anything to Jira.** The only write this skill makes is a comment; if you are about to create an issue or edit a field, you are in the wrong skill. Read `references/transcript-to-op-comments-workflow.md` in full before parsing the transcript or querying Jira — it carries the hardcoded config (Jira cloud ID, board, banned verbs) and every step. Read the whole file you reach for.

1. **Resolve the transcript** — look in the usual transcript folder, show candidates with modified times if more than one fits, and copy the true filename from the listing. Done when one file's exact absolute path is confirmed.
2. **Establish the meeting date — never guess.** Calendar entry plus any in-audio time reference. Done when the date and how it was established are stated.
3. **Parse the transcript** by running `scripts/vtt_to_text.py` with `terminal` (never a hand-rolled parser), per `references/vtt-parsing.md`; non-`.vtt` input is read directly. Done when cue count, word count, first/last cue and the speaker-collapse warning are checked.
4. **Read the whole transcript and extract** decisions. Done when every decision has a timestamp.
5. **Pull the OP board** (`project = OP AND issuetype != Sub-task`, paged; recover from the persisted output file on overflow — never re-run blind). Done when you hold key/summary/status/parent for the board.
6. **Map decisions onto existing tickets** — cross-cutting direction goes on the parent once. Done when each decision has a ticket or is marked unmapped.
7. **Three-way split** — in scope / excluded / unattributable. Done when every topic sits in exactly one bucket.
8. **Draft the comments** in the house shape, each opening with the meeting date. Done when every in-scope ticket has one comment.
9. **Preview and approval** — every comment as rendered markdown, never fenced; an explicit yes. Done when the user has approved the exact set.
10. **Post** with `addCommentToJiraIssue` (`contentFormat: "markdown"`). Done when each approved comment returns an id.
11. **Verify the returned body against what was sent** and report any converter drift. Done when drift is reported or none confirmed.
12. **Offer the meeting-notes page** once — on a yes follow `references/meeting-notes-page.md`. Done when the offer is answered.
13. **Hand back** — what was posted, what was excluded and why, what was unattributable (timestamps + skipped keys), and routing for anything that needs a new ticket. Done when nothing left off the board is unmentioned.

## Load-bearing rules

Restated here because each one has already produced a wrong or unpostable result on a real transcript.

1. **Comments only, on tickets that already exist.** The single permitted write is `addCommentToJiraIssue`, with `contentFormat: "markdown"`. Never `createJiraIssue`, `editJiraIssue`, `transitionJiraIssue`, `addWorklogToJiraIssue`, `createIssueLink`, `createConfluencePage` or `updateConfluencePage`. A decision with no ticket to land on gets reported to the user, not given one — and don't chain into the skill that would raise it either. Name `/create-devsecops-ticket` (OP/BT) or `/drive-iso27001` (CSIP) as the user's next step and stop.
2. **OP (Perun) is the board. BT only if the user names it. CSIP never.** Not on request, not when a decision obviously belongs there — say so in the hand-back and route it to `/drive-iso27001`. Never comment on a ticket whose summary matches `Drata | Bitpool | DCF-xxx`: those are Drata-generated control parents, they all live in CSIP, and every write there has to cite a control. This skill also needs no SharePoint state folder and keeps no worklog; never stop because one is missing.
3. **Never guess the meeting date.** The `.vtt` carries none. Confirm it against the calendar entry and any in-audio time reference, and say how you established it. Every comment is stamped with that date, so a wrong one misfiles the whole set.
4. **Never invent attendees, and never attribute a decision to a person the audio does not name.** Teams routinely tags every cue with one speaker even when several people spoke — record decisions as the meeting's, and take attendees from the calendar entry instead.
5. **Unattributable content is reported, never written.** Where the recording does not make clear what was decided, by whom, or what is already done, leave those tickets untouched and tell the user — naming the timestamps and the ticket keys you skipped. A confident-sounding guess on a ticket is worse than a gap.
6. **Cross-cutting direction goes on the parent once.** When a decision governs a whole family of sub-tasks, comment on the parent and say which children it covers. Repeating it on every child is noise that makes the real per-ticket updates harder to find.
7. **Render the preview, don't dump its source.** Show every comment as actual markdown in the chat — real headings, bold and tables — never wrapped in a code fence. A fence shows raw `|---|---|` instead of a table, defeating the point of the review.
8. **Say what you left out, and why.** An engineering meeting carries material that does not belong on the board — commercial decisions, workflow preferences, personnel matters. Name the excluded topics in the hand-back rather than silently dropping them.
9. **Check the returned body against what you sent.** Jira's markdown converter rewrites some emphasis, notably a bold run ending immediately before a code span. Report the drift plainly instead of claiming the text went up verbatim.
10. **This skill maps no controls.** No DCF table, no Drata call, no GitBook lookup. Name a control inline only where the meeting itself raised it. Many OP descriptions already carry a `## DevSecOps / ISO 27001 context` table written by `/create-devsecops-ticket` — read it for context, never reproduce, extend, correct or cite it, and link only OP keys from a comment, never a CSIP ticket or an `app.drata.com` URL.

## Pitfalls

- **Multi-line cues** — only the first line of a cue carries the `<v>` tag; a per-line regex silently drops about half the words and still reads fluently. Run the shipped parser.
- **Speaker collapse** — one distinct `<v>` tag across a multi-person meeting means attribution is unavailable for the whole run.
- **Inline heredocs for Python** — transcript punctuation breaks the quoting; the parser ships as a file for that reason.
- **Retyping the transcript filename** — names get renamed; copy the exact string from the listing.
- **The 267 KB board overflow** — page the JQL and read the persisted output file rather than re-running.
- **Commenting on CSIP or a `Drata | Bitpool | DCF-xxx` parent** because the user asked mid-run — that is a request to run `/drive-iso27001`.

## Verification

- Only `addCommentToJiraIssue` calls were made; all on OP (or a user-named BT) tickets.
- Every comment opens with the confirmed meeting date and attributes nothing to an unnamed person.
- Returned bodies were compared with what was sent; any drift was reported.
- The hand-back names excluded topics, unattributable timestamps with skipped keys, and next-step skills.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/transcript-to-op-comments-workflow.md` | The hardcoded Bitpool config, the golden rules, and the full workflow from resolving the transcript to handing back — the OP board query and its overflow trap, the parent-versus-sub-task rule, the in-scope / excluded / unattributable split, and the house comment shape. |
| `references/vtt-parsing.md` | Reading a Teams `.vtt` without losing or misattributing words — the single-speaker tag trap, the multi-line cue trap, running the shipped parser (with its WSL fallback), and what to do with non-`.vtt` input. |
| `references/meeting-notes-page.md` | The optional markdown write-up offered after the comments are posted — filename, section order, and the tables it carries. Read only if the user accepts the offer. |
| `scripts/vtt_to_text.py` | Turns a Teams `.vtt` into one timestamped line per cue, warning when the file collapses every speaker into a single tag. Executed via `terminal`, never retyped or replaced by a hand-rolled parser. |

Config, golden rules and workflow steps → `references/transcript-to-op-comments-workflow.md`. Transcript-parsing mechanics → `references/vtt-parsing.md`, and the parser itself → `scripts/vtt_to_text.py`. The write-up format → `references/meeting-notes-page.md`. Control mapping, DCF tables and Drata behaviour belong to `/create-devsecops-ticket` and `/ask-drata` — never add either here.
