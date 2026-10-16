# Republish (steps 8 and 9)

The edited mod goes back to the repo found in `find-the-mod.md`. **How** it goes up is the user's
choice: the branch, the commit message, and whether it's a pull request or a direct push. Propose a
default for each, with one line on why, and wait for an explicit answer.

## What goes up

The package folder: `README.md`, `docs/`, `hermes-home/`, `tests/`. **Leave out** `.git/`,
`node_modules/`, `__pycache__/`, `.pytest_cache/`, logs and scratch files. No credentials, tokens,
or absolute paths from someone's machine:

```bash
grep -rnF -e 'C:\Users\' -e '/Users/' -e '/home/' --exclude-dir=.git --exclude-dir=node_modules "<package folder>"
```

Read anything it finds. `$HERMES_HOME/...` paths in the README are expected, not leaks.

## Step 8 — agree how it goes up

### Show first

List every file that changed (added, changed, removed) against the published copy, the old and new
**Version**, and a one-line summary. For its own repo, `git status --short` and `git diff --stat`.
For the Hermes repo, the drift-check list from `find-the-mod.md`, run again.

### Then ask the three questions

Ask with `clarify`, the recommended option first, one question at a time.

**1. Pull request or direct push?**

| Destination | Options |
|---|---|
| Hermes repo | **Pull request** is the only way: `main` only changes through a reviewed PR. Say this rather than offering a push. |
| Its own repo, default branch protected | **Pull request** only. Check with `gh api repos/<owner>/<repo>/branches/<default> --jq .protected`. |
| Its own repo, not protected | **Pull request** (recommended if anyone else uses the mod), **push straight to `<default>`** (fine for a mod only the user uses), or **push a branch, no PR yet**. |
| Someone else's repo | **Pull request from the user's fork**, or stop at a local commit. |

**2. Which branch?**

| Destination | Default to propose |
|---|---|
| Hermes repo | `edit-mod/<mod-name>`, branched from `main`. Lowercase. |
| An open PR this user already has on the mod | That PR's branch. Pushing to it resets any approval. |
| Its own repo, PR | `edit-mod/<short-topic>`, from the default branch. |
| Its own repo, direct push | The default branch. |

The user can name any other branch. Check it doesn't already exist on the remote; if it does and
it isn't this mod's open PR, stop and ask. Never overwrite it.

**3. Commit message?**

Look at what the repo already does first:

```bash
git -C "<package folder>" log --oneline -10       # its own repo
gh api "repos/Lolman-bot/Hermes-Repository-/commits?path=mods/<mod-name>&per_page=5" --jq '.[].commit.message'
```

Default: `Update <mod-name> mod: <one-line summary>` (the counterpart of `/build-hermes-mod`'s
`Add <mod-name> mod: ...`). If the repo uses a convention (`feat:`, `fix:`, a ticket key), propose
that shape. Show the full message.

Silence, "probably" or "whatever you think" is not an answer. Propose again and ask for a choice.

## Step 9a — the Hermes repo, through the GitHub API

No clone. Everything through `gh api` in **one commit**, the same way `/build-hermes-mod`
publishes. `REPO=Lolman-bot/Hermes-Repository-`.

1. Base commit: the tip of the branch being added to (an existing PR's branch), else `main`:
   `gh api repos/$REPO/git/ref/heads/<base> --jq .object.sha`.
2. New branch only: `gh api -X POST repos/$REPO/git/refs -f ref=refs/heads/<branch> -f sha=<sha>`.
3. A blob per added or changed file (`POST git/blobs`, base64).
4. A tree on top of the base commit's tree (`POST git/trees` with `base_tree`), paths
   `mods/<mod-name>/...`. **Each removed file is an entry with `"sha": null`**, or it stays.
5. A commit (`POST git/commits`) with the agreed message, the new tree, the base commit as parent.
6. Move the branch: `PATCH git/refs/heads/<branch>` with the new sha. Never `force: true`.
7. New PR only:

   ```bash
   gh pr create --repo $REPO --base main --head <branch> \
     --title "<the commit subject>" --body-file "<temp file>"
   ```

   The body, in plain words: what changed and why, the updated chart in a ```mermaid block if it
   changed, old and new version, that tests and checks passed on the Hermes version used, and that
   the user checked it on that date.

Write temp files under the Hermes scratch directory, not `/tmp`.

## Step 9b — its own repo, through git

Only after the `show-toplevel` check in `find-the-mod.md` passed for this folder.

```bash
cd "<package folder>"
git checkout -b <branch>             # skip for a direct push to the default branch
git add -- README.md docs hermes-home tests
git status --short                   # read it: only the mod's own files
git commit -F "<temp file holding the agreed message>"
git push -u origin <branch>
```

Never `git add -A` or `git add .`. For a PR:
`gh pr create --repo <owner>/<repo> --base <default> --head <branch> --title "<subject>" --body-file "<temp file>"`.

## If something's refused

| What goes wrong | What to do |
|---|---|
| 403 or no write access to the Hermes repo | Tell them to ask Eric to add them to the repo (send him their GitHub username). Stop. The local edit is safe. |
| 403 on its own repo | They can't push there. Offer a fork and PR, or leave it local. Stop. |
| Push rejected: the remote branch moved | `git pull --rebase origin <branch>`, run step 6 again, show the diff again, then push. Never `--force`. |
| Push rejected: protected branch | They chose a direct push to a protected branch. Say so and go back to question 1. |
| `gh` missing or signed out, after a git push | Give `https://github.com/<owner>/<repo>/compare/<base>...<branch>?expand=1` and the title and body to paste. |
| Anything else | Say what GitHub said, in plain words, and stop. |

Never push to `main` on the Hermes repo, never force-push, never approve, merge or turn on
auto-merge.

## Afterwards

Report facts:

- the PR link and number, or the branch and commit pushed
- the mod's old and new version, and the change in one sentence
- the user's live copy already has the change
- **Hermes repo:** it isn't on `main` until an approver merges it; pushes after approval reset it
- others get the change by re-running `/install-mod <mod-name>` after the merge
