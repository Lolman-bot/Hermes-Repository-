# Getting the change ready, then raising the pull request

The change goes up as **one pull request** against `main` on `Lolman-bot/Hermes-Repository-`, from
the `edit/<skill-name>` (or `retire/<skill-name>`) branch made in `choose-and-pull.md`. `main` only
changes through a pull request, and a push after an approval means the approver has to look again.
So the pull request is raised **once, when the change is finished**.

## Run the housekeeping first

Run `/update-hermes-skill` **before** the readiness check: the `version` bump (patch for a content
fix, minor for new behaviour or a new support file, major for a rename or a change to what it
writes/where it publishes), the README row, and the checker. Run it after and the approver reviews a
half-change.

## Refresh the skills-catalogue snapshot

Bring `skills/bitpool-required-skills/skills-catalogue/references/catalogue-snapshot.md` in line with the README's
now-updated Skills table — add, remove or reword rows so it says exactly what the README says — bump
its **Snapshot taken:** date line to today, and bump `skills-catalogue`'s `version` (patch). Skip
only when the skill you changed *is* `skills-catalogue` and your edit already covers the snapshot. If
the file has moved, find it with `search_files` and say what you found. A skipped refresh means
`skills-catalogue` quietly gives people a wrong answer.

## Everything in one pull request

- the skill folder changes — or, on the retire route, the `git mv` into `retired/`
- the bumped `version` in every skill touched (including duplicated-reference carriers and any skill
  whose pointer you fixed)
- the README row change
- the refreshed `skills-catalogue` snapshot

## The readiness check

### 1. The checks

```bash
python skills/bitpool-required-skills/update-hermes-skill/scripts/verify_repo.py . --base origin/main
```

Show it as a ✅ / ❌ table. Then confirm by reading:

| Check | How |
|---|---|
| The change does what the user asked, in the right file | Re-read the before/after |
| Body sections still in house order, Procedure steps have "Done when" | Read `SKILL.md` |
| README row summary matches the new behaviour | Read the row |
| Every duplicated-reference copy got the same change | `search_files` `target="files"` for the filename under `skills` |
| Snapshot refreshed and dated today | Read it |
| No credentials, tokens or someone's absolute paths in the diff | `search_files` the changed folders for `C:\\Users\\`, `/Users/`, `/home/`, `token`, `secret`, `password` |
| Tests under `scripts/` pass, if any | Run them |
| Retire route: renames, not deletions | `git status --short` shows `R`, no `D` |

Every ❌ gets fixed first.

### 2. Ask whether it's really ready

Stage with a pathspec and show the full diff:

```bash
git add -- skills README.md        # retire route: git add -- skills README.md retired
git status --short
git diff --cached --stat
git diff --cached
```

Say plainly what raising it means, then ask with `clarify`:

> Raising the pull request sends this to the repo's approver. Once merged, anyone who installed the
> skill gets it with `hermes skills update`. If anything changes after approval, it needs approving
> again — so it should be finished now, not nearly finished. Is it ready?

Choices:

- **It's finished — raise the pull request** → next section.
- **Try it out first** → save on the branch (below) and test locally (below). The user runs
  `/edit-skill` again afterwards; section 6 of `choose-and-pull.md` picks the branch back up.
- **Not yet — I want to change more** → back to the route.

If the changed behaviour hasn't run on a real task, say so and put **Try it out first** first,
marked recommended. Silence, "probably" or "close enough" is not a yes.

**Saving without publishing:**

```bash
git commit -m "WIP: <skill-name> — not yet raised"
```

### Trying the change locally

Copy the branch version over the user's installed copy so `/<skill-name>` runs it:

```bash
mkdir -p "$HERMES_HOME/skills/bitpool"
cp -r "skills/<section>/<skill-name>" "$HERMES_HOME/skills/bitpool/"
```

If the skill is installed elsewhere (another category), copy over that folder instead — find it with
`skill_view(name="<skill-name>")`, which reports its directory — so there aren't two copies. Then
`/reload-skills` or a new session. If `$HERMES_HOME` is unset in the shell, ask the user (or run
`hermes config path`) rather than guessing.

Tell them: this copy is now "locally modified", so `hermes skills update` will skip it. Once the PR
merges, run `hermes skills update <skill-name> --force` to go back to the published version.

## Commit, push, raise the pull request

Only after an explicit **It's finished**:

```bash
git commit -m "Update <skill-name> to <new-version>" -m "<One or two lines on what changed and why.>"
git push -u origin "<branch>"
gh pr create --repo Lolman-bot/Hermes-Repository- --base main --head "<branch>" \
  --title "Update <skill-name> to <new-version>" --body-file "<temp file in the scratch dir>"
```

For a retirement the subject is `Retire <skill-name>`, and the body says it moved to
`retired/<section>/<skill-name>/`.

PR body, plain words:

```markdown
## What changes
<What the skill does differently now, and why. Two or three sentences. For a rename or retirement,
what installed users must do.>

## What's in it
- skills/<section>/<skill-name>/ <old-version> → <new-version>
- README Skills row
- skills-catalogue snapshot refresh (<old> → <new>)
- <any other skill bumped, and why>

## Ready to publish
- House-rules checker: all PASS
- Tried on a real task: <yes — what / no — why not>
- Confirmed ready by <user> on <date>
```

Don't request reviewers by hand unless asked; never approve, merge or enable auto-merge.

| What goes wrong | What to do |
|---|---|
| Push refused, 403 | No write access. Stop; tell them to ask Eric to add their GitHub username to the repo. The commit is safe on the branch. |
| Push refused, remote branch moved | `git pull --rebase origin "<branch>"`, re-check the diff, push again. Never `--force`. |
| `gh` missing / not signed in | The branch is pushed. Give them `https://github.com/Lolman-bot/Hermes-Repository-/compare/main...<branch>?expand=1` plus the title and body to paste. |

Adding to a PR this user already has open: push to the same branch, skip `gh pr create`, and say it
resets any approval.

## After the pull request is up

```bash
gh pr view "<branch>" --repo Lolman-bot/Hermes-Repository- --json number,url,title
git log --oneline -1
```

Tell the user plainly:

- the PR link and number, and what's in it;
- **it isn't live yet** — it needs approving and merging; nobody approves their own PR;
- **anything changed from here resets the approval**;
- after merge, installed copies update with `hermes skills check` / `hermes skills update`
  (`--force` if they tested locally); a rename or retirement needs the uninstall/install steps above.

Return the clone to `main`:

```bash
git checkout main
git merge --ff-only origin/main
```

Leave the branch; a later run can `git branch -D "<branch>"` once `gh pr view "<branch>" --repo
Lolman-bot/Hermes-Repository- --json state` shows `MERGED`.

## The `/skill-health` offer

`/skill-health` grades a skill on a run that actually happened, so it belongs **before** the PR.
Offer it when the user comes back from **Try it out first**, or when a real run of the changed skill
is in front of you. Explain first, in plain words:

> Want me to run `/skill-health` on that run? It grades the skill on how it actually behaved rather
> than what its instructions claim — it turns the skill's own steps and rules into a checklist,
> scores each against what really happened, traces any miss to the line that caused it, and ends
> with a score out of 100 and a ranked list of edits it can apply.

Ask with `clarify`. A yes runs it; silence or no doesn't. Its fixes join this change. After the PR is
up, don't offer it. If they say no, don't re-pitch.

## Never

- Commit or push on `main`, or push anything but this run's branch.
- Raise a PR without an explicit **It's finished** — not for WIP, not "for feedback", not as a draft.
- Raise a second PR for a skill that already has one open.
- Approve, merge or enable auto-merge.
- `git push --force`.
- `git add -A` from the root without a pathspec.
- Commit a credential, a token, or an absolute path from someone's machine.
