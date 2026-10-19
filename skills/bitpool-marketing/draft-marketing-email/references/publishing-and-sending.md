# Publishing (verify + rewrite) and sending

Two different things live in this doc:

- **Publishing** (verify assets, rewrite local paths to CDN URLs) — the agent does this,
  mechanically, once assets are confirmed. No credentials needed.
- **Sending** (getting the file to a recipient) — handled by **`/send-marketing-email`**
  (individual and Graph-CSV batch), or a manual SendGrid upload (SendGrid batch).
  Neither is this skill's job — `draft-marketing-email` stops the moment a file is
  verified and published.

## Part 1 — Asset verification

### Step 1: inventory every image the draft references

Extract every `<img src>` and CSS `background-image` URL from the draft
(`<slug>.html`, whichever mode built it). Sort each into one of four buckets:

- **`{{COMMON_CDN}}` / `cdn.bitpool.com/email/common/...`** → a shared asset claiming to
  be live. Verify it (step 2). The local mirror is `Email Marketing/Common resources/` —
  that folder *is* the manifest of what belongs on this path, so there's no separate
  checklist file to keep.
- **`{{COMMON_LOCAL}}` / `../../Common%20resources/...`** → a **new** common asset staged
  but not yet uploaded. Needs the IT hand-off (step 3), targeting `email/common/`.
- **`{{CAMPAIGN_LOCAL}}` / `email%20assets/...`** → a campaign-specific image not yet on
  the CDN. Needs the IT hand-off (step 3), targeting `email/<year>/<slug>/`.
- **`{{CAMPAIGN_CDN}}` / `cdn.bitpool.com/email/<year>/<slug>/...`** → claims to be live
  already. Verify in step 2; cross-check this campaign's `campaign.md` table.

### Step 2: verify, don't assume

For anything claiming to be live, **verify the URL actually resolves** — fetch it and
confirm a `200`, not a `403`/`404`. "IT said they uploaded it" is not confirmation; a
typo'd filename or wrong path is the most common failure here, and it produces a broken
image in a sent email, which can't be undone.

```bash
curl -s -o /dev/null -w "%{http_code}  %{url_effective}\n" "<each cdn url>"
```

Only tick a checkbox in `campaign.md` once you've confirmed a real `200`. Anything
unverified is **blocking** — say so plainly and do not proceed to publish.

### Step 3: the IT hand-off (when images aren't uploaded yet)

Two possible targets, and a campaign can need both:

| Unuploaded asset kind | Local folder to send IT | CDN path IT uploads to |
|---|---|---|
| Common / reusable | `Email Marketing/Common resources/` | `s3://bitpool-cdn-production/email/common/` |
| Campaign-specific | `<year>/<slug>/email assets/` | `s3://bitpool-cdn-production/email/<year>/<slug>/` |

1. Tell the user exactly which folder(s) IT needs, per the table above.
2. Ask them to **right-click that folder → Copy link** in SharePoint/OneDrive and send it
   to **IT (Eric)**, stating which CDN path it lands at — the two are not interchangeable
   and IT can't infer it from the folder alone.
3. **Draft the hand-off message for them**, listing the exact unconfirmed filenames from
   step 1 grouped by target path, so IT knows precisely what's new versus already live.
   Don't send it yourself; that's the user's action.
4. Stop there. The campaign is blocked until IT confirms upload and step 2 verifies it.

## Part 1.5 — `follow-up.md`: tracking what's still outstanding

Not a shipped template — create it at `<year>/<slug>/follow-up.md` the first time
this campaign has anything blocking a clean send: a common-asset curl check that
didn't return `200` (step 5), an image still waiting on the IT hand-off (step 6/7),
or any other loose end worth not forgetting (an undecided signature, a CSV that
still needs a column, anything else). It's a general punch-list, not only about
images.

Format — one line per item, each naming what's outstanding, why, and who needs to
act:

```markdown
# Follow-up — spring-promo

- [ ] hero_spring-promo.jpg — not yet uploaded, IT hand-off sent 2026-07-29
- [ ] bitpool_logo_v2.png — curl returned 404 at https://cdn.bitpool.com/email/common/bitpool_logo_v2.png,
      check the filename actually matches what's in Common resources/
- [ ] Signature — user hasn't decided yet, asked again 2026-07-29
```

Check a box (or delete the line) only once the item is genuinely resolved — same
discipline as `campaign.md`'s asset tables. **`send-marketing-email` checks this file
before allowing a send** (its Sending a campaign email (see the `/send-marketing-email` skill) step 1) — an unresolved `follow-up.md` is a
hard stop, same as an un-rewritten local-path token. Clear it entirely (or delete the
file) once a campaign is genuinely ready; don't leave stale checked-off history
sitting around a "ready" campaign.

## Part 2 — The publish rewrite

Once every referenced image is confirmed live:

```
email%20assets/<file>            → {{CDN_BASE}}/<year>/<slug>/<file>
../../Common%20resources/<file>  → {{CDN_BASE}}/common/<file>
{{CDN_BASE}}/common/<file>       → unchanged, already live
```

Copy `<slug>.html` → `<slug>-cdn.html`, applying the rewrite — the same operation
regardless of which of the three modes built the draft (individual, SendGrid batch,
or Graph batch). Never hand-edit the CDN file for content — if copy needs to change,
change the draft and re-publish.

Handle both the encoded and literal forms (`email%20assets/` **and** `email assets/`,
`Common%20resources/` **and** `Common resources/`), in both quoted `src="…"` and CSS
`url(…)` contexts. After rewriting, grep the output for `email assets/`,
`Common resources/`, and `sharepoint.com` — any hit means the rewrite missed
something.

There's no `-draft` suffix to drop any more (see `send-modes.md` for why) — the
draft/published distinction is entirely the `.html`/`-cdn.html` filenames, and the
real safety brake is structural: `send-marketing-email`'s guard checks refuse to send
a file that still contains any of the local-path tokens above, so an unpublished
draft can't slip through even if handed to the send skill by mistake.

---

## Part 3 — Sending

### Individual and Graph batch → `/send-marketing-email`

Both hand off to the `send-marketing-email` skill, which signs in via Microsoft
Graph (delegated — a real person signs in through a browser, no application
permission) and sends directly, bypassing Outlook's rendering entirely. Tell the
user:

> `<slug>-cdn.html` is ready — every image verified live on the CDN. Run
> `/send-marketing-email` to send it — that skill handles sign-in, recipient/CSV
> handling, and the actual send.

Don't attempt any part of the send yourself from this skill — recipient/From/Reply-To
prompting, the confirm gate, and the actual API call all live in
`send-marketing-email`, not here. This skill's job stops at a verified, published
file. If this campaign has anything staged in its `attachments/` folder (physical
files or `linked-attachments.md` entries), mention it exists — `send-marketing-email`
checks there itself, no need to re-describe every file.

### Batch — SendGrid (manual, human-operated)

This is entirely a human, manual action — no API, no automated list send, and not
something `send-marketing-email` touches either.

Deliver `<slug>-cdn.html` as verified and ready, then hand off:

1. Whoever owns the send uploads it to SendGrid.
2. They set the audience/segment there.
3. They send from SendGrid.

**Be explicit that nothing has been sent.** A verified production file is not a sent
campaign, and this is the easiest place in the whole workflow to leave a false
impression. Say "ready to upload to SendGrid" — never "sent" or "live."

Also confirm before hand-off that the **unsubscribe footer survived the publish
rewrite**. It's a legal requirement on a list send, and a rewrite that accidentally
strips it turns a compliant email into a non-compliant one.

## Quick reference

| Situation | Path | Setup needed |
|---|---|---|
| 1 recipient, one-off | `/send-marketing-email --to` | WSL/Python setup (once) |
| Several named recipients | `/send-marketing-email --to` (comma-separated — each gets an isolated send) | WSL/Python setup (once) |
| Smaller, already-informed list | `/send-marketing-email --csv` (Graph batch) | WSL/Python setup (once) + a recipients CSV |
| A real list / broad segment | SendGrid, human-operated | SendGrid access |
