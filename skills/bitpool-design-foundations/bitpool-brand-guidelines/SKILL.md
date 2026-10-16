---
name: bitpool-brand-guidelines
description: "Use when writing or naming anything as Bitpool. Brand voice."
version: 1.0.1
author: Bitpool, Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bitpool, brand, voice, copywriting, naming, positioning]
    category: bitpool
    related_skills: [bitpool-design-system, bitpool-search]
---

# Bitpool Brand Guidelines

The verbal and conceptual brand: what Bitpool is, how it sounds, and the rules that hold it together when it speaks. Full detail ships with this skill in `references/`. Read the file you need with `read_file`; nothing is fetched.

Visual rules (colours, typography, layout, components) live in `/bitpool-design-system`. Verbal tasks (writing, naming, positioning, copy) belong here. Most real tasks need both, so load the two together with `skill_view`.

## When to Use

- Writing, naming, positioning or speaking as Bitpool: marketing copy, blog and social posts, sales emails, pitch decks, press releases, product and feature names, taglines, customer comms, error messages, onboarding flows, internal memos, partner outreach, investor updates, recruitment copy.
- The user says "write something for Bitpool", or asks how Bitpool talks, what it sounds like, what's on-brand, or whether something fits the brand.

Don't use for:
- HTML, CSS, components or visual layout on their own: use `/bitpool-design-system`.
- A search bar or typeahead: use `/bitpool-search`.
- Internal engineering RFCs, support escalations or legal copy where plainness beats personality (see "When to depart" below).

## Procedure

1. **Read the five pillars below.** For a sentence, a button label or a post they may be all you need. Done when every pillar has been applied to the draft.
2. **Identify the context:** strategic, product, sales or technical. Done when you can name it in one word.
3. **Collect two or three concrete facts:** numbers, named industries, real outcomes. If you don't have them, ask with `clarify`. Never invent a number. Done when each claim in the draft traces to a fact the user gave or a reference file states.
4. **For anything longer** (a landing page, press release, pitch deck or email sequence), read the relevant reference file in full before drafting. Done when the whole file has been read, not skimmed.
5. **Draft** in the voice for that context.
6. **Audit against the pillars.** Is anything italic? Is anything vague that could be specific? Is any word from the banned list in `references/voice-and-tone.md` present? Does it sound like every other SaaS site? Done when every check comes back clean.
7. **Deliver.** In a terminal session, write longer pieces to a file with `write_file` and give the path. On a messaging platform, paste short copy inline, or send longer pieces as an attached `.md` file with `MEDIA:/absolute/path`.

## The five pillars

These are the load-bearing rules, summarised because every task needs them. Full elaboration and examples are in `references/voice-and-tone.md`.

### 1. Boldly practical, unapologetically real

**Bold**: confident and declarative, doesn't hedge. **Practical**: solves something concrete. **Unapologetic**: no corporate cushioning. **Real**: facts, not vibes. Specific numbers and named outcomes, not "transformation" or "synergy."

### 2. Confident, not preachy

State, don't sell.
- ❌ "Imagine if your building could think for itself."
- ✅ "Buildings that run themselves."

### 3. Bold cyan replaces italics, in writing too

For emphasis, **bold it** semantically and never use italics. Bold is a knife, not a brush: one or two load-bearing words per line, never a whole sentence.

### 4. Specific over vague, always

- ❌ "Lots of data" → ✅ "60 billion records"
- ❌ "Many customers" → ✅ "500+ buildings"

If you don't have a real number, don't invent one; write a different sentence.

### 5. Build, don't blah: verbs over jargon

Use: build, ship, run, watch, learn, act, save, fix, monitor, automate.
Avoid: leverage, empower, transform, revolutionize, synergize, seamless, best-in-class, cutting-edge, AI-powered.

## The brand in one paragraph

> Bitpool is the platform you never have to log in to. We collect 60 billion data points from buildings every year, learn what each building does, and quietly make it do it better. No dashboards to babysit. No alerts to triage. Just buildings that run themselves. Boldly **practical** and unapologetically **real** — tomorrow's autonomy, **shipping today.**

## Naming: quick rule

**Bitpool** is one word, capital B, lowercase rest. Never BitPool, bitpool or BITPOOL outside the wordmark. Feature names are plain English, two ordinary words ("Building intelligence," not "BuildingIQ™"). Full trademark and legal usage rules are in `references/identity.md`.

## When to depart from this guideline

This is the marketing and strategic front-door voice. Internal docs, engineering RFCs, support escalations and legal copy read differently, and that's correct; don't force brand voice where plainness or precision matter more than personality. If unsure, ask the user what context the writing is for.

## Pitfalls

- **Invented numbers.** A specific-sounding made-up stat is worse than a plain sentence. Every number must come from the user or a reference file.
- **Italic emphasis creeping in.** Markdown `*word*` and `_word_` count as italics. Use `**word**`.
- **Bolding whole sentences.** That dilutes the emphasis; keep it to one or two words per line.
- **Skimming references.** The examples carry as much of the rule as the rule text does.

## Verification

- No italics anywhere in the output.
- No banned words (check against the full list in `references/voice-and-tone.md`).
- "Bitpool" is spelled exactly that way everywhere.
- Every number or named outcome traces to a source the user gave or a reference file.
- Read aloud, it sounds like a real person stating something true.

## Reference files

| File | Covers |
|---|---|
| `references/voice-and-tone.md` | Voice, tone, the banned-word list, tone by context (technical docs, sales email, support, social) |
| `references/identity.md` | Logo usage and clear space, naming rules, trademark usage, feature naming |
| `references/boilerplate.md` | Ready-to-use copy: taglines, 25/50/150-word descriptions, bios |
| `references/narrative.md` | Positioning, the founding story, how Bitpool talks about competitors |
