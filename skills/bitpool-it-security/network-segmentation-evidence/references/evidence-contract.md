# The evidence contract

What a run must produce, what each finding means, and what would resolve it. Read this at Step 3
before handing a pack to anyone.

## What a run produces

| Artefact | Purpose |
| --- | --- |
| `network-evidence-pack.html` | The auditor-facing artefact. Self-contained — **no external assets at all**, no webfont, no CDN, no remote anything |
| `adjacency.md` | The peering graph as Mermaid, fenced in Markdown so it renders in Drata's evidence viewer rather than showing as raw source |
| `dump/` | The raw JSON the pack was built from, with `_manifest.json` |

**All three go to Drata and nowhere else.** `adjacency.md` carries VPC names and CIDR ranges, which
the sensitivity rule (`placement-and-closure.md`) puts in the Drata-only column — it is evidence, not a wiki
diagram, and it is attached alongside the pack. Earlier wording here described it as being "for
embedding in a wiki page"; that predates the 2026-09-01 one-home decision and was wrong from the day
that decision was taken.

**The dump is not optional.** Without it the pack is an assertion; with it the pack is reproducible.
Attach both or neither — and **nothing here is committed to a documentation repo.**

## What makes the pack evidence rather than a document

Four properties, all mechanical:

1. **It is dated at collection**, not at file-save. The manifest records a UTC timestamp taken when
   the sweep started.
2. **It is attributed.** The caller ARN is recorded, so "who produced this" is answerable.
3. **It is hashed.** A SHA-256 digest over every file in the dump, printed in the page header.
4. **It is reproducible.** Same dump in, same page out.

Those four are what let a reviewer approve *this* artefact rather than approving a diagram whose
currency nobody can establish.

## The findings, and what resolves each

Findings are computed in `scripts/findings.py`. Severity is a function of the data, so a fixed
problem disappears on the next run without anyone remembering to delete a paragraph.

| Finding | Which control's words it tests | Severity logic | What resolves it |
| --- | --- | --- | --- |
| **Accounts neither surveyed nor excluded** | Bounds both claims | Always high | Add a local profile so the account is swept, or a written exclusion in `exclusions.json` with a reason and a named decision-maker. Both are acceptable; silence is not |
| **Default VPC carries live workloads** | `DCF-22` *"system boundaries"* — an undocumented segment | High per offending VPC | Migrate the workloads out and delete it, or record a decision that it stays and why |
| **Production and development peered** | `DCF-748` *"control traffic between them"* | High when both are routed | Remove the peering, or state the business need and narrow the path to it |
| **Data-store ports unrestricted by source** | `DCF-748` *"control traffic between them"* | High if any group sits on an internet-facing load balancer, otherwise medium | Narrow the source range to the segments that need it. On an internal load balancer this is not internet exposure — but it is not a boundary either |
| **Security groups are the sole enforcement layer** | `DCF-748` *"segmentation and/or other techniques"* | Low, and only when true of every live network | Nothing. One layer satisfies the control — the finding exists so the choice reads as deliberate |

### What was deliberately removed, and why

Narrowed 2026-09-01. These four were reported by the first version and are **not** to be
reintroduced:

| Removed | Belonged to |
| --- | --- |
| VPC flow-log coverage | Logging / `DCF-91` — monitoring, not segmentation |
| Unrestricted egress to the internet | `DCF-85` — a third control this review never assessed |
| VPCs outside the primary region | `DCF-20` asset inventory |
| Unused empty default VPCs | No control at all — it was labelled "housekeeping" |

Each is a real observation. None is evidence for these two controls, and an artefact that raises
them hands an auditor questions this review never answered. **Adding a check back is a scope
decision: name the phrase in `DCF-748` or `DCF-22` that it tests, or leave it out.**

## What to say when handing a pack over

The question is **not** what changed since the last run. At annual cadence that is close to
meaningless, and it is not what either control asks for — Step 3 (`placement-and-closure.md`) is the authority
here. For every finding, say which of the three positions it puts Bitpool in: already compliant,
a gap being accepted with a stated reason, or a gap being fixed. A pack handed over without that
has been generated, not reviewed.

## What this pack is not

- **Not a reference document.** Nobody should read it to learn the network. Point them at AWS.
- **Not a remediation plan.** It states position; `/manage-drata-control` decides treatment.
- **Not complete coverage of A.8.22.** It covers the AWS estate. The office guest/corporate network
  split and the OT/edge estate are separate, and the pack does not speak to either — the edge estate
  in particular must never be inferred from AWS evidence.
- **Not uploadable from here.** `update:evidence` is not granted on the Drata connection; the user
  attaches it.

## Scope boundaries worth stating in the artefact

An auditor tests scope claims first. The pack states its own boundary — every account from
Organizations, every enabled region — and names what it excludes and why. Keep that true:

- If an account is added to the Organization, it is swept or excluded. There is no third option.
- If an opt-in region is ever enabled, it enters the probe list automatically.
- If the estate grows beyond AWS, this pack does **not** silently cover it, and the hub page must
  say so.
