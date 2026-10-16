# Route B — retire a skill

The user wants a skill to stop shipping. It moves to `retired/`, not deleted, and everything that
advertised it is cleaned up in the same pass. Afterwards the live repo has no trace of a skill that
no longer exists, and the skill itself is still readable in `retired/<skill-name>/`.

## Confirm first, and say what will happen

> "That retires `bacnet-diagnostics`. The folder moves to `retired/bacnet-diagnostics/` — still
> readable, nothing deleted — and its row comes out of the README Skills table. It can no longer be
> installed from the repo. Anyone who already has it keeps their copy until they run
> `hermes skills uninstall bacnet-diagnostics`. Go ahead?"

Get an explicit yes with `clarify`. "Get rid of X" in a hurried message is not enough on its own.

## 1. Move the skill folder

```bash
mkdir -p retired
git mv "skills/<skill-name>" "retired/<skill-name>"
```

`git mv`, always — `git log --follow` on the retired files still shows how they got there. Never `rm`.
Keep the whole folder intact — `SKILL.md`, `references/`, `assets/`, `scripts/`, `templates/`. A
retired skill missing its reference files isn't readable, which defeats the point.

`retired/` isn't a tap path, so `hermes skills tap` and `hermes skills install` never see it, and it
needn't stay compliant with later house-rule changes. Don't bump its `version`.

## 2. Strip it from everywhere that advertised it

All in the same commit as the move:

1. **The README Skills table row** — remove it.
2. **Other skills' pointers.** `search_files` for `<skill-name>` across `skills/` and `README.md`.
   Expected remaining hits: none, except a skill that legitimately mentions the name in plain prose.
   Fix each live pointer:
   - a `related_skills` entry → remove it;
   - a `Don't use for: ... use /<skill-name>` line → point at the skill that now owns that work, or
     drop the line;
   - a Procedure step that hands over to `/<skill-name>` → ask the user what replaces it.

   Every skill you edit here gets its own patch `version` bump.
3. **The `skills-catalogue` snapshot** — handled in `publish.md`, same as any change.

If the retired skill was the only owner of something another skill depends on, stop and raise it —
that's a bigger change than a retirement, and the user's call.

## Before you leave this route

- [ ] `git status --short` shows renames (`R`) into `retired/<skill-name>/`, not deletions (`D`).
      If you see `D`, undo it (`git restore --staged` + `git checkout -- <paths>`) and redo it with
      `git mv`.
- [ ] The whole folder is under `retired/<skill-name>/`, references and assets included.
- [ ] The README row is gone.
- [ ] No live skill still points at it in `related_skills`, `Don't use for:` or a hand-over step.
- [ ] Every other skill you touched has a version bump.
