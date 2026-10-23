# Examples intake (steps 1 and 2)

The examples are how Hermes learns the job. Two ends: what the work looks like **when it arrives**
(inputs) and what it looks like **when it's finished** (outputs). For each end, the person can give
real files — up to five — or **describe it in words**. Files are better, so ask for them first, but
a good description is enough to go on.

## How to ask

Ask for the inputs first, in plain words, one message, and offer both ways in:

> "Let's start with what the work looks like when it lands on your desk. Can you upload up to five
> real examples? PDFs, spreadsheets, exports, screenshots, an email — whatever you actually start
> with. If you haven't got one to hand, just describe it in words instead."

Then, once those are read or described, the outputs:

> "Now the other end. Can you upload up to five examples of the finished work — what you'd hand
> over or send when the job's done? Or describe it if there's no file to share."

Pair them where you can: "Is this report the finished version of that spreadsheet?" A matched
input/output pair is worth more than five unrelated files, because it shows the change in between.

A person can mix the two: files for one end and a description for the other, or a file plus a
description of how other jobs differ from it.

## How many is enough

- **Minimum: each end covered once** — one input (a file or a description) and one output (a file
  or a description). Load-bearing rule 1. Don't move on without both.
- **Two or three examples of each is the sweet spot.** Enough to see what changes from one job to the
  next and what stays the same.
- **More than five:** ask them to pick the five most typical, plus one awkward one if they have it.
  The awkward case is where a skill most often goes wrong.

## Reading each file

Read every example in full before saying anything about it. Load the matching bundled skill with
`skill_view` for the file type — `pdf` for PDFs, `xlsx` for spreadsheets and CSVs, `docx` for
Word, `powerpoint` for slides — `read_file` for plain text, and `vision_analyze` for screenshots
and photos. Files sent on a messaging app arrive as attachments Hermes saves locally; read those
paths the same way. Then say back, in a sentence or two per file, what you see: "This is a
monthly energy export — one row per meter per day, kWh in column D."

Note, for writing the skill later:

- **What's the same every time** — the shape, the columns, the headings, the layout. This becomes
  the skill's route and its templates.
- **What changes every time** — the client, the dates, the figures. This becomes what the skill
  asks for or reads in.
- **What must match exactly** — a branded template, a fixed layout, a logo. This becomes an asset,
  copied byte for byte (load-bearing rule 7).

## Taking a description instead of a file

A description replaces a file only when it answers the same questions a file would. Ask until each
one has a real answer — "a spreadsheet" or "a report" alone isn't enough to build on.

**For an input, ask:**

1. **What is it?** "The monthly meter export from the portal", "a customer's email asking for a
   quote".
2. **What format?** PDF, spreadsheet, export, email, form, notes, photos.
3. **Where does it come from?** Who sends it, or which system it's pulled from.
4. **What's in it?** The columns, fields, sections or pieces of information that matter, in the
   person's words.
5. **What changes from one job to the next?** The client, the dates, the number of rows, missing
   bits.

**For an output, ask the same five, plus:**

6. **How is it laid out?** The sections, pages or columns, in order.
7. **What must look the same every time?** A branded template, a logo, fixed wording, a house
   format.
8. **Who gets it, and how?** Emailed, uploaded, printed, published.

Invite a pasted sample where it's cheap — a few rows, a heading list, one paragraph — with real
names and figures swapped out. A short paste beats a long description.

Then say the description back in a sentence or two, exactly as you would for a file — "So the
input is a CSV export from the portal, one row per meter per day, and the number of meters varies"
— and get a yes before moving on.

**One thing a description can't replace:** if the finished work has to match a branded template,
logo or exact layout, ask for that file. It goes into the skill's `assets/` byte for byte
(load-bearing rule 7), and it can't be recreated from words. If they can't supply it, say plainly
that the skill will describe the layout rather than reproduce it exactly, and note that in the
skill.

When a whole end was described rather than shown, say so at step 6, when the full skill is shown,
and suggest they try the skill on a real job before publishing it. A skill built from descriptions
is only as right as the description.

## Sensitive content in examples

Examples are often real client work. Before anything from an example goes into the skill itself,
ask: "This has client names and real figures in it. I'll use it to understand the job, but I won't
copy those into the skill. Is there a version with the details blanked out you'd rather I keep as
a template?" Never ship real customer data, names or figures in the skill. The same goes for
anything pasted into a description.

## When someone can neither share nor describe the work

If they can't share a file and can't answer the description questions for an end — they don't yet
know what the input or the finished work looks like — this isn't the right route. Offer
`/create-new-skill`'s interview route instead, which builds from a conversation. Don't invent example
files or descriptions to fill the gap.
