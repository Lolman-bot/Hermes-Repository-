# Drafting a campaign email

Builds a Bitpool email marketing campaign from scratch through to a verified, CDN-linked, ready-to-send file. Built for the `Email Marketing` SharePoint workspace (`.../General/15 HTML/Email Marketing` — synced to a different local path per employee, see step 0.5).

> **Important**
> **Drafting never sends anything, ever.** Sending is a separate step, handed off once a file is verified and CDN-linked: `/send-marketing-email` (Graph, individual or CSV batch), or a manual SendGrid upload for a broad/uninformed list. See step 8.


> **Note**
> The four scaffolds — `individual-template.html`, `batch-template.html`, `graph-batch-template.html`, `campaign.md` — ship locally with the `draft-marketing-email` skill. This page is the method; those files are the machinery.


## 0. Surface check — local file tools available?

This workflow reads and writes real files in a SharePoint-synced Windows folder, so it needs Hermes's local file tools (`terminal`, `read_file`, `write_file`, `patch`, `search_files`). If running on a surface without those tools (e.g. a chat-only gateway with file tools disabled), **stop before scaffolding anything** and tell the user:

> This skill needs local file access to manage the campaign folder — that's not available here. Switch to a Hermes session with the file and terminal tools enabled (e.g. the Hermes CLI on your own machine) and re-run `/draft-marketing-email` there.

Then ask: **stop here**, or **proceed anyway** in an advisory-only mode (draft copy and HTML in chat, with the user creating folders and placing files themselves). Don't silently proceed as if nothing were missing.

**Ideal setup:** the user starts Hermes with the `Email Marketing` folder itself as the working directory. That sidesteps everything in step 0.5 — don't ask them to do it retroactively if you can already tell you're in the right place.

### Flag the CDN gate up front

**Early in the conversation — before drafting starts, not after** — tell the user any brand-new image this campaign uses will need a CDN upload before it can be sent, so it isn't a surprise later:

> Heads-up before we start: while drafting, any brand-new image points at your local `email assets/` folder, so it'll preview fine for you. That's staging, not hosting — it still needs IT to upload it to the CDN before this can go out. I'll track every image this email uses in `campaign.md` and only tick a box once I've actually confirmed it live on the CDN myself.

Say it once, plainly, then get on with the draft. The point is that the user knows the gate exists while there's still time to gather assets — not to nag.

## 0.5. Locate the workspace — don't assume a fixed local path

**Different employees sync SharePoint at different roots**, so the local path varies machine to machine — one person might have `...\Bitpool Pty Ltd\Marketing - Bitpool - Documents\General\15 HTML\Email Marketing`, another might sync starting from `General` itself. **Never hardcode or assume a specific `C:\Users\<name>\...` path** — resolve it fresh every time:

1. Check the current working directory first. If it's already the `Email Marketing` folder — recognisable by containing (or being ready to contain) year folders like `2026/` with `<slug>/campaign.md` inside — you're set; skip to step 1.
2. If the cwd looks like a **parent** of it (`15 HTML`, `General`, `Marketing - Bitpool - Documents`, or any other SharePoint library root), search downward a few levels for a folder literally named `Email Marketing`. If you find exactly one, confirm the resolved path with the user before creating or writing anything in it.
3. If you can't confidently locate it (nothing found, or more than one candidate), **stop and ask**. Don't guess a path and start creating folders speculatively.
4. Once resolved, treat that path as the workspace root for the rest of the session.

This affects only where files are **read and written**. It has nothing to do with image URLs inside the email — those are local relative paths while drafting and CDN URLs in production, never a SharePoint URL either way (see step 5).

## 1. Load brand context first

Before writing anything, read the two design skills this one hard-depends on — do not hand-roll brand styling:

- **`bitpool-design-system`** — colours (`#00ADEF` cyan), Inter type, the bold-cyan emphasis rule, the cube logo, light/dark tokens. Treat it as the single source of truth rather than re-reading the standalone brand-guide doc.
- **`bitpool-brand-guidelines`** — voice: boldly practical, unapologetically real, bold cyan replaces italics, specific over vague, no SaaS clichés.

Both ship in the **bitpool-design-foundations** section of the Bitpool Hermes skills repo, not this one — install them alongside the **bitpool-marketing** skills so `/bitpool-design-system` and `/bitpool-brand-guidelines` are available (load with `skill_view`) while drafting.

## 2. The two non-negotiables

1. **No vector images, ever.** Every image is a raster export — PNG for logos, icons and anything needing transparency; JPG for photography. Design in vector if you like, but export to PNG/JPG before it goes anywhere near an email. No `.svg` in `email assets/` and no inline `<svg>` in the HTML.
2. **No base64 / `data:` URIs, ever.** Every `<img src>` is either a real `https://cdn.bitpool.com/…` URL or, pre-publish, a local relative path — never an inlined data URI.

## 3. If the campaign folder doesn't exist yet — scaffold it

Ask for the **campaign name** (used to derive the slug) if not given. Slug rules: lowercase, hyphen-separated, no spaces, no year (e.g. `spring-promo`). Year is the current calendar year unless told otherwise.

The workspace as a whole — note `♻️ Common resources/` lives at the **root**, shared by every campaign, and already exists (never recreate it):

```
Email Marketing/
├── ♻️ Common resources/      ← shared, reusable images — mirrors cdn…/email/common/
└── <year>/<slug>/            ← one folder per campaign, created by you
    ├── 🖼️ email assets/      ← images THIS email uses — mirrors cdn…/email/<year>/<slug>/
    ├── 📎 attachments/       ← files THIS email attaches — physical copies + linked-attachments.md
    ├── 📥 resources/         ← drop-zone: pitch decks, briefs, .md/.docx notes, raw photos
    └── 📝 campaign.md        ← metadata + asset checklist (copy assets/campaign.md)
```

Create only the `<year>/<slug>/` part, including an empty `attachments/` folder even if nothing needs attaching yet. Explain the folders to the user with their emoji:

- **🖼️ `email assets/`** — "This holds the finished images your email uses (hero, feature shots, campaign-specific icons). I populate this — please don't hand-edit its contents, since filenames here are wired directly into the HTML."
- **📎 `attachments/`** — "Anything you want attached to the sent email goes here — two ways. **Drop a physical file** directly into this folder and I'll attach that copy. Or, if it's a **live document that keeps changing** (a pricing sheet, a tracker workbook) and you'd rather not attach a stale snapshot, tell me its full file path in chat instead of copying it in — I'll record that path in `attachments/linked-attachments.md` so `/send-marketing-email` reads the current version fresh at send time. Nothing in here is emailed automatically until you send — it's just staged, same as the other folders."
- **📥 `resources/`** — "Drop anything here that should shape the email: pitch decks (`.pptx`), briefs or copy (`.md`, `.docx`), PDFs, raw photos, brand approvals. Nothing in here is published, emailed, or attached automatically — it's just material for me to draw from. If in doubt, drop it here and tell me what it's for."
- **♻️ `Common resources/`** (mention only if a common asset comes up) — "Shared images every campaign can reuse — the logo, standard icons, generic accent art. Anything here is already on, or on its way to, the shared CDN path, so campaigns link to it rather than keeping their own copy."

Do not create multiple mode scaffolds side by side "just in case" — see step 4, build only the scaffold for the chosen send mode.

## 4. Ask the send mode

Before building the email, ask the user to choose (state a recommendation only if one context clearly fits better — e.g. "sounds like a 1:1 follow-up" → individual):

- **Individual** — one or a handful of named recipients (a follow-up, a personal outreach). No `{{merge}}` tokens, no unsubscribe footer. Sent via `/send-marketing-email --to`, which sends each recipient their own isolated Graph API call.
- **Batch — SendGrid** — a broad or uninformed list/segment where real unsubscribe suppression matters for compliance. Uploaded to SendGrid by a human and sent from there. Carries `{{personalisation tokens}}` and the mandatory unsubscribe footer.
- **Batch — Graph (CSV)** — a smaller, already-informed list (existing customers, partners, event registrants) where a manual reply-to-unsubscribe convention is acceptable. Sent via `/send-marketing-email --csv`, one isolated Graph call per CSV row.

Every mode produces the same file: `<slug>.html` (draft), published to `<slug>-cdn.html` once assets are verified (step 7).

| Mode | Copy this template | Save as |
| --- | --- | --- |
| Individual | `assets/individual-template.html` | `<slug>.html` |
| Batch — SendGrid | `assets/batch-template.html` | `<slug>.html` |
| Batch — Graph (CSV) | `assets/graph-batch-template.html` | `<slug>.html` |

Full detail on all three formats, the merge-token conventions, and the footer/unsubscribe rules is in [Send modes](send-modes.md) — read it before building any of them.

> **Warning**
> **The moment you copy a template, resolve its URL-base tokens to literal values — never leave `{{...}}` brace syntax sitting in a real campaign's `<slug>.html`.** These are shorthand for you to fill in, not runtime placeholders anything substitutes later.
>
> | Token in the template | Write this literal value instead, immediately |
> | --- | --- |
> | `{{COMMON_CDN}}/<file>` | `https://cdn.bitpool.com/email/common/<file>` |
> | `{{COMMON_LOCAL}}/<file>` | `../../Common%20resources/<file>` |
> | `{{CAMPAIGN_LOCAL}}/<file>` | `email%20assets/<file>` |
>
> A literal `{{COMMON_CDN}}` surviving into a real campaign file is a broken image for every recipient, and it's exactly what `send-via-graph.py`'s guard checks refuse to send. `{{CAMPAIGN_CDN}}` is the only token you never write by hand — it appears only from the step 7 publish rewrite.


### For individual sends specifically — always ask these three things

Before filling in the template, ask (don't assume or invent any of these) and record the answers in `campaign.md`:

1. **Recipient(s).** Ask for the email address(es). If they might have more than one person in mind, explain up front: "separate multiple addresses with commas, e.g. `jane@example.com, bob@example.com`." `/send-marketing-email` sends each address its own isolated Graph API call — no one ever sees anyone else's address, and there's no Bcc mechanism because there's no shared recipient list to begin with.
2. **From address.** Ask which mailbox this sends from. `/send-marketing-email` can send as whoever signs in, or **Send As** a shared mailbox (`--send-as`) if the signing-in user has that Exchange permission. Record the intended address so the right person knows to sign in — sending will still ask for the exact Send As mailbox fresh at send time.
3. **Reply-To.** Ask whether replies go to that same address or somewhere else. If different, record it; if the same, leave it blank.

### For Graph batch specifically — also ask for the recipients CSV

Ask for the path to a CSV with an `email` column plus one column per `{{merge}}` token the template uses (see `recipients-template.csv` in the `send-marketing-email` skill's assets for the shape). Record the path in `campaign.md`.

## 4.5. Ask about a signature

Ask every campaign, regardless of mode: **"Do you want a signature on this email?"** Don't assume yes or no, and don't invent one.

- **No** → skip it entirely — delete the signature block from the template rather than leaving `[Sender name]`/`[Sender role]` bracket placeholders in a sent email. The bracket-placeholder guard in `send-via-graph.py` would refuse the send anyway, but make the deliberate choice yourself.
- **Yes** → offer the standard Bitpool signature (below) and ask which fields to fill in. Name is the only one that really makes a signature read as one; role, email and phone are each optional. If they'd rather paste an exact signature they already have, use that verbatim.

Record the decision and the actual content in `campaign.md`'s Signature field, then fill in (or fully delete) the signature block.

### Standard Bitpool signature — fields and markup

Name (bold) → Role · Bitpool (muted) → an optional contact line with email (cyan link) and/or phone (muted), separated by a middot if both are given:

```html
<p style="margin:0; font-family:'Inter',sans-serif; font-weight:600; font-size:15px; color:#1B2732; letter-spacing:-0.01em;">[Sender name]</p>
<p style="margin:3px 0 0 0; font-family:'Inter',sans-serif; font-weight:400; font-size:13px; color:#6e7c8b; letter-spacing:0.01em;">[Sender role] &middot; Bitpool</p>
<p style="margin:10px 0 0 0; font-family:'Inter',sans-serif; font-weight:400; font-size:13px; color:#6e7c8b;">
  <a href="mailto:[sender email]" style="color:#00ADEF; text-decoration:none;">[sender email]</a>&nbsp;&middot;&nbsp;[sender phone]
</p>
```

This matches the typography every template already uses for its signature block — the contact line is the only genuinely new piece. Drop the whole third `<p>` if neither email nor phone was given; drop just the phone half (and its `&nbsp;&middot;&nbsp;` separator) if only email was given, and vice versa. If role wasn't given, drop `[Sender role] &middot; ` and leave just `Bitpool`.

## 5. Assets — common vs campaign-specific

Read [CDN and common assets](cdn-and-common-assets.md) before wiring any image URL. Short version — two asset categories, each with a local SharePoint folder mirroring a CDN path:

| Kind | Local folder (staging) | CDN path (what emails reference) |
| --- | --- | --- |
| **Common** — reusable across campaigns | `Email Marketing/Common resources/` | `https://cdn.bitpool.com/email/common/<file>` |
| **Campaign-specific** — this send only | `<year>/<slug>/email assets/` | `https://cdn.bitpool.com/email/<year>/<slug>/<file>` |

Both are flat, and the filename is the whole mapping. **`Common resources/` is the manifest of what belongs on the common CDN path** — list that folder to see what's available rather than guessing or maintaining a separate list.

- **Common assets already live** (logo, the standard icon set) → reference the real `https://cdn.bitpool.com/email/common/<file>` URL directly. Don't copy the logo into a campaign folder again.
- **Campaign-specific images** → stage in `email assets/`, reference `email%20assets/<file>`. Publish rewrites to the campaign CDN path.
- **New common assets** → stage in `Common resources/`, reference `../../Common%20resources/<file>`. Publish rewrites to the real common CDN URL.

**Verify a common asset immediately, don't wait for step 7.** The moment you reference an already-live common asset, curl it:

```bash
curl -s -o /dev/null -w "%{http_code}  %{url_effective}\n" "https://cdn.bitpool.com/email/common/<file>"
```

`200` → tick that row in `campaign.md` right away. Anything else → don't assume it's fine just because the file sits in `Common resources/` locally. Leave the box unchecked and add a line to this campaign's `follow-up.md` (create it at `<year>/<slug>/follow-up.md` if it doesn't exist — format in [Publishing and sending](publishing-and-sending.md)) naming the file and what curl actually returned. `follow-up.md` is the running list of everything blocking a clean send.

### Routing a new image — decide before wiring it in

Whenever you create an image, or the user hands you one that isn't staged yet, ask: **would another campaign plausibly reuse this?**

- **Yes** (logo variants, generic icons, standard footer art, generic accent graphics, stock skyline/building photography) → `Common resources/`
- **No** (this send's hero, a screenshot for one announcement, event-specific art) → `<year>/<slug>/email assets/`

When it's genuinely unclear, ask the user. **Always tell the user which folder you put a file in**, since that determines what they hand IT. Staging a file locally does *not* put it on the CDN.

**Never use a SharePoint URL for an image.** Drafts use local paths; production uses CDN URLs. There is no third option, and a SharePoint image URL would be auth-gated and broken for recipients anyway.

As you build, keep `campaign.md`'s asset tables up to date with every image the draft references, unchecked by default — that checklist is what step 7 gates on. Don't check a box yourself; that's confirmation of a live CDN upload, which only happens once IT has actually done it.

## 6. When the draft looks done — check for local image references

**Trigger this yourself** whenever the draft appears finished: the user says it looks good, stops requesting changes, asks what's next, or starts talking about sending. Don't wait to be asked, and don't let a session end with an unchecked draft.

This is a mechanical, text-level check — no browser, no waiting on OneDrive sync, nothing for the user to do. Its job: **confirm no local image reference survived anywhere in the email**. Grep the **draft only** for every local-path pattern, in both encoded and literal-space form:

```bash
grep -niE 'email%20assets/|email assets/|Common%20resources/|Common resources/' "<slug>.html"
```

Don't run that same grep blindly against `campaign.md` — its own section headers describe the folder structure in prose and will always contain these substrings, on every campaign, forever. It's guaranteed noise, and it wouldn't catch a real problem anyway: a genuine asset row only ever lists a bare filename, never a path.

Instead, **read** `campaign.md`'s asset tables and reconcile them against what the HTML grep found: a file referenced locally in the HTML needs a matching unchecked row; a row already ticked as confirmed-live needs its HTML reference to actually be a CDN URL. The two must agree — a structural check on checkbox state per filename, not a text search.

> **Note**
> **Why a grep is enough, and a rendered preview isn't.** The failure mode is a local relative path (`email%20assets/hero.jpg`) that resolves on your machine because the browser resolves it against the file's own location, and resolves against nothing wherever a recipient opens it. That's a property of the *text of the file*, which grep answers with certainty.
>
> An earlier version of this workflow had the user open the draft from SharePoint Online and eyeball whether images loaded — **don't resurrect that.** SharePoint's inline HTML previewer sandboxes external resources and can show a broken image for a URL that's genuinely live on the CDN, making it false-negative-prone for exactly the thing it was meant to verify.


This matters most for the user who believes they don't need IT at all ("I only used the logo, that's already up" — true, but check anyway if any *new* image made it in unnoticed). **Treat it as a check to run, not a question to ask** — never accept "I don't think I need IT" as a substitute.

Then act on the result:

- **No local-path hits** → every image already resolves to a real CDN URL. Proceed to step 7 with no IT hand-off needed.
- **Any local-path hit** → that file is **not** on the CDN yet. List them explicitly by filename, make sure each has an unchecked row in `campaign.md`, and add a line to `follow-up.md` naming exactly what's outstanding and who needs to act (usually IT).

Never describe a draft as "ready" before this check has actually been run and come back clean.

## 7. Verify assets and publish

Once step 6 comes back clean (or once IT confirms an upload), do this yourself — it's mechanical, needs no credentials, and doesn't require the user to do anything but tell you the upload is done.

1. **Check `follow-up.md` first, if this campaign has one.** Every line needs to be resolved (or explicitly re-verified as fixed) before you proceed — a common-asset curl failure logged in step 5 doesn't get fixed by step 6 passing.
2. **Verify, don't just trust.** For every image the draft references, fetch its CDN URL and confirm a real `200` — "IT said they uploaded it" is not confirmation, and a typo'd filename or wrong path is the most common failure here:
   ```bash
   curl -s -o /dev/null -w "%{http_code}  %{url_effective}\n" "<each cdn url>"
   ```
   Only tick a box in `campaign.md` once you've confirmed a real `200` yourself.
3. **If anything is unverified, stop here.** Tell the user exactly which files and which folder(s) still need to go to IT (Eric) — `Common resources/`, this campaign's `email assets/`, or both — and draft the hand-off message for them to send (don't send it yourself). Log it in `follow-up.md`. Full detail, including the exact folder→CDN-path mapping, is in [Publishing and sending](publishing-and-sending.md).
4. **Once everything verifies, run the publish rewrite** — copy `<slug>.html` → `<slug>-cdn.html`, replacing every `email%20assets/` with the real campaign CDN URL and `../../Common%20resources/` with the real common CDN URL. Never hand-edit the production file for content; change the draft and re-publish.
5. **Confirm no local reference survived the rewrite** — grep the output for `email assets/`, `Common resources/` (both encoded and literal-space forms), `sharepoint.com`, and any stray `{{...}}` brace token. Any hit means the rewrite missed something, or a token was never resolved during drafting.
6. **Clear `follow-up.md`** once every line is genuinely resolved. Don't leave it half-resolved — sending treats its presence with unresolved items as a hard stop.

## 8. Hand off for sending

The file is now verified and CDN-linked. **Stop here — drafting's job is done.**

For individual or Graph batch:

> `<slug>-cdn.html` is ready — every image verified live on the CDN. Run `/send-marketing-email` to send it from here — that skill handles Graph sign-in, recipient/CSV handling, and the actual send.

For SendGrid batch:

> `<slug>-cdn.html` is ready and verified. Upload it to SendGrid and send from there — nothing has gone out yet.

Say this plainly every time. A verified, published file is not a sent campaign, and this is the easiest place in the whole workflow to leave a false impression.

## Anti-patterns

- Embedding an image as a `data:` URI "just this once" — never, no exceptions.
- Shipping an `.svg` into `email assets/` or inlining `<svg>` markup.
- Building more than one send-mode scaffold for a campaign that only needs one.
- Copying the logo into a campaign's `email assets/` instead of pointing at `email/common/`.
- Assuming `resources/` (drafting material) is a place `/send-marketing-email` will look for attachments — it isn't, and never will be. Only `attachments/` is read at send time.
- Copying a live, frequently-updated document into `attachments/` as a static snapshot instead of recording its full path in `attachments/linked-attachments.md`.
- Saying a campaign is "ready to send" before the step 6 local-image-reference check *and* step 7 CDN verification have both actually happened.
- Pointing an `<img src>` at a SharePoint URL.
- Treating a clean local preview as proof the images work — it proves only that the files exist on that one machine.
- Re-introducing a SharePoint-preview visual test as a substitute for (or addition to) the step 6 grep.
- Accepting "I don't think I need IT to upload anything" without running the step 6 check.
- Ticking an asset checkbox without an actual `200` from step 7.
- Assuming a common asset is live just because the file exists in `Common resources/` locally.
- Leaving `follow-up.md` around with unresolved items once a campaign is called ready.
- Sending anything yourself, or implying the file being ready means it's been sent.
- Skipping `bitpool-design-system` / `bitpool-brand-guidelines` and improvising the look or voice.
- Assuming a campaign wants (or doesn't want) a signature instead of asking, or leaving bracket placeholders in a sent email.
- Writing a literal `{{COMMON_CDN}}`, `{{COMMON_LOCAL}}` or `{{CAMPAIGN_LOCAL}}` brace token into a real campaign's `<slug>.html`.
- Using the SendGrid batch template's unsubscribe tags in an individual or Graph-batch send, or vice versa.
