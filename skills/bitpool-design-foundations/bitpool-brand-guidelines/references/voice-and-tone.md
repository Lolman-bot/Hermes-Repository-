# Voice & Tone

The detailed guide. The SKILL.md sets the rules; this file shows them in operation across every kind of writing Bitpool does.

## The voice in one paragraph

Bitpool writes the way a senior engineer who has shipped the thing would talk about it. Confident because the thing works. Specific because numbers are how it earns trust. Brief because the audience is busy. Warm because there's a human on the other end. Past the point of selling — just stating what's true. Boldly practical and unapologetically real.

## The five voice qualities (and what they mean in writing)

### 1. Boldly practical
- Make claims. Don't hedge.
- Lead with the outcome, not the mechanism.
- ❌ "Our advanced machine-learning algorithms continuously analyse building telemetry to identify opportunities for energy optimisation."
- ✅ "We watch the building. It uses less power. That's the product."

### 2. Unapologetically real
- Specific names, specific places, specific numbers.
- Don't dress things up. Don't soften the punchline.
- ❌ "Our customers report significant operational improvements."
- ✅ "Westpac Place dropped energy spend 30% in year one."

### 3. Confident, not preachy
- State, don't sell. The brand doesn't need to convince.
- Don't ask the reader to imagine. Tell them what is.
- ❌ "Imagine a building that thinks for itself. Picture the savings. Imagine the impact."
- ✅ "Buildings that run themselves."

### 4. Casual without being cute
- Talk like a person, not a brand voice.
- No exclamation marks. No "Hey there 👋". No "rocketship". No "team Bitpool".
- ❌ "We're SO excited to share that we just shipped a HUGE update! 🚀"
- ✅ "New today: autonomous setpoint control. It's live. Here's what changed."

### 5. Build, don't blah
- Action verbs. Ordinary English. Subject, verb, object.
- Avoid abstract nouns ("solution," "platform," "ecosystem") when a verb will do.
- ❌ "Our solution provides comprehensive visibility across your portfolio."
- ✅ "See every building. Drill into any zone. Fix the broken thing."

## Voice modes by context

The DNA stays the same. The dial moves.

### Strategic / investor / pitch deck

Biggest, boldest, fewest words. Sentences of three or four words. Single ideas, massive type, lots of white space.

- "Buildings that run themselves."
- "Tomorrow's autonomy, **shipping today.**"
- "60 billion records. One platform."
- "$2.5M ARR by 2027."
- "Boldly **practical** & unapologetically **real.**"

Headlines stand alone. If they need a sub-line, it pays off the headline in one short sentence:

> **Buildings that run themselves.**
> No dashboards to babysit. No alerts to triage.

### Product marketing / website

Slightly more explanatory but still lean. Two-tier sentence structure per section: title-line sets the idea, payoff-line lands it.

> **One platform, every signal.**
> Bitpool ingests telemetry from any controller, any vendor, any vintage. The hard part — making them speak the same language — is already done.

Three-part pillar copy is common:

> **See.** Watch every signal across every building, in real time.
> **Know.** Patterns surface themselves. The platform learns what each building does.
> **Act.** Setpoints, schedules, alarms — adjusted automatically, day and night.

### Sales / outreach

Warmer, prospect-specific, but still doesn't oversell. References their context. Drops numbers. Doesn't open with "Hope you're well!"

> Hi Sarah,
> Saw Argyll has six new retail sites in the Highlands. Bitpool runs 40+ Highland sites already — Tesco, M&S, two of your direct neighbours on Princes Street. Worth 20 minutes?
> — Alex

Three short paragraphs maximum. One specific thing to do (a 20-min call, a link to a case study, a yes/no question).

### Customer comms / lifecycle email

Helpful, specific, no marketing inside the email. The customer is already a customer; they want service, not a pitch.

> Your March report is in. Three things worth a look:
> 1. Block F's chillers are running 18% over target. Already routed to your facilities lead.
> 2. The new tenant on Floor 12 doubled occupancy — we re-tuned the setpoints automatically last Tuesday.
> 3. Year-on-year savings now sitting at £142,400.
> Anything to dig into, reply and we'll set up a call.

No subject line emoji. No "I hope this finds you well." No "synergize."

### Technical documentation / API docs

Direct, precise, no brand voice — but still no jargon. Explain what the code does in plain English.

> `GET /v1/devices/{id}/state`
> Returns the latest known state for a device. State is updated every 60 seconds; if the device hasn't reported in the last 5 minutes, the response includes `stale: true`.

No "leverages our advanced API to enable real-time insights." Just what it does.

### In-product UI copy

Short. Helpful. Never preachy. Every piece of micro-copy answers one of three questions: where am I, what can I do here, what just happened.

- Empty state: "No alarms today. Quiet building."
- Error: "We couldn't reach this controller. Last seen 14 minutes ago. Retry."
- Success toast: "Saved. Setpoint change scheduled for 6am Monday."
- Confirmation: "This will turn off scheduled cooling for 12 hours. Proceed?"

### Internal / engineering / RFC

Plain English, technical precision, no brand voice. The audience is colleagues; they want the substance, not the polish.

> We're going to deprecate the `legacy_devices` table in Q3. Three reasons: it duplicates data in `devices`, the column types drift between writers, and nobody owns it. Migration plan in the doc below.

This is fine. Don't try to make it sound like marketing.

## Banned words and their replacements

These words signal off-brand voice and should be avoided in any customer-facing copy. The replacement column gives the spirit, not a literal swap — sometimes the right move is to delete the sentence entirely.

| Don't use | Instead |
|---|---|
| Leverage | Use |
| Empower | Help, let, give |
| Transform | Change, fix, replace |
| Revolutionize | Just delete the sentence |
| Synergize / synergy | Delete |
| Holistic | Complete, full, every |
| Robust (adjective) | Just say "works" |
| Best-in-class | Drop the claim; show the number |
| Cutting-edge | Drop |
| Mission-critical | Important; or just "the building" |
| End-to-end | From X to Y (name them) |
| Frictionless / seamless | Quiet, fast, automatic |
| Holistic | Every building, every signal (be concrete) |
| Paradigm shift | Delete |
| Disrupt | Delete |
| Unlock | Open, allow, free |
| Enable (verb form) | Let, help — or rewrite with active verb |
| Reimagine | Delete |
| Accelerate (as in "accelerate transformation") | Speed up — and name what's speeding up |
| AI-powered | Lead with outcome; don't lead with mechanism |
| Cloud-native | Almost never necessary |
| Future-proof | Delete |
| Game-changer | Delete |
| Pivot | Delete |
| Bandwidth (as in "no bandwidth") | Time, capacity |
| Circle back | Follow up |
| Touch base | Talk |
| Ecosystem | Network, partners, platform |
| Solution | Whatever it actually is — product, platform, fix, tool |
| Stakeholder | Person, team, customer, owner |
| Reach out | Email, call, message |
| At the end of the day | Delete |
| Move the needle | Make a difference (and quantify it) |
| Low-hanging fruit | Quick wins (and name them) |

## Before / after — sentences

### Hero headline
- ❌ "Empowering building owners to leverage data-driven insights for transformative outcomes."
- ✅ "Buildings that run themselves."

### Product description
- ❌ "Bitpool is a cutting-edge AI-powered platform that unlocks the full potential of your building data."
- ✅ "Bitpool watches every signal in every building, learns what each one does, and quietly makes it do it better."

### Stat callout
- ❌ "Our customers experience significant savings."
- ✅ "30% less energy at Westpac Place. Year one."

### Sales opener
- ❌ "Hope this finds you well! I'd love to set up a quick chat to explore how we can help you leverage your building data."
- ✅ "Bitpool already runs 40+ retail sites in your region. Worth 20 minutes?"

### Error message
- ❌ "An unexpected error has occurred. Please contact support if the issue persists."
- ✅ "We couldn't load this. Try refreshing. If it keeps happening, drop us a line."

### Empty state
- ❌ "It looks like you don't have any data yet. Get started by connecting a device!"
- ✅ "No devices connected yet. Add one to get started."

### CTA button
- ❌ "Discover more" / "Learn how"
- ✅ "See it work" / "Read the case study" / "Book the call"

### Investor pitch slide
- ❌ "Bitpool is positioned to disrupt the global building management ecosystem through its proprietary AI platform."
- ✅ "60 billion records. 500+ buildings. One platform. Buildings that run themselves."

## The two-tier sentence pattern

Bitpool's most common sentence shape is two-tier: title-line sets the idea, payoff-line lands it. Use it for section headers, pillar cards, axiom cards, hero/sub combos.

> **See every signal.**
> Across every building, every controller, every vendor.

> **No dashboards to babysit.**
> Bitpool watches so you don't have to.

> **Tomorrow's autonomy.**
> Shipping today.

The two lines should be close in length (visual rhythm) and the second should pay off the first — give it weight, make it land. If the payoff line is just a rephrase of the title line, cut one of them.

## Sentence rhythm and length

- Short sentences are the default. Three to ten words.
- A longer sentence is okay if it's earning the length — usually because it's listing three concrete things.
- Never start a paragraph with "Furthermore" or "Moreover."
- Two-word sentence fragments are fine and often the best move. "Quietly." "Shipping." "Done."
- Sentences ending in a number land hard. Use this.

## Punctuation conventions

- Sentence case in headlines (not Title Case, not ALL CAPS except eyebrows).
- Em dashes — used liberally — to add a clause or a beat.
- Ampersands (&) in headlines for compression. "**Practical** & **real.**"
- Periods at the end of bolded phrases pull weight. "Shipping today." not "Shipping today"
- No Oxford comma in marketing copy (matter of taste; consistent within a piece).
- No exclamation marks anywhere customer-facing. Ever.
- Single space after periods.
- No emoji in headlines, body copy, or any marketing surface. Emojis are fine in casual internal Slack but never in the brand voice.

## How to bold

The bold-cyan rule is the spine of the brand. Two principles:

**Bold the load-bearing word.** The one carrying the line's meaning. Usually a verb, a number, or the noun the sentence is about.

> "Bitpool is the platform you never have to **log in to.**"
> "We help **buildings** run themselves."
> "**60 billion** records. Every year."

**Never bold a whole sentence.** Bold is contrast; if everything is bold, nothing is. Two consecutive words can be bolded if they form a single locked phrase ("**shipping today.**", "**boldly practical**"). Three or more consecutive bolded words are almost always wrong.

In plain text (where the visual bold-cyan colouring isn't available) use `**markdown bold**` for the same job. The semantic emphasis carries; the colour is a visual amplifier.

## What to do when you have no specifics

The brand demands specifics — numbers, named buildings, named industries. What if you don't have them?

The answer is never to make them up. Three legitimate moves:

1. **Use the strategic numbers you already have.** "60 billion records," "500+ buildings," "$2.5M ARR by 2027" are all approved company-level figures. Use these.
2. **Use an unnamed but real instance.** "A 40-storey commercial tower in central Sydney." "A retail chain with 80 stores across the UK." These are anonymized but concrete.
3. **Rewrite without the specific.** If you have nothing real, write a shorter sentence that doesn't claim anything you can't back up. "Bitpool runs in real buildings. Quietly." beats "Bitpool delivers significant energy savings for our customers."

A short true sentence always beats a long vague one.

## Final read-aloud test

Before anything goes out: read it aloud.

- Does it sound like a real person stating something true?
- Does it have at least one specific noun or number?
- Could it be on any SaaS company's website, or is it unmistakably Bitpool?
- Did you avoid every word on the banned list?
- Are the emphases doing real work, or is it just "more brand"?

If all five answer yes — confident, specific, ours, clean, earned — ship it.
