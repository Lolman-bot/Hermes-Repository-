# Find the mod, and where it publishes (steps 1 and 2)

Nothing gets edited until this file's steps are done. Their job is to make sure you're about to
edit the package the user meant, and that you know exactly which repo the change will go to.

## 1. List the mods on this machine

A mod package is a folder with `README.md`, `docs/flow.mmd`, `hermes-home/` and `tests/`. Look in:

```bash
ls -d "$HERMES_HOME"/mods/*/ 2>/dev/null                 # built by /build-hermes-mod or installed by /install-mod
ls -d "$HERMES_HOME"/profiles/*/mods/*/ 2>/dev/null       # other profiles, only if the user mentions one
```

For each package, read the README's at-a-glance table: **Kind**, **Version**, **Installs**,
**Switch on**, and the first sentence under the title.

If the user names a mod that has no package here:
- It's on `main` in the repo (`gh api repos/Lolman-bot/Hermes-Repository-/contents/mods --jq '.[].name'`):
  offer to download it into `$HERMES_HOME/mods/<mod-name>/` first (or run `/install-mod`). Never
  write over an existing folder.
- It's only a live extension (a `desktop-plugins/<id>/`, `hooks/<id>/`, `plugins/<id>/`, ...) with
  no package: say it was not built as a Bitpool mod. Offer to wrap it into a package (README from
  `/build-hermes-mod`'s template, a chart drawn from the code and agreed, tests) before editing, or
  stop.

## 2. Ask which one, then confirm

Ask with `clarify`, one choice per mod, labelled with its first sentence so the user recognises it.
Then say the folder back and get a yes:

> "That's `$HERMES_HOME/mods/git-chip-mod`, the git-chip desktop plugin, version 1.0.0. It's
> switched on in the desktop app. That the one?"

Check the live files: for each path under **Installs**, compare the live copy with the package's
`hermes-home/` copy (`cmp` or a hash). If they differ, someone edited the live copy; show the diff
and ask which one is the starting point before going on.

A missing `docs/flow.mmd` is common in mods built elsewhere. Don't create one unless the user
agrees (it then becomes the chart, drawn from the current code and agreed).

## 3. Work out where it publishes

Two things decide it: whether `mods/<mod-name>/` exists in `Lolman-bot/Hermes-Repository-`, and
whether the package folder has **its own** git.

```bash
cd "<package folder>"
git rev-parse --show-toplevel 2>/dev/null     # must print this exact folder to count as its own
git remote get-url origin 2>/dev/null
```

Compare the top-level path to the package folder after normalising slashes and case. **If it prints
a parent folder (the Hermes home, say), the mod has no git of its own.** Never run `git add`,
`git commit` or `git push` in it; they would act on the parent repo.

| What you find | Destination | Notes |
|---|---|---|
| `mods/<mod-name>/` on the repo's `main` (or an open PR adding it), no git of its own | **The Hermes repo** | The usual case. Published through the GitHub API, no clone. |
| Its own git, `origin` is some other repo | **Its own repo** | Published with ordinary git. If `origin` isn't the user's or Bitpool's, ask: they may need a fork. |
| Both of the above | Ask | Show both and ask which is right. Don't pick one. |
| Neither | Nowhere yet | Ask: publish it as a new mod (hand over to `/build-hermes-mod`'s publish step), or edit locally and stop after step 7. |

Say the destination back in one sentence and get a yes.

## 4. Pre-flight for that destination

Any surprise stops the run and goes to the user. Don't work around it.

### The Hermes repo

```bash
REPO=Lolman-bot/Hermes-Repository-
gh auth status
gh api repos/$REPO --jq .full_name
gh api repos/$REPO/contents/mods/<mod-name> --jq '.[].name'
```

| What you find | What to do |
|---|---|
| `gh` missing or not signed in | Say so. They can still edit locally (steps 3 to 7), but it can't be republished. Don't install `gh` or sign in for them. |
| `mods/<mod-name>/` isn't on `main` | Never merged. Check for an open PR (below); if there's none, it's a new mod: hand over to `/build-hermes-mod`'s publish step. |

**Drift check.** Before editing, check the local package still matches `main`, so the change
doesn't quietly undo someone else's merged edit or carry an unreviewed one along:

```bash
gh api "repos/$REPO/git/trees/main?recursive=1" \
  --jq '.tree[] | select(.type=="blob" and (.path | startswith("mods/<mod-name>/"))) | "\(.sha)  \(.path)"'
# then, from the package folder, for each file:
git hash-object "<file>"
```

Leave out `node_modules/`, `__pycache__/`, `.git/` and logs. Report any file that differs, is only
local, or is only on `main`, and ask: start from `main`'s copy, keep the local copy (its
differences go up with this change), or stop.

### Its own repo

```bash
cd "<package folder>"
git status --short                     # expect empty
git fetch origin --prune
git status -sb                         # first line: behind? ahead?
git symbolic-ref refs/remotes/origin/HEAD --short   # the default branch
```

| What you find | What to do |
|---|---|
| Uncommitted changes | Show them and ask. Never sweep someone else's work into this change. |
| Behind `origin` | Ask before `git pull --ff-only`. If it won't fast-forward, stop and say so. |
| Ahead of `origin` | Unpushed commits. Show them (`git log origin/<branch>..`) and ask whether they go up too. |
| `git fetch` fails | Stop and report it; it's a network or sign-in problem. |

## 5. Open pull request check

One open pull request per mod.

```bash
# The Hermes repo
gh pr list --repo Lolman-bot/Hermes-Repository- --state open --json number,title,author,headRefName,url,files \
  --jq '.[] | select(any(.files[]; .path | startswith("mods/<mod-name>/")))
        | "#\(.number)  \(.author.login)  \(.headRefName)  \(.url)"'
# Its own repo
gh pr list --repo <owner>/<repo> --state open --json number,title,author,headRefName,url
```

| What you find | What to do |
|---|---|
| Nothing | Carry on. |
| One this user raised | Don't open a second. This change goes on that branch (`republish.md`). Say pushing to it resets any approval. |
| One someone else raised | Stop. Name it, its author and its link. The user sorts it out with them first. |
