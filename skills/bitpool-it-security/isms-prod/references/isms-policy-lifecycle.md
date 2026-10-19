# ISMS Policy Lifecycle

Bitpool's controlled ISO 27001 policies move through two stages, each owned by its own skill.
**Markdown is the source of truth** for policy content; the controlled `.docx` is the published
artifact, produced at promotion.

### Stage 1 — Draft

`/isms-draft` authors and edits Markdown drafts in:

```
security-documentation\ISMS\ISMS - Draft\
security-documentation\ISMS\ISMS - Draft (New)\
```

Both are live draft areas. Wherever this file writes `ISMS - Draft/` in a path — while drafting and
at promotion — read it as whichever of the two folders holds the draft.

Never promotes. Never touches the `isms` production repo.

### Stage 2 — Promote

`/isms-prod` promotes an approved draft into:

```
isms\<Policy Name>.md + .docx
```

Writes and commits **only** in the `isms` repo. The commit message is the audit record.

> **Important**
> No other skill authors or edits policy content. `/bitpool-docs`, `/drive-iso27001` and
> `/create-drata-test` all redirect here if a request turns out to be about a policy.
> `security-documentation/policies/` is a pointer folder — never real policy content.


## Drafting

### Scope and boundaries

- ✅ Create and edit `<policy>.md` drafts in `ISMS - Draft/` or `ISMS - Draft (New)/`.
- ✅ Seed a brand-new draft from an existing `.docx` (one-time, via `docx2txt`).
- ⛔ Never write to the **`isms`** prod repo — promotion is `/isms-prod`.
- ⛔ Never edit production policies or claim a draft is "live".
- ⛔ Never invent policy or control content. Mark `<!-- TODO: needs owner input -->`.

### Mode A — Seed a draft from a `.docx`

When a policy `.docx` is present in `ISMS - Draft/` and has no `.md` yet:

## Extract the text

```bash
docx2txt "ISMS - Draft/<Policy>.docx" - > "ISMS - Draft/<policy-slug>.md.tmp"
```

`docx2txt <file> -` writes to stdout. **It is lossy** — plain text only. Images, tables,
headers/footers and styling do not survive.

## Reshape into clean Markdown

Proper headings, and **prepend the policy front-matter** (template below). Reshape only: the body
is the controlled wording as it stands, so don't rewrite it to the ISMS Policy writing profile in the
same step — list what the profile would change and let the user decide. The durability check covers
only the front matter you wrote; the seeded body gets the list of what the profile would change
instead.

## Flag what docx2txt dropped

Insert `<!-- TODO: image — re-add at promotion -->` where images belong, and
rebuild any tables by hand from the source `.docx` — open it to read.

## Save and clean up

Remove the `.md.tmp`. Save as `ISMS - Draft/<policy-slug>.md`.

## Delete extracted images that duplicate assets/common/

A seed that extracts media — `_tools/docx-to-md.sh` writes every embedded image to
`assets/<policy-slug>/media/`; `docx2txt` extracts none — also pulls out the cover artwork every
policy shares. The cover comes from `Templates/policy-template.docx` at build time, so those copies
are never referenced and only duplicate `assets/common/`.

Compare each extracted image with `assets/common/` **by decoded pixels, not by bytes** — a re-saved
image can differ byte for byte and still be the same picture — and delete every match. This needs
Pillow in the WSL `python3` (`python3 -c "import PIL"`):

```bash
wsl -e bash -lc 'cd "/mnt/c/BitpoolDev/Github-Bitpool/security-documentation/ISMS/ISMS - Draft/assets" && python3 - <<EOF
import glob
from PIL import Image
def px(p):
    try:
        im = Image.open(p).convert("RGBA")
    except Exception:
        return None  # .emf and other formats Pillow cannot decode: never a match, keep them
    return im.size, im.tobytes()
common = {k: c for c in glob.glob("common/*") if (k := px(c))}
for f in sorted(glob.glob("<policy-slug>/media/*")):
    k = px(f)
    if k and k in common:
        print(f, "duplicates", common[k])
EOF'
```

Delete each file it lists. Where the body links to a listed file, repoint the link to its
`assets/common/` twin instead of leaving it broken. Everything else stays in
`assets/<policy-slug>/`. Remove `assets/<policy-slug>/` if nothing is left in it.

## Retire the draft .docx

Where its controlled copy already lives in the `isms` repo, confirm with the user, then move or
remove the draft `.docx` — don't leave a duplicate in the draft area. Check first: a draft may have
no controlled copy yet (drafts in `ISMS - Draft (New)/` may have none), and then its `.docx` is not a
duplicate — keep it unless the user decides otherwise. **Ask before deleting.**

### Mode B — Author or edit a draft

Create or edit `ISMS - Draft/<policy-slug>.md` directly. Keep the Markdown clean and atomic so
`git diff` is readable — that diff is the working change history.

**What the text says follows `/bitpool-writing-standard`'s ISMS Policy profile** (section
`bitpool-general`), body and front matter both. Load it before writing policy text; `/isms-draft`'s
load-bearing rules say when the durability check is shown. This file covers structure and workflow
only.

Reference images as files, stored in one of two places under the draft folder's `assets/`:

- **Shared images** — used by more than one draft, such as the Bitpool logo and the cover
  artwork — live once in `ISMS - Draft/assets/common/`. An image a second draft needs belongs
  there, with both drafts pointing at it.
- **Images unique to one draft** stay in `ISMS - Draft/assets/<policy-slug>/`.

```markdown
![alt text](assets/common/<description>.png)
![alt text](assets/<policy-slug>/<slug>-NN-<description>.png)
```

At promotion pandoc resolves them relative to the `.md`, so keep them with the draft. Before adding
an image to `assets/<policy-slug>/`, check `assets/common/` for it. For a draft in
`ISMS - Draft (New)/`, ask where a shared image should live before copying one in — never create a
second `common/` folder silently.

### Draft front-matter template

**Exactly four cover keys, in this order, in every draft.** They are the four the Word cover
renders — `Templates/policy-template.docx` contains only `{{title}}`, `{{subtitle}}`, `{{date}}`
and `Document Owner: {{owner}}`, and `build_policy.py` fills them from these keys. Never add a
cover key beyond these four.

```yaml
---
title: "<Policy Name>"
subtitle: "<one sentence describing what the policy covers — this renders on the cover>"
date: "<D Month YYYY, e.g. 25 August 2026>"
owner: "<owning role, e.g. Head of Information Security>"
---
```

**Three optional build keys are also real**, and may follow the four. `build_policy.py` reads each
one, and a document carries it only when its layout needs it — for example, the Risk Assessment
Policy carries `risk_matrix_colours`. **Never strip one a draft already carries**: removing it
silently changes the built `.docx`, and "exactly four keys" does not mean these. Never add one to a
draft that does not need it.

| Key | What it does in the build | Value |
|---|---|---|
| `trim_cover_spacing` | Removes surplus empty spacer lines above a long, wrapping cover title | `true` keeps two; an integer keeps that many |
| `subheading_shading` | Shades table sub-heading rows (left-only or merged full-width rows) in a lighter tint | `true` |
| `risk_matrix_colours` | Shades the first cell of each data row, in every table, on the risk heat scale — a cell carrying a `(1)`–`(5)` level, or reading Low, Medium, High or Critical | `true` |

The build reads no other front-matter key, so any other key is ignored rather than rendered.

`owner` names the owning **role**, exactly as Bitpool's RACI tables name it — never a person. Who
owns the policy is a fact with one home, the policy's owner in Drata; a name on the cover is a second
copy that goes false at the next change of holder, and correcting it is a controlled-document
revision. If the owning role is not clear, ask. Existing drafts that still name a person convert to
the role in a batch the user confirms, per `/isms-draft` — never as a side-effect of another edit.
Before converting one, confirm that the policy's owner in Drata holds the named person, and where it
is blank have it filled first: a conversion never removes the only record of who owns the policy
(ISMS Policy profile §3.2).

> **Corrected 2026-08-25.** This template previously prescribed an 18-key schema — `description`,
> `audience`, `last_reviewed`, `status`, `doc_type`, `sources`, `keywords`, `iso27001_controls`,
> `drata_controls`, `policy_version`, `policy_owner`, `policy_approved_by`, `policy_effective_date`,
> `policy_review_cycle`. **It had never been used and it produced a broken document.** It carries no
> `subtitle`, `date` or `owner`, which are three of the four fields the cover renders, so following
> it yielded a `.docx` with the title filled and the subtitle, date and owner blank. Verified:
> `git log -S "policy_version"` over the draft folder returns zero commits, and none of the 31
> drafts used any key from that schema. The optional build keys in the table above are a separate
> thing: real, read by the build, and carried only by the documents that need them — but not part
> of the standard template.

The body carries **no** title heading — the cover supplies it. Start at the first real section.
House style uses `#` for top-level sections and `##` for subsections, and **never numbers a
heading**: Word's Heading 1 style auto-numbers, so `# 1. Purpose` renders as "1. 1. Purpose".

```markdown
# Document Version Control

| Last Modified Date | Document Changes |
|---|---|
| <Month D, YYYY> | Initial development |

<!-- pagebreak -->

# <First section>

## <Subsection>

<!-- pagebreak -->

# Policy Compliance 
```

Each Version Control row is a **snapshot** of one change — its date, what changed and why, and the
originating `DCF` and clause. Be specific there; `/isms-prod` builds the commit message from it, and
the durability check does not apply to it.

Supported markers, all handled by `build_policy.py`: `<!-- pagebreak -->`, `<!-- toc -->` (a native
updatable Word TOC — opt-in, used by long documents), `<!-- landscape -->` / `<!-- portrait -->`,
and `<!-- header-rows... -->` before a table.

Note the **trailing space** after `# Policy Compliance` — every policy in the set has it; keep it so
diffs stay clean.

### Versioning drafts

Draft `.md` changes are versioned in the **`security-documentation`** repo. Offer to commit with a
clear message:

```
draft(<policy-slug>): <what you changed in this draft>
```

This is working history — lighter than the production change-log convention. The authoritative
change-log commit happens later, in the `isms` repo.

## Promotion

### Hard rules

> **Important**
> - ⛔ **Only promote on explicit request**, naming the policy. Never infer.
> - ⛔ **Git writes and commits happen ONLY in the `isms` repo.** Read the draft from
>   `security-documentation`; never commit there from the promotion path. The one write outside
>   git is the `CYB` ticket.
> - ⛔ **Never auto-commit.** Stage, present, and STOP for explicit approval — plus confirmation of
>   the Drata upload and named sign-off.
> - 🔧 **The `.docx` is BUILT, never hand-edited.** Run `md-to-docx.sh` from
>   `security-documentation/ISMS/_tools/`; the cover comes from the template, not from Word.
> - 🎫 **Every promotion raises a `CYB` Task** recording that the Drata upload is outstanding —
>   staged with the commit message, created only after the commit lands. The Privacy Policy
>   also gets a website-handoff sub-task.
> - 🚨 **Every promotion ends with the warning banner** — canonical copy at
>   `isms/_meta/policy-change-banner.md`.


## In the bulk promotion, read the policy queue first

The policy set is promoted in one bulk event, tracked by the policy queue: the standing `IRT` ticket
found with `project = IRT AND labels = PolicyQueue`, indexed on its page in `security-documentation`
(`compliance/isms-policy-queue.md`). Read the page file from disk in the main working copy, not the
published page, which lags until the user pushes. Its **Pending changes** table lists every row,
**Status** says which rows promote together, and **At promotion** lists the steps to take, in order.
Each row's detail — origin, clause and the change in full — is its comment on the ticket; the
ticket's description holds only the queue's standing rules.

After the bulk promotion, `/isms-prod` hands the page update to `/manage-drata-control` and says so
in the promotion report, naming the rows that landed — `/isms-prod` does not edit the queue page.
`/manage-drata-control` marks each landed row by writing
`promoted YYYY-MM-DD` after the policy name in its Policy cell, and updates the Status headline: on
the page, never in the ticket's description.

## Identify the pair

Map the draft slug to the production filename — `backup-policy.md` → `Backup Policy.md` /
`Backup Policy.docx`. Confirm the target with the user if ambiguous, including which draft folder
holds it (Stage 1). Read
`isms/_meta/commit-convention.md`.

## Diff draft vs production

```bash
git -C "C:\BitpoolDev\Github-Bitpool\isms" diff --no-index -- "<Policy>.md" "C:/BitpoolDev/Github-Bitpool/security-documentation/ISMS/ISMS - Draft/<policy-slug>.md"
```

Summarise the substantive changes. **List every image asset the change touches**, in
`assets/<policy-slug>/` and in the shared `assets/common/` — these must be re-linked in the `.docx`.
If the prod `.md` doesn't exist yet, this is a first publication; say so.

## Draft the change-log commit message

Per `isms/_meta/commit-convention.md`:

```
policy(<slug>): v<old> → v<new> — <one-line summary>

What changed:
- <concrete change>

Rationale:
<why>

ISO 27001: <clauses>  |  Annex A: <controls>
Drata: <DCF ids>
Approved by: <name/role>          (effective <YYYY-MM-DD>)
Drata uploaded: <yes/no>
Author: <name>
```

Present this for review. Ask for the approver name, effective date, and version bump if not
already known.

## Update the production .md

Write the approved draft content into `isms/<Policy>.md`, updating the `date` front-matter field to
the effective date. The other three keys — `title`, `subtitle`, `owner` — carry over unchanged
unless the change alters them.

## Build the .docx — the scripted toolchain

**Corrected 2026-08-25.** This step used to say the `.docx` was updated by a human in Word via the
Claude add-in, and that "the CLI never edits the `.docx`". **That is wrong and was blocking the
tooling that actually produces every published policy.** Verified by comparing the built output
against the artefacts already in the `isms` repo: their style distribution, page headers and field
structure are identical, which means the production `.docx` set was generated by this toolchain,
not by the add-in.

The toolchain lives in `security-documentation/ISMS/_tools/` and is deterministic — pandoc plus
`docxtpl`/`docxcompose`, no AI in the conversion. Run it in WSL:

```bash
wsl -e bash -lc 'cd "/mnt/c/BitpoolDev/Github-Bitpool/security-documentation/ISMS/_tools" && bash md-to-docx.sh --out-dir "/mnt/c/BitpoolDev/Github-Bitpool/isms" "../ISMS - Draft/<Policy Name>.md"'
```

The branded cover comes from `Templates/policy-template.docx`, whose `{{title}}`, `{{subtitle}}`,
`{{date}}` and `{{owner}}` placeholders are filled from the front-matter. Re-theming every policy
means editing that template and re-running the script — never hand-editing a `.docx`.

**Check the build output before continuing.** Confirm the cover fields are filled, and list any
images the change touched so they can be verified in the rendered document.

Two known characteristics of the output, both pre-existing and estate-wide — mention them, do not
"fix" them mid-promotion:

- **The TOC renders as a placeholder line** until the reader right-clicks and chooses *Update
  Field*. This is deliberate: `build_policy.py` explains that setting `w:updateFields` makes Word
  prompt "update fields?" on every open.
- **Body text renders in the pandoc default styles**, not the template's `Body` style, because
  pandoc emits style IDs (`FirstParagraph`, `Compact`, `BodyText`) that the template does not
  define. Every published policy shares this, so a new policy matches the set.

## Generate the public website extract — Privacy Policy only

**Only when the policy being promoted is the Privacy Policy.** The controlled document is the
master and `bitpool.com/privacy` is a downstream copy, so the promotion also produces the public
extract the website team publishes.

Write `security-documentation/ISMS/Website/Privacy Policy Website.md`, containing the public
sections **only** — everything from the first content section through `# Contact Us`, with the
`# Document Version Control` table, the `<!-- toc -->` / `<!-- pagebreak -->` markers and the
`# Policy Compliance` block all removed. Prepend a `# Privacy Policy` heading and a
`Last updated: <Month YYYY>` line derived from the front-matter `date`, because control `DCF-120`
requires the online notice to show when it was last updated.

The extract lives in `ISMS/Website/`, outside both draft folders, because it is a generated public
copy and not a draft: nothing in it is edited, and no draft sweep should pick it up as policy.

The file opens with this generated-file banner, so nobody edits the extract by hand. Its source of
truth is the controlled document in the `isms` repo — never a draft, and never a file beside the
extract:

```markdown
<!-- GENERATED FILE - DO NOT EDIT DIRECTLY.
     Source of truth: "Privacy Policy.md" in the isms repo (the controlled ISMS document).
     Regenerate with /isms-prod when the controlled policy changes.
     This extract is the public web copy for bitpool.com/privacy: the controlled
     document minus its Document Version Control table and Policy Compliance section. -->
```

It is the artefact attached to the CYB website-handoff sub-task below.

## Retire a superseded supporting document — only when the change replaces one

`isms/Documents/` holds the supporting documents that are not policies — registers, templates,
playbooks. When a promotion replaces one, retire it in the same promotion, so two controlled
versions of the same content never sit side by side. It is replaced when:

- **a promoted draft supersedes it** — for example the Incident Response Playbook, now drafted as a
  document of its own and promoted with the policies; or
- **its content moves to the wiki** — a register or reference page the wiki now holds.

Remove it with `git rm`, staged with the rest of the promotion, so the removal lands in the same
promotion commit. Git history keeps the file, so nothing is lost from the record.

```bash
git -C "C:\BitpoolDev\Github-Bitpool\isms" rm "Documents/<file>"
```

Record it in that commit's message in this shape, where `<new home>` names what replaces it — the
promoted document's filename, or the wiki page's title:

```
doc(<slug>): retire — superseded by <new home>
```

When the retirement rides in the replacing document's own promotion commit, this line goes in as a
`What changed:` bullet. When nothing else is promoted with it — content that moved to the wiki — it
is the commit's subject line.

The canonical commit format is `isms/_meta/commit-convention.md`, and it does not carry this shape
yet. Add it there in the IRT-17 bulk promotion (the policy queue ticket in Jira `IRT`), which is its
first use; until then this section is the only statement of it.

## Update the wiki copies of controlled tables

Two controlled documents hold a table that the Bitpool Private Wiki also carries as a labelled copy.
When a promotion changes one of these tables, the copy is updated in the same session, and its
"Copied on" line then names the promoted version. The controlled document governs wherever the two
differ.

| Controlled document | Table | Wiki copy in `security-documentation` |
|---|---|---|
| Risk Assessment Policy | Risk Score Matrix | `risk-management/risk-matrix.md` |
| Business Continuity Plan | RTO Objective table and priority | `compliance/rto-rpo-objectives.md`, *Business-function RTOs* |

`/isms-prod` never writes to `security-documentation` (rule 2), so hand the copy update to
`/bitpool-docs` and say so in the promotion report.

## Drata and approval

Prompt the user to upload the updated policy to the **Drata Policy Center**, and to capture the
**named approver** (e.g. CISO / MD) and effective date. Record the outcome in the commit message.

## Stage, then STOP for approval

```bash
git -C "C:\BitpoolDev\Github-Bitpool\isms" add "<Policy>.md" "<Policy>.docx"
```

The `isms` repo keeps no `assets/` folder: every image, shared ones in `assets/common/` included,
is embedded in the built `.docx`. Include any `git rm` from the retirement step above.

```bash
git -C "C:\BitpoolDev\Github-Bitpool\isms" status
```

**Do not commit yet.** Ask the user to confirm: draft approved, `.docx` updated, Drata uploaded,
approver captured.

## Commit — only after explicit approval

```bash
git -C "C:\BitpoolDev\Github-Bitpool\isms" commit -m "<message>"
```

Confirm with `git log -p -1 -- "<Policy>.md"` that the change trail is readable.

## Raise the CYB ticket

**The commit is not the end of the promotion.** The Drata Policy Center upload outlives the session,
and a prompt in a chat window is not a record that it is outstanding. So every promoted policy gets
a Jira **Task** in `CYB`.

**Project:** `CYB` — Cyber Security Recurring Tasks, project id `13173`
**Issue types:** `Task` = `10948` · `Sub-task` = `10949`

### Ordering — this matters

1. **Draft the ticket text** and show it with the commit message at the *stage-and-STOP* step, so
   the user approves both together.
2. **Create the ticket only after the commit lands.** A ticket raised before the commit describes a
   promotion that may never have happened, and `CYB` is where real outstanding work lives.
3. Report the created key back — `CYB-nnn` — in the same response as the commit hash.

> ⛔ **Never invent a due date.** Propose one with your reasoning and get agreement, exactly as the
> approver name and effective date are agreed. A ticket with no due date is still better than one
> carrying a date nobody chose.

### The Task

```
Project ...... CYB (13173)          Issue type ... Task (10948)
Summary ...... Drata upload | <Policy Name> v<new>
Due date ..... <agreed with the user — never invented>
Labels ....... isms-promotion

Description:

<Policy Name> was promoted to the controlled isms production repo on <YYYY-MM-DD>.

| | |
|---|---|
| Version | <old> → <new> |
| Effective date | <YYYY-MM-DD> |
| Approved by | <name / role> |
| What changed | <one-line summary> |
| isms commit | <short hash> |

**Outstanding — this ticket is not done until both are true:**

- [ ] The updated `<Policy Name>.docx` is uploaded to the Drata Policy Center.
- [ ] The named approver and effective date are recorded against it in Drata.

The Markdown and .docx are already committed in the isms repo; that is the audit record of the
change. This ticket tracks only the Drata side, which the commit cannot do for you.
```

### The Privacy Policy sub-task

**Only when the policy being promoted is the Privacy Policy.** Bitpool decision, 2026-08-25:
the ISMS document is the **master** and `https://www.bitpool.com/privacy` is a **downstream copy**.
So a promotion that changes the ISMS text leaves the public page stale until someone publishes it.

Create this as a `Sub-task` (`10949`) with the Task above as its parent:

```
Project ...... CYB (13173)          Issue type ... Sub-task (10949)
Parent ....... <the Task created above>
Summary ...... Website handoff | publish Privacy Policy v<new> to bitpool.com/privacy
Due date ..... <agreed with the user — never invented>

Description:

The Privacy Policy was promoted on <YYYY-MM-DD>. The ISMS document is the master; the public
page is a downstream copy and is now out of date.

Hand the new content to the website team for publication at https://www.bitpool.com/privacy.

Source of truth: `C:\BitpoolDev\Github-Bitpool\isms\Privacy Policy.md` (isms commit <short hash>)

**The published page must carry a visible "Last updated" date.** Control DCF-120 requires the online
privacy notice to show when it was last updated, and requires customers to be notified of changes
and of the nature of those changes — posting alone does not satisfy the second part.

- [ ] Content handed to the website team
- [ ] Published at bitpool.com/privacy
- [ ] Published page shows the new "Last updated" date
- [ ] Customer notification of the change considered and actioned or explicitly ruled out
```

> **Only the Privacy Policy gets this sub-task.** No other ISMS policy has a public counterpart.
> If that changes, add the policy here rather than inferring it from the policy name at run time.

## End with the warning banner

Append the filled banner from `isms/_meta/policy-change-banner.md` as the **final element** of the
response. One banner, all touched policies listed.

### The banner

```markdown
---

> # 🚨🚨 CONTROLLED POLICY CHANGED 🚨🚨
>
> ## ⚠️ A policy in the `isms` production repo was created or modified. This is a change to a controlled ISO 27001 ISMS document. ⚠️
>
> | | |
> |---|---|
> | 📄 **Policy** | **[POLICY NAME]** |
> | 📁 **Files** | `[Policy].md` + `[Policy].docx` (isms repo) |
> | 🔖 **Version** | `[old]` → **`[new]`** |
> | 📅 **Effective date** | **[YYYY-MM-DD]** |
> | ✏️ **What changed** | [one-line summary] |
>
> ### ✅ Confirm these are done:
>
> - [ ] 📝 `.docx` rebuilt with `md-to-docx.sh` (cover fields filled from front-matter)
> - [ ] 🖼️ Touched images re-linked: [asset paths or "none"]
> - [ ] ☁️ Uploaded to the Drata Policy Center
> - [ ] ✍️ Named approver + effective date captured in the commit
> - [ ] 💾 `.md` + `.docx` committed together in the `isms` repo (the audit record)
>
> ### 🟥 If you did NOT intend to change a controlled policy, revert before pushing. 🟥
>
> _Policies change only on explicit request, through `/isms-prod`._

---
```

### What promotion must never do

- Never promote without an explicit, named request.
- Never commit in `security-documentation` — commit **only** in the `isms` repo.
- Never auto-commit or skip the approval gate.
- Never hand-edit a `.docx` in Word — rebuild it from the Markdown with `md-to-docx.sh`.
- Never re-theme by editing one document — edit `Templates/policy-template.docx` and rebuild.
- Never leave a superseded supporting document in `isms/Documents/` beside its replacement, and
  never remove one other than by `git rm` in a promotion commit.
- Never omit the warning banner.
- Never paste secrets or PII; reference locations only.
- Never create the `CYB` ticket before the commit lands — it would record a promotion that may not
  have happened.
- Never invent a due date for the `CYB` ticket; propose it and get agreement.
- Never raise the website-handoff sub-task for a policy other than the Privacy Policy — no
  other ISMS policy has a public counterpart.
- Never treat the `CYB` ticket as a substitute for the in-session Drata prompt, or the prompt as a
  substitute for the ticket. The prompt catches the upload while the user is here; the ticket
  catches it when they are not.
