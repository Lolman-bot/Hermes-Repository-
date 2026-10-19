# Send modes: individual, SendGrid batch, Graph batch

Ask which mode applies before building anything — build only that mode's scaffold
(see the [workflow](campaign-email-drafting.md) step 4). Don't build more than one "just in case."

This doc covers the **drafting** shape of each mode — what the file looks like, what
goes in it, what to ask the user. Sending itself is a separate skill,
`/send-marketing-email` (individual and Graph batch), or a manual SendGrid upload
(SendGrid batch) — see `publishing-and-sending.md` for the hand-off, and
`send-marketing-email`'s own references for how the Graph send actually works.

**All three modes produce `<year>/<slug>/<slug>.html`** as the draft, published to
`<year>/<slug>/<slug>-cdn.html` — one naming convention regardless of mode. There's no
`-draft` suffix distinction any more: a `.html` file isn't double-click-sendable the
way a `.eml` was, so the old naming-as-safety-brake isn't needed. The actual safety
brake is structural instead — `send-marketing-email`'s guard checks refuse to send a
file that still contains local-path tokens, which is exactly what an unpublished
draft looks like. See `publishing-and-sending.md`.

## Individual send

**When:** one or a small handful of named recipients — a follow-up, a personal
outreach, a reply-style email that happens to need Bitpool styling. Not for a real
list — if it's more than a handful of people, or an ongoing segment, that's batch
instead (SendGrid or Graph CSV); check with the user if it's borderline.

**File:** `assets/individual-template.html`, copied to `<year>/<slug>/<slug>.html`.

**What it is:** just the HTML body — no MIME headers, no `From`/`To`/`Subject`
fields baked into the file. Those are supplied at send time as arguments to
`send-marketing-email`'s script, not stored in the email file itself. This is a
deliberate change from the old `.eml` format (which carried its own RFC 5322
headers): Graph's `sendMail` takes subject, recipients, and body as separate
parameters, so there's nothing for the file to carry beyond the body.

### Always ask: recipient(s), From, Reply-To

Never invent any of these three — ask, every time, and record the answers in
`campaign.md` so `send-marketing-email` doesn't have to ask cold (though it will
still confirm them again before the real send — see its own docs):

**1. Recipient(s).** Ask for the email address(es) this goes to. If there's any
chance of more than one person, tell the user how to enter it: *"separate multiple
addresses with commas, e.g. `jane@example.com, bob@example.com`."* Record the full
list in `campaign.md` — however many there are, `send-marketing-email` sends each
one their own isolated Graph API call. Nobody ever sees anyone else's address; there
is no Bcc mechanism involved because there's no shared recipient list to begin with.

**2. From address.** Ask which mailbox this sends from. **Important limitation:**
`send-marketing-email` can currently only send as whoever signs in through the
browser at send time — there's no way yet to send as a different mailbox (Send As
for a shared mailbox isn't built). Record the intended mailbox here anyway, so
whoever actually runs the send knows which account needs to sign in.

**3. Reply-To.** Ask: "should replies go to that same address, or somewhere else?"
If the same, leave this blank in `campaign.md` — `send-marketing-email` only sets a
Reply-To header when one is explicitly given. If different, record the address.

**Images:** same two-stage model as batch — `{{COMMON_CDN}}/...` (already live)
directly, `{{CAMPAIGN_LOCAL}}/...` (a local relative path) for anything
campaign-specific and new. The publish step ([workflow](campaign-email-drafting.md) step 7) rewrites
`{{CAMPAIGN_LOCAL}}` → `{{CAMPAIGN_CDN}}`, same rewrite as any batch mode. Never a
`data:` URI, ever. See `cdn-and-common-assets.md`.

**No `{{merge}}` tokens, no unsubscribe footer.** `{{first_name}}`-style tokens and
the SendGrid `<%asm_group_unsubscribe_raw_url%>` / `<%asm_preferences_raw_url%>` tags
have no meaning outside their respective send paths and must never appear in an
individual send — `send-marketing-email`'s guards refuse to send a body containing
either. Hardcode the recipient's name directly. **Stripping the unsubscribe footer
from an individual send is mandatory**, not a style choice — it's a personal email
from a named sender, not a list send.

**Sending it:** `/send-marketing-email`, individual mode (`--to`), once the draft is
verified, published, and (in `campaign.md`) the recipient/From/Reply-To details are
recorded.

## Batch send — SendGrid

**When:** a genuine bulk or uninformed-list send — a broad segment, a whole customer
base, anything where automatic unsubscribe suppression matters for compliance.

**Files:** `assets/batch-template.html`, copied to `<year>/<slug>/<slug>.html`
(draft), published to `<year>/<slug>/<slug>-cdn.html` (production).

**Personalisation tokens:** `{{first_name}}` etc. — SendGrid's Handlebars-style merge
fields.

**Unsubscribe footer — mandatory, never stripped.** The footer block in
`batch-template.html` carries SendGrid's raw-URL tags:

```
<%asm_group_unsubscribe_raw_url%>
<%asm_preferences_raw_url%>
```

This is a compliance requirement (anti-spam law), not a design preference — never
remove it to "clean up the footer" or because a draft looks unfinished. SendGrid
handles actual list suppression when someone unsubscribes; that's the reason to
choose this mode over Graph batch for a real bulk send (see below).

**Sending it:** `<slug>-cdn.html` is uploaded to SendGrid manually by whoever owns
that send — this workflow doesn't touch SendGrid's API or dashboard at any point.

## Batch send — Graph (CSV)

**When:** a smaller, already-informed list — existing customers, partners, event
registrants — where a reply-to-unsubscribe convention plus manually maintaining the
CSV between sends is acceptable. **Not for a genuine bulk/uninformed marketing
blast** — Graph has no equivalent of SendGrid's list-suppression, so there's no
automatic unsubscribe handling; see the caveat in `graph-batch-template.html` and in
`send-marketing-email`'s `sending-and-guards.md`.

**Files:** `assets/graph-batch-template.html`, copied to `<year>/<slug>/<slug>.html`
(draft), published to `<year>/<slug>/<slug>-cdn.html` (production) — same publish
step as every other mode.

**Personalisation tokens:** `{{first_name}}` etc., same `{{token}}` syntax as
SendGrid's, but filled by `send-marketing-email`'s own CSV-merge logic at send time,
not SendGrid. Add a column to the recipients CSV for every token the template uses —
the send script refuses to send if a token has no matching column, or if any row
leaves it blank.

**Unsubscribe — manual only.** The footer uses a plain `mailto:` link, not SendGrid's
ASM tags (which mean nothing in a Graph send and would appear as broken literal
text). Someone has to actually read those replies and remove the address from the
next CSV — there is no automated suppression list.

**Recipients CSV:** one row per recipient, an `email` column required, plus one
column per `{{token}}` the template uses. See the `recipients-template.csv` shipped
in `send-marketing-email`'s own assets for the shape. Record the CSV's path in
`campaign.md`.

**Sending it:** `/send-marketing-email`, batch mode (`--csv`), once the draft is
verified and published.

## Quick comparison

| | Individual | Batch — SendGrid | Batch — Graph (CSV) |
|---|---|---|---|
| Recipients | One, or a handful of named people | A broad list/segment | A smaller, already-informed list |
| File produced | `<slug>.html` → `<slug>-cdn.html` | `<slug>.html` → `<slug>-cdn.html` | `<slug>.html` → `<slug>-cdn.html` |
| Personalisation tokens | No — hardcode the name | Yes — `{{first_name}}` etc. | Yes — `{{first_name}}` etc., via CSV |
| Unsubscribe | **Stripped, always** | **Present, automatic suppression** | Manual `mailto:` convention only |
| Reply-To | Ask; omit if same as sender | N/A (SendGrid sender config) | Ask; omit if same as sender |
| Isolation | One Graph call per recipient | SendGrid's own personalisation | One Graph call per CSV row |
| Sent via | `/send-marketing-email --to` | SendGrid upload (manual) | `/send-marketing-email --csv` |
