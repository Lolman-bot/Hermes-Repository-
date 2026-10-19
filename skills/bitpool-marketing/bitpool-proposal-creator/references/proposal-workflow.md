# Proposals

A Bitpool product-sales proposal is a single self-contained HTML file matching the canonical format established by BP-0815 (Dexus, Woodside Perth): light Bitpool theme, scroll reveals, animated beat backgrounds, print-perfect PDF export.

> **Warning**
> **The skill never generates fees itself.** Always ask the user for customer details and pricing before writing — never invent a fee, a quote number, or a term total.


> **Note**
> `assets/proposal-template.html` ships locally with the `bitpool-proposal-creator` skill — the canonical tokenized template with all CSS, the embedded cube logo, animations, print styles and the PDF button. This page is the method; that file is the machinery.


## 1. Intake — always ask, never invent

The typical starting point is an email request or a CRM opportunity pasted into chat. Extract everything you can from it, then **ask the user for whatever is missing** before writing. Ask in one terse batch; don't drip-feed.

Two things are non-negotiable:

**Customer details** — always confirm:

| Field | Notes |
| --- | --- |
| Client | Legal/trading name as it should appear |
| Site | Building name, city, state |
| Quote number | `BP-XXXX` — ask, do not invent |
| Revision | `R1.0` default for new |
| Term and date | e.g. 3 years |
| Signatory | Name, role, email, mobile. Default **Peter Palonek, Chief Partner Officer, ppalonek@bitpool.com, 0429 688 868** — but confirm |

**Pricing** — ask for:

- Base line items (item code, title, one-off vs per-year, amount ex GST)
- Variations if any (additional points, IP ranges, rectification day rate, etc.)
- Confirm the term-total maths with the user's numbers before finalising

Also gather, from source material or by asking: the product being sold (BOSv2, Edge, Point Packs, Bitpool Cloud, etc.), what it integrates to (BMS vendor/system, protocols), capacity assumptions (points, IP ranges, devices), what's explicitly out of scope, any open items or unknowns, and any dependencies on the client or third parties.

## 2. Build from the template

Copy `assets/proposal-template.html` and replace every `{{TOKEN}}`. The template already carries the full Bitpool light theme CSS, the embedded cube logo (`--logo` variable — never re-embed or modify), the favicon script, reveal animations, print styles, and a floating **PDF ↓** button (hidden in print). Do not restyle; only fill content.

**Fixed structure — keep this section order:**

1. **Hero beat** — headline, sub, 6-cell meta row (Prepared for · Site · Quote · Revision · Term · Date)
2. **Overview** — "thank you for the opportunity" opening, what's proposed, assumptions stated plainly, closing line; 3-step engagement grid (01/02/03)
3. **The deployment** — product card with tier, name, description, 4-cell spec grid
4. **Capability beat** — 4 stats on animated background (capacity, hardware, protocol, term are the usual four)
5. **Deliverables** — two columns: Deployment **Once** / Ongoing management **For term**
6. **Scope** — "What this price is built on." lead, In scope / Out of scope columns, contingency line, optional open-item callout(s)
7. **Coordination & implementation** — "What we need from {client} to deliver." two labelled columns (typically On site / BMS access)
8. **Fees** — "Pricing." base table plus optional variations table, TERM TOTAL row, price-foot disclaimers
9. **Commercial notes** — "Clarifications." two-column notes list
10. **Sign-off card and footer**

**Optional blocks** (delete cleanly if unused): open-item callout, variations table, third overview paragraph.

**Product image:** default is the cube placeholder already in the template. Only swap in a product photo if the user supplies one (base64-embed it).

## 3. Content rules

- **Voice** — boldly practical. Plain declarative sentences. State assumptions and unknowns honestly: the baseline proposal openly says the documentation "does not fully resolve the total point count" and prices around it. Never paper over gaps; surface them as open items or clarifications with a price attached.
- **Emphasis** — `<strong>` renders bold cyan and replaces italics. Never use `<em>` or italic styles. Bold the product name, key numbers, protocols, and hard commitments.
- **Headlines** — sentence case ending in a full stop where the baseline does ("Pricing.", "Clarifications.", "What this price is built on."). Hero headline ≤ 18ch-ish, product bolded.
- **Pricing tables** — item codes in mono caps (`BOSv2`, `CYBER TEST`, `+ POINTS`), every fee cell notes cadence (`per year, ex GST` / `one-off, ex GST`), the TERM TOTAL row shows the breakdown maths in the description cell. All AUD ex GST.
- **Clarifications** — the template ships six standard notes (MSA/SSA, 30-day validity, term basis, annual-in-advance, remote works, orders@bitpool.com). Keep them, then add deal-specific notes: capacity/range inclusions, exclusions with reasons, third-party responsibilities (e.g. the BMS contractor rectifies network issues at their cost), the remote-access model (outbound connection, BOS-only), rectification day-rate triggers. Adjust standard notes only if the user's deal terms differ.
- **Scope symmetry** — anything excluded that has a price belongs in Out of scope *with the price inline* (e.g. "+$600 pa each"), and again in variations and clarifications.
- **No emojis, no dark theme, no board language.** This is a commercial proposal, not a board paper.

## 4. Output

- Filename: `Bitpool_{PRODUCT}_Proposal-{Client}_{Site}_{QUOTE_NO}.html`
- Single file, everything embedded. Verify no `{{` tokens remain before delivering.
- Save to outputs and present the file. No postamble.
