# Intake — steps 2 to 4

Getting everything the deck needs, asking as little as possible.

## Step 2 — the three things always asked first

Ask these together, in one message, before reading anything:

1. **Deck title** — e.g. "Building Dashboards in Bitpool Cloud". Goes in the page title, the cover and the
   navigator.
2. **Who it's for** — staff or customers, and roughly how familiar they already are. This sets the
   tone: staff decks can name internal tools and people; customer decks never do.
3. **Top-corner label** — the short text shown top-right on every slide with the pulse dot, e.g.
   "Dashboards · Bitpool Cloud". Suggest one built from the title if they're unsure.

The footer text defaults to "<short title> Training" (e.g. "Bitpool Cloud Training"). Say what you'll
use; don't ask separately.

## Step 3 — read everything already given

Read every file in full before saying anything about the content. Use the matching skill:

| They give you | How to read it |
|---|---|
| PowerPoint (.pptx) | The `powerpoint` skill (`skill_view`). Take each slide's small label, title, body text, card and step text, and every image. Note which numbers sit on top of a screenshot — those become pins (see `screenshot-pins.md`). |
| Word (.docx) | The `docx` skill (`skill_view`). Headings become sections and slide titles; lists become steps or card bullets. |
| PDF | The `pdf` skill (`skill_view`). Same as Word. |
| Pasted notes or an outline | Read as-is. Headings or blank-line gaps usually mark slides. |
| Images and screenshots | Look at each one with `vision_analyze`. Say back what it shows ("Bitpool Cloud Dashboards page, Add Widget modal"). |
| Screen recordings (.mp4/.webm) | Accept them (you can't watch them; ask what each shows only if it isn't clear from the name or context) — they go on a slide like a screenshot. **Never ask for videos;** they're optional. |

Then say back, briefly, what you found: how many slides or sections, which images go with which
part, and anything you can't place.

Copy images and videos into a `media/` folder next to the draft deck, named by slide
(`media/s07-add-widget.png`). Keep originals untouched.

## Step 4 — ask only for what's missing

Check the content against what each planned section needs. Missing means:

- A section with a title but no content.
- A numbered step that says "click X" with no screenshot to show X.
- An image with no clear slide to go on (ask where it belongs, or whether to drop it).
- Anything you'd otherwise have to invent: a figure, a name, a URL, a price.

Ask for all the gaps in one message. If nothing is missing, say so and move on. Never ask again for
something already supplied, and never ask for videos.

## Sensitive content

Screenshots often show chat histories, names, emails or customer data. Point out anything
customer-facing decks shouldn't show and offer to blur or crop it (Pillow) before it goes in. For
customer decks this check is mandatory.
