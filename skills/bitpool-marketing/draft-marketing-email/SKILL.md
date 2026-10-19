---
name: draft-marketing-email
description: "Use when drafting a Bitpool marketing email campaign."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, marketing, email, campaign, html, cdn, sendgrid]
    category: bitpool
    related_skills: [send-marketing-email, bitpool-brand-guidelines, bitpool-design-system, bitpool-case-study-creator, bitpool-proposal-creator, bitpool-presentation-creator]
---

# Draft Marketing Email

Builds a Bitpool email marketing campaign from scratch through to a verified, CDN-linked, ready-to-send file, in the `Email Marketing` SharePoint workspace: scaffolds the campaign folder, builds on-brand HTML in one of three send modes (individual, SendGrid batch, Graph-CSV batch), verifies every referenced image is live on the CDN, and runs the local→CDN publish rewrite.

**This skill does not send anything, ever.** Sending is a separate step: `/send-marketing-email` (Graph, delegated sign-in) or a manual SendGrid upload for a broad/uninformed list. The method ships in `references/`; the byte-exact scaffolds in `assets/`.

## When to Use

- `/draft-marketing-email`, or requests to build, draft, or scaffold a Bitpool marketing/campaign email, follow-up, or newsletter ("build the spring promo email", "start an email campaign for ARBS").
- Publishing an existing draft: asset verification and the local→CDN rewrite.

Don't use for:
- Case studies, proposals or slide decks: use `/bitpool-case-study-creator`, `/bitpool-proposal-creator`, `/bitpool-presentation-creator`.
- Marketing copywriting with no email artefact requested: use `/bitpool-brand-guidelines`.
- Sending an already-drafted email: use `/send-marketing-email`, or a manual SendGrid upload.

## Prerequisites

- **Local file access.** Hermes `terminal`, `read_file`, `write_file`, `patch`, `search_files` on a machine with the `Email Marketing` SharePoint folder synced. Ideal: start Hermes with that folder as the working directory.
- `/bitpool-design-system` and `/bitpool-brand-guidelines` installed (the bitpool-design-foundations section) — load both with `skill_view`.
- `curl` (or `web_extract`) to confirm CDN URLs return `200`.

## Procedure

1. **Surface check.** Confirm the file and terminal tools are available. If not, stop before scaffolding and offer advisory-only mode (`references/campaign-email-drafting.md` §0). Done when tools are confirmed or the user chose a mode.
2. **Flag the CDN gate up front** — any brand-new image needs an IT upload to the CDN before sending. Say it once, early. Done when the user has heard it before drafting starts.
3. **Locate the workspace** fresh (§0.5): cwd first, then search downward for a folder literally named `Email Marketing`; confirm the resolved path with the user. Stop and ask if none or several. Done when the workspace root is confirmed.
4. **Read the method.** `read_file` `references/campaign-email-drafting.md` in full; `references/send-modes.md` before building a template; `references/cdn-and-common-assets.md` before wiring any image URL. Done when all three are read this run.
5. **Load brand context** — `skill_view` `bitpool-design-system` and `bitpool-brand-guidelines`. Done when both are loaded.
6. **Scaffold** `<year>/<slug>/` if it doesn't exist (§3), copying `assets/campaign.md` in with `cp`. Never recreate `♻️ Common resources/`. Done when the folder and `campaign.md` exist.
7. **Ask the send mode** (§4) and the mode's details — individual: recipients, From mailbox, Reply-To; Graph batch: the recipients CSV. Use `clarify`. Then `cp` the matching template (`individual-template.html`, `batch-template.html`, `graph-batch-template.html`) and immediately resolve `{{COMMON_CDN}}` / `{{COMMON_LOCAL}}` / `{{CAMPAIGN_LOCAL}}` to literal values. Done when the draft exists with no brace path tokens.
8. **Signature and content** (§4.5, §5): ask about the signature, write the copy, route every image (common vs campaign) and record it in `campaign.md`. Done when every image is listed in `campaign.md`'s asset tables.
9. **Local-reference check** (§6) — run it yourself when the draft looks done: `grep -niE 'email%20assets/|email assets/|Common%20resources/|Common resources/' "<slug>.html"` via `terminal`, and reconcile against `campaign.md`. Done when every local hit has a matching unticked asset row.
10. **Verify assets and publish** (§7): resolve `follow-up.md` first; `curl` every CDN URL for a real `200`; if anything is unverified, stop and tell the user which files go to IT. Once all verify, write `<slug>-cdn.html` via the publish rewrite and grep it for local paths, `sharepoint.com` and stray `{{...}}`. Done when the published file has zero hits and every asset box is ticked by you.
11. **Hand off** (§8): say plainly the file is verified and published but **not sent**, and point to `/send-marketing-email` or SendGrid. Done when the user has the `-cdn.html` path and the next step.

## Load-bearing rules

Restated here because getting these wrong sends a broken or unintended campaign.

1. **Local file access is required.** Without Hermes's file and terminal tools, stop before scaffolding and tell the user to switch to a Hermes session that has them.
2. **Never hardcode the workspace path.** Employees sync SharePoint at different roots — resolve the `Email Marketing` folder fresh every session, and stop and ask if you can't locate it confidently.
3. **No vector images and no `data:` URIs, ever.** Every image is a raster PNG/JPG, and every `<img src>` is either a real `https://cdn.bitpool.com/…` URL or, pre-publish, a local relative path. Never a SharePoint URL.
4. **Resolve `{{COMMON_CDN}}` / `{{COMMON_LOCAL}}` / `{{CAMPAIGN_LOCAL}}` to literal values the moment you copy a template.** A surviving brace token is a broken image for every recipient and a hard send-time guard failure.
5. **Run the local-reference grep before calling a draft ready** — trigger it yourself when the draft looks done. It is a check to run, not a question to ask, and a clean local preview proves nothing.
6. **Only tick an asset checkbox after you personally get a `200`.** "IT said they uploaded it" is not verification.
7. **This skill never sends.** A verified, published file is not a sent campaign — say so plainly at hand-off.
8. **Copy the scaffolds; never reconstruct them from prose.** Email HTML has to be byte-exact.

## Pitfalls

- **Improvising asset routing, the publish rewrite, or a footer/unsubscribe rule from memory** — each mode's footer is a compliance decision (`references/send-modes.md`).
- **Grepping `campaign.md` blindly** — its headers describe the folder paths in prose; read its asset tables instead.
- **Hand-editing `<slug>-cdn.html`** — change the draft and re-publish.
- **Half-resolved `follow-up.md`** — sending treats any unresolved item as a hard stop. `follow-up.md` is not a shipped template; create it on demand the first time a campaign has an outstanding item.
- **Graph batch for a bulk/uninformed list** — that needs SendGrid's real unsubscribe suppression.

## Verification

- Workspace path was confirmed with the user, not assumed.
- The draft has no brace path tokens, no `data:` URIs, no `<svg>`.
- Every asset box in `campaign.md` was ticked only after a `200` you observed.
- `<slug>-cdn.html` grep is clean of local paths, `sharepoint.com` and `{{...}}`.
- The hand-off said "not sent".

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/campaign-email-drafting.md` | The full drafting workflow — surface check, workspace resolution, folder scaffold, send-mode choice, signature, asset routing, the local-reference check, the CDN publish rewrite, and the hand-off to sending. |
| `references/cdn-and-common-assets.md` | Email hosting config, the common/ versus year/slug asset split, and the full token table for local versus CDN image URLs. |
| `references/publishing-and-sending.md` | The asset-verification gate, the IT hand-off, the publish rewrite reference, and the hand-off to sending. |
| `references/send-modes.md` | Individual, SendGrid batch and Graph batch in full — merge-token conventions, unsubscribe-footer rules, and recipient/From/Reply-To handling. |
| `assets/individual-template.html` | Scaffold for individual sends. |
| `assets/batch-template.html` | Scaffold for SendGrid batch sends. |
| `assets/graph-batch-template.html` | Scaffold for Graph-CSV batch sends. |
| `assets/campaign.md` | Metadata + asset-checklist template, copied into every new campaign folder. |

Workflow, asset routing, send-mode formats and publish procedure are edited in `references/`; the four scaffolds in `assets/`.
