# Documenting to OU Repos

Guide for contributing Bitpool knowledge to the right **documentation repository**. There are
**seven** today: six **organisational-unit (OU)** repos across **four OUs** and **two access tiers**,
plus **`bitpool-projects`**, the record of projects that tie to more than one OU. Each is a git repo,
each synced to GitBook via Git Sync, each read by an internal MCP connection (added to Hermes as an MCP server), and each aligned with
the [OKF](https://github.com/google/knowledge-catalog) (Open Knowledge Format) spec on top of its own
richer frontmatter schema.

| OU | Public tier | Restricted tier |
|---|---|---|
| **IT** | `it-documentation` | `it-documentation-restricted` |
| **Security** | `security-documentation` | `security-documentation-restricted` |
| **Development** | `development-documentation` | *(none — see below)* |
| **Misc** | `misc-documentation` | *(none — see below)* |
| *Not an OU* — **Projects** (cross-OU project record) | `bitpool-projects` | *(none — see below)* |

Routing is therefore **three decisions, in order**: project record or OU documentation (Step 0a),
which OU (Step 0b), then which access tier (Step 0.25). Never collapse them into one judgement.

> **Important**
> **This never authors or edits policy documents**, regardless of which OU the request looks like
> it belongs to. Controlled ISMS policies live in the separate `isms` repo (production) and
> `security-documentation/ISMS/ISMS - Draft/` and `ISMS/ISMS - Draft (New)/` (Markdown drafts), and
> are handled **only** by
> `/isms-draft` and `/isms-prod`.
>
> If asked to create or change a **policy**, redirect: "Policies are handled by `/isms-draft`
> (draft) and `/isms-prod` (promote to production). Want me to start there?"
> `security-documentation/policies/` is a pointer folder, never real policy content.


## Never hardcode a repo path

Repo locations, and the OKF spec itself, can change. **Every run**, locate the target repo fresh
by name — never remember or assume a path from a previous turn.

1. Find the folder that holds the person's Bitpool repo checkouts. Ask `/user-config-store` for
   `get bitpool-docs repos_root`; if it is missing, ask once with `clarify` (Bitpool's Windows
   convention is `C:\BitpoolDev\`, so offer that as the default), say it will be remembered, and
   `set bitpool-docs repos_root "<path>"`. Then search under `<repos_root>` for a directory whose name
   exactly matches the target repo. A `search_files` file search (`target="files"`) for
   `<repo-name>` under `<repos_root>` (or a targeted `find` via `terminal` if that is too slow over
   the whole tree) is enough — these repos are a few levels deep, typically under
   `<repos_root>/Github-Bitpool/<repo-name>`, but don't assume that exact parent folder name.
2. Confirm it's really the right repo, not a decoy folder: it must contain `_meta/` and
   `README.md` at its root — the same heuristic the repos' own `regenerate-indexes.py` uses via
   `_looks_like_docs_repo()`.
3. **Match the name exactly.** `it-documentation` and `it-documentation-restricted` are different
   repos with different audiences, and a prefix match will happily return the wrong one. The same
   applies to `security-documentation` vs `security-documentation-restricted`. `bitpool-projects`
   breaks the `*-documentation` naming pattern, so a search for that suffix will not find it.
4. If more than one directory matches, or none do, **stop and ask**. Do not guess.

## Step 0a — Project record or OU documentation?

Before choosing an OU, ask whether the content is **the record of a project**, or **documentation the
business will run from**. They go to different repos, and a page is only ever in one.

| The content is… | Goes to |
|---|---|
| The brief, goal, scope, plan and phases, decision records, meeting and status notes, or cross-OU hand-offs of a project that ties to **two or more** OUs | **`bitpool-projects`** — the project's own folder |
| The same, for a project that ties to **one** OU | That OU's repo — continue at Step 0b |
| A working page used only while the project runs — a cutover checklist, a migration procedure | **`bitpool-projects`**, beside the project's `README.md` |
| A page the business will operate from after the project closes — a runbook, configuration or admin page, architecture, a standing procedure — **even one a project produced** | The **owning OU repo** — continue at Step 0b. The project `README.md`'s **Outputs** section names it by repo and page title |
| Anything that isn't project work | Continue at Step 0b |

The test for "two or more OUs" is the project `README.md`'s `ous` frontmatter field — `it`,
`security`, `development`, `misc` — which that repo's index script checks. If you would have to pad
the list to reach two, the project belongs in its one OU's repo.

> **Warning**
> **Trap 1 — the record vs the manual.** The recurring failure is a project's runbook written into
> `bitpool-projects` and *also* into `it-documentation` — two copies, one of which goes stale the
> first time either is edited. While a cutover procedure is in use by the project, it can live in
> the project folder. Once it is what people operate from, it is written in the OU repo and the
> project page is archived with a pointer to it. Never keep both live.
>
> "Record why we picked this identity provider" → **`bitpool-projects`** (a `Decision Record`).
> "Write up how the identity provider is configured now it's live" → **`it-documentation`**.
> "Minutes of the portal project's kickoff with Dev, IT and Security" → **`bitpool-projects`** (a `Note`).
> "A project only IT is working on" → **`it-documentation`**.

Within `bitpool-projects`, **every top-level folder is one project**. A new project folder is
proposed with a `kebab-case` name, a one-line scope and its OUs, and created only on approval. A
project's lifecycle is its `README.md`'s `status` (`draft` proposed, `active` running, `archived`
closed) — **never move or rename a project folder**, because every GitBook URL under it breaks.

If it is genuinely unclear whether a page is project record or manual, **ask the user**.

## Step 0b — Decide the OU

| Signal | OU | Repo family |
|---|---|---|
| ISO 27001 / ISMS governance, risk register & treatment, compliance & Drata control mapping, incident-response process, supplier/vendor security assessments, security training & awareness | **Security** | `security-documentation*` |
| Bitpool-operated infrastructure & accounts (AWS, M365, identity/access), endpoints, networking, integrations with business systems, internal IT automation/scripts, runbooks, and **operational/technical security hardening** (WDAC, Purview, Sentinel, Defender, email security — configuration and how-to, not governance) | **IT** | `it-documentation*` |
| **The product Bitpool builds and ships** — Bitpool Cloud, Bitpool Edge and the apps: system and service architecture, data models, product APIs and integration contracts, coding standards and conventions, product build/release/deployment pipelines, developer environment setup and onboarding, product repo layout, design decision records | **Development** | `development-documentation` |
| Doesn't clearly fit any of the above — general company process, cross-cutting notes, anything without an obvious home | **Misc** | `misc-documentation` |

> **Warning**
> **Trap 2 — IT vs Security.** `it-documentation` has its own `security/` topic folder for
> *technical hardening* — how to configure WDAC, set up Sentinel alerts, harden email. That is a
> completely different thing from the `security-documentation` repo, which is the ISO 27001
> *governance/ISMS* doc layer: policies-adjacent procedures, risk, compliance, incident response.
>
> "How do I configure Defender for Office 365" → **IT**.
> "What's our documented incident-response procedure" → **Security**.

> **Warning**
> **Trap 3 — Development vs IT.** The line is **product codebase vs internal IT systems**, not
> "does it involve code". `it-documentation/automation/` is full of scripts and Lambda patterns
> and stays exactly where it is — those automate *internal IT systems*. A pipeline that builds and
> ships the product is Development; a script that provisions an IT system is IT.
>
> "How does the Edge telemetry pipeline batch and retry" → **Development**.
> "How does the Chargebee→Xero sync Lambda work" → **IT**.
> "What's our API versioning policy" → **Development**.
> "How do I refresh the 1Password API secret" → **IT**.
>
> **Internal developer tooling is the recurring grey area** — a CI runner, a shared build image, a
> local dev environment that also touches IT-managed infrastructure. If it's genuinely ambiguous,
> **ask the user**. Then put the page in exactly one repo and reference it by name from the other;
> never write the same page into two repos, and never split one page across them.

If a piece of content is genuinely ambiguous between any two OUs, **ask the user** rather than
guessing.

## Step 0.25 — Decide the access tier

Once the OU is settled — or the content is going to `bitpool-projects` — decide **which tier**
the content belongs to. Restriction is
enforced entirely by **who has permission to the git repo** — nothing in the documents themselves
marks or protects anything.

### The rule

**Default to the public tier. Never silently promote or demote content between tiers.**

If **any** sensitivity signal below is present, **stop and ask**, naming both candidate paths in
full:

> "This mentions the break-glass rotation mechanics. That could go in
> `it-documentation/identity-access/…` or `it-documentation-restricted/…`. Which tier?"

### Sensitivity signals

Any one of these is enough to trigger the question:

- **Credential handling detail** beyond naming the storage location — break-glass procedures,
  rotation mechanics, recovery contacts, seal/unseal steps.
- **Security control configuration** specific enough to be a roadmap for an attacker — conditional
  access policy detail, detection rule logic, exact allow-list contents, bypass conditions.
- **Client or contract-specific commercial terms** — pricing, clause interpretations, named
  customer commitments.
- **Named individuals' access, entitlements, or personal detail** beyond their role.
- **The user says so.** An explicit "keep this restricted" settles it with no further analysis.

Absence of all five is not proof something is safe — it's the trigger list, not a clearance test.
If something feels sensitive and isn't on the list, ask anyway.

### Never copy across tiers

- **Never copy content from a `-restricted` repo into its public counterpart**, a ticket with a
  wider audience, or any other lower-restriction destination — even if it would obviously be
  useful there. If the user wants part of it duplicated down, they have to say so explicitly.
- Copying *upward* (public → restricted) is not automatically safe either: it removes the content
  from the audience that currently relies on it. Move, don't fork, and confirm first.
- Before quoting anything as coming from the restricted tier, **confirm you're actually reading
  that repo** and not its sibling.

### Development, Misc and Projects have no restricted tier

`development-documentation`, `misc-documentation` and `bitpool-projects` have **no** `-restricted`
counterpart, and one should not be created or assumed.

If Development, Misc or project content trips a sensitivity signal, **stop and raise it with the user** —
don't file it in the public repo by default, and don't reroute it into `it-documentation-restricted`
or `security-documentation-restricted` just because those exist. The right answer is usually one of:
hold it, put it somewhere outside these repos entirely, or make a deliberate decision to create a
new restricted repo. All three are the user's call, not yours.

## Step 0.5 — Ask about diagrams

Every time, before writing the page, ask:

> "Are there any diagrams (e.g. from your Obsidian vault) that should be included with this
> documentation?"

If the user has an Obsidian IT vault synced locally, resolve its path through `/user-config-store`:
`get bitpool-docs obsidian_vault_path` (the same OneDrive `skill-config/bitpool-docs.md` file, with
the `$HERMES_HOME/bitpool-config/` fallback). If the key is there, use it without asking. If not,
**ask the user for the vault path once** with `clarify`, say it will be remembered, and
`set bitpool-docs obsidian_vault_path "<path>"`. Don't hardcode the path; it differs by machine.

Then read `<obsidian_vault_path>\Diagram Documentation Tracker.md` directly. **Never search for the
tracker or the vault by walking a directory tree** — no recursive `search_files`, `find` or directory listing. The
vault commonly lives inside a synced SharePoint library, where a recursive walk hydrates Files
On-Demand placeholders and pulls unrelated compliance documents into context. If the file is not at
the stored path, ask the user rather than searching. If found, read its frontmatter:

- If a diagram relevant to this topic is listed with `documented: false`, name it and ask whether
  to include it now.
- Obsidian `.canvas` files are JSON and not renderable directly in GitBook — a diagram the user
  wants included must be exported to an image (PNG/SVG) first, then handled per the image step
  below like any other image.
- Once the page ships with the diagram embedded, flip that diagram's `documented` entry to `true`
  in the tracker's frontmatter (or tell the user to run its `scripts/check_diagram_docs.py`) so
  the tracker stays accurate.
- If the user says no diagrams apply, or no tracker file exists, proceed without asking again.

Architecture diagrams carry unusual weight in `development-documentation` — a correct diagram of
how services actually talk to each other outlives most prose there. Ask with a bit more intent when
the OU is Development.

## The two modes

### Mode 1 — Explicit invocation

Triggers on `/bitpool-docs`, "document this", "add this to the docs", "add to it-docs" /
"security docs" / "dev docs" / "misc docs" / "project docs".

Proceed with the workflow directly — the user has already asked, so no need to confirm before
writing. Still confirm before anything destructive: delete, mass-rename, taxonomy change. Still
ask about diagrams first. **Still ask about the access tier** if a sensitivity signal fires — Mode 1
approves the documenting, not the audience.

### Mode 2 — Conversational (proactive)

Triggers when the conversation organically produces documentable knowledge: a new procedure or
runbook, a fix or config change, a script or integration, a compliance or risk decision, an
architecture or API decision, an incident learning, or a decision or plan in a project that spans
several OUs.

**Always ask first:** "It looks like we captured something worth documenting (e.g. *[short
description]*). Should I add it to `[repo]` under
`[proposed-folder]/[proposed-filename].md`?" — `[repo]` being the OU repo, or `bitpool-projects`
for a multi-OU project's record.

If the topic turns out to be a policy, don't offer to write it here at all — point straight to
`/isms-draft`.

## The workflow

## Locate the repo, then load its methodology

After Steps 0a, 0b and 0.25 resolve a repo **and a tier**, `read_file` these from **that repo** — paths
relative to its root, and don't confuse one repo's copy for another's:

- `_meta/documentation-methodology.md` — taxonomy, naming, page anatomy, quality bar
- `_meta/frontmatter-schema.md` — required fields and validation for this repo
- `_meta/okf-mapping.md` — this repo's OKF `okf_version` target and its `type` controlled vocabulary
- `_meta/skill/reference/topic-folder-map.md` — quick disambiguation guide, if present
- `CLAUDE.md` (or `AGENTS.md`) at the repo root, if present — repo-specific standing instructions;
  the docs repos keep the `CLAUDE.md` name, and Hermes reads it as repo guidance like any other file
- `_meta/writing-standard.md` — **`security-documentation`, `it-documentation` and
  `bitpool-projects` only**: that repo's writing profile under `/bitpool-writing-standard`. Load the
  skill's `SKILL.md` first, then this file — see *The writing standard* below. The other four repos
  have none, and none applies to them.

Read fresh at the start of every task, even if you documented something in this same repo minutes
ago. These evolve, and **every repo's taxonomy, vocabulary and schema can differ** — the differences
are real, not cosmetic:

- `development-documentation` adds a `dev-team` audience value, a `repos:` frontmatter field, and
  `Architecture` / `API Reference` / `Decision Record` to its OKF `type` vocabulary. None of those
  are valid in the other OU repos. `bitpool-projects` also accepts `dev-team` and `Decision Record`,
  but not `repos:`, `Architecture` or `API Reference`.
- `security-documentation` uses source prefixes (`isms-prod:`, `drata:`, `jira-csip:`, `jira-irt:`)
  that exist nowhere else.
- `development-documentation` prefers `github:<repo>:<path>` and `github-pr:<repo>#<n>` sources;
  `it-documentation` uses `github:<repo>:<path>` and `confluence:` (attribution for migrated content
  only), and has retired `bitbucket:` as a source prefix — its `frontmatter-schema.md` forbids
  reintroducing it.
- `bitpool-projects` starts from `it-documentation`'s schema and adds an `ous` field — required on
  every project `README.md`, two or more of `it`, `security`, `development`, `misc` — a cross-OU
  `audience` list (`it-team`, `security-team`, `dev-team`, `management` and the shared values),
  `jira:` and `internal-transcript` sources, and `Decision Record` in its `type` vocabulary. On a
  project `README.md`, `status` is the project's lifecycle.
- Five of the seven repos (`development-documentation`, `bitpool-projects`, both restricted repos,
  and effectively `misc-documentation`) have **no fixed taxonomy** — folders are created one at a
  time with explicit user approval. In `bitpool-projects` each folder is one project. Only
  `it-documentation` and `security-documentation` ship a settled folder list.

## Decide scope and target within the repo

1. **Pick the topic folder** from that repo's taxonomy. **In the five emergent-taxonomy repos there
   may be no suitable folder at all** — that is the normal state, not a problem to route around.
   Propose a `kebab-case` name plus a one-line scope description and get explicit approval before
   creating it. Do not fall back to a `miscellaneous/` catch-all; those repos deliberately don't
   have one. In `bitpool-projects` the folder is the project's own: propose its name, scope and
   OUs, and give it a `README.md` following that repo's project-folder anatomy. In
   `it-documentation` and `security-documentation`, the bar for a new top-level folder is the one in
   their own methodology docs (≥3 pages, no existing folder fits).
2. **Pick a filename**: `kebab-case`, lowercase, descriptive, matching existing patterns in that
   folder.
3. **New page or edit?** Use `search_files` to check for an existing page first. Prefer editing.

## Identify sources

Capture every origin in the page's `sources` field, using **that repo's** source-reference
conventions. They differ per repo — check `_meta/frontmatter-schema.md` for the exact vocabulary and
don't assume it carries across.

## Write the page

**Load the `/gitbook-docs` skill before writing any page body or frontmatter.** All seven
repos are GitBook-synced, so every page renders through GitBook — use it for block syntax and
page-frontmatter chrome.

> **Warning**
> **One exception:** do **not** hand-edit `SUMMARY.md`. In these repos it (and the other indexes)
> is regenerated by the repo's own `regenerate-indexes.py`, so ignore `/gitbook-docs`'s
> SUMMARY.md-editing guidance here.


Use that repo's `_meta/skill/reference/page-template.md`. In addition to the repo's normal
required fields, set the OKF-required field:

```yaml
type: <value from this repo's _meta/okf-mapping.md vocabulary>
```

**Never invent a `type` value** outside that repo's documented vocabulary. If nothing fits, that's
a signal the vocabulary needs a new entry — ask the user before adding one, then record it in
`_meta/okf-mapping.md`.

Quality bar, the same across all seven repos: an AI given only this page could act on it correctly;
all links resolve; all images load or have a `<!-- TODO -->`; frontmatter validates against that
repo's schema; no credentials, secret values or PII anywhere on the page. In the three registered
repos, apply the quality-bar limits the repo's writing profile sets (IT Documentation §3.3; Security
Documentation §2–§3; Projects Documentation §3.4).

**Extra care in `bitpool-projects`**, which records projects that keep moving:

- A project `README.md` states the **standing position** — goal, scope, OUs, owner role, the
  tracker where progress lives, links to its decisions, and its outputs. Progress, dates and
  assignments stay in the tracker it names.
- **Decisions get their own `Decision Record` page**, and meetings their own `Note`. Both are dated
  snapshots — specific by design.
- An **Outputs** entry names the OU repo and page title in prose. Never copy the output's content
  into the project folder.

**Extra care in `development-documentation`**, which documents a moving codebase:

- Document the **stable layer** — contracts, data shapes, invariants, and the *why* behind a
  design. Those survive refactors; line-by-line implementation walkthroughs become confidently
  wrong.
- **Don't paste source files into pages.** Short illustrative snippets only; name the repo and path
  and record it in `repos:` instead. A page that mirrors code silently diverges from it.
- Anything version-specific (API version, dependency floor, endpoint) gets stated and dated so the
  next reader knows what to re-verify. If you can't verify it, write
  `<!-- TODO: needs input from owner -->` rather than guessing.

## The writing standard — three registered repos only

`/bitpool-writing-standard` applies to page text and frontmatter in exactly three repos, each with
its own writing profile at `_meta/writing-standard.md`, and within each repo only in the folders that
profile lists as in scope:

| Repo | Writing profile | Its character |
|---|---|---|
| `security-documentation` | **Security Documentation** | The auditor-facing ISMS governance layer — strict point-don't-copy |
| `it-documentation` | **IT Documentation** | Operator-facing — runbooks and configuration pages are the declared home of the specifics they maintain; narrative pages point |
| `bitpool-projects` | **Projects Documentation** | Modelled on IT Documentation — a project `README.md` states the standing position and points at the tracker for progress; decision records and notes are dated snapshots; working procedures are the home of their specifics while the project uses them |

- **In a registered repo**, load the skill with `skill_view` — its `SKILL.md` (the target gate, the
  three kinds of record) and its `references/core-rules.md` (the six core rules) — then the repo's
  profile, before drafting. The profile says which page types
  are durable, which are snapshots — the snapshot page types its §2 declares, which stay as specific
  as the moment warrants — and which are the declared home of specific values.
- **Show the durability check** (the skill's `references/durability-check.md` §1) on the durable
  text you changed, not the whole page: directly under the staged text whenever you show a draft
  before writing, otherwise in the report. Values the page is the declared home of take one row.
  When you apply text that `/manage-drata-control` has already staged with its check, do not repeat
  the check; check only what you change.
- **Frontmatter `owners`** names roles or teams only — never an email address or a personal name.
- **`ISMS/ISMS - Draft/` and `ISMS/ISMS - Draft (New)/`** are the **ISMS Policy** profile, written
  only through `/isms-draft` — never here.
- **A registered repo with no `_meta/writing-standard.md`** is out of scope until the file is
  restored. Say so once.
- **Any other repo** — `development-documentation`, `misc-documentation`, both `-restricted` repos —
  has no writing standard. Write to its own methodology, and do not carry these rules or the
  durability check into it.

## Rewrite cross-page links

Internal links are relative repo paths, computed from the current page's location to the target.
Never absolute paths, and **never links across repos** — cross-repo relative links don't resolve in
GitBook, and this now includes the public↔restricted pairs, which are separate repos despite the
related names, and every link between `bitpool-projects` and an OU repo. Name the other repo and
page textually instead, e.g. "see the `isms` repo's Backup Policy" or "see `it-documentation`'s AWS
Organisation Configuration and SSO page". A project `README.md`'s **Outputs** entries are always written this
way.

## Handle images

Save under `assets/<topic>/<page-slug>/` in that repo, reference with relative markdown and
meaningful alt text. Leave `<!-- TODO: image needs to be added -->` if one can't be fetched.

## Regenerate the indexes

After **every** add/move/rename/frontmatter-change, run that repo's own script by its full
discovered path, with `terminal`:

```bash
python "<repo-path>/_meta/skill/scripts/regenerate-indexes.py"
```

On a Windows machine where Python only runs through WSL, translate the discovered path to its
`/mnt/c/...` form:

```bash
wsl -e bash -lc 'python3 "/mnt/c/BitpoolDev/Github-Bitpool/<repo-name>/_meta/skill/scripts/regenerate-indexes.py"'
```

It prints `Using repo root: …` to stderr — **confirm it points at the repo you intended**, not one
of the other six. This is the single highest-consequence check in the workflow: all seven repos ship
a near-identical script that auto-locates its repo by name, so running the wrong copy from the wrong
directory rewrites a sibling repo's indexes with no error. Use `--check` to validate without
writing.

This regenerates `manifest.json`/`INDEX.md`/`SUMMARY.md` *and* the OKF per-directory `index.md`
files. GitBook ignores the `index.md` files since they aren't referenced in `SUMMARY.md`, so this is
safe with respect to GitBook rendering.

Two stderr WARNs matter:

- `missing OKF type` — fix the page's frontmatter before finishing.
- `no/invalid frontmatter` — the page was **skipped entirely** and is absent from all three indexes.
  This one is quiet; a page can vanish from the docs without any error.

`bitpool-projects` adds a third: a project `README.md` whose `ous` is missing, names fewer than two
OUs, or holds an unknown value. Fix the field — or, if the project really ties to one OU, move the
content to that OU's repo with the user's approval rather than padding the list.

## Confirm and report

Before ending the turn: report what was added or changed (**repo including tier**, path, brief
description), surface any TODOs, suggest related pages that might need updating. In
`security-documentation`, `it-documentation` or `bitpool-projects`, include the durability check on
the durable text you changed, unless it was already shown under a staged draft. When you wrote a
project's output into an OU repo, say whether its `bitpool-projects` `README.md` **Outputs** section
names it yet — and offer to add it. For anything destructive, always ask first.

## Common scenarios

<details>
<summary>A — Explicit "document this" / <code>/bitpool-docs</code></summary>

Mode 1. Step 0a (project record or OU documentation), classify OU, decide tier, locate repo,
write/edit, regenerate indexes, report.
</details>

<details>
<summary>B — Conversation organically produces documentable info</summary>

Mode 2. Ask first, phrased with the proposed repo and path. Proceed as Mode 1 if approved; drop it
if declined.
</details>

<details>
<summary>C — Genuinely ambiguous OU</summary>

Don't guess. Ask: "This could go in either `[OU-A]` or `[OU-B]` — which fits better, or do you
want it split?" The most common instance is Development vs IT over internal developer tooling.
</details>

<details>
<summary>D — "Update/create the [named] policy"</summary>

Out of scope regardless of OU. Redirect to `/isms-draft` (draft) / `/isms-prod` (promote). Offer
to document any *procedure* that implements the policy instead.
</details>

<details>
<summary>E — "Review the [IT/security/dev/misc/projects] docs, what's missing?"</summary>

`read_file` that repo's `manifest.json`. Flag `status: needs-review` or stale `last_reviewed` pages, and
any page still missing a `type` field. The staleness bar is 12 months in most repos, but
`development-documentation` treats 6 months as suspect on implementation-adjacent pages, and
`bitpool-projects` treats 3 months as suspect on an `active` project's `README.md` — check each
repo's own schema. In `bitpool-projects`, also flag a project `README.md` with no **Outputs** entry
for an output you know exists in an OU repo. **Do not write anything** without further instruction.
</details>

<details>
<summary>F — New top-level folder wanted</summary>

Don't create it without confirmation, in any of the seven repos. In the five emergent-taxonomy repos
(`development-documentation`, `misc-documentation`, `bitpool-projects`, and both restricted repos)
this comes up on the *first* page in a new area, not after a page-count threshold — asking is the
normal path, not an exception. In `bitpool-projects` that first page is a new project: propose the
folder name, scope and OUs. Note it requires updating that repo's `README.md` (except in
`bitpool-projects`, whose `README.md` lists no projects), its `topic-folder-map.md` folder list, and
the regenerated indexes together — and, in `bitpool-projects`, a `log.md` entry recording the new
project folder.
</details>

<details>
<summary>G — Content looks sensitive</summary>

Stop and ask which tier, naming both candidate paths in full. For IT and Security there is a real
choice between the public and `-restricted` repos. For Development, Misc and Projects there is no
restricted counterpart, so raise it rather than defaulting into the public repo — and don't reroute
it into another OU's restricted repo just because one exists.
</details>

<details>
<summary>H — "This dev page should also be in the IT docs"</summary>

Don't duplicate. One page, one repo; reference it from the other by naming the repo and page in
prose. Cross-repo relative links don't resolve in GitBook, and a forked page diverges the moment
one copy is edited.
</details>

<details>
<summary>I — "Document this project's decision / meeting / plan"</summary>

Step 0a. Check the project ties to two or more OUs — its `README.md`'s `ous`, or ask. If it does,
it goes in `bitpool-projects`: a decision as a `Decision Record`, a meeting as a `Note`, a plan as
a `Reference` page, in the project's folder. If the project has no folder yet, propose one (name,
scope, OUs) and wait for approval. If it ties to one OU, it goes to that OU's repo.
</details>

<details>
<summary>J — "The project delivered — write up the runbook"</summary>

Step 0a: a page the business will operate from is OU documentation. Write it in the owning OU repo,
under that repo's rules and profile. Then offer to add it to the project `README.md`'s **Outputs**
section by repo and page title, and — if a working procedure in the project folder carried the same
content — to set that page to `status: archived` with a pointer to the new home. Never leave both
live.
</details>

## What this must never do

- **Never author or edit ISMS policy content**, in any repo — redirect to `/isms-draft` / `/isms-prod`.
- **Never write to a repo from conversational context without explicit approval.** Mode 2 always asks first.
- **Never hardcode a repo's filesystem path** — resolve it fresh by name under the remembered `repos_root` (Bitpool's Windows convention: `C:\BitpoolDev\`) every time, matching the name exactly so a `-restricted` repo is never mistaken for its public sibling.
- **Never silently choose an access tier** when a sensitivity signal is present — ask, naming both candidate paths.
- **Never copy content out of a `-restricted` repo** into its public counterpart or any wider-audience destination.
- **Never assume a restricted counterpart exists** for `development-documentation`, `misc-documentation` or `bitpool-projects` — none has one, and none should be created without an explicit decision.
- **Never file a single-OU project in `bitpool-projects`**, never keep a project's lasting output there as well as in the OU repo, and never move or rename a project folder.
- **Never let `/notes` build an OU `notes/` tree in `bitpool-projects`.** A project meeting is a `Note` page in the project's folder, written here with `internal-transcript` in `sources`.
- **Never delete pages without explicit confirmation.** Archive (`status: archived`) instead.
- **Never modify a repo's `_meta/` files without explicit confirmation** — they're the contract, including `okf-mapping.md`.
- **Never invent a `type` value** outside a repo's documented OKF vocabulary, or write technical content with no source — mark `<!-- TODO: needs input from owner -->` instead of guessing.
- **Never duplicate a page across repos**, and never split one page across two.
- **Never include credentials, secret values, or PII**, even if present in source material — reference locations only. This holds in the restricted repos too; restriction is an audience boundary, not a secrets store.
- **Never push content back to Confluence** — it is no longer a documentation destination.
- **Never apply the writing standard outside `security-documentation`, `it-documentation` and `bitpool-projects`**, and never skip it in the folders their profiles cover.

## If the OKF spec changes

The fix lives in each repo's own `_meta/okf-mapping.md` (target `okf_version`, `type` vocabulary)
and the shared shape of its `_meta/skill/scripts/regenerate-indexes.py` — not in the skill and not
on this page. Re-read those fresh and they'll reflect whatever the current spec expects. This
workflow's job is routing, not owning the spec mapping.

## If a repo is added or removed

Update the table at the top of this page, the Step 0a or Step 0b table it routes through, the
Step 0.25 tier rules, and the repo count in `SKILL.md`'s body. The repos themselves
stay authoritative for their own taxonomy — this page owns only the routing.

A repo comes under the writing standard only through `/bitpool-writing-standard`'s five-step
process — a row in that skill's target register and a `_meta/writing-standard.md` in the repo. Then
add it to the table under *The writing standard* above and to `SKILL.md` rule 11. Until both exist,
no writing standard applies to it.
