# CDN structure: common vs campaign assets

## Hosting configuration (established, don't invent alternatives)

```
CDN_BASE          = https://cdn.bitpool.com/email
S3_BUCKET         = bitpool-cdn-production
S3_REGION         = ap-southeast-2

SHAREPOINT_BASE   = https://bitpoolau.sharepoint.com/sites/Marketing-Bitpool/Shared%20Documents/General/Email%20Marketing
                    ^ where the workspace lives. Never used as an image URL inside an
                      email.
```

Two asset paths, each with a **local SharePoint folder that mirrors a CDN path**. The
local folder is where files are staged; the CDN path is what emails actually reference.

| Kind | Local (SharePoint) folder | CDN path it mirrors | Contents |
|---|---|---|---|
| **Common** (shared) | `Email Marketing/Common resources/` | `https://cdn.bitpool.com/email/common/<file>` | Logo, standard icons, reusable accent/hero art — anything used across campaigns |
| **Campaign** | `Email Marketing/<year>/<slug>/email assets/` | `https://cdn.bitpool.com/email/<year>/<slug>/<file>` | This campaign's own hero/feature images only |

Both are flat — no subfolders. A file dropped in `Common resources/` becomes
`…/email/common/<same-filename>`, so the filename is the whole mapping.

Uploads to either CDN path are done **manually in the S3 web console** by IT, after being
notified (see `publishing-and-sending.md` for the hand-off). This skill has no
S3 credentials and never uploads anything itself. Dropping a file in the local folder does
**not** put it on the CDN — that always needs the IT hand-off.

### `Common resources/` is the manifest

The folder *is* the record of what belongs on `email/common/` — there's no separate
checklist file to maintain. To know what common assets exist, list the folder.

Verified in sync on 2026-07-28 (all 11 returned HTTP 200 at
`https://cdn.bitpool.com/email/common/<file>`):

```
ai_network_accent.png   bitpool_logo.png        hero_starry_buildings.jpg
icon_globe.png          icon_handshake.png      icon-billing.png
icon-changelog.png      icon-growth.png        icon-help.png
icon-proposal.png       icon-roadmap.png
```

Treat that as a snapshot, not gospel — list the real folder rather than trusting this
list, since files get added. Note both `icon_*` and `icon-*` naming exist historically;
match whatever an existing file is actually called rather than "correcting" it, and prefer
hyphens for anything new.

## Why the split matters

Before this skill existed, every campaign copied the logo and standard icons into its
own `resources/` folder and re-uploaded them per campaign — self-contained, but wasteful
and meant the logo could quietly drift between campaigns. `email/common/` fixes that:
upload the logo and standard graphics **once**, reference the CDN URL directly from
every campaign, forever. Only genuinely new, campaign-specific imagery (this month's
hero shot, a one-off feature graphic) goes through the per-campaign path.

A useful side effect: because common assets are already live, a brand-new campaign that
only reuses common assets needs **no CDN upload at all** before it's sendable — only
campaigns with new imagery need the IT hand-off.

## Where a NEW image goes — decide this every time

Whenever you create an image, or the user supplies one that isn't already staged, route it
**before** wiring it into the HTML. Ask: *would another campaign plausibly reuse this?*

| Answer | Goes in | Referenced while drafting as | Examples |
|---|---|---|---|
| **Yes — reusable** | `Email Marketing/Common resources/` | `{{COMMON_LOCAL}}/<file>` if new, `{{COMMON_CDN}}/<file>` if already live | logo variants, generic icons, standard footer art, generic accent graphics, stock building/skyline photography |
| **No — this campaign only** | `<year>/<slug>/email assets/` | `{{CAMPAIGN_LOCAL}}/<file>` | this send's hero, a product screenshot for one announcement, an event-specific graphic |

Getting this wrong is cheap to fix but worth avoiding: a reusable asset filed under a
campaign path gets re-uploaded and re-diverges next time (exactly the problem
`email/common/` exists to solve), and a one-off filed under common clutters a folder every
future campaign reads.

When in doubt, ask the user — "is this something other campaigns will reuse, or just this
one?" is a quick question with a clear answer.

**Always say which folder you put a file in**, so the user knows what to hand IT. And
remember: a file staged locally is not on the CDN until IT uploads it.

## Draft vs production URLs

While drafting, campaign-specific images aren't on the CDN yet, so there's no remote URL
to point at. Use a **local relative path** — the draft then previews with real images
straight from the campaign folder, with no upload, no sync wait, and no dependency on
anything remote:

The four tokens, and when each applies:

| Token | Resolves to | Use for |
|---|---|---|
| `{{COMMON_CDN}}` | `https://cdn.bitpool.com/email/common` | A common asset **already live** on the CDN — the normal case. No rewrite at publish. |
| `{{COMMON_LOCAL}}` | `../../Common%20resources` | A **new** common asset you just staged, not yet uploaded. Publish rewrites → `{{COMMON_CDN}}`. |
| `{{CAMPAIGN_LOCAL}}` | `email%20assets` | A new campaign-specific image. Publish rewrites → `{{CAMPAIGN_CDN}}`. |
| `{{CAMPAIGN_CDN}}` | `https://cdn.bitpool.com/email/<year>/<slug>` | Production form of the above; the publish step writes it, you don't. |

Both local tokens are **relative to the draft file**, which sits at
`<year>/<slug>/<file>`. That's why common is `../../Common%20resources` — up out of the
slug folder, up out of the year folder, then back down. Both resolve when the draft is
opened straight from the campaign folder in a browser.

**Use the real `https://cdn.bitpool.com/email/common/<file>` URL for anything already
live — don't switch it to a local path.** The `{{COMMON_CDN}}` notation in this table
is shorthand for you to resolve immediately, not literal syntax that belongs in a
real campaign file — write the actual URL the moment you reference an already-live
asset, same as the logo already is in every template. A literal `{{COMMON_CDN}}`
surviving into `<slug>.html` breaks that image for every recipient (it's not a valid
relative path) and is exactly what `send-via-graph.py`'s guards refuse to send.
Referencing the real CDN URL (rather than a local path) for anything already live also
keeps the step 6 grep meaningful: it flags exactly the files still needing an IT
upload, not ones that are already hosted. Turning an already-live asset into a local
path for no reason would make step 6 flag a false positive — a file that's actually
fine, but now reads as unresolved.

**Common assets are verified immediately, not deferred to step 7.** Since the file
already exists in `Common resources/` and the CDN path never changes, curl the real
URL as soon as you reference it (`curl -s -o /dev/null -w "%{http_code}\n"
"https://cdn.bitpool.com/email/common/<file>"`) rather than waiting for the final
gate. Tick `campaign.md`'s box on a `200` right away. On anything else, don't assume
it's fine — log it in the campaign's `follow-up.md` (see the [workflow](campaign-email-drafting.md) step 5) and leave
the box unchecked. Step 6's grep check still runs regardless — its job is confirming
no *local* image reference survived anywhere in the email, which a curl check on
already-resolved CDN URLs can't tell you.

### The trap this creates — and the check that catches it

A local relative path renders **for you and nobody else**. It will look perfect in your
browser while being completely broken for every recipient. So a clean local preview is
*not* evidence the email is ready, and it's specifically not evidence that "I didn't need
IT to upload anything."

The only thing that settles it is checking the file's actual markup for local-path
patterns — a local relative path is either present in the text or it isn't, which is
exactly what step 6's grep in the [workflow](campaign-email-drafting.md) catches, deterministically, every time. No
rendering, no eyeballing, and no dependency on how any particular previewer chooses to
sandbox external resources (SharePoint's inline HTML preview, for one, can show a
broken image for a URL that's genuinely live — an unreliable substitute for the grep,
not a stronger version of it).

While drafting, just keep `campaign.md`'s asset tables populated with every file the draft
references, unchecked. Once the draft looks done, **step 7 in the [workflow](campaign-email-drafting.md)** (with the full
procedure in `publishing-and-sending.md`) verifies each one against the CDN
and runs the rewrite — don't tick a box yourself before that happens.
