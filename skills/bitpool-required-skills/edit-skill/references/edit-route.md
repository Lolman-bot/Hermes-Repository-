# Route A — change an existing skill

The user wants the skill to behave differently. Find out precisely what, put the change in the right
file, and leave the skill compliant and self-contained.

## 1. Get a specific enough answer

> "What do you want it to do differently?"

"Make it better" isn't actionable. Push until you can state the change as a before and an after:

- *It fires when I don't want it to* → which prompt fired it? That phrasing becomes a
  `Don't use for:` entry (and maybe a tighter `description`).
- *It doesn't fire when I want it to* → what did they type? That becomes a `## When to Use` bullet.
- *It gets step 3 wrong* → read the current step 3 back and ask what it should say. Never rewrite a
  step from your own idea of how the job works.
- *It needs to handle a new case* → a new Procedure branch or a new reference file (table below).
- *The output looks wrong* → if it comes from a file in `assets/` or `templates/`, fix the file, not
  the prose.

**Never invent the substance.** If they're vague about the correct behaviour, ask for a real example
of a run that went wrong and one that went right. A `/skill-health` report on a real run is the best
input of all.

## 2. Put the change in the right file

| Kind of change | Goes in | Why |
|---|---|---|
| When it fires, or must not | `## When to Use` / `Don't use for:`; the `description` only if the 57-char trigger is wrong | The description is what the skill index shows; the body is read once loaded |
| A rule that must hold every run | `## Load-bearing rules` | Always in context when the skill loads |
| The ordered steps | `## Procedure`, each with "Done when ...", pointing at a reference for detail | Short here, detailed there |
| A known failure mode | `## Pitfalls` — a rule plus one clause of why | Lessons, not incident logs |
| A procedure, table, checklist, query library | `references/<topic>.md` — extend an existing topic file before adding one | Read on demand |
| A template, layout, logo, scaffold | `assets/` or `templates/`, edited as a file, byte-exact | A regenerated asset is a different asset |
| A helper script | `scripts/`, run via `${HERMES_SKILL_DIR}/scripts/<file>` | Paraphrasing a script silently changes it |
| A new dependency (CLI, MCP server, access) | `## Prerequisites`, and re-audit `platforms` | Installers need to know before it fails |

Sizing: `SKILL.md` ~100-200 lines. If the edit pushes it past ~200, split a section into
`references/` and index it.

## 3. Keep it compliant

Fix rather than report:

- [ ] Frontmatter matches the README shape; `description` ≤ 60 chars, starts `Use when`, ends `.`,
      quoted. Measure: `python -c "import sys; print(len(sys.argv[1]))" "<description>"`.
- [ ] `name` still matches the folder and slash command.
- [ ] Body sections in house order.
- [ ] Hermes tool names only (`terminal`, `read_file`, `write_file`, `patch`, `search_files`,
      `clarify`, `skill_view`, `delegate_task`, `memory`, `cronjob`, ...).
- [ ] No machine-local paths (`$HERMES_HOME`, never a hardcoded home); no `../` out of the skill.
- [ ] Every support file named in `SKILL.md` exists, and every file in the folder is indexed.
- [ ] Nothing fetches the skill's own instructions from a wiki, page or API. Snapshots in
      `references/` state their date and what an absent entry doesn't prove.
- [ ] Every copy of an edited duplicated reference file got the same edit.
- [ ] `related_skills` names only skills in `skills/`.

`/update-hermes-skill` (step 4 of `SKILL.md`) runs the checker that confirms most of this.

## 4. If it's a rename

A rename moves three things together, or the skill stops loading:

```bash
git mv "skills/<section>/<old>" "skills/<section>/<new>"
```

1. The folder — `git mv`, so history follows.
2. The frontmatter `name:`.
3. The slash command — automatic, but every mention of `/<old>` and every `related_skills: [<old>]`
   in other skills and the README must change:

   `search_files` for `<old>` across `skills/` and `README.md`, and fix each hit.

It's a **major** version bump. Say plainly: the old slash command stops working; installed copies
are tracked under `skills/<section>/<old>` so `hermes skills update` won't follow the rename — people must
`hermes skills uninstall <old>` and
`hermes skills install Lolman-bot/Hermes-Repository-/skills/<section>/<new> --category bitpool`.

## Before you leave this route

Print the full changed `SKILL.md` (and any changed reference file) in chat and get an explicit yes.
That is the only review this change gets before the pull request.
