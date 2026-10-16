# Pre-flight, and finding the right skill

Nothing gets edited until this step finishes. Its job is to make sure you're in the right repo, on a
clean and current tree, about to edit the folder the user actually meant.

All commands run in `terminal` from the clone root. Quote every path.

## 1. Find the clone

Don't probe a guessed path. Ask `/user-config-store` for this skill's `clone_path`. If it's there,
confirm it still resolves:

```bash
git -C "<clone_path>" rev-parse --show-toplevel
```

If it's missing, ask the user with `clarify` where their clone is, explain once it'll be remembered,
and save it. Never guess a second path — a second clone is how someone edits one copy and pushes
from the other.

No clone at all? Offer to make one in a folder they choose and remember it:

```bash
git clone https://github.com/Lolman-bot/Hermes-Repository-.git "<their folder>"
```

## 2. Git pre-flight

```bash
git remote get-url origin              # must be github.com/Lolman-bot/Hermes-Repository-(.git)
git status --short                     # expect empty
git fetch origin --prune
git branch --list "edit/*" "retire/*"  # unfinished work from an earlier run?
```

| What you find | What to do |
|---|---|
| `origin` is `bitpool/ai-skills` or `bitpool/ai-skills-beta` | Stop. That's the Claude plugin repo. Offer to clone the Hermes repo (section 1) and update `clone_path`. Never repoint remotes quietly. |
| `origin` is anything else | Stop. This isn't the skills repo. |
| Uncommitted changes | Stop. Show the list and ask. Never sweep someone else's work into your change. |
| `git fetch` fails | Stop and report — network or sign-in, not something to work around. |
| A local `edit/<skill-name>` or `retire/<skill-name>` branch | Unfinished work — handle in section 6 once you know the skill. Never delete it without asking. |

**Nothing is ever edited on `main`.** The branch is made in section 6, once the skill is confirmed.

## 3. Read the house rules fresh

```bash
git show origin/main:README.md
```

Read all of it from `origin/main` — what's live. Where it disagrees with this skill's references, the
README wins; say so out loud.

## 4. Locate the skill

The user will name it loosely — "the BACnet one", "/notes", "the PDF skill". Resolve to exactly one
`skills/<section>/<name>/` folder:

- List every skill: `search_files` with `target="files"`, pattern `SKILL.md`, path `skills`.
- Narrow by name fragment: `search_files` `target="files"`, pattern `*<fragment>*`, path `skills`.
- Narrow by content when the name is vague: `search_files` for `<fragment>` in `skills/*/*/SKILL.md`.

Then read what's there before proposing anything: the full `SKILL.md` (`read_file`) and the folder
listing (`search_files` `target="files"`, path `skills/<section>/<name>`).

### Things that go wrong here

- **Near-identical names.** `pdf-to-md` and `pdf-to-md-rich` are different skills. Never resolve one
  of a near-pair by assumption.
- **Duplicated reference files.** Some skills carry an identical file under `references/` on
  purpose. If the change touches one, find the others (`search_files` `target="files"`, pattern
  `<filename>`, path `skills`) — every copy gets the change and every carrying skill gets a bump.
  Tell the user it's more files than they expected.
- **It's in `retired/`.** Retired skills don't ship. Ask whether the user wants to revive it — that's
  `git mv retired/<section>/<name> skills/<section>/<name>` on this branch plus a README row and a version bump.
- **It's a mod (`mods/<name>/`).** Out of scope; point at `/edit-mod` and stop.
- **It isn't in this repo.** A skill that lives only in the user's `$HERMES_HOME/skills/` or another
  repo isn't this repo's to edit. Say so and stop.

## 5. Confirm before the first edit

Say the path back and get a yes:

> "That's `skills/<section>/bacnet-diagnostics/` — `SKILL.md` plus `references/`, currently version 1.3.0.
> That the one?"

## 6. Check for an open pull request, then branch

One skill, one open pull request at a time:

```bash
gh pr list --repo Lolman-bot/Hermes-Repository- --state open \
  --json number,author,headRefName,url,files \
  --jq '.[] | select(any(.files[]; .path | startswith("skills/<section>/<skill-name>/"))) | "#\(.number) \(.author.login) \(.headRefName) \(.url)"'
gh api user --jq .login
```

| What you find | What to do |
|---|---|
| Nothing | Make a fresh branch (below). |
| An open PR **this user** raised | Don't open a second one. `git checkout <branch>`, `git pull --ff-only`, and work there. Say pushing resets any approval. |
| An open PR **someone else** raised | Stop. Name the PR, author and link. Two PRs on one skill means one overwrites the other. |
| A local `edit/<skill-name>` branch with no PR | Unfinished work. Ask with `clarify`: pick it up (`git checkout edit/<skill-name>`) or start again. Never delete without asking. |
| `gh` missing or not signed in | Say so; ask the user to check https://github.com/Lolman-bot/Hermes-Repository-/pulls for that skill. Don't install `gh` for them. |

```bash
git checkout -b "edit/<skill-name>" origin/main
```

Branch names are lowercase. Then go to step 2 of `SKILL.md` — change or retire. If they pick retire,
rename the branch before the first `git mv`:

```bash
git branch -m "retire/<skill-name>"
```
