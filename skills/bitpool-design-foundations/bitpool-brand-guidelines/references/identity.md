# Identity

The fixed parts of the brand — the name, the mark, and how both are used. Visual rules that are easy to get wrong and hard to undo once they're out in the wild.

## The name

The product is **Bitpool**. Always:

- One word
- Capital B
- Lowercase i-t-p-o-o-l
- Roman type (never italic, never script)
- Always proper-noun capitalized in sentence case ("Bitpool ships every fortnight" not "bitpool ships every fortnight")

Never write:

- ❌ BitPool, Bit Pool, Bit-Pool (camelcase / split / hyphenated)
- ❌ bitpool (all lowercase, except in URLs, code identifiers, and email addresses)
- ❌ BITPOOL (all caps, except inside the wordmark image itself or in eyebrow-style UC labels)
- ❌ bitpool.io (use bitpool.com unless you're specifically referring to the .io domain)
- ❌ Bitpool™ or Bitpool® in body copy — see the trademark section below

Possessive: "Bitpool's platform" — apostrophe-s like any proper noun.

Adjective form: "the Bitpool API," "a Bitpool customer," "Bitpool buildings." The word stays a noun-form proper noun; it doesn't morph (no "bitpooled," no "Bitpooling").

## The logo

The Bitpool mark is the cube. The mark exists in three forms:

1. **Cube alone** — for favicons, app icons, very small contexts, social avatars
2. **Cube + wordmark (horizontal lockup)** — the default lockup for headers, nav, business cards, footers
3. **Wordmark alone** — rare; only used where the cube is already present in the same composition or where size is too small for the cube to read

The cube colours come from the actual logo file — outer hexagon shell in deep navy, inner cube in cyan with a lighter top face. Don't recolour. Don't outline. Don't gradient it.

### Clear space

The minimum clear space around the logo is the height of the cube on every side. Nothing — not text, not imagery, not other logos — sits closer than that. In tight layouts the lockup gets smaller before it loses its clear space.

### Minimum sizes

- **Cube alone**: 16px square (favicon territory). Below 16px the cube stops reading and the favicon should be a simpler "B" mark.
- **Horizontal lockup**: 120px wide minimum. Below that the wordmark becomes hard to read and the cube alone is better.
- **Print**: 12mm wide for the lockup, 6mm for the cube alone.

### Logo backgrounds

The cube reads best on:
- Near-black backgrounds (`#0b1218`, the brand bg)
- Deep navy (`#1B2732`)
- Architectural photography that is dark and uncluttered in the logo placement area

Never place the logo on:
- Bright cyan (it competes with the cube's own cyan)
- Busy textures, gradients with strong directional colour, or photography with high-contrast detail behind the lockup
- Pure white — there is a light-mode variant of the cube for this; check `assets/cube-logo.png` in the design system skill for the canonical files

### Prohibited modifications

Don't do any of these to the logo. Each example has been seen in the wild and corrected.

- ❌ Recolour the cube to match a partner's brand colour
- ❌ Add a drop shadow, glow, bevel, or 3D-extrude effect
- ❌ Rotate, skew, or distort the cube
- ❌ Place the cube inside a circle, square, or rounded rectangle "badge" container
- ❌ Outline the cube
- ❌ Animate the cube's individual components separately (the cube is one mark; if it animates, it animates as one mark — see the design system's cube animation)
- ❌ Use a screenshot of the cube instead of the vector asset
- ❌ Stack the cube and wordmark vertically (we don't have an approved vertical lockup; if you need one, use the cube alone)
- ❌ Place the wordmark in any font other than the Inter weight 500 it ships in

If the situation seems to call for one of these, ask before doing it.

## Trademark and legal usage

**In running copy:** "Bitpool" with no symbol. The brand doesn't carry ™ or ® in marketing copy. It looks heavy and signals insecurity.

**In legal copy** (terms of service, privacy policy, master service agreements, formal contracts, regulatory filings): "Bitpool®" with the registered mark on first use per document, "Bitpool" thereafter. Check with the legal team for the canonical form in any specific jurisdiction.

**In partner co-marketing** where the partner expects to see formal trademark treatment: follow the partner's contractual requirements; default to "Bitpool®" on first use.

**Copyright notice:** "© Bitpool Pty Ltd [year]" is the canonical footer copyright. The year should be a single year (the current year) — not a range, not "All rights reserved" appended unless the partner contract requires it.

**Linking to the brand from external sites:** "Bitpool" with a link to bitpool.com. No "click here," no naked URL in body text.

## Co-branding and partner lockups

When Bitpool appears alongside another logo:

- Use a vertical hairline divider between the two marks (1px, `rgba(255,255,255,0.14)`)
- Equal optical weight — adjust sizes so the two marks read at the same visual scale, not the same pixel height (most partner logos need to be slightly larger than the Bitpool cube to look equal because the Bitpool cube has more visual density)
- 32px minimum gap between the cube and the partner mark
- "Bitpool + Partner" or "Bitpool × Partner" is acceptable in copy; "Bitpool partners with Partner" is also fine. "Bitpool/Partner" with a slash is not.

When listing multiple partner logos in a row (the customer logo row pattern), each logo gets equal spacing and the row reads alphabetically by company name unless there's a strategic reason to break order.

## How the brand voice handles the name

The name is a noun, not a verb. Don't say:

- ❌ "We Bitpooled the data."
- ❌ "Get Bitpooling."
- ❌ "Bitpool your buildings."

Say:

- ✅ "Bitpool reads the data."
- ✅ "Get started with Bitpool."
- ✅ "Bitpool runs in your buildings."

The brand earns by stating what *Bitpool does*, not by verbing the brand name. The latter sounds like every other startup.

## Product, feature, and service naming

When Bitpool needs to name a new feature, capability, or product line:

1. **Plain English wins.** Two ordinary words describing what the thing does. "Building intelligence" beats "BuildingIQ™." "Autonomous control" beats "AutoCtrl Engine."
2. **No version numbers in marketing.** Internal versioning is fine ("v2.4 of the controller daemon"); on the website it's just "the controller."
3. **No trademark symbols on features.** Only the master brand gets the ®; features don't carry ™.
4. **Avoid sub-brands.** Bitpool is the brand. New things are Bitpool features, not new brands. "Bitpool Insights" risks becoming a sub-brand with its own personality and visual; "the insights view" stays a feature.
5. **If it must have a name, the name should describe the outcome, not the mechanism.** "Autonomy" not "ML-based control loop."

Example of the rule in action: the four pillars of the platform are named **See**, **Know**, **Act**, **Grow** — four ordinary verbs, no trademarks, no qualifiers. Each describes an outcome the customer gets. That's the standard.

## URLs, domains, and digital identity

- Primary: `bitpool.com`
- Documentation: `docs.bitpool.com`
- Status page: `status.bitpool.com`
- App: `app.bitpool.com`

Never use bare URLs in customer-facing copy. Always wrap them in linked text: "the docs" links to `docs.bitpool.com`; "the status page" links to `status.bitpool.com`. The exception is a footer where the URL is the link.

Email addresses are lowercase: `hello@bitpool.com`, `sales@bitpool.com`. In running copy these are also wrapped in linked text rather than displayed bare unless the context is asking the reader to copy them.

Social handles are `@bitpool` where available, `@bitpool_io` as a documented fallback where `@bitpool` is taken.

## When something feels off

Identity errors compound. A wonky logo in a deck multiplied by 200 attendees, a misspelled name in a press release picked up by ten outlets, a clear-space violation in a partner asset that becomes the default template — these are slow leaks that damage the brand over months. If something feels wrong, stop and check this document. The cost of asking is always lower than the cost of fixing a viral mistake.

If a vendor, agency, or partner asks for permission to modify the logo, the default answer is no. Send them this document. If they have a legitimate need that this document doesn't address, escalate to the brand owner before saying yes.
