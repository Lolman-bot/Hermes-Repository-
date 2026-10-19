# Placing the output, the sensitivity rule, and closing the loop

Relocated from the skill's main file: the detail behind Steps 3-5 of the Procedure.

## Positioning each finding (Step 3)

The pack computes its own findings. The question is **not** "what changed since last time" — at
annual cadence that is close to meaningless, and it is not what either control asks for. The
question is **whether the position each finding describes is a defensible one.**

For every finding, work out which of these three it is. They are very different positions:

| | Situation | Right artefact | Where |
|---|---|---|---|
| **A** | There is a genuine business need, and the traffic is scoped to it | **Recorded scoping rationale.** The control is *met* — scope was determined by risk, which is what DCF-748 asks for | `Rationale` column of `compliance/drata-controls-register.md`, via `/bitpool-docs` |
| **B** | The need is genuine but the traffic is wider than it requires | **Risk entry with a treatment plan** and an accepted residual | Drata risk register, via `/manage-drata-control` |
| **C** | Nobody can state why the path exists | **A real gap.** Remediate, or re-plan it honestly | Engineering work; where a commitment is made it gets an `IRT` ticket — created **undated**, labelled and estimated. Raise it via `/manage-drata-control` |

**You usually cannot tell from the data which one applies — ask.** A peering connection tagged
"Development to Production" tells you it exists, not why. Establishing the business need is a
conversation with whoever owns the infrastructure, and it is the actual next step after a run.

**Do not default to writing a risk.** A risk entry asserts an unresolved exposure. Where the path
is justified and scoped, recording that is the *stronger* position — and a register padded with
"accepted risks" that are really design decisions dilutes the entries that matter.

See `evidence-contract.md` (alongside this file) for what each finding means and what would resolve it.

## Placing the output (Step 4)

A run produces three artefacts — the pack, `adjacency.md` and the zipped dump — and all three go
to one place.

**Drata's Evidence Library — the primary home.** The pack is attached against `DCF-748` and
`DCF-22` with an **annual renewal schema**. That is what makes the artefact self-policing: when it
lapses, Drata marks the control not ready on its own. A calendar reminder cannot do that, because
it chases the task rather than the artefact.

**This skill cannot perform the upload.** `update:evidence` is not granted on the Drata MCP
connection — `Drata_updateEvidenceArtifacts` returns `403 Missing required OAuth scope(s)`. This is
a real capability limit, not a policy choice, so say so plainly and never offer to do it. The user
attaches it.

**Zip the dump and attach it alongside, together with `adjacency.md`.** The dump is what makes the
artefact reproducible; without it the pack is an assertion. `adjacency.md` carries VPC names and
CIDR ranges, so it is Drata-only like the rest — it is evidence, not a wiki diagram, whatever
earlier wording in the generator and the evidence contract implied. All three go to Drata, so
there is exactly one home.

**Nothing is committed to a documentation repo.** Earlier versions of this skill archived packs in
`security-documentation-restricted`. That was removed on 2026-09-01: at annual cadence with no
change-diff step, the archive earned nothing that Drata does not already provide, and it put
internal addressing and exposure detail in a second place. One home, and it is the one the auditor
already opens.

## The sensitivity rule — what you write *about* the pack

This is the easy one to get wrong, and it was got wrong on 2026-09-01: the pack was placed correctly
while notes summarising it — in `it-documentation` and `security-documentation` — carried VPC IDs,
a peering connection ID, an account number, internal CIDR ranges and the line *"security groups
allow `0.0.0.0/0` on PostgreSQL and Redis ports"*. Putting the artefact behind the right door and
then describing its contents on the way out defeats the point.

**Findings belong in the wiki. Identifiers belong only in Drata.** The split:

| Wiki / documentation repos — keep | Drata only |
|---|---|
| "Production and development are peered, routed both ways" | The `pcx-` connection ID |
| "A default VPC in the production account carries live workloads" | The `vpc-` ID and the account number |
| "Data-store security groups are unrestricted at the source-address level" | `0.0.0.0/0` on named ports, and the `sg-` IDs |
| "Separate production, development and deployments VPCs" | Their CIDR ranges |
| "Flow logs cover production only" | — |

The test: **an identifier that adds nothing for the reader but everything for an attacker belongs
only in Drata.** Nobody in IT needs a peering connection ID from a summary page; they need to
know the peering exists. Grep any page you write for `vpc-`, `pcx-`, `sg-`, `subnet-`,
`0.0.0.0/0`, account numbers and RFC1918 ranges before saving it anywhere.

## Closing the loop (Step 5)

- **Each finding** → route it by its Step 3 position. Situation **A** is a register rationale;
  **B** is a risk via `/manage-drata-control`; **C** is engineering work, and where a commitment is
  made it gets an `IRT` ticket — **created undated**, labelled, with an Original Estimate in hours,
  and any date the controlled document states quoted in the body as its `Date constraint:`. Raise it
  via `/manage-drata-control`; the convention is §1 of that skill's IRT-tickets reference.

  > **Updated 2026-09-15.** This read *"an `IRT` ticket only if a dated commitment is being made
  > against a controlled parent of record"*. Both halves were retired that day: tickets are created
  > undated, and a parent-of-record date is no longer a precondition for creating one.
- **The recurrence** → the Drata evidence **renewal schedule**, set to annual. **Neither control
  states a cadence**, so annual is a proportionality choice about evidence freshness, not a
  requirement being met. It needs no ticket anywhere.

  **Do not raise a Jira task for the recurrence.** It was considered and rejected on 2026-09-01:
  the renewal clock already fires on the artefact, so a `CYB` task would be a second chaser for
  one obligation, and the two would drift. A run produces one artefact and one approval; there is
  no multi-step work for a ticket to coordinate.
