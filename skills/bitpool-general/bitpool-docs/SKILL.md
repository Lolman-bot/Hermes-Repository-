---
name: bitpool-docs
description: "Use when documenting Bitpool knowledge. Routes to the repo."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, documentation, gitbook, okf, knowledge-base, routing]
    category: bitpool
    related_skills: [gitbook-docs, bitpool-writing-standard, notes, isms-draft, isms-prod, manage-drata-control, user-config-store]
---

# bitpool-docs

Routes Bitpool knowledge into the right **documentation repository** and writes it there following
that repo's own taxonomy, frontmatter schema, index tooling and (in three repos) writing profile.
There are **seven** repos: six **organisational-unit (OU)** repos across four OUs and two access
tiers, and one cross-OU project repo. It never authors or edits ISMS policy documents.

| OU | Public tier | Restricted tier |
|---|---|---|
| **IT** — infrastructure, accounts, endpoints, internal automation, technical hardening | `it-documentation` | `it-documentation-restricted` |
| **Security** — ISO 27001 / ISMS governance, risk, compliance, incident response | `security-documentation` | `security-documentation-restricted` |
| **Development** — the product Bitpool ships: architecture, APIs, coding standards, release, developer onboarding | `development-documentation` | *(none)* |
| **Misc** — general company process with no obvious home | `misc-documentation` | *(none)* |
| *Not an OU* — **Projects**: the record of a project that ties to two or more OUs — its brief, scope, plan, decisions, notes and hand-offs, one folder per project | `bitpool-projects` | *(none)* |

Each is a git repo, synced to GitBook, aligned with the
[OKF](https://github.com/google/knowledge-catalog) spec on top of its own richer frontmatter schema.
The workflow ships in `references/documenting-to-ou-repos.md`; each repo's own `_meta/` files remain
the authority on its taxonomy.

## When to Use

- The user runs `/bitpool-docs`, says "document this" or "add to the docs", or another skill hands
  it documentation to file.
- **Offer it** — ask first, never write unasked — when a conversation produces documentable Bitpool
  knowledge, product engineering and cross-OU projects included.

Don't use for:
- ISMS policy text, drafts or promotions: use `/isms-draft` or `/isms-prod`.
- Filing a meeting transcript into an OU repo's `notes/` tree: use `/notes` (but a
  `bitpool-projects` meeting comes back here as a `Note` page — rule 12).
- GitBook block syntax or frontmatter on its own: use `/gitbook-docs`.

## Prerequisites

- Local checkouts of the target repos under one parent folder. Its path is remembered per person by
  `/user-config-store` (skill `bitpool-docs`, key `repos_root`; Bitpool's Windows convention is
  `C:\BitpoolDev\`). The Obsidian vault path, if used, is key `obsidian_vault_path` in the same file.
- `python` (directly, or through WSL on Windows machines set up that way) to run each repo's
  `_meta/skill/scripts/regenerate-indexes.py`.

## Procedure

1. **Apply the policy rule and the mode rule** (rules 1–2). Done when you know the request is not
   policy text, and you either were invoked explicitly or have the user's approval to write.
2. **Read the workflow** — `references/documenting-to-ou-repos.md` with `read_file`, the whole file.
   Skimming for the line you expect is how a threshold or a flag gets missed. Done when it has been
   read this run.
3. **Classify in order: project record or OU documentation, then OU, then access tier** (Steps 0a,
   0b, 0.25 of the workflow). They are separate decisions. Collapsing the last two is how sensitive
   content lands in a broad-audience repo; skipping the first is how a project's runbook ends up in
   two repos (rule 12). Done when you can name the repo **and** tier, and any sensitivity signal has
   been put to the user with `clarify`, naming both candidate paths.
4. **Locate the repo fresh** (rule 3): get `repos_root` from `/user-config-store` (ask once with
   `clarify` if missing), find the exact-name match with `search_files`, and confirm `_meta/` and
   `README.md` at its root. Done when exactly one directory matches.
5. **Load the repo's own rules** (rule 6) — its `_meta/` methodology, frontmatter schema and
   okf-mapping, its root `CLAUDE.md` if present (a docs-repo file name; read it as repo guidance),
   and in a registered repo its `_meta/writing-standard.md` after `/bitpool-writing-standard`
   (rule 11). The seven repos genuinely differ — audience values, `type` vocabularies, source
   prefixes and required fields are not interchangeable. Done when each file was read this task.
6. **Ask about diagrams, then write** the page with `write_file` / `patch`, after loading
   `/gitbook-docs` (rule 8). Done when the page and its frontmatter match the repo's schema, and
   in a registered repo the durability check is shown under the staged text or kept for the report.
7. **Regenerate the indexes** with the repo's own script via `terminal` (rule 9). Done when the
   script's `Using repo root: …` line names the intended repo and no `missing OKF type` or
   `no/invalid frontmatter` WARN remains for the pages you touched.
8. **Confirm and report** — repo including tier, path, brief description, TODOs, related pages that
   may need updating, the durability check where it applies, and for a project output whether the
   `bitpool-projects` `README.md` **Outputs** section names it. Done when the report is sent.

## Load-bearing rules

Breaking any of these writes the wrong thing to the wrong place, or writes something that should
never be written.

1. **Never author or edit ISMS policy content**, in any repo. Redirect: "Policies are handled by `/isms-draft` (draft) and `/isms-prod` (promote to production). Want me to start there?" `security-documentation/policies/` is a pointer folder — never write policy text into it.
2. **Mode 2 always asks first.** Never write to a repo from conversational context without explicit approval. Explicit invocation (`/bitpool-docs`, "document this") may proceed directly — but it approves the documenting, not the audience: a sensitivity signal still forces the tier question.
3. **Never hardcode a repo's filesystem path.** Resolve it fresh by name under the remembered `repos_root` every run — matching the name **exactly**, so `it-documentation` is never confused with `it-documentation-restricted` — and confirm it has `_meta/` and `README.md` at its root. If more than one matches, or none, stop and ask.
4. **Never silently choose an access tier.** Default to the public tier; if credential-handling detail, attacker-useful configuration, client contract terms, or named-individual detail is present, stop and ask, naming both candidate paths. **Never copy content out of a `-restricted` repo** into its public counterpart or any wider-audience destination.
5. **`development-documentation`, `misc-documentation` and `bitpool-projects` have no restricted counterpart.** If their content looks too sensitive for the public tier, raise it — don't file it anyway, and don't reroute it into another OU's restricted repo.
6. **Read the target repo's `_meta/` files fresh every task** — methodology, frontmatter schema, okf-mapping, plus its root `CLAUDE.md` if present, and in `security-documentation`, `it-documentation` or `bitpool-projects` its `_meta/writing-standard.md` — even if you wrote to that repo minutes ago.
7. **Never invent a `type` value** outside that repo's documented OKF vocabulary, and never invent a new top-level folder without approval. Five of the seven repos have no fixed taxonomy, so "no folder fits yet" is the normal state there, not a reason to improvise one. In `bitpool-projects` every top-level folder is one project, proposed with its name, scope and OUs and approved before it is created.
8. **Load `/gitbook-docs` before writing page body or frontmatter** — but do **not** hand-edit `SUMMARY.md` here; it's regenerated by the repo's own script.
9. **Regenerate the indexes after every change**, and confirm the script's `Using repo root: …` line points at the repo you intended. All seven ship a near-identical auto-locating script; running the wrong copy rewrites a sibling's indexes with no error.
10. **Never delete pages** without explicit confirmation — archive instead. **Never modify `_meta/`** without confirmation. **Never duplicate a page across repos.** **Never include credentials, secrets or PII** — in any repo, restricted ones included. **Never push to Confluence.**
11. **The writing standard applies in three repos only.** `security-documentation` (writing profile **Security Documentation**), `it-documentation` (**IT Documentation**) and `bitpool-projects` (**Projects Documentation**) are registered targets of `/bitpool-writing-standard`, in the folders each repo's profile lists as in scope. Before drafting page text or frontmatter for any of them, load that skill with `skill_view` — its `SKILL.md` for the target gate and its core-rules reference for the six core rules — then the repo's `_meta/writing-standard.md`. Show the durability check (its durability-check reference, §1) on the durable text you changed: under the staged text whenever you show a draft before writing, otherwise in the report. When you apply text that `/manage-drata-control` has already staged with its check, such as register `Rationale` wording, do not repeat the check; check only what you change. Snapshots — the snapshot page types the repo profile's §2 declares — stay specific, and frontmatter `owners` names roles or teams only. **No writing standard applies in any other repo**: `development-documentation`, `misc-documentation` and both `-restricted` repos follow only their own `_meta/` rules. `ISMS/ISMS - Draft/` and `ISMS/ISMS - Draft (New)/` are the **ISMS Policy** profile, reached only through `/isms-draft` (rule 1). Detail: *The writing standard* in `references/documenting-to-ou-repos.md`.
12. **`bitpool-projects` holds the project record; the OU repo holds the manual.** A project's brief, scope, plan, decisions, notes and hand-offs go to `bitpool-projects` only when it ties to **two or more** OUs — a single-OU project goes to that OU's repo. A page the business will operate from after the project closes — a runbook, configuration page, architecture, procedure — is written in the owning OU repo, and the project `README.md`'s **Outputs** section names it by repo and page title. Never both. A project's lifecycle is its `README.md`'s `status`; **never move or rename a project folder**, which breaks its GitBook URLs. A project meeting's notes are a `Note` page in the project's folder, written by this skill — `/notes` does not write to `bitpool-projects`. Detail: *Step 0a* in `references/documenting-to-ou-repos.md`.

## Pitfalls

- **Prefix-matching a repo name.** `it-documentation` also matches `it-documentation-restricted`;
  `bitpool-projects` doesn't match a `*-documentation` search at all.
- **Running the wrong repo's index script.** It succeeds silently against a sibling repo — always
  read the `Using repo root:` line.
- **The quiet WARN.** `no/invalid frontmatter` means the page was skipped and vanished from every
  index without an error.
- **Walking the Obsidian vault.** Read the tracker at the stored path only; a recursive search
  hydrates OneDrive/SharePoint placeholders and pulls unrelated compliance files into context.
- **Cross-repo relative links.** They don't resolve in GitBook, public↔restricted pairs included;
  name the other repo and page in text instead.
- **Treating one repo's `_meta/` as another's.** Vocabularies and required fields differ per repo.

## Verification

- The repo and tier were named, and any sensitivity signal was asked about, before writing.
- Every `_meta/` file (and writing profile, where registered) was read this task.
- The index script ran, its repo root is the intended repo, and no relevant WARN remains.
- No page was deleted, no `_meta/` file changed, no secret or PII written, without confirmation.
- In a registered repo, the durability check was shown once — with the draft or in the report.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/documenting-to-ou-repos.md` | How to route Bitpool knowledge into the right repo and access tier — telling a cross-OU project record from OU documentation, classifying the OU, the sensitivity signals that force a tier question, locating the repo fresh every run, loading that repo's own taxonomy, where the writing standard applies (three repos only), and the write-and-reindex workflow. |

Related skills: `/gitbook-docs` (block syntax and page-frontmatter chrome, not duplicated here),
`/isms-draft` and `/isms-prod` (the only skills that touch policy content),
`/bitpool-writing-standard` (the standard for the three registered repos; not restated here).

**Editing this skill:** project-vs-OU routing, OU classification, access-tier rule, workflow and
scenarios live in `references/documenting-to-ou-repos.md`. A repo's taxonomy, schema or OKF
vocabulary lives in that repo's `_meta/` files; a registered repo's writing profile in its
`_meta/writing-standard.md`; the gate and core rules in `/bitpool-writing-standard`. If a repo is
added or removed, update the tables in both this file and the reference file. Publish changes
through `/edit-skill`.
