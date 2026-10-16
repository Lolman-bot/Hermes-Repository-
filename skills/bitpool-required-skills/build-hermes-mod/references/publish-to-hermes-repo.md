# Publish to the Hermes repo (step 11)

Mods are published to **`Lolman-bot/Hermes-Repository-`** on GitHub, in `mods/<mod-name>/`, through
**one pull request** from an `add-mod/<mod-name>` branch into `main`. `main` only changes through a
reviewed pull request, so the PR is raised once, after the user has tried the mod and said it's
finished. Read the repo's `README.md` on `main` first; it is the source of truth for the rules.

## 1. Pre-flight

Everything goes straight to GitHub through `gh`. Nothing is cloned locally.

```bash
REPO=Lolman-bot/Hermes-Repository-
gh auth status                                   # signed in, with the repo scope
gh api repos/$REPO --jq .full_name                # reachable
gh api repos/$REPO/contents/mods/<mod-name> 2>/dev/null && echo EXISTS
gh pr list --repo $REPO --state open --search "<mod-name> in:title"
```

| What you find | What to do |
|---|---|
| `gh` missing or not signed in | Say so and stop. Don't install it or sign in for them. |
| `mods/<mod-name>/` already exists on `main` | Stop and ask. This skill makes new mods; changes go through `/edit-mod`. |
| An open pull request for this mod | If it's this user's, add to its branch. If it's someone else's, stop and say who. |

## 2. What goes up

The package folder: `README.md`, `docs/`, `hermes-home/`, `tests/`. **Leave out** `.git/`,
`node_modules/`, `__pycache__/`, `.pytest_cache/`, logs, scratch files, and anything holding a
token, password or machine-local path:

```bash
grep -rnF -e 'C:\Users\' -e '/Users/' -e '/home/' --exclude-dir=node_modules --exclude-dir=__pycache__ .
```

Read anything it finds; paths written as `$HERMES_HOME/...` are fine. The first mod also creates
`mods/` at the repo root, just by adding a file under it.

## 3. Show, then ask

Show the list of files and the branch name, then ask with `clarify`: "Raise a pull request adding
`mods/<mod-name>/` to Lolman-bot/Hermes-Repository- now?" (Yes / Not now). Go ahead only after a
clear yes, every time. A yes for one mod doesn't carry over to the next.

## 4. Branch, files, pull request

Through the GitHub API, in this order:

1. Tip of `main`: `gh api repos/$REPO/git/ref/heads/main --jq .object.sha`.
2. Branch from it: `gh api -X POST repos/$REPO/git/refs -f ref=refs/heads/add-mod/<mod-name> -f sha=<sha>`.
3. All files in **one commit**: a blob per file (`POST git/blobs`, base64), a tree on top of
   `main`'s tree (`POST git/trees` with `base_tree`, paths `mods/<mod-name>/...`), a commit
   (`POST git/commits`) with the message `Add <mod-name> mod: <one-line summary>`, then move the
   branch to it (`PATCH git/refs/heads/add-mod/<mod-name>`, never `force: true`).
4. Raise the pull request:

   ```bash
   gh pr create --repo $REPO --base main --head add-mod/<mod-name> \
     --title "Add <mod-name> mod" --body-file "<temp file>"
   ```

   The body, in plain words: what the mod does and its kind, the flow chart (```mermaid block),
   that the tests and checks passed on the Hermes version used, and that the user tried it and
   confirmed it on that date.

Branch names are lowercase. Write temp files under the Hermes scratch directory, not `/tmp`. Don't
add reviewers by hand unless the repo README says to.

## 5. If something's refused

| What goes wrong | What to do |
|---|---|
| 403 / no write access | Tell them to ask Eric to add them to the repo (send him their GitHub username). Stop. |
| The branch already exists | Stop and ask. Never overwrite or delete it. |
| Anything else | Say what GitHub said, in plain words, and stop. |

Never push to `main`, never force-push, never approve, merge or turn on auto-merge.

## 6. After the pull request is up

Give the user the PR link, and say plainly that the mod **isn't in the repo until an approver
merges it**, and that others install it with `/install-mod <mod-name>` after that. Their installed
copy is what's switched on, and it works already. Pushes to the branch after approval reset it.
