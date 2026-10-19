---
name: network-segmentation-evidence
description: "Use when generating A.8.22 network segmentation evidence."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, aws, iso27001, drata, network-segmentation, evidence, security, read-only]
    category: bitpool
    related_skills: [aws-context, aws-query, manage-drata-control, ask-drata, bitpool-docs, isms-draft, isms-prod]
---

# network-segmentation-evidence

Produces Bitpool's evidence artefact for **ISO 27001 A.8.22 — segregation of networks** from live AWS state rather than a maintained diagram: a read-only sweep of every account in the Organization and every enabled region, rendered as a dated, hashed, auditor-facing HTML pack with computed findings. It serves Drata **DCF-748** (Segmentation of Networks) and **DCF-22** (Network Diagram).

Scripts ship in `scripts/`; the evidence contract, IAM permissions, control scope and placement rules in `references/`.

## When to Use

- `/network-segmentation-evidence`, or a request to generate, refresh or review the segmentation evidence, the AWS network diagram, or evidence for DCF-748 / DCF-22 / A.8.22.
- "Is our segmentation documentation current?" — regenerate; don't read a document.

Don't use for:
- Understanding the network for engineering work: use `/aws-query` — never an evidence pack.
- Deciding a control's treatment or writing a risk: use `/manage-drata-control`.
- Drata connection quirks: use `/ask-drata`.
- ISMS policy authoring: use `/isms-draft` or `/isms-prod`.

**Understanding vs evidencing.** "What does the network look like right now?" is answered by querying AWS — any document is stale the moment it is written. "What did we review, and when?" needs a dated snapshot — you cannot approve a live query. This skill only does the second. The full argument (clause 7.5.3(a), the C4 worked example), what each control actually asks, and where every artefact lives are in `references/control-scope.md` — read it before a run.

## Prerequisites

- A live AWS session as the dedicated `eric-mcp@Bitpool.com` SSO principal (`/aws-context`).
- The permission set extended per `references/permissions.md` (the sweep needs slightly more than `aws-mcp-access` grants).
- PowerShell to run `scripts/collect.ps1`: Windows PowerShell on Windows, `pwsh` on Linux/macOS. It reads `AWS_CONFIG_FILE` or `$HOME/.aws/config`.
- Python 3 (stdlib only) for the renderer. On Windows, the bare `python3` alias may be a Microsoft Store stub — use the Hermes/real `python`, or WSL `python3`.

## Procedure

Use a working directory outside the skill folder (e.g. the scratch dir or a dated folder the user names) for `dump/` and `out/`; never write the pack into a documentation repo.

1. **Confirm the session and identity.** Run `/aws-context` if `aws sts get-caller-identity` hasn't been verified this session. The identity must be the dedicated `eric-mcp@Bitpool.com` SSO principal, not a personal admin account — the two share an Entra tenant and the wrong browser profile authenticates silently as the wrong one. Done when the caller ARN shows the dedicated identity.
2. **Collect.** From the Hermes `terminal`, with this skill's `scripts/` as the script path:
   `powershell -NoProfile -ExecutionPolicy Bypass -File <skill>/scripts/collect.ps1 -OutDir <work>/dump -OrgProfile aws-master` (`pwsh -File ...` on Linux/macOS). Several minutes — use a generous `timeout` or `background=true` and poll. It resolves accounts from Organizations, probes every enabled region for VPCs, sweeps in full only where VPCs exist, and writes `_manifest.json` (UTC timestamp, caller ARN, region list, declared exclusions, SHA-256 digest). Done when it prints `COLLECTION COMPLETE` **and** you have read its output: any account reported neither surveyed nor excluded is a scope gap — resolve it or add a written exclusion to `scripts/exclusions.json` (reason, date, named decision-maker) before the pack is treated as evidence.
3. **Render.** If any script has been edited, first run `python test_model.py` from `scripts/` (all checks must pass). Then `python <skill>/scripts/render.py <work>/dump <work>/out`. Done when `network-evidence-pack.html`, `adjacency.md` and the archived `dump/` exist in `out/`, and `search_files` for `http` in the HTML finds only `http://www.w3.org/2000/svg`.
4. **Position every finding.** For each computed finding, establish which position it puts Bitpool in — **A** genuine business need, scoped (a recorded rationale: the control is met); **B** genuine need, traffic wider than required (a risk with treatment); **C** nobody can state why the path exists (a real gap). You usually cannot tell from the data — ask the infrastructure owner with `clarify`. Do not default to writing a risk. Table, routes and reasoning: `references/placement-and-closure.md`; finding meanings: `references/evidence-contract.md`. Done when every finding has a position, or an open question named for its owner.
5. **Hand over for Drata.** Zip the dump. All three artefacts — the pack, `adjacency.md` and the zipped dump — go to Drata's Evidence Library against `DCF-748` and `DCF-22` with an **annual renewal schema**, and nowhere else. **You cannot upload them**: the Drata MCP server lacks the `update:evidence` scope (`Drata_updateEvidenceArtifacts` returns `403 Missing required OAuth scope(s)`) — say so plainly; the user attaches them. Done when the user has the three files, their target controls and the renewal setting.
6. **Close the loop.** A → register rationale via `/bitpool-docs`; B → risk via `/manage-drata-control`; C → engineering work, with an undated, labelled, estimated `IRT` ticket raised via `/manage-drata-control` where a commitment is made. Recurrence is the Drata renewal schedule — **no Jira task**. Done when each finding is routed and no recurrence ticket was created.

## Load-bearing rules

- **Read-only, always.** Every call is `describe-*` or `list-*`. This skill must never modify an AWS resource. If a future need appears to require a write, it belongs somewhere else.
- **Tier comes from the route table, never the Name tag.** The single most important rule in the tool: `public-bp-zone-a-db-subnet` is named public and routed private. A hand-drawn diagram copies the name and is wrong. `scripts/test_model.py` guards this.
- **Scope comes from AWS Organizations, never a hardcoded list.** The first run of this rule found ten active accounts where the documented estate said seven.
- **An excluded account is a scope statement; an unaccounted account is a finding.** Exclusions live in `scripts/exclusions.json` with a reason, a date and a named decision-maker. Anything in the Organization that is neither surveyed nor excluded fails loudly, and should.
- **Every enabled region is probed.** "We only operate in one region" is a claim about *all* regions and can only be evidenced by looking at all of them.
- **The pack reports on two controls and nothing else.** Adding a check is a scope decision, not an improvement: name the DCF-748 or DCF-22 phrase it tests, or it does not belong. Extra findings are added audit surface — *"it just exposes us more."* Detail in `references/control-scope.md`.
- **Neither control requires management approval or a cadence.** The approver Bitpool's Network Security Policy names for allowed paths is **an authorised person** (exceptions to the Information Security Team). Never introduce "management" or a job title into any artefact, and never reintroduce a review-and-approval clause into DCF-22.
- **Never write findings by hand.** They are computed in `scripts/findings.py`, so re-running after a fix makes a resolved finding disappear on its own.
- **Never emit Mermaid `block-beta`.** GitBook renders it as a raw code block and fails silently. The emitter is restricted to `flowchart`, and the test guards it.
- **Every Mermaid output is a `.md` file with a fenced block, never a bare `.mmd`.** A bare `.mmd` does not render in Drata's evidence viewer; fenced in Markdown it renders there and degrades to readable source elsewhere.
- **The pack must make zero network requests.** No webfont or CDN; a **complete** document with `<!doctype html>`, `<head>` and `<body>`; **never** `<pre class="mermaid">` (a browser opening a local file shows a wall of code). Mermaid goes to `adjacency.md`. All three are guarded in `render.py`.
- **The pack goes to Drata and nowhere else.** Not into any documentation repo, and never published as a shareable link or page. **Never commit** — stage output and tell the user what changed; commits and pushes are theirs.
- **Findings belong in the wiki; identifiers belong only in Drata.** The sensitivity rule applies to what you write *about* the pack too. Before saving any page anywhere, check it for `vpc-`, `pcx-`, `sg-`, `subnet-`, `0.0.0.0/0`, account numbers and RFC1918 ranges. The split table is in `references/placement-and-closure.md`.

## Pitfalls

- **Generating the pack to answer an engineering question.** Point them at `/aws-query`.
- **Skipping the collector's coverage output.** An uncovered account silently narrows the claim.
- **Summarising the pack with its identifiers.** It was done on 2026-09-01 — right artefact location, wrong notes around it.
- **Offering to upload to Drata.** The scope isn't granted; this is a capability limit, not a policy choice.
- **Raising a recurrence ticket.** The Drata renewal clock already chases the artefact; a `CYB` task would be a second chaser that drifts.
- **Editing the generator without sweeping its prose.** `render.py`'s `INTRO`, `PIPE_TMPL` and "What this unlocks" text make claims an auditor can test — see `references/editing-the-generator.md`.

## Verification

- `_manifest.json` exists with timestamp, caller ARN and digest; the collector reported every org account surveyed or excluded.
- `python test_model.py` prints `All checks passed.` (after any script edit).
- The HTML's only `http` hit is the SVG namespace; it starts with `<!doctype html>` and contains no `<pre class="mermaid">`.
- Every finding has an A/B/C position or a named open question; nothing was written to a documentation repo or committed.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/control-scope.md` | Understanding vs evidencing, what DCF-22 and DCF-748 each ask (and don't), the two-controls-only scope rule, and where every artefact lives. |
| `references/placement-and-closure.md` | The A/B/C finding positions, placing the three artefacts in Drata, the sensitivity rule and its split table, and closing the loop (IRT tickets, recurrence). |
| `references/evidence-contract.md` | What the pack contains, what each finding means and what would resolve it, and what to say when handing a pack over. |
| `references/permissions.md` | The verified minimum AWS-managed policies the sweep needs, and why the alternatives were rejected. |
| `references/editing-the-generator.md` | Rules for changing the scripts or the process without leaving stale claims in the generated pack. |
| `scripts/collect.ps1` | Read-only collector: Organizations scope, every enabled region, manifest with SHA-256 digest. |
| `scripts/exclusions.json` | Declared account exclusions (reason, date, decision-maker). |
| `scripts/model.py`, `scripts/findings.py`, `scripts/svg.py`, `scripts/style.py`, `scripts/render.py` | Normalise, compute findings, lay out SVG, style, and emit the pack + `adjacency.md`. |
| `scripts/test_model.py` | Guards route-table tiering, world-open rule detection and the flowchart-only Mermaid emitter. |
