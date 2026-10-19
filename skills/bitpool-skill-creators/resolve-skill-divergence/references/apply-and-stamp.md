# Making the change, then closing the log

Order matters throughout: **repo first, log second.** A log stamped against a change that never
landed is worse than an open log, because nobody looks again.

## Applying a fix yourself

Pre-flight, on the same lines as `/create-new-skill` and `/edit-skill`. The clone path comes from
`/user-config-store` (`get edit-skill clone_path`); if it's missing, ask once with `clarify` and
`set` it. Never probe guessed paths. Then, with `terminal`:

```bash
cd "<clone_path>"
git remote get-url origin         # must be github.com/Lolman-bot/Hermes-Repository-(.git)
git status --short                # note anything already there
git fetch origin --prune
git checkout -b edit/skill-divergences-<yyyy-mm-dd> origin/main
```

If `origin` is the Claude-era `bitpool/ai-skills` (or the retired `ai-skills-beta`), stop — that
clone publishes Claude plugin skills, not these. If `origin` is anything else, stop. If someone
else's uncommitted work is sitting in the tree, show it and ask before adding to it.

**Never edit on `main`.** It only takes changes through a pull request that an approver signs off,
so every fix in this pass goes on the one `edit/skill-divergences-<date>` branch (lowercase). Before
editing a skill, check nobody already has a pull request open on it:

```bash
gh pr list --repo Lolman-bot/Hermes-Repository- --state open \
  --json number,author,headRefName,url,files \
  --jq '.[] | select(any(.files[]; .path | startswith("skills/<section>/<skill-name>/"))) | "#\(.number) \(.author.login) \(.headRefName) \(.url)"'
```

If one is open, name it and leave that skill's rows `unresolved` until it merges — two pull requests
changing one skill at once means one overwrites the other.

Then edit with `patch` (targeted) or `write_file` (whole file, after a full `read_file`). Every fix
you make yourself still owes the full house obligations from the repo `README.md` ("House rules for
authoring skills" — read it fresh; it wins over this file):

1. **The skill's own files** — `SKILL.md` and any `references/`, `assets/`, `scripts/`,
   `templates/`. Frontmatter stays in the house shape; a `description` change stays <= 60 chars and
   starts `Use when`.
2. **A `version` bump in that skill's frontmatter** — content and wording fixes are patch
   (`1.0.0` → `1.0.1`). Without it `hermes skills update` never offers the fix to installed copies.
3. **The README Skills row**, if the skill's one-line summary is now wrong.
4. **The `skills-catalogue` snapshot**, if the change makes the published row misleading (same
   refresh `/edit-skill` does — see its `references/publish.md`).
5. **Duplicated reference files.** Several skills deliberately ship identical files under
   `references/`. If the wrong line lives in one of those, it lives in all of them: find the copies
   with `search_files` (`target="files"`, pattern `<filename>`, path `skills`). Fix every copy and
   bump every skill that carries one.

Then run `/update-hermes-skill` for the housekeeping sweep (it runs
`python skills/bitpool-required-skills/update-hermes-skill/scripts/verify_repo.py . --base origin/main`;
it must exit 0), show `git diff --cached`, and **stage without committing**. The user commits, and
the branch goes up as **one** pull request for the whole pass — `git push -u origin <branch>` then
`gh pr create --repo Lolman-bot/Hermes-Repository- --base main --head <branch>`, or the compare link
`https://github.com/Lolman-bot/Hermes-Repository-/compare/main...<branch>?expand=1` if `gh` isn't
set up. Say that, and say that the fixes aren't live until an approver signs it off and it merges.

If several logs touch the same skill, apply them together and bump that skill once. Multiple bumps
for one editing pass is noise — and so is more than one pull request for one pass.

## Handing off to `/edit-skill`

For `escalate` rows, invoke `/edit-skill` (load it with `skill_view`) and give it the finding, not
the log file — the skill, the file, what is wrong, and what the log proposed. Let it run its own
route, which ends in its own pull request for that skill. Don't also fix that skill directly in this
pass — every finding for a skill that's going to `/edit-skill` goes to it, so the skill has one pull
request, not two.

The log stays `unresolved` until that hand-off actually produces a change. If the user abandons it
part-way, that is a real outcome: leave the log open and say so.

## Stamping the log

Only after the repo change is on disk and you have verified it. Only for rows that were actioned.

Update the frontmatter in place with `patch` — the fields are already present and empty (field
names per `/log-skill-divergence`'s `references/log-file-spec.md`):

```yaml
status: resolved
resolved_at: 2026-10-25T14:20+10:00
resolved_by: [the person's display name]
resolution: Replaced the hardcoded clone probe in all three locations with a user-config-store lookup.
resolution_pr:
duplicate_of:
archived_at: 2026-10-25T14:22+10:00
```

| Field | Rule |
|---|---|
| `status` | `resolved`, `wont-fix` or `duplicate`. Never anything else, and never back to `unresolved`. |
| `resolved_at` | ISO 8601 with local offset. Absolute, never relative. |
| `resolved_by` | Who ran this. The same source `/log-skill-divergence` uses for `logged_by`: `/user-config-store` `get log-skill-divergence display_name`; if missing, ask once with `clarify` and `set` it. Never read credential files for a name. |
| `resolution` | One or two sentences: what was actually done, or the real reason it was not. **An empty `resolution` on a closed log is a defect.** |
| `resolution_pr` | The pull request URL, once the user has pushed and raised it. Leave empty while only staged, and say so — do not invent one. |
| `duplicate_of` | Only on `duplicate`. The earlier log's filename, exactly. |
| `archived_at` | When you moved the file into `Archive/`. Set it in the same pass as the move, never before. |

If an older log carries `resolution_commit` instead of `resolution_pr`, fill the field it has; don't
rename fields in someone else's file.

Then append a resolution block to the bottom of the log, below the marker comment the template
leaves there:

```markdown
## Resolution

**resolved** — 2026-10-25 by [name]

[What was changed, in which files. If the fix differed from what the log proposed, say how and why —
that difference is the most useful thing on the page for whoever writes the next log.]

[For `wont-fix`: the actual reasoning. For `duplicate`: which log supersedes this one and why that
one is the better record. For `already-fixed`: what changed the skill, and roughly when.]
```

Never edit the sections above that marker. The original finding stays exactly as it was written,
including the parts that turned out to be wrong — that is the point of a record.

## Archiving the file

A log that has reached a terminal status is **moved** out of the root:

```
Hermes Skill logging/Archive/<YY-MM>/<original-filename>.md
```

`<YY-MM>` is the month in `resolved_at` — **the month it was resolved, not the month it was logged**.
A log raised in July and closed in September 2026 files under `26-09`. Create the folder if it is
not there. Move with a cross-platform command via `terminal`, e.g.
`python -c "import os,shutil,sys; os.makedirs(sys.argv[2],exist_ok=True); shutil.move(sys.argv[1],sys.argv[2])" "<log>" "<lib>/Archive/<YY-MM>"`.

The order matters:

1. The repo change is on disk and verified.
2. Stamp the frontmatter — `status`, `resolved_at`, `resolved_by`, `resolution`.
3. Move the file into `Archive/<YY-MM>/`.
4. Set `archived_at` and repoint the index link.

Never move a file you did not stamp, and never stamp a status you did not act on. If the move fails,
leave `archived_at` empty and say so — a log sitting in the root with a terminal status is obvious
and recoverable, whereas one that claims to be archived and is not is a lie in the record.

**Never delete a log, and never rename one on the way in.** The filename is how the index row, other
logs' `duplicate_of` fields, and any conversation about it all refer to the file.

## Updating the index

The `status` cell in `index.md` must match the log's frontmatter, and the link must point at wherever
the file now lives — `Archive/<YY-MM>/<filename>` once archived. Rewrite **only those two cells** on
the affected row with `patch`; leave every other row untouched, and never reorder.

**The row itself never moves.** The index is the full history of every log ever written, archived or
not, in one place.

If a row is missing for a log that exists, add it. If `index.md` disagrees with the logs across the
board, say so — the index has drifted and the user should know.

> **Never round-trip these files through Windows PowerShell.** `Get-Content` defaults to the ANSI
> codepage and mangles every em-dash; `Set-Content -Encoding utf8` on PowerShell 5.1 adds a BOM.
> Both were observed the first time the Claude-era divergence logger ran. Use `patch` for a targeted
> change, or build the whole file and `write_file` it once.

## Reporting back

Facts, not a summary:

- Which skills changed, which files, and each new `version` — from `git diff --cached --stat`.
- Which logs closed, and as what — and which `Archive/<YY-MM>/` folder each went to.
- Which stayed `unresolved`, and the specific reason for each.
- That the change is **staged, not committed**, and that installed copies will not see it until the
  pull request merges and they run `hermes skills update`.
- If any `resolution_pr` is empty pending the user's commit and pull request, say which logs need it
  filled in.
