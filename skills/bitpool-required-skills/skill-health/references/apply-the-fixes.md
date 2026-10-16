# Applying the fixes

Only reached after the user has said yes to the question at the end of the report. Up to this point
nothing has been edited.

Before anything else, confirm **which** of the recommended edits they want. "Yes" to the report is not
"yes" to all of them — read back the ranked list and get the subset with `clarify` (one option per
fix, multi-select). Applying an edit the user didn't pick, alongside ones they did, is how a review
loses its welcome.

## Find out where the skill actually lives

`skill_view(name="<skill-name>")` shows which copy is live. Then check, in this order — they take
different routes.

### 1. One of this repo's skills (`Lolman-bot/Hermes-Repository-`)

Two signs, either is enough:

- It was installed from the repo: `hermes skills list --source hub` (via `terminal`) lists it with
  that source, or `$HERMES_HOME/skills/.hub/lock.json` records `Lolman-bot/Hermes-Repository-` for it.
- It exists in the user's clone at `skills/<section>/<skill-name>/`. Don't probe a guessed path: `/edit-skill`
  remembers where the clone is (via `/user-config-store`). If a path is remembered, confirm it:

  ```bash
  git -C "<clone_path>" remote get-url origin      # must be Lolman-bot/Hermes-Repository-
  ls -d "<clone_path>/skills/<section>/<skill-name>"
  ```

Either way → **load `/edit-skill`** and hand it the findings. Don't edit the files yourself, and
don't patch the installed copy. `/edit-skill` carries the pre-flight checks, the housekeeping pass
via `/update-hermes-skill`, the `version` bump, the README row, the readiness check and the pull
request, and every one of those is a thing this skill would otherwise get wrong or skip. All the
picked fixes go to it together, so they land in **one** pull request — never one per fix.

What to hand over, per fix: the exact file and line, the current text, the replacement text, and the
one-line reason. `/edit-skill` asks which skill and which route — the answers are the skill you just
reviewed, and "change it".

Found in **more than one** place (a project `.hermes/skills/` copy, a local copy and the installed
one, or the same name under `skills.external_dirs`) → it's mirrored or shadowed. Say so before
anything is edited, name which copy `skill_view` loads, and make sure the fix goes to the source of
truth. Editing the shadowed copy changes nothing; editing only the live one creates drift that
surfaces months later.

### 2. Installed from somewhere else, or bundled with Hermes

A hub-installed or bundled skill lives in `$HERMES_HOME/skills/`, but its source of truth is
upstream. Patching it with `skill_manage` marks it **user-modified**: `hermes skills update` then
skips it, so it silently stops receiving upstream fixes, until someone runs
`hermes skills update <skill-name> --force` (or `hermes skills reset <skill-name>` for a bundled
skill) and the local fix is overwritten.

Say that plainly, then offer the two real options:

- **Fix it upstream** — the durable route: a pull request or issue on the skill's own source.
- **Patch the local copy** with `skill_manage` (`action: patch`) — fine for testing a fix before
  proposing it, and worth doing precisely because a pairwise comparison (`multi-run-statistics.md`,
  step 10) needs both versions. Say out loud that it freezes updates for that skill.

Never patch it silently. A fix nobody knows is there, on a skill that has quietly stopped updating,
is worse than no fix.

### 3. A local-only skill

Agent-created or hand-written skills in `$HERMES_HOME/skills/<category>/<skill-name>/`, under
`skills.create_dir`, or a project skill in `<project>/.hermes/skills/`. Edit it directly with
`skill_manage` (`action: patch`, `old_string` / `new_string`, `file_path` for a reference file).
Still:

- **Show the exact diff before writing**, per fix. Same standard as the repo route — the user's yes was
  to the finding, and they should see the wording.
- **One patch per fix**, so a fix that turns out wrong can be backed out on its own.
- **If the skill sits in a git repo** (a project skill, or a `create_dir` that's a repo), say whether
  the file is tracked. An untracked edit to a tracked skill folder is a change with no history.

After editing, `/reload-skills` or a new session picks up the change.

## The rules for every route

1. **Apply only the fixes the user picked.** Named individually, not "the recommendations".
2. **Apply them as written in the report.** The counterfactual test in `single-run-review.md` was run
   against that specific wording. Improvising a better version at apply time throws away the only
   evidence the fix works.
3. **Prefer moving or sharpening a line over adding one.** Same ordering as the counterfactual test,
   for the same reason: every added line dilutes the ones already there.
4. **Never edit the skill you're running.** If the review lands on `skill-health` itself, hand the
   findings to `/edit-skill` and say why you're not doing it directly.
5. **Re-check the size rule after editing.** If `SKILL.md` has grown past roughly 200 lines, there's a
   reference file hiding in it — say so, even though it's outside what was asked.

## After applying

Report the facts, not a summary: which fixes were applied, which were skipped and why, the file paths,
and — on the `/edit-skill` route — the pull request link and the skill's new `version`, and that the
fix isn't live until the pull request is merged and installs run `hermes skills update`.

Then the one thing people forget: **the fix is unverified.** A counterfactual argument is not a
measurement. Say plainly that the next comparable run is the test, and that a pairwise comparison
against the old version (`multi-run-statistics.md`, step 10) is how to check it — not a re-score of the
new one on its own.

## Before you finish

- [ ] The user picked specific fixes, and only those were applied.
- [ ] Repo skills went through `/edit-skill`, not direct edits.
- [ ] Mirrored or shadowed copies were flagged before any edit.
- [ ] A local patch to a hub-installed or bundled skill was declared, with the update freeze named.
- [ ] Fixes were applied with the wording from the report.
- [ ] The user was told the fix is unverified and how to verify it.
