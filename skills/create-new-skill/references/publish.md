# Writing it into the repo, then raising the pull request

The new skill goes up as **one pull request** against `main` on `Lolman-bot/Hermes-Repository-`,
from an `add/<skill-name>` branch. `main` only changes through a pull request, and a push after an
approval means the approver has to look again. So the pull request is raised **once, when the skill
is finished** — never as a way of saving work in progress.

All commands run in `terminal` from the clone root. Quote every path.

## Pre-flight

Run all of these before writing a single file. Any surprise stops the run and goes to the user.

```bash
git remote get-url origin        # must be github.com/Lolman-bot/Hermes-Repository-(.git)
git status --short               # expect empty
git fetch origin --prune
git branch --list "add/*"        # unfinished work from an earlier run?
```

| What you find | What to do |
|---|---|
| `origin` is `bitpool/ai-skills` or `bitpool/ai-skills-beta` | Stop. That's the Claude plugin repo, not the Hermes one. Offer to clone the Hermes repo fresh into a folder they choose (`git clone https://github.com/Lolman-bot/Hermes-Repository-.git "<folder>"`) and update `clone_path` via `/user-config-store`. Never repoint remotes quietly. |
| `origin` is anything else | Stop. This isn't the skills repo. |
| Uncommitted changes | Stop. Show the list and ask. Never sweep someone else's work into your change. |
| `git fetch` fails | Stop and report it — network or sign-in, not something to work around. |
| A local `add/<skill-name>` branch exists | Unfinished work, usually from **Try it out first**. Ask with `clarify`: pick it up (`git checkout add/<skill-name>`) or start again. Never delete it without asking. |

Then check nobody already has a pull request open adding that name:

```bash
gh pr list --repo Lolman-bot/Hermes-Repository- --state open \
  --json number,author,headRefName,url,files \
  --jq '.[] | select(any(.files[]; .path | startswith("skills/<skill-name>/"))) | "#\(.number) \(.author.login) \(.headRefName) \(.url)"'
gh api user --jq .login          # who "this user" is, for the table below
```

| What you find | What to do |
|---|---|
| Nothing | Carry on. |
| An open PR **this user** raised | Don't open a second one. `git checkout <branch>` then `git pull --ff-only`, and work there. Say that pushing resets any approval it has. |
| An open PR **someone else** raised | Stop. Name the PR, author and link. Same idea → talk to them first; otherwise pick a different name. |
| `gh` missing or not signed in | Say so; ask the user to check https://github.com/Lolman-bot/Hermes-Repository-/pulls for that name before going on. Don't install `gh` for them. |

Then branch from what's live:

```bash
git checkout -b "add/<skill-name>" origin/main
```

Branch names are lowercase. **Nothing is ever written on `main`.**

## Write the files

```
skills/<skill-name>/SKILL.md
skills/<skill-name>/references/*.md
skills/<skill-name>/assets/*   templates/*   scripts/*
```

Write text with `write_file`. Copy assets, templates and scripts with `terminal` `cp`, byte for byte —
a regenerated asset is a different asset. If the skill ships `scripts/`, `SKILL.md` runs them via
`${HERMES_SKILL_DIR}/scripts/<file>`, never paraphrases them.

## Housekeeping and the catalogue snapshot

1. Run `/update-hermes-skill` (load with `skill_view` if needed): it confirms `version: 1.0.0`, adds
   the README **Skills** row (`` | `name` | summary | references/, assets/ ... or — | ``) and runs
   the checker.
2. Refresh `skills/skills-catalogue/references/catalogue-snapshot.md` from the README's now-updated
   Skills table — the new row included, worded exactly as the README states it — bump its
   **Snapshot taken:** date line to today, and bump `skills-catalogue`'s `version` (patch).
   `skills-catalogue` answers offline from that snapshot; skip this and it doesn't know the skill
   exists. If that file has moved, find the snapshot with `search_files` and say what you found.

Both happen **before** the readiness check, so the whole change is one pull request.

## The readiness check

### 1. The checks

```bash
python skills/update-hermes-skill/scripts/verify_repo.py . --base origin/main
```

Show the result to the user as a ✅ / ❌ table (one row per check line). Then confirm by reading:

| Check | How |
|---|---|
| Body sections in house order, each Procedure step has "Done when" | Read `SKILL.md` |
| Every support file is indexed, nothing indexed is missing | Compare the index with the folder listing |
| README row summary matches what the skill does | Read the row |
| Snapshot lists the new skill and is dated today | Read it |
| No credentials, tokens or someone's absolute paths | `search_files` the skill for `C:\\Users\\`, `/Users/`, `/home/`, `token`, `secret`, `password` |
| Any tests under `scripts/` pass | Run them |

Every ❌ gets fixed before going further — an approver would only send it back.

### 2. Ask whether it's really ready

Print the full `SKILL.md`, then stage with a pathspec and show the diff:

```bash
git add -- "skills/<skill-name>" "skills/skills-catalogue" README.md
git status --short
git diff --cached --stat
```

Say plainly what raising it means, then ask with `clarify`:

> Raising the pull request sends this to the repo's approver, and once it's merged anyone can
> install it with `hermes skills install`, and people who already have it get it via
> `hermes skills update`. If anything changes after approval, it needs approving again — so it should
> be finished now, not nearly finished. Is it ready?

Choices:

- **It's finished — raise the pull request** → next section.
- **Try it out first** → save on the branch (below) and install a local test copy (below). The user
  runs `/create-new-skill` again afterwards; the pre-flight picks the branch back up.
- **Not yet — I want to change more** → back to the route. Nothing saved or raised.

A brand-new skill has usually never run on a real task. When so, say it and put **Try it out
first** first, marked recommended. Silence, "probably" or "close enough" is not a yes — ask again or
treat it as **Not yet**.

**Saving without publishing:** commit on the branch, don't push:

```bash
git commit -m "WIP: <skill-name> — not yet raised"
```

### Trying it out locally

Install a copy into the user's Hermes so it runs as `/<skill-name>`:

```bash
mkdir -p "$HERMES_HOME/skills/bitpool"
cp -r "skills/<skill-name>" "$HERMES_HOME/skills/bitpool/"
```

(Or `skill_manage` `create` with `category: bitpool` for `SKILL.md`, then `write_file` ops for each
support file — but `cp` keeps assets byte-exact.) Then `/reload-skills` or start a new session, and
use it on a real task. If `$HERMES_HOME` is unset in the shell, ask the user for their Hermes home
(`hermes config path` shows where config lives) rather than guessing.

Tell the user to remove that copy once the pull request merges (`skill_manage` `delete`), then install
the published one — otherwise the hand-copied version shadows it and `hermes skills update` won't
manage it.

## Commit, push, raise the pull request

Only after an explicit **It's finished**:

```bash
git commit -m "Add <skill-name> skill" -m "<One or two lines: what it does and who it's for.>" \
  -m "Ships SKILL.md[, references/, assets/]. Adds the README row and refreshes the skills-catalogue snapshot."
git push -u origin "add/<skill-name>"
gh pr create --repo Lolman-bot/Hermes-Repository- --base main --head "add/<skill-name>" \
  --title "Add <skill-name> skill" --body-file "<temp file in the scratch dir>"
```

PR body, plain words, so the approver needn't read the diff to know what they're approving:

```markdown
## What this adds
<What the skill does, who it's for, how it's started (`/<skill-name>`). Two or three sentences.>

## What's in it
- skills/<skill-name>/ (version 1.0.0)
- README Skills row
- skills-catalogue snapshot refresh (<old> → <new>)

## Ready to publish
- House-rules checker: all PASS
- Tried on a real task: <yes — what / no — why not>
- Confirmed ready by <user> on <date>

Install after merge: `hermes skills install Lolman-bot/Hermes-Repository-/skills/<skill-name> --category bitpool`
```

Don't request reviewers by hand unless the user asks; never approve, merge or enable auto-merge.

| What goes wrong | What to do |
|---|---|
| Push refused, 403 | No write access yet. Stop; tell them to ask Eric to add their GitHub username to the repo. The commit is safe on the branch. |
| Push refused, remote branch moved | `git pull --rebase origin "add/<skill-name>"`, re-check the diff, push again. Never `--force`. |
| `gh` missing / not signed in | The branch is pushed. Give them `https://github.com/Lolman-bot/Hermes-Repository-/compare/main...add/<skill-name>?expand=1` plus the title and body to paste. |

Adding to a PR this user already has open: push to the same branch, skip `gh pr create`, and say it
resets any approval.

## After the pull request is up

```bash
gh pr view "add/<skill-name>" --repo Lolman-bot/Hermes-Repository- --json number,url,title
git log --oneline -1
```

Tell the user plainly:

- the PR link and number, `skills/<skill-name>/`, and the slash command `/<skill-name>`;
- **it isn't live yet** — it needs approving and merging; nobody approves their own PR;
- **anything changed from here resets the approval**;
- after merge: `hermes skills install Lolman-bot/Hermes-Repository-/skills/<skill-name> --category bitpool`
  (after `hermes skills tap add Lolman-bot/Hermes-Repository-` once), then `/reload-skills`;
- if they installed a local test copy, delete it first.

Return the clone to `main`:

```bash
git checkout main
git merge --ff-only origin/main
```

Leave the branch; a later run can `git branch -D "add/<skill-name>"` once
`gh pr view "add/<skill-name>" --repo Lolman-bot/Hermes-Repository- --json state` shows `MERGED`.

## The `/skill-health` offer

`/skill-health` grades a skill on a run that actually happened, so it belongs **before** the PR.
Offer it when the user comes back from **Try it out first**, or when a real run is in front of you.
Explain first, in plain words:

> Want me to run `/skill-health` on that run? It grades the skill on how it actually behaved rather
> than what its instructions claim — it turns the skill's own steps and rules into a checklist,
> scores each against what really happened, traces any miss to the line that caused it, and ends
> with a score out of 100 and a ranked list of edits it can apply.

Ask with `clarify` (yes / no, carry on). A yes runs it; silence or no doesn't. Its fixes join this
change. After the PR is up, don't offer it — a fix then resets the approval for the sake of a grade.
If they say no, don't re-pitch.

## Never

- Commit or push on `main`, or push anything but this run's branch.
- Raise a PR without an explicit **It's finished** — not for WIP, not "for feedback", not as a draft.
- Raise a second PR for a skill that already has one open.
- Approve, merge or enable auto-merge.
- `git push --force`.
- `git add -A` from the root without a pathspec.
- Commit a credential, a token, or an absolute path from someone's machine.
