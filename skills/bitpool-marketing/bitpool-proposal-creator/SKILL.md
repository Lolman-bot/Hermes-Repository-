---
name: bitpool-proposal-creator
description: "Use when writing a Bitpool sales proposal or quote."
version: 1.0.0
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, marketing, sales, proposal, quote, html, pdf]
    category: bitpool
    related_skills: [bitpool-brand-guidelines, bitpool-design-system, bitpool-case-study-creator, bitpool-presentation-creator]
---

# Bitpool Proposal Creator

Builds a Bitpool product-sales proposal as a single self-contained HTML file, matching the canonical format established by BP-0815 (Dexus, Woodside Perth): hero with quote meta row, Overview, product/deployment card, Deliverables, Scope in/out, "What we need from you", Pricing tables with term total, Clarifications and signatory card. Light Bitpool theme, scroll reveals, animated beat backgrounds, print-perfect PDF export.

The method ships with this skill in `references/`; the tokenized template lives in `assets/`. **Always ask for customer details and pricing before writing — never invent fees.**

## When to Use

- The user asks for a Bitpool proposal, quote, quotation, sales proposal, subscription proposal, deployment proposal, or a BOS / BOSv2 / Edge / Point Pack proposal.
- "Turn this email/CRM opportunity into a proposal", "quote this up", "proposal for [client]" — even if they only paste an email thread or opportunity notes and say "proposal please".

Don't use for:
- Customer case studies: use `/bitpool-case-study-creator`.
- Pitch or sales decks: use `/bitpool-presentation-creator`.
- Marketing emails: use `/draft-marketing-email`.

## Prerequisites

- Hermes `read_file`, `write_file`, `patch`, `terminal`.
- `/bitpool-design-system` and `/bitpool-brand-guidelines` available (load with `skill_view` for voice and tokens).

## Procedure

1. **Extract first, then run the intake.** Pull everything you can from the pasted email/CRM notes, then ask the remaining intake questions from `references/proposal-workflow.md` §1 in **one terse batch** (`clarify` for choices) — customer, site, quote number, term, base line items, variations, signatory. Asking can start immediately; the load-bearing rules below are enough to know what to ask. Done when every fee, the quote number and the signatory came from the user.
2. **Read the method.** `read_file` `references/proposal-workflow.md` in full before writing. Done when read this run.
3. **Copy the template.** `cp assets/proposal-template.html <output-name>.html` (naming per `references/proposal-workflow.md` §4). Done when the copy exists.
4. **Fill the ten fixed sections in order** (hero, overview, deployment, capability beat, deliverables, scope, coordination, fees, clarifications, sign-off) by replacing every `{{TOKEN}}` with `patch`. Don't restyle — only fill content; never re-embed or modify the `--logo` variable. Done when every section has content from the intake.
5. **Check the maths.** Recompute the term total from the user's line items and show it back. Done when the user confirms the numbers.
6. **Verify no tokens remain.** `search_files` the output for `{{`. Done when there are zero hits.
7. **Deliver** the file path with a list of stated assumptions and open items. Done when the user has both.

## Load-bearing rules

Restated here because these are commercial commitments, not formatting.

1. **Never invent fees.** The skill does not generate pricing itself — ask the user for base line items, variations, and confirm the term-total maths against their numbers before finalising.
2. **Never invent a quote number.** `BP-XXXX` comes from the user; `R1.0` is the default revision for a new proposal.
3. **Always confirm the signatory.** Default **Peter Palonek, Chief Partner Officer, ppalonek@bitpool.com, 0429 688 868** — but confirm it every time.
4. **Ask in one terse batch**, don't drip-feed questions, and extract everything you can from the pasted email or CRM opportunity first.
5. **State assumptions and unknowns honestly** — surface gaps as open items or clarifications with a price attached rather than papering over them.
6. **Anything excluded that has a price** belongs in Out of scope *with the price inline*, and again in variations and clarifications.
7. **Verify no `{{` tokens remain** before delivering. All amounts AUD ex GST. No emojis, no dark theme, no board language.
8. **Copy the template; never reconstruct it from prose.**

## Pitfalls

- **Inventing a section or a clarification note** — the ten-section order is fixed; extra sections break the format.
- **Defaulting the signatory silently** — the default exists, but it is confirmed every time.
- **GST ambiguity** — every amount is AUD ex GST; say so in the price-foot.
- **Papering over unknowns** — an unpriced unknown becomes an open-item callout, not a vague sentence.

## Verification

- Zero `{{` hits in the output.
- The term total matches the user's line items and was confirmed.
- Quote number, revision and signatory are user-supplied/confirmed.
- Every priced exclusion appears in Out of scope, variations and clarifications.

## Reference files

Read the file itself — the table is an index, not a substitute.

| File | Covers |
|---|---|
| `references/proposal-workflow.md` | The full proposal workflow — intake questions that must always be asked, the fixed ten-section structure, content and pricing rules, and output naming. |
| `assets/proposal-template.html` | The canonical tokenized template (from BP-0815 Dexus Woodside): all CSS, embedded cube logo, animations, print styles, PDF button. |

Intake questions, section order, content and pricing rules are edited in `references/proposal-workflow.md`; the template in `assets/`.
