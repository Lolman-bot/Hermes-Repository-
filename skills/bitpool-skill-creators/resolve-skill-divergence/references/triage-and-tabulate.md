# Re-verifying, deciding, and putting it to the user

## Re-verify first — always

A log is a claim about a repo that existed when it was written. Before you recommend anything, go
and look at the repo as it is **now**.

For each log:

1. Open the file at `skill_path` in the clone with `read_file` (on `origin/main`, freshly fetched).
   Does it still exist? Has it moved? Is the repo `version` newer than the log's `skill_version`?
2. Find the quoted text from **What the skill claims**. Is it still there, word for word?
3. If the claim is a factual one, re-test it if you cheaply can. A `fact-contradicted` log about a
   connector is worth one live call; a log about a filesystem path is worth one `search_files`.
4. Check whether the same wording appears elsewhere. A stale line copied into three skills is one
   finding with three fixes, not three findings.

`search_files` with the quoted phrase as the pattern and `path` = `skills` in the clone (the
equivalent of `git grep -n "<the quoted phrase>" -- skills/`).

That grep is the single highest-value step in this file. It catches the case where the log named one
file and the problem lives in four, and it catches the case where somebody already fixed it.

**Never recommend from the log's text alone.** If you could not verify — the connector is down, the
path is on another machine — say so in the row and recommend `needs-info`, rather than proposing a
fix you cannot stand behind.

## The seven verdicts

Every row gets exactly one.

| Verdict | When | What it does |
|---|---|---|
| `apply-as-proposed` | The log's suggested fix is still correct and still applies cleanly. | Edit the skill as the log proposes. Closes the log `resolved`. |
| `apply-modified` | The diagnosis holds but the proposed fix is wrong, incomplete, or has a better form. | Edit with your wording, and record in `resolution` how it differed and why. Closes `resolved`. |
| `already-fixed` | The skill has changed since the log; the problem is gone. | No repo change. Closes `resolved`, with `resolution` naming what changed and roughly when. |
| `duplicate` | The same finding as an earlier log. | No repo change. Closes `duplicate`, sets `duplicate_of` to the earlier log's filename. Fix the *earlier* one. |
| `wont-fix` | The behaviour is deliberate, or the cure costs more than the disease. | No repo change. Closes `wont-fix`, and `resolution` must give the actual reason — "by design" alone is not a reason. |
| `escalate` | The fix is structural: a rename, a retirement, a split, a move between sections. | Hand to `/edit-skill`. Closes `resolved` only once that lands; otherwise stays `unresolved`. |
| `needs-info` | It cannot be decided without something you do not have — a decision, an account, a working connector. | Stays `unresolved`. Record the specific question and who can answer it. |

Two habits worth keeping:

- **Prefer `apply-modified` over `apply-as-proposed` when in doubt.** The log's author was mid-task
  and proposing quickly; you are looking at it deliberately. Improving the fix is the job.
- **`wont-fix` is a real answer, not a failure.** A log that was considered and rejected has done its
  work. Say why, clearly enough that the same thing does not get logged again next month.

## Standard remedy: paths and per-person settings

The most common divergence by far is a value hardcoded for one person — a repo checkout location, a
browser profile, an install directory. It is worth knowing the house answer before you triage one,
because the obvious fix is the wrong one.

**Never recommend a second hardcoded value.** Adding this machine's path alongside the original, or
trying both in turn, is `apply-as-proposed` thinking: it clears the row and re-opens it the next
time someone with a third layout runs the skill.

The remedy is `/user-config-store` (`skills/bitpool-required-skills/user-config-store/`) — ask once,
store `- key: value` in `<OneDrive>\skill-config\<skill-name>.md`, read it back thereafter (see
its `references/config-file-pattern.md`). When a
log proposes a hardcoded path, that is normally `apply-modified`, not `apply-as-proposed`, and the
modification is this.

Before recommending it, check three things:

1. **The skill still exists.** Confirm the folder is there. Recommending a retired skill is exactly
   the kind of stale claim these logs exist to catch — do not become the next entry.
2. **The value is not a credential.** `user-config-store` refuses secrets, tokens and passwords by
   design. If that is what is being hardcoded, this is not the fix and the finding is more serious
   than a path issue — raise it (secrets belong in `required_environment_variables` /
   `$HERMES_HOME/.env`).
3. **How many files carry the same value.** One stale path is usually several. Search (`search_files`) before you scope
   the fix, and fix every copy in the same pass.

Say plainly in the `Why` column when the fix would be the first use of the pattern in the repo. It
is still the right answer, but the user is approving a convention as well as a change, and they
should know that is what they are doing.

## Structural versus content — where the line sits

| Do it yourself | Hand to `/edit-skill` |
|---|---|
| Correcting wording in `SKILL.md` or a reference file | Renaming a skill (folder + `name` + slash command) |
| Fixing a stale path, command, flag or threshold | Retiring or archiving a skill |
| Adding a missing step, caveat or anti-trigger | Splitting one skill into two, or merging two |
| Tightening the `description` (<= 60 chars) or the `## When to Use` / `Don't use for:` list | Moving a skill between sections |
| Adding or correcting a `references/` file | Anything that changes what the skill *is* |

When you do it yourself you still owe the full house obligations — see
`references/apply-and-stamp.md`. Doing the edit is not the whole job.

## The table

One table, every selected log, before anything is written. Order by severity descending, then oldest
first.

```markdown
| # | Log | Skill | Type | Sev | Still true? | Recommended | Why |
|---|---|---|---|---|---|---|---|
| 1 | 2026-08-25_1116 | create-new-skill | workflow-gap | low | Yes — 3 files | `apply-modified` | Path is stale in 3 places, not 1; store it via user-config-store instead of a second guess |
| 2 | 2026-08-19_0930 | ask-drata | fact-contradicted | high | No | `already-fixed` | Line was corrected on 2026-08-22; current wording matches observed behaviour |
```

Rules for the table:

- **`Still true?` is not optional.** It is the column that proves you re-verified rather than
  re-read. "Yes", "No", or "Couldn't check — <reason>".
- **`Why` must be specific enough to disagree with.** A user should be able to look at one row and
  say "no, do the other thing". "Needs updating" gives them nothing to push back on.
- Use the log's date-time stem as its `Log` label, not the whole filename — the table has to stay
  readable in a terminal.
- If two rows propose conflicting changes to the same file, mark both and say so under the table.
  Never quietly apply both.

## Then ask

Put the rows to the user with `clarify`, **nothing pre-selected**. `clarify` takes one answer from
up to four choices plus free text, so offer groupings ("all `already-fixed` rows", "rows 1, 3"),
and accept a free-text list of row numbers. Group
sensibly when there are many: "all the `already-fixed` ones" is a reasonable single option, because
they carry no repo change.

State plainly under the table what the approved set would touch — how many skills, how many files,
which skills get a `version` bump. The user is approving a repo change, not a spreadsheet.

Rows the user does not pick stay `unresolved`. Do not argue for them a second time.
