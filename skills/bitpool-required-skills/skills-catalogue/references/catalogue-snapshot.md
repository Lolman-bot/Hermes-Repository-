# Bitpool Hermes skills catalogue — snapshot

**Snapshot taken: 2026-10-19.** Mirrors the Skills table of the `README.md` in
**https://github.com/Lolman-bot/Hermes-Repository-**, which is the live catalogue and the authority.
If something someone asks about isn't below, that means it wasn't in the repo on the snapshot date —
it does **not** prove it doesn't exist today. Say so and point at the README.

## How anyone uses a skill

1. **Type the command.** It's always the skill's own name — `/teacher`, `/create-new-skill`.
2. **Just ask in plain words.** "Help me make a skill for site reports" finds `/create-new-skill`.

Works in the terminal, the desktop app and on Discord/Telegram/Slack.

## How to install one

Needs access to the repo (see `/onboarding`). Install each skill by its full path, which includes
its section folder (e.g. `bitpool-required-skills`, `bitpool-it-security`):

```
hermes skills install Lolman-bot/Hermes-Repository-/skills/<section>/<skill-name> --category bitpool
```

Start a new conversation (or `/reload-skills`) so the `/command` appears. `hermes skills check` and
`hermes skills update` keep installed skills current.

## Skills — required (`skills/bitpool-required-skills/`, baseline on every Bitpool Hermes install)

| Skill | What it does |
|---|---|
| `build-hermes-mod` | Builds a Hermes mod (desktop plugin, TUI widget, gateway hook or skin) from a plain description — flow chart for a yes, tests, README, a trial run — then a pull request adding it to the repo's `mods/` folder. |
| `build-skill-from-examples` | Builds a new skill from examples of the work coming in and going out, plus a process you draw on a point-and-click canvas, then hands it to `create-new-skill` for the pull request. |
| `create-new-skill` | Takes a new skill from idea to a pull request — a plain-language interview, bringing in a skill you already have, or a hand-over from `build-skill-from-examples` — with readiness checks and your confirmation before it goes to a reviewer. |
| `edit-mod` | Changes a Hermes mod you already have — the change, its tests, README and flow chart kept in step — then publishes it back the way you confirm. |
| `edit-skill` | Changes or retires a skill that already ships in the repo, as one pull request once you confirm it's finished. Retiring archives it to `retired/`, never deletes. |
| `install-mod` | Installs a mod from the repo's `mods/` folder onto your machine, or removes one — follows the mod's own install steps, shows every change for a yes first, never changes the repo. |
| `log-skill-divergence` | Records when a skill's documented claim turns out to be wrong (or it misfired), so the finding reaches whoever maintains it. Asks first; logs only. |
| `onboarding` | Walks a new starter through getting set up with Hermes, one step at a time — model, GitHub, repo access, installing the required skills. |
| `skill-health` | Grades how well a skill actually performed on a run, scores it out of 100, traces each miss to its cause, then offers to apply the fixes. |
| `skills-catalogue` | This one — the repo link and what's in it. |
| `teacher` | Explains how Hermes works in plain words — surfaces, models, memory, long conversations, skills, scheduled jobs, subagents, connections, profiles and mods. |
| `update-hermes-skill` | Keeps the skills repo internally consistent whenever a skill changes — version bumps, README table sync, frontmatter compliance. |
| `user-config-store` | Remembers a per-person setting a skill needs — a path, a browser profile — so the skill only asks once. Never stores secrets. |

## Skills — design foundations (`skills/bitpool-design-foundations/`, brand layer for visual and customer-facing work)

| Skill | What it does |
|---|---|
| `bitpool-brand-guidelines` | How Bitpool sounds — the five voice pillars, naming rules, ready-made boilerplate and positioning — for any copy, name or message written as Bitpool. |
| `bitpool-design-system` | How Bitpool looks — the six non-negotiables, light and dark tokens, components, the cube logo and a starter HTML template — for any page, deck, report or visual. |
| `bitpool-search` | A drop-in, on-brand predictive search box (typeahead, cyan highlights, keyboard control) for Bitpool pages with lists or tables. |

## Skills — support (`skills/bitpool-support/`, building-automation engineering and hands-on Bitpool Cloud work)

| Skill | What it does |
|---|---|
| `bacnet-diagnostics` | Diagnoses and fixes BACnet network alerts (MS/TP, BACnet/IP, BBMD, traffic rates, TrendLogs) and ASHRAE 135-2008 errata from vendor-confirmed reference entries. |
| `bitpool-dashboard-builder` | Builds, extends or rearranges Bitpool Cloud dashboards by driving a signed-in browser, with permission gates on every write. |
| `bitpool-hvac-schematics` | Builds self-contained, on-brand HTML BMS/SCADA graphics for HVAC and central plant with live data chips, animated flow and alarms. |
| `bitpool-report-builder` | Builds paginated Bitpool Cloud reports (wizard, canvas, data sources, Preview PDF) by driving a signed-in browser, with permission gates on every write. |
| `bitpool-training-deck-builder` | Turns raw training material into a reviewed, self-contained Bitpool HTML training deck built from a 28-layout template plus a 50-animation layout library. |

## Skills — prototyping (`skills/bitpool-prototyping/`, rubric-driven generate → evaluate → review design loop)

| Skill | What it does |
|---|---|
| `loop-engineering-start` | Entry point to the rubric-scored generate → evaluate → review loop: confirms intent, sets up, resumes or archives `.loop-engineering/`, and hands off to `/project-context`. |
| `project-context` | Captures the user's project brief verbatim and copies their reference files into `.loop-engineering/` before any criteria are set. |
| `generate-rubric` | Interviews to sharpen the brief, then builds 4-6 weighted criteria with observable 0-10 anchors, optional gates, a threshold and a pass cap in `rubric.json`. |
| `design-generation` | Produces the next versioned design and its attribute rationale against the rubric anchors and review directives, without grading itself. |
| `design-evaluation` | Scores a design blind against the anchors with evidence, calibrates against history, logs the pass and routes to finish, review or a cap check-in. |
| `review-solution` | Checks in with the user, then analyses scoring history at a rigour tier matched to the number of candidates and writes 3-6 evidence-backed directives for the next pass. |

## Skills — images and videos (`skills/bitpool-images-and-videos/`, Gemini / Veo prompt-writing for Bitpool visuals)

| Skill | What it does |
|---|---|
| `bitpool-3d-image` | Writes Gemini image-to-image prompts that turn an attached photo, plan or diagram into a Bitpool archviz render, with an optional HTML mockup or handoff page. |
| `bitpool-cinematic-photo` | Writes Gemini prompts for Bitpool marketing stills (towers, plant rooms, data centres, cutaways, exploded views) from seven master templates, with optional HTML. |
| `bitpool-cinematic-video` | Writes 8-second Veo/Gemini video prompts for Bitpool assembly sequences, fly-throughs and exploded views, with an optional timed HTML animation preview. |

## Skills — general (`skills/bitpool-general/`, utilities for any role: docs, writing standard, conversions, transcription)

| Skill | What it does |
|---|---|
| `bitpool-docs` | Routes Bitpool knowledge into the right one of seven docs repos (OU, access tier or cross-OU project) and writes it following that repo's taxonomy, schema, index script and writing profile. |
| `bitpool-writing-standard` | Applies Bitpool's durable-writing standard to a closed register of targets (Drata, Jira IRT/ICR/CSIP, ISMS drafts, three docs repos), with a target gate, six core rules and a durability check. |
| `gitbook-docs` | Reference for authoring GitBook-synced docs as plain files: custom block syntax, page frontmatter, variables, `.gitbook.yaml` and `SUMMARY.md` rules. |
| `notes` | Turns a meeting transcript into structured notes in a repo's `notes/` folder, split by the repo's own OUs, with action items in exactly one OU and the original stored. |
| `docx-to-md` | Converts Word .docx files to GitHub-flavoured Markdown with pandoc in Ubuntu WSL, extracting images, testing one file before batching, and never adding frontmatter. |
| `pdf-to-md` | Converts PDFs to text-only Markdown with pymupdf4llm in WSL, OCRs scanned pages automatically, then runs a required cleanup pass for picture-text markup and OCR noise. |
| `pdf-to-md-rich` | The image-extracting version of `pdf-to-md`: same engine, OCR and cleanup pass, but every embedded image goes into `assets/<file-slug>/` and is linked inline. Only for explicit image requests. |
| `transcribe-video` | Transcribes local video or audio with Whisper (whisper-ctranslate2) and ffmpeg in WSL, entirely offline, writing per-file transcripts plus one combined Markdown document. |
| `obsidian-canvas-creation` | Builds readable Obsidian `.canvas` diagrams with swimlanes, centre-aligned rows, a fixed edge-label gap formula and group enclosure checks, with the coordinate maths checked. |

## Skills — finance (`skills/bitpool-finance/`, finance and business-intelligence reporting)

| Skill | What it does |
|---|---|
| `ai-spend-report` | Generates the Bitpool AI Spend & Usage Report as one HTML file: Xero AI vendor billing plus Claude subscription and GitHub usage, every figure from validated SQL. |

## Skills — it and security (`skills/bitpool-it-security/`, ISMS and ISO 27001: policies, Drata, Jira, AWS/Azure, evidence)

| Skill | What it does |
|---|---|
| `isms-draft` | Drafts and edits Bitpool ISMS policy drafts as Markdown in security-documentation, seeding from .docx and logging each change to the IRT policy queue, never promoting. |
| `isms-prod` | Promotes an explicitly named, approved ISMS policy draft into the isms repo: diff, change-log commit, built .docx, Drata upload prompt, CYB tickets and warning banner. |
| `change-request` | Raises a Bitpool change-management ticket in Jira CHAN, run only by typing `/change-request`: infers the fields, confirms with the user, creates the issue, then sets the request type. |
| `drive-iso27001` | Runs a bounded ISO 27001 session that checks Drata (read-only), Jira CSIP, the documentation index and optional read-only AWS against each other, keeps a SharePoint worklog and stages Jira writes for approval. |
| `ask-drata` | Confirmed quirks of the Drata MCP connection (broken search mode, filters, pagination, OAuth scopes, write traps, unreliable flags) plus the per-skill Drata write-policy table. |
| `create-drata-test` | Designs a Drata Custom Test rule for one DCF control from the user-pasted real schema, scoped to the control's literal wording, and documents it in security-documentation. |
| `drata-control-insights` | Slash-command-only single-control snapshot that joins Drata flags, Jira CSIP data, a documentation-index check and a bounded read-only AWS check into an HTML matrix. |
| `manage-drata-risks` | Verifies one Drata risk and its IRT treatment plan claim by claim, stops for the user to answer the discrepancies, then rewrites and re-scores it only with explicit approval. |
| `manage-drata-control` | Resolves one Drata control's unresolved position: gates mandatory clauses vs Annex A, offers paths, writes the approved risk, opens undated `IRT` tickets, and closes or holds the `ICR` ticket. |
| `manage-drata-vendors` | Maintains Bitpool's Drata vendor register: adds and classifies vendors, corrects records field by field, and runs the whole-register review cycle, staging each write in an approved per-vendor note. |
| `create-devsecops-ticket` | Adds an ISO 27001 / Drata control-context section to an engineering ticket's description, grounded in live AWS state, with staged approval and an optional move of the starting CSIP ticket. |
| `update-devsecops-ticket` | Turns a DevSecOps meeting transcript into approved, dated direction-update comments on existing OP board tickets, and reports what was excluded or couldn't be attributed. Comments only. |
| `describe-dcf-jira-ticket` | Writes Bitpool's four-section control explainer onto a Drata-generated CSIP DCF ticket, reading Drata read-only, with staged approval and an optional transition and dated comment. |
| `aws-context` | Checks the AWS CLI and SSO session are ready before AWS work, and makes sure sign-in lands on the dedicated read-only identity, not a personal admin account. |
| `aws-query` | Queries Bitpool's AWS accounts with the AWS CLI: example queries, the loop across all accounts, JMESPath gotchas, AWS Knowledge MCP checks and the asset-register tag-coverage script. |
| `azure-context` | Checks the Azure CLI is reachable (via WSL on Windows) and signs in to one of Bitpool's three Entra tenants safely, with a diagnostic tree for failures. |
| `azure-query` | Queries Bitpool's Azure estate read-only, searches Sentinel/Defender incidents with KQL, and produces the quarterly point-in-time Azure asset register dump. |
| `network-segmentation-evidence` | Runs a read-only sweep of the whole AWS Organization and every enabled region, and renders a dated, hashed, offline HTML evidence pack for Drata DCF-748/DCF-22 (ISO 27001 A.8.22). |
| `quarterly-configuration-and-asset-review` | Runs Bitpool's quarterly ISO 27001 cycle: snapshot-diffs the AWS, Azure and GitHub tag registers, reconciles Intune against the hardware register, and diffs Intune configuration against ratified hardening standards. |

## Skills — marketing (`skills/bitpool-marketing/`, case studies, proposals, decks and email campaigns)

| Skill | What it does |
|---|---|
| `bitpool-case-study-creator` | Builds a print-ready, single-file HTML Bitpool customer case study in the fixed five-page A4 format, with image pipeline, token build and Playwright fit-to-A4 QA. |
| `bitpool-presentation-creator` | Builds interactive Bitpool HTML decks from the canonical pitch-deck template: fixed 1920×1080 slides, animations, reorder/lock/delete editor, save-in-place and Playwright-checked PDF export. |
| `bitpool-proposal-creator` | Turns an email or CRM opportunity into an on-brand single-file HTML sales proposal or quote in the fixed ten-section format, asking for all fees, quote number and signatory first. |
| `draft-marketing-email` | Scaffolds and drafts a Bitpool campaign email in the SharePoint workspace, checks every image returns 200 on the CDN and creates the CDN-linked copy; never sends. |
| `send-marketing-email` | Sends a published Bitpool campaign email through Microsoft Graph with the user signing in themselves, one send per recipient, with check-only, explicit-yes and Send-As guards. |

## Skills — skill creators (`skills/bitpool-skill-creators/`, meta-skills for maintaining Bitpool's own skills)

| Skill | What it does |
|---|---|
| `report-skill-builder` | Turns an interactively built SQL report into a repeatable Bitpool report skill with a SQL-driven HTML scaffold, validation checks and a checklist, then hands off to `/create-new-skill`. |
| `resolve-skill-divergence` | Triages the divergence logs from `/log-skill-divergence`, re-checks each against the current repo, applies approved fixes on one branch, and stamps and archives the closed logs. |

## Mods

None in `mods/` on the snapshot date. `/build-hermes-mod` creates them; `/install-mod` installs them.

## Outside Bitpool

Public skills from the Hermes Skills Hub (not Bitpool's): `hermes skills browse` and
`hermes skills search <word>`. Those are third-party — read before installing.

## A few things worth knowing

- **Skills ask before doing anything irreversible** — publishing, installing, sending.
- **Skills don't make up facts.** If one needs something it can't find, it stops and asks.
- **You don't have to pick the right one.** Describe what you want; if two could apply, you'll be
  asked which you meant.
