---
name: skills-catalogue
description: "Use when asked what Bitpool skills exist. Dated list."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, catalogue, skills, mods, discovery]
    category: bitpool
    related_skills: [teacher, onboarding, create-new-skill, edit-skill, skill-health, update-hermes-skill, install-mod]
---

# Skills Catalogue

Points someone at Bitpool's Hermes skills repo and tells them what's in it, in one reply. They end up
with the repo link and enough of the contents to know whether the thing they want already exists.
Answers only from a dated snapshot in `references/` — no GitHub calls, no network.

## When to Use

- The user types `/skills-catalogue` (optionally with a job or skill name after it).
- Someone asks what skills or mods exist or where the list lives: "what skills do we have", "is
  there a Bitpool skill for X", "where's the list of skills", "what mods are there".

Don't use for:

- Making a skill → `/create-new-skill`; changing or retiring one → `/edit-skill`.
- Grading how a skill performed → `/skill-health`; repo housekeeping → `/update-hermes-skill`.
- How skills work in general → `/teacher`.
- Public skills from outside Bitpool → tell them to run `hermes skills browse` or
  `hermes skills search <word>` themselves (step 6).

## Procedure

1. **Give the link first.** `https://github.com/Lolman-bot/Hermes-Repository-` on its own line,
   before anything else, noting the README there is the live catalogue. Done when the link is the
   first line of the reply.
2. **Read `references/catalogue-snapshot.md`** with `read_file`. Never answer from memory. Done when
   read this run.
3. **Default reply: the list.** The required skills, name + one line each, plus the mods section
   (currently empty). Done when every entry in the snapshot's tables is accounted for.
4. **Go narrower only if they asked.** If they named a job or a skill ("anything for reviewing a
   skill?", "/skills-catalogue install-mod"), skip the full list and name the matching skills with
   their slash commands — or say plainly that nothing in the snapshot matches. Steps 1 and 5 still
   happen.
5. **Close with the snapshot date and how to use one.** State the snapshot date, say the repo README
   is the authority, and remind them a skill fires from its `/name` or from a plain-words request.
   If they asked about something not installed, give the install command from the snapshot.
6. **Outside Bitpool, only if asked.** For public skills, tell them `hermes skills browse` (everything,
   official first) and `hermes skills search <word>`; those are the Hermes Skills Hub, not Bitpool's
   repo, and anything installed from there is third-party.

## Load-bearing rules

1. **Every reply carries the repo link,** first line, no exceptions — a one-skill lookup, a "no,
   nothing like that", a follow-up in the same conversation.
2. **Never fetch the repo or README live.** No `web_extract`, `terminal` `gh`, or `browser_*` calls
   for the catalogue — a skill never fetches its own content (house rule), and it would fail for
   anyone without repo access. The snapshot is the source.
3. **Never invent a skill, mod or command.** If it isn't in the snapshot, say you don't see one and
   point at the README. A plausible invented slash command sends someone hunting for something that
   was never built.
4. **Always state the snapshot date, and always say the README wins.** An absent entry proves only
   that it wasn't there on the snapshot date.
5. **Listed is not installed.** If a skill isn't responding, it's usually not installed on that
   profile: give the `hermes skills install ...` line and `/reload-skills`; if they can't reach the
   repo at all, send them to `/onboarding` (repo access via Eric). Don't diagnose further.

## Pitfalls

- **Repo link 404s for them.** The repo needs access; a 404 means they haven't been added or haven't
  accepted the GitHub invite — that's `/onboarding` step 3, not a broken link.
- **Confusing the hub with Bitpool's repo.** `hermes skills browse/search` show public registries;
  Bitpool's skills appear there only via the tap (`hermes skills search <word> --source github`).

## Verification

- First line of the reply is the repo link.
- Every skill named appears in `references/catalogue-snapshot.md`.
- The reply states the snapshot date.

## Reference files

| File | Covers |
|---|---|
| `references/catalogue-snapshot.md` | The dated snapshot: every skill and mod in the repo with a one-line summary, and the install commands. The only source this skill answers from. |

### Keeping the snapshot current

The snapshot mirrors the **Skills** table in the repo's `README.md`. Whenever a skill or mod is
added, renamed or retired, refresh `references/catalogue-snapshot.md` from that table in the same
pull request, update its date line, and bump this skill's `version`. Nothing checks this file
automatically, so it goes stale silently if skipped.
