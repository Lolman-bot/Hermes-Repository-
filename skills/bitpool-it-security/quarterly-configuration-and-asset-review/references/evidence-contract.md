# The evidence contract

Shared by every sub-task. Read this on every run.

The thing being evidenced is **that the review happened and what it found** — not that the estate is
perfect. An auditor asking "show me the register as at 30 June" cannot be answered by a live query,
because a live query only ever shows today. The retained extract and the dated comment are the
answer.

## Order of the last three steps

Non-negotiable, and the most common way this cycle goes wrong:

1. **Correct the register.**
2. **Retain the evidence** — save the extracts to the cycle folder, post the comment.
3. **Close the ticket** — the user does this, not Hermes.

A closed ticket over a register that still disagrees with live state is worse than an open one. It
asserts a check passed when it did not.

## Where the evidence is retained

**Not on the Jira ticket.** Changed 2026-09-17. The extracts live in the GRC SharePoint library, in a
folder named for the cycle:

    https://bitpoolau.sharepoint.com/sites/GRC/Shared Documents
      /General/Drata/Evidence/Asset register review
        /Asset register review - <YYYY> <MM>/

So this quarter's folder is `Asset register review - 2026 09`.

**Cite the SharePoint path in a ticket, never the local one.** The library syncs to
`...\GRC - Bitpool - Documents\General\Drata\Evidence\Asset register review\`, but a
`C:\Users\<someone>\...` path is that one person's machine and means nothing to the next reader.

Grouping by **cycle** rather than by register is deliberate. The question an auditor asks is "show me
the register as at <date>" — one folder answers it whole. Grouped by register, the same question
means opening six folders and filtering each by date.

The folder is named `- 2026 09`, not `- 2026 Q3`, because Bitpool's financial year starts in July:
"Q3" means Jul–Sep to a calendar reader and Jan–Mar to a finance reader. The month number has no
second meaning.

### The one exception: the Intune configuration dump

Changed 2026-09-24. The **configuration** half of the Intune run — `intune-config-export.json` and
the files collected with it — is not filed in this folder. The exporter places it, unaltered, into
`security-documentation-restricted/configuration-hardening/dumps/YYYY-MM-DD/`, and that dated folder
in the repo is its retention store; the evidence pack built from it is what goes to Drata. Cite it by
that repo path, never a local one. See `configuration-evidence-pack.md`.

Everything else in this contract applies to it unchanged: raw and unedited, the filename kept, the
comment quoting it exactly, and the order of the last three steps. The **device** export from the
same Intune run is an ordinary extract and comes here.

### Files keep the name the source gave them

**Do not rename an export.** An untouched filename is a provenance argument — nobody can claim the
file was edited between extraction and filing — and the cycle folder already carries the date.

**The consequence: the comment must quote the filename exactly.** Export filenames are frequently
opaque. `DevicesWithInventory_f12b09a1-7f35-4009-a3b9-143987848c40.csv` says nothing about what it
is, when it was taken, or which cycle it belongs to. That exact string is the **only** join between
the comment and the file on disk, so a comment that refers to "the Intune export" points at nothing
and the evidence is orphaned the moment a second one exists.

The extracts are the **raw** output, unedited, exactly as the source produced them. Not a cleaned-up
version, not a summary, not a spreadsheet someone tidied.

Hermes **cannot write to SharePoint and cannot attach to Jira**. Name the files and the cycle folder
they belong in, then let the user save them. Track the backlog if they are batching — never claim a
file has been retained.

A comment asserting a conclusion with no extract behind it is an assertion, not evidence.

### What this arrangement trades away

A Jira attachment travelled with the ticket and could not be quietly replaced. A SharePoint folder is
neither of those things: a file can be overwritten or deleted, version history can be pruned, and the
ticket no longer carries its own evidence. Two habits are what hold it together:

- **A closed cycle's folder is not reopened.** Corrections go in the next cycle's folder with a
  comment explaining them, exactly as `## Correcting an earlier comment` requires.
- **The comment names the exact filename**, so a missing file is *detectable* on inspection rather
  than silently absent.

## The comment shape

Post one comment per sub-task, per cycle. Six sections, in this order.

### 1. Sources and extract dates

A table, one row per source: what it is, **the filename exactly as saved**, the cycle folder it sits
in, the date it was pulled, and anything about its scope worth knowing. Two sources pulled a week apart will disagree about anyone who joined or
left in between, and that disagreement will read as a finding.

### 2. Scope of the extract

What the extract actually covers, in counts. "28 devices — 21 Windows, 3 macOS, 4 iOS. `Ownership =
Corporate` on all 28." This is what makes the result reproducible.

### 3. Outcome per check

One subsection per check the register's procedure defines. State the result even when it is clean,
**with the count** — "populated on 28 of 28". A check listed with no outcome reads as skipped.

### 4. Findings, with a disposition each

A table: the finding, and what was done about it. Every exception gets its own row. "8 devices
missing, all added" with the identifiers beats "the register had drifted".

A finding with no disposition is an open loop that nobody owns.

### 5. What remains open

Anything not resolved this cycle, and why. An honest open item is fine; a silently dropped one is
not. Where a `TODO` was left on a wiki page, say so and quote it.

### 6. Limits of this extract

Only where a real one exists — a blind spot the method cannot see. State it rather than letting a
reader assume the coverage was total. Worked example: the Intune extract lists only Intune-managed
records, so a device that is Entra-joined but never enrolled is invisible to it.

## Recording a no-change result

**The most common outcome, and it still needs the full comment.** Sources, dates, scope, and each
check with its count — then "no findings this cycle".

Do not shorten it to "no change". That sentence is indistinguishable from nobody having looked, and
it is the one an auditor will push on.

## Correcting an earlier comment

If a previous cycle's comment recorded something wrongly, post a **new** comment correcting it and
say plainly what the earlier one got wrong. Never quietly edit history — the correction is itself
part of the record, and an amended comment with no trail looks worse than the original error.
