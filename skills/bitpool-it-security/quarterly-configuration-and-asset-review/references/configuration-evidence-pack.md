# The configuration evidence pack

Read before sub-task 8. The values-free published counterpart is
`security-documentation/compliance/configuration-baseline-drata-upload.md`.

## Why this is its own sub-task

It is **the only step in the cycle Hermes provably cannot perform.** Drata's evidence write scopes
are not granted on this connection — `Drata_updateEvidenceArtifacts` returns
`403 Missing required OAuth scope(s). Required one of: update:evidence` (code 12330), and Bitpool
enables only `read:evidence`. This is a capability limit, not a policy choice, so **never offer to
upload it.**

Folded into the diff it hides, and a quarter ends with the comparison done, assessed, and nothing in
Drata. That is the silent failure this separation exists to prevent.

## Building it

`scripts/build_evidence_pack.py`, normally through the cycle wrapper:

```bash
S=<this skill's scripts/ folder, as a WSL path>   # e.g. under $HERMES_HOME/skills/
wsl -e bash -lc "python3 $S/run_config_cycle.py pack YYYY-MM-DD"      # baseline defaults to RATIFIED

# the same thing, direct
wsl -e bash -lc "python3 $S/build_evidence_pack.py --folder <dumps>/YYYY-MM-DD --baseline <dumps>/<RATIFIED date> --out <dumps>/YYYY-MM-DD/evidence-pack.html"
```

One pack per cycle: **`evidence-pack.html`, written into that cycle's dated folder** in
`security-documentation-restricted/configuration-hardening/dumps/`. With `--baseline`, the builder
runs the differ itself through its CLI, so the pack's findings are the differ's findings and not a
second interpretation of them. The wrapper passes the `RATIFIED` folder as the baseline unless that
is the folder being packed; `--no-baseline` suppresses it. Without a baseline — cycle 1, a
ratification — there is nothing to compare against, and the pack evidences the baseline itself.

**A folder with no `collection-manifest.json` refuses to pack** (exit `2`) unless
`--allow-missing-manifest` is given; the wrapper and the builder both take it. No retained folder
needs it — see *The five mechanical properties* below.

## Order — non-negotiable

1. **The standard is correct and committed.** After a ratification, `ratify` has written the pages;
   the user reviews and commits them.
2. **The evidence is retained** — the dated folder, including the pack, committed to the repo by the
   user, then zipped whole and uploaded to Drata by the user.
3. **The user closes the ticket.**

A closed ticket over a standard that still disagrees with running configuration asserts a check
passed when it did not.

## The five mechanical properties

The first four match `/network-segmentation-evidence` exactly, so the two packs read as one system
to an auditor. The fifth, **Approved**, is this pack's own: a hardening standard is approved, and a
network capture is not. Each property has a named source, so none of them rests on the pack
builder's say-so.

| Property | What it means | Where it comes from |
|---|---|---|
| **Dated at collection** | The UTC instant the dump **started**, not when a file was saved | `collected_at_utc` in `collection-manifest.json`, captured once at run start — the same instant the folder's date derives from |
| **Attributed** | The identity that collected it | `collector` in the manifest — the signed-in account's `upn` (or `preferred_username`) and `oid`, decoded from the access token's claims. If it could not be determined it is `null`, and the pack must say *not recorded* — **never invent it** |
| **Hashed** | SHA-256 of **every input file**, printed in the pack header | Computed by the builder over every file it read. The manifest's own recorded hashes are the independent check — `run_config_cycle.py status` compares them |
| **Reproducible** | Identical inputs give **byte-identical** output | Every timestamp comes from the manifest, never the clock, and every list is sorted deterministically |
| **Approved** | Who approved the standard, when, at which version, and from which dump | The approval table of each hardening-standard page, written by `ratify` with a named approver, and checked against `dumps/RATIFIED` and the ratified folder's hashes — see below |

**The pack shows the approval**, because it is the document an auditor reads in Drata, and DCF-12
asks whether the standard is *approved*. Its header carries an *Approval of the standard* table read
from each hardening-standard page: Standard ID, Version, Approved by, Approved on, Effective from
and Ratified from. The wrapper passes the standards folder it resolved (`--standards-dir`). Each
page is hashed with the other inputs. `RATIFIED` alone is a pointer, not an approval, so when it is
set, every page must:

- record approving the dump it names, with `Ratified from` reading exactly
  `dumps/<date> (sha256 <16 hex>)`;
- cite that dump's raw sha256 as it hashes now;
- have a generated block that cites the `baseline-rows.json` sha256 that folder's rows still hash
  to, so rows edited after approval never read as approved.

Otherwise the pack raises a **high** finding for that platform: page missing or unreadable, no
approver, date or version, another folder or hash cited, the rows changed after approval, or the
wrong Standard ID. **A check that cannot be made is a finding, never a match.** If the ratified
folder's raw export or rows cannot be read, the page reads *does not match RATIFIED*. A page that
records an approval when there is no `RATIFIED` at all raises a **medium** finding. The page's
layout rule is ratify's own: the approval table may sit anywhere outside the frontmatter and the
generated markers.

The collector is the **person who signed in**, not an application. The `client_id` in the manifest
is the app registration the device-code flow ran through — by default Bitpool's own
`bitpool-intune-config-export` registration — so it says which tool was used, not who used it.

**A folder with no manifest cannot be dated or attributed at collection, so the builder refuses
it** unless `--allow-missing-manifest` is given. With the flag it still hashes every input, prints
every provenance field as `NOT RECORDED`, raises a high-severity finding saying so, and warns on
stderr. The only folder that ever needed the flag, 2026-09-24, predated the manifest and was
retired on 2026-09-28; every folder from 2026-09-27 on carries one. Such a pack evidences a
descriptive dump, never a ratified baseline. Never backfill a manifest to make the header look
complete.

Plus three hard rules:

- **Findings are computed**, from the data, every run. Never written by hand — so a resolved problem
  disappears on the next run without anyone remembering to delete a paragraph.
- **Zero network requests.** No external stylesheet, font, script or image; a complete
  `<!doctype html>`. **Grep the pack for `http` before handing it over** — the only permitted hit is
  the SVG namespace declaration.
- **Every value is HTML-escaped.** Policy names and setting values are untrusted text typed into a
  third-party portal. An unescaped one is an injection into the artefact an auditor opens.

```bash
wsl -e bash -lc 'grep -o "http[^\"<> ]*" "<dumps>/YYYY-MM-DD/evidence-pack.html" | sort | uniq -c'
```

The expected output is one line naming `http://www.w3.org/2000/svg`, or nothing at all.

## Where each output goes

Changed 2026-09-24, when the user decided the dumps live in the repo. Changed again 2026-09-28: the
whole folder, not only the pack, goes to Drata.

| Output | Destination | Why |
|---|---|---|
| The approved standards | `security-documentation-restricted/configuration-hardening/` | Authoring and version control |
| Raw dumps, setting definitions, collection manifest, generated rows, cycle record, diff reports, the pack | The same repo, `configuration-hardening/dumps/YYYY-MM-DD/`, committed by the user | **The retention store.** The previous cycle's dated folder is what the next cycle diffs against, so it has to live somewhere a run cannot overwrite it |
| The whole dated folder, zipped: the pack plus every file beside it | Drata, uploaded by the user as a new version of `Endpoint Configuration Hardening` | **The auditor disclosure channel.** It carries the renewal clock. The pack is what an auditor reads; the files beside it let the auditor recompute every hash the pack prints |

**The repo is where the evidence is kept; Drata holds a copy of each cycle's folder.** Until
2026-09-28 only the pack was uploaded. The reasoning was that the repo already held the dump and the
pack's hashes anchored it there, and the full folder carries more than the control needs: every app
deployment, the full source of the exported scripts, the unassigned policies, and the tenant and
group identifiers. The user weighed that and accepted it. Drata is a reviewed vendor that already
holds sensitive evidence, the pack already carries every enforced setting, and a count-only scan of
the 2026-09-27 dump found no secrets. The residual is that anyone with Drata access can read the
whole Intune configuration. **Check the exported scripts for embedded secrets before every
upload.** **The pack's hashes are what anchor it.** Its header carries the sha256 of every
input it read, current and baseline, and its section 06, *How this page was made*, gives the
`sha256sum` command that recomputes the input digest printed under *Inputs, hashed* from the files
in `dumps/`. Run against the committed folder, that command ties the pack to the exact dump it was
built from. The upload zip carries the dated folder, so the dump files' hashes can also be
recomputed from Drata's copy; the three standard pages the pack hashes are not in it.

The raw files are committed exactly as the exporter wrote them. `.gitattributes` marks them
`-text -diff`, so no line-ending normalisation can alter a byte and no 1.9 MB single-line JSON lands
in a `git diff`. The markdown records in a dated folder carry `type: Record` frontmatter and sit in a
directory the index generator skips; see `configuration-baseline.md`.

**What replaced physical separation.** The earlier design kept dumps out of the standards repo so a
commit to a standard would always be a human act. That guarantee is now mechanical: machine-written
content on a standard page is confined to the `GENERATED:START` / `GENERATED:END` markers, and only
`ratify`, with a named approver, writes there. Nothing `pack` does touches a standard page.

## The renewal tripwire

One bucket, **`Endpoint Configuration Hardening`** (Drata evidence 196, created 2026-09-28), with
`renewal_schedule_type: THREE_MONTHS`, attached to `DCF-12` and `DCF-171`. Each cycle adds a new version
to that bucket and archives the previous one. **Do not create a new bucket each quarter.** The
first renewal is due 2026-12-28.

Miss a cycle and the bucket walks `EXPIRING_SOON` then `EXPIRED`, dragging the mapped controls
not-ready. **That is the desired behaviour, not a side effect** — it is the only mechanism that makes
a skipped cycle visible without someone happening to notice.

This is Bitpool's first non-annual renewal, so it is a deliberate and visible choice.

## Control mapping

| Control | Attach | Why |
|---|---|---|
| `DCF-12` System Security Configuration and Hardening Standards | **Yes — primary** | Its own description covers cloud computing and endpoint devices; this pack evidences the endpoint half |
| `DCF-171` Documented Operating Procedures | **Yes** | The quarterly cycle **is** a documented operating procedure, reviewed more often than its annual floor. Currently ready with zero evidence, which an auditor reads as unsupported |
| `DCF-784` Software Composition Analysis | **No — deliberately** | Shares requirement `A.8.9` but is the SBOM obligation and carries its own evidence bucket. Attaching here misfiles it and masks the real gap |
| `DCF-20` Asset Inventory | **No** | The asset stream owns it, with its own artefact and clock |

**Volunteering an artefact against a control the review never assessed just exposes Bitpool
further.** If the cycle did not assess it, do not attach to it.

## The caveat to state every time

`DCF-12` is **already** `isReady: false`, and its only other evidence is a test-result bucket for
monitoring test `292` (AWS EC2 Instances IMDSv1 Disabled), which has `lastPassedAt: null` and has been
failing since 2024-11-27. That test gates the **AWS** plane and is carried separately on `IRT-75`
under risk `CR-14`.

**Attaching this pack will not flip `DCF-12` to ready.** Promise the tripwire and the endpoint
evidence — not a green tick.
