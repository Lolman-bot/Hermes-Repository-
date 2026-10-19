# Campaign: [Campaign name]

| Field | Value |
|-------|-------|
| Slug | `[slug]` |
| Year | `[year]` |
| Send mode | `[Individual (Graph) / Batch — SendGrid / Batch — Graph (CSV)]` |
| Status | `Draft` |
| Owner | `[name]` |
| Send date | `[date or TBC]` |

## Email
- **Subject line:** [subject]
- **Preview text:** [preview text — individual sends can leave this blank]
- **From address:** [marketing@bitpool.com — the shared mailbox is the default for
  marketing sends; a personal address only for genuinely 1:1 mail]
- **Reply-To:** [same as From / different address — if different, note it]
- **Audience / segment:** [who this goes to]
- **Send platform:** `[send-marketing-email — individual / send-marketing-email — Graph batch (CSV) / SendGrid batch]`
- **Signature:** `[None / Standard Bitpool (name, role, email, phone as given) / Custom — see below]`
  - If standard: [Sender name] · [Sender role] · [email] · [phone]
  - If custom: [pasted signature, or a note on where it came from]

### Recipients (individual send mode only)
- **Recipient(s):** [address, or comma-separated addresses]
- Multiple named recipients are never put in a shared To/Cc/Bcc — `send-marketing-email`
  sends each their own isolated Graph API call, one address at a time. Nobody sees
  anyone else's address. See `references/publishing-and-sending.md`.

### Recipients CSV (Graph batch mode only)
- **CSV path:** [path to the recipients CSV — see the `recipients-template.csv`
  shipped in `send-marketing-email`'s own assets for the required `email` column
  plus one column per `{{merge}}` token this template uses]

## Links & tracking
- **UTM source:** `[slug_year]` (batch only — individual sends usually skip UTM)
- **CTAs:** [links used]

## Assets

### Common (shared) — staged in `Email Marketing/Common resources/`, served from `email/common/`
Assets reused across campaigns — logo, standard icons, standard accent/hero art. Do
**not** re-upload these per campaign; only list ones this email actually references.
Most will already be live, so this table is usually all pre-checked; a row is unchecked
only when a *new* file was added to `Common resources/` for this campaign.

| File | Confirmed live on CDN? | Notes |
|------|:---:|-------|
| `bitpool_logo.png` | [ ] | |

### Campaign-specific — staged in `[year]/[slug]/email assets/`, served from `email/[year]/[slug]/`
Everything unique to this send. Anything reusable belongs in `Common resources/` instead.

| File | Confirmed live on CDN? | Notes |
|------|:---:|-------|
| `hero_[slug].jpg` | [ ] | |

> Check a box only once you (or IT) have confirmed the file actually resolves at its
> `https://cdn.bitpool.com/...` URL — not just that it was handed off for upload. Any
> unchecked row referenced by the email is **not ready to send**.

## Attachments

Files to attach to the *sent* email — staged in this campaign's `attachments/` folder,
not `resources/` (drafting material only, never attached automatically).

| File / linked path | Physical or linked? | Notes |
|---|:---:|---|
| `[none yet]` | | |

- **Physical** — a copy dropped directly into `attachments/`.
- **Linked** — a full local path recorded in `attachments/linked-attachments.md`,
  pointing at a live document elsewhere (e.g. still being edited) — `send-marketing-email`
  reads its current content at send time rather than a frozen copy.

## Checklist

Drafting (`/draft-marketing-email` steps 1–6):
- [ ] Draft file built (`[slug].html`) with local `email assets/` paths for new
      campaign-specific images
- [ ] **Local-image-reference check run** — `[slug].html` grepped for local path
      patterns (`email%20assets/`, `email assets/`, `Common%20resources/`, `Common
      resources/`), then any hit reconciled against this file's asset tables below
      (not grepped — its own headers describe these same folder paths in prose, so a
      blind text search on this file is noise, not signal). Result: `[clean — no hits
      / these files still local: ...]`. A clean *local* preview does not count; this
      is a text check on the file, not a visual one.
- [ ] Reviewed by [owner]
- [ ] Recipients / From / Reply-To (or recipients CSV) recorded above
- [ ] Signature decided (none, standard, or custom) — recorded above, block filled
      in or deleted from the template accordingly

Verify & publish (`/draft-marketing-email` steps 7–8):
- [ ] Every image verified live on the CDN (a real 200) — all Assets rows ticked
- [ ] Handed off to IT (Eric) for any new uploads — folder link(s) sent
- [ ] Production artefact generated (`[slug]-cdn.html`)

Sending (see `references/publishing-and-sending.md`):
- [ ] Attachments (if any) staged in `attachments/` — physical copies and/or
      `linked-attachments.md` entries — and listed in the table above
- [ ] Sent via `/send-marketing-email` (individual or Graph batch) / handed to
      SendGrid (SendGrid batch — still a manual, human-operated upload)

## Notes
[anything else worth recording — why this campaign exists, decisions made, follow-ups]
