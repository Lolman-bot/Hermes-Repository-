# Hermes skills repo — house rules (working copy)

The checklist for keeping `Lolman-bot/Hermes-Repository-` consistent whenever anything under
`skills/` changes.

> **The repo's own `README.md` is the source of truth** — "House rules for authoring skills" and
> "Note to future AI assistants". Read it fresh every run. If this page disagrees with it, the README
> wins and this page gets corrected in the same pull request.

All commands run from the repo root in the `terminal` tool. They use only `git`, `gh` and `python`,
so they behave the same on Linux, macOS and Windows (git-bash or PowerShell; quote paths).

## Repo layout

```
README.md                 catalogue (Skills table) + house rules
skills/<section>/<skill-name>/  one folder per skill, inside its section folder
  SKILL.md
  references/ assets/ scripts/ templates/   optional
mods/<mod-name>/          Hermes mods (desktop plugins, TUI widgets, hooks, skins)
retired/<section>/<skill-name>/     retired skills, kept readable, never installed
```

There are no plugin manifests, no marketplace file and no catalogue folder. The per-skill `version`
in frontmatter is the only version, and the README **Skills** table is the only catalogue.

## Folder, name and slash command

- Folder name == frontmatter `name` == slash command. Lowercase, hyphen-separated, ≤ 64 chars.
- Every skill lives in a section folder: `skills/<section>/<skill-name>/`. Sections mirror the README
  `### ` groups (`bitpool-required-skills`, `bitpool-design-foundations`, ...). Section names are
  lowercase-hyphen; nothing sits directly under `skills/`.
- Skill names are unique across all sections (Hermes installs them into one `bitpool` category).
- A new section = a new folder **and** a new README heading `### \`<section>\` — ...` with its own
  table, in the same PR.
- Install paths include the section:
  `hermes skills install Lolman-bot/Hermes-Repository-/skills/<section>/<skill-name> --category bitpool`.
  `hermes skills tap add` only scans one level under `skills/`, so it doesn't list sectioned
  skills; install by full path instead.

## Frontmatter

```yaml
---
name: skill-name
description: "Use when <trigger>. <one-line behaviour>."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, ...]
    category: bitpool
    related_skills: [other-skill-in-this-repo]
---
```

- `description`: ≤ 60 characters, starts `Use when`, ends with a period, double-quoted. Hermes's
  skill index truncates at 57, so the trigger must make sense in that window. Triggers, phrasings
  and anti-triggers go in the body's `## When to Use`.
- `version`: semver. New skill `1.0.0`.
- `author`: Bitpool first, then Hermes Agent.
- `license`: `Proprietary`.
- `platforms`: audited from what the skill really runs. Hermes tools + `gh`/`git`/`python` = all
  three. bash-only pipelines = `[linux, macos]`.
- `metadata.hermes.tags` includes `bitpool`; `category: bitpool`; `related_skills` names only skills
  that exist in `skills/` (or ship bundled with Hermes).
- No other top-level keys are required; don't invent new ones.

## Body

Section order: `# Title` + 2-3 sentence intro, `## When to Use` (with a `Don't use for:` list),
`## Prerequisites` (if any), `## Procedure` (numbered, each step with a checkable completion
criterion), `## Load-bearing rules` (if any), `## Pitfalls`, `## Verification`, `## Reference files`
(index of support files, when there are any).

- **Hermes tool names only**: `terminal`, `read_file`, `write_file`, `patch`, `search_files`,
  `clarify`, `skill_view` / `skill_manage`, `delegate_task`, `cronjob`, `memory`, `web_search` /
  `web_extract`, `browser_*`, `vision_analyze`. Never the Claude tool names (the ask-user, read,
  edit, glob, grep, bash, tool-search or skill tools).
- **No machine-local paths.** Resolve the Hermes home from `$HERMES_HOME`, never a hardcoded
  `~/.hermes`. Repo paths are relative to the repo root. To run a bundled script from `SKILL.md`,
  use `${HERMES_SKILL_DIR}/scripts/<file>` — Hermes substitutes the absolute skill path at load.
- **No `../` links out of the skill.** The hub installer rejects support paths that climb out with `..` and bundles only
  the skill's own folder.
- **SKILL.md stays ~100-200 lines.** Detail → `references/*.md`; byte-exact content → `assets/` or
  `templates/` (copied with `cp`, never retyped); executable code → `scripts/`.
- **Self-contained, no live wiki.** Wiki-derived content ships as a dated snapshot in `references/`
  that states its date and what an absent entry does *not* prove.

## Classify the change, then bump

| Change | `version` bump | README Skills table |
|---|---|---|
| Wording / content fix, same behaviour | patch `1.2.0 → 1.2.1` | reword the row only if the summary is now wrong |
| New behaviour, new step, new reference/asset/script file | minor `1.2.0 → 1.3.0` | update summary and the "ships alongside" column |
| Changes what the skill writes, where it publishes, or drops a capability people use | major `1.2.0 → 2.0.0` | update the row; say what breaks in the PR body |
| New skill | starts at `1.0.0` | add a row |
| Rename (folder + `name` + slash command together) | major — the old slash command stops working | replace the row; fix every `related_skills` and `/old-name` mention |
| Retire (`git mv skills/<section>/<n> retired/<section>/<n>`) | no bump needed on the retired copy | remove the row; fix every `related_skills` and `/name` pointer to it |

If it's ambiguous whether a change is breaking, ask the user with `clarify` rather than guessing.
Every *other* skill whose files you touched (e.g. `skills-catalogue`'s snapshot) gets its own bump.

## Sync the README

- Row shape: `` | `name` | one-sentence summary | references/, assets/ ... or — | ``.
- The last column lists the support folders actually on disk, or `—` when there are none.
- Keep rows alphabetical within the section unless the README orders them otherwise.
- The README and the skills change in the **same** pull request. Nobody should have to grep
  `SKILL.md` files to know what's published.

## Duplicated reference files

Some skills carry an identical file under `references/` so each installs standalone. Before editing
one, find the others and change every copy:

```bash
python -c "import pathlib,sys; [print(p) for p in pathlib.Path('skills').glob('*/*/references/'+sys.argv[1])]" "<filename>"
```

## Verify before finishing

### 1. The checker (all house-rule checks in one run)

```bash
git fetch origin --prune
python skills/bitpool-required-skills/update-hermes-skill/scripts/verify_repo.py . --base origin/main
```

It prints `PASS` / `FAIL` / `WARN` per check and exits 1 on any FAIL. It covers:

- every `skills/*/*/SKILL.md` starts with `---` and parses as a YAML mapping;
- `name` == folder, lowercase-hyphen, ≤ 64;
- `description` ≤ 60 chars, starts `Use when`, ends `.`;
- `version` semver, `author` starts `Bitpool`, `license: Proprietary`, valid `platforms`;
- `tags` include `bitpool`, `category: bitpool`, `related_skills` exist in `skills/` (WARN if not —
  acceptable only for skills bundled with Hermes);
- every `references/`, `assets/`, `scripts/`, `templates/` path named in a `SKILL.md` exists;
- no `../` escapes; no Claude-only tool names, `allowed-tools`, plugin manifests, `~/.claude`,
  hardcoded `~/.hermes`, user-home paths or wiki calls in any `SKILL.md`;
- every skill folder has a README row, every row has a folder, no row for a `retired/` skill;
- with `--base`, every skill folder changed against that ref has a higher `version` than on it.

### 2. Things the checker can't judge — read them

```bash
git diff --stat origin/main
git status --short            # retirements and renames must show R, not D
```

- The README row's summary still describes what the skill does now.
- Body sections are in the house order and each Procedure step has a completion criterion.
- Any snapshot in `references/` states its date and what an absent entry doesn't prove.
- Nothing in the skill tells it to fetch its own instructions from a URL, wiki or API.
- No credentials or tokens anywhere in the diff:

```bash
git diff origin/main -- skills README.md | python -c "import re,sys; t=sys.stdin.read(); [print('CHECK:',m) for m in sorted(set(re.findall(r'(?i)(?:api[_-]?key|token|secret|password)\s*[:=]\s*\S+|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}', t)))]"
```

### 3. Pull-request state (when a PR is involved)

```bash
gh pr list --repo Lolman-bot/Hermes-Repository- --state open \
  --json number,author,headRefName,url,files \
  --jq '.[] | select(any(.files[]; .path | startswith("skills/<section>/<skill-name>/"))) | "#\(.number) \(.author.login) \(.headRefName) \(.url)"'
gh pr view <branch> --repo Lolman-bot/Hermes-Repository- --json number,url,state
```

`--jq` is built into `gh`; no separate `jq` install is needed.

## Hand back

Summarise in two or three sentences: skills touched, old → new versions, README rows
added/changed/removed. **Stage but do not commit** unless the user explicitly asks. Staging happens
on an `add/`, `edit/` or `retire/` branch, never on `main`. When this pass runs inside
`/create-new-skill` or `/edit-skill`, those skills own the commit, the branch and the pull request.
