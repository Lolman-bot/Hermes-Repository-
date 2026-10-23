---
name: build-skill-from-examples
description: "Use when building a skill from examples or a drawn process."
version: 1.0.1
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, skills, authoring, examples, mermaid, process-diagram]
    category: bitpool
    related_skills: [create-new-skill, skills-catalogue, edit-skill]
---

# Build Skill From Examples

Turns "here's what I start with, here's what I end up with, and here's how I get from one to the
other" into a finished Hermes skill folder, then hands it to `/create-new-skill` to put it in the
`Lolman-bot/Hermes-Repository-` repo and raise the pull request. The person never has to describe
their job in the abstract: the examples and a point-and-click process diagram do that.

## When to Use

- `/build-skill-from-examples`, or the user wants a skill built from their examples or wants to
  draw a skill's process: "here's what my work looks like, turn it into a skill", "build a skill
  from these files", "I want to draw the process".

Don't use for:

- A general "I want to make a skill" with no examples or diagram: `/create-new-skill` asks which
  route.
- Bringing in an existing skill folder: `/create-new-skill`.
- Changing or retiring a skill: `/edit-skill`.

## Prerequisites

- `python` (standard library only) to run `scripts/canvas_server.py`.
- A working folder for this build: `$HERMES_HOME/build-skill/<skill-name>/` (seed, diagram,
  draft). It is scratch and never committed.

## Procedure

Seven steps, in order. Each step's output is the next step's input.

1. **Collect the input examples.** Ask for up to five examples of the work as it arrives: PDFs,
   spreadsheets, exports, data. Read every one in full. With no file to share, take a description
   in words, asking the intake questions until it's specific, and say it back for a yes.
   `references/examples-intake.md`. *Done when:* at least one input is read or confirmed.
2. **Collect the output examples.** Up to five examples of the finished work, or a description, the
   same way. A template or logo the work must match exactly still has to be a file.
   *Done when:* at least one output is read or confirmed.
3. **Have the person draw the process.** Seed the canvas with a suggested outline from the
   examples, clearly marked as a starting point. If the person is on the machine Hermes runs on
   (CLI, TUI, desktop app), serve it with `scripts/canvas_server.py` and give them the link; if
   they're elsewhere (a messaging app, a remote host), write the self-contained canvas file and
   send it as an attachment. `references/process-canvas.md`. *Done when:* you hold the diagram.
4. **Read the diagram back.** Say every step and branch in plain words; flag anything that doesn't
   add up (a question with one answer, a duplicate link, a dead end, a box with no real name). If
   they fix it, read it back again. *Done when:* an explicit yes.
5. **Write the skill.** Turn the examples and the approved diagram into a skill folder in the
   working folder: `SKILL.md` plus `references/` and `assets/` as needed, in this repo's house
   format. `references/writing-the-skill.md`. *Done when:* every file named in `SKILL.md` exists.
6. **Show the full skill and get a yes.** Print the whole `SKILL.md`, list every other file, and
   name everything you inferred. Change what they ask for and show it again.
   *Done when:* an explicit yes.
7. **Hand over to `/create-new-skill`** with the finished folder, skipping its route choice and
   drafting. On a messaging gateway the person may need to finish from a machine with the repo
   cloned. `references/handover.md`. *Done when:* `/create-new-skill` has the folder.

## Load-bearing rules

1. **No skill is written until both ends are known: at least one input and one output, each a real
   example or a specific description the person has confirmed.** Without both ends you're guessing
   what the job is, and a skill built on a guess fires wrong. "A report" is a guess; ask until it
   isn't.
2. **The steps come from the person's diagram, never from you.** Where the diagram is unclear, ask.
   A suggested starting outline is only a suggestion until the person changes or confirms it.
3. **Read the diagram back in plain words and get a yes before writing anything.** A diagram can
   look right and still mean something else; reading it back is how that gets caught.
4. **Show the full skill and get a yes before it goes anywhere near the repo.** The person has to
   recognise their own job in it.
5. **One pull request, only after the person says it's finished.** That's `/create-new-skill`'s rule
   too: hand over, don't publish from here.
6. **Plain language throughout.** No "frontmatter", no "metadata", no "references". The person
   using this has probably never written a skill.
7. **Examples stay in the skill only where they belong.** A template, layout or logo the finished
   work must match exactly goes in `assets/`, copied byte for byte with `terminal` `cp`. Real
   customer data, names or figures never ship in the skill; ask before including anything from an
   example verbatim.

## Pitfalls

- **Never open the canvas blank.** A seeded outline gets a better diagram faster; an empty one
  stalls people.
- **Don't send a `127.0.0.1` link to someone on a phone.** It points at their phone, not the Hermes
  host. Use the standalone file for anyone not on the Hermes machine.
- **Run the server in the background** (`terminal` with `background=true`); in the foreground it
  blocks the chat until the diagram arrives.
- **Opening `assets/process-canvas.html` raw doesn't work.** It needs the server or the
  `--standalone` build; it has neither the library nor the seed on its own.
- **Don't fix the diagram silently.** Every oddity is a question to the person (rule 2).

## Verification

- At least one input and one output are on record, read or confirmed.
- The diagram was read back and approved; the skill's steps match its boxes one for one.
- The new `SKILL.md` parses, `name` matches its folder, `description` is ≤ 60 characters and starts
  `Use when`, and every support file it names exists.
- No real customer data in the folder; the person said yes to the full skill.

## Reference files

Read the file itself; this table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/examples-intake.md` | Asking for input and output examples, reading each file type, how many is enough, turning a description into something to build on, sensitive content, and when someone can neither share nor describe the work. |
| `references/process-canvas.md` | Seeding the canvas, served versus standalone mode, how the diagram gets back, the copy-and-paste fallback, and the diagram checks for step 4. |
| `references/writing-the-skill.md` | Turning examples plus diagram into a Hermes `SKILL.md`: route, rules, triggers, and what splits into `references/` and `assets/`. |
| `references/handover.md` | Handing the finished folder to `/create-new-skill`, finishing from a messaging gateway, and clean-up. |

Assets (copied, never retyped) and scripts (run, not described):

| File | What it is |
|---|---|
| `assets/process-canvas.html` | The point-and-click canvas. Served mode: Submit saves the diagram to a file. Standalone mode: Copy or Download sends it back through the chat. |
| `assets/mermaid-10.9.0.min.js` | The Mermaid drawing library, pinned, so nothing is fetched from the web. Never edited. |
| `assets/mermaid-LICENSE.txt` | Mermaid's MIT licence, which must ship alongside the bundled library. |
| `scripts/canvas_server.py` | Standard-library Python, cross-platform. Serves the canvas on 127.0.0.1 and writes the submitted diagram to `--out`, or with `--standalone` writes one self-contained HTML file. |

The repo house rules live in the repo's root `README.md` and the repo steps in `/create-new-skill`;
change them there, not here. If `/create-new-skill`'s steps change, update `references/handover.md`
in the same pass.
