# Control scope — what this pack is for, and what each control asks

Relocated from the skill's main file. Read it before deciding whether to generate a pack, and before
adding or changing anything the pack reports.

## The distinction this skill exists to hold

Two jobs look identical and are not:

| | Understanding the network | Evidencing the network |
|---|---|---|
| Question | "What does it look like right now?" | "What did we review and approve, and when?" |
| Right answer | **Query AWS.** Any document is stale the moment it is written | **A dated snapshot.** You cannot approve a live query |
| Tool | `/aws-query`, or the CLI directly | **this skill** |

Clause **7.5.3(a)** requires documented information to be *"available and suitable for use, where
and when it is needed."* A diagram that no longer matches the network is not suitable for use,
however recently someone signed it — Bitpool already has the worked example, where the C4
architecture set carried a `last_reviewed` date fifteen months newer than its content because the
date recorded a file migration rather than a technical review.

**So: never generate this pack to answer an engineering question.** If someone wants to know what
the network looks like, point them at AWS. This artefact exists to be dated, attached and relied on.

## The two controls want different things — do not conflate them

Corrected 2026-09-01, after this skill spent its first version treating them as one obligation and
propagating a management-approval requirement onto DCF-748, where it never existed. **DCF-22 was
then narrowed the same day** so it no longer carries one either.

| | **DCF-22 — Network Diagram** | **DCF-748 — Segmentation of Networks** |
|---|---|---|
| Asks for | A diagram that documents system boundaries and external connections | Segmentation *"to isolate portions of the environment and to control traffic between them **based on security and business needs**"* |
| Cadence | **None stated** | **None stated** |
| Approval | **None required** | **None required** |
| Satisfied by | This pack, generated and held in Drata | Segmentation that demonstrably follows stated needs |

> **Do not reintroduce a review-and-approval clause into DCF-22.** It carried one until 2026-09-01
> — *"reviewed and approved by management at least annually and updated as necessary when there are
> changes to the environment"* — which was Drata template language with SOC 2 lineage. It appears in
> neither A.8.20 nor A.8.22, and the Network Security Policy requires none of it. The policy now
> states that the representation is *generated from live cloud infrastructure state rather than
> maintained by hand*, which answers clause 7.5.3(a) more directly than a review cadence.
>
> **One forward-looking caveat.** DCF-22 also links SOC 2 **CC2.1**, which is currently **out of
> scope** — Bitpool has zero in-scope SOC 2 requirements, verified 2026-09-01. CC2.1's points of
> focus include *"Documents Data Flow"* and information being *"timely, current… reviewed"*. If
> Bitpool ever brings SOC 2 into scope, both the data-flow representation and the currency language
> come back, and this narrowing must be revisited.

**DCF-748 is risk-based by construction.** It does not demand total isolation; it demands that
isolation follow security and business needs. A documented business need is therefore not an
exception to the control — it is the control being met.

**The Network Security Policy does not require management approval of the diagram**, only that it
is *"kept up to date through periodic reviews"*. It does require, of every allowed path:

> "All services, protocols, and ports allowed must be identified, documented, approved, and have a
> defined business need." … "Inbound firewall rules must be approved and documented by an
> authorised person, and include the business need in the documentation."

So the approver Bitpool's own policy names is **an authorised person**, with exceptions going to
the Information Security Team. Not "management", and not a specific job title. Do not introduce one
into any artefact this skill produces.

## The pack reports on two controls and nothing else

Narrowed 2026-09-01. Its first version also reported VPC flow-log coverage, unrestricted egress,
regional VPC spread and unused default VPCs — belonging to logging, `DCF-85` and `DCF-20`
respectively, none of which the review that produced the pack had assessed.

**That is not harmless breadth, it is added audit surface.** An evidence artefact that volunteers
findings against controls it did not assess hands an auditor questions nobody has answered, and
invites them into a scope the review never covered. The risk owner's words, 2026-09-01: *"it just
exposes us more."*

**Adding a check is a scope decision, not an improvement.** Before adding one, name which of these
two sets of words it tests:

- `DCF-748` — segmentation to isolate portions of the environment, and **to control traffic
  between them** based on security and business needs.
- `DCF-22` — a documented representation of **system boundaries** and **connections to external
  networks**.

If you cannot point at the phrase, it does not belong in the pack. Note what a *scope statement*
is not: recording which accounts and regions were swept bounds the claim and stays, because
segmentation cannot be claimed for what was never examined.

## Where everything lives

| Thing | Home | Why there |
|---|---|---|
| **Scripts** | `scripts/` in this skill | The scripting content lives with the skill that runs it |
| **Overflow** | `security-tools` repo | Anything too heavy to ship inside a skill |
| **Generated pack, `adjacency.md` + raw dump** | **Drata only**, attached to `DCF-748` and `DCF-22` | All three carry internet-facing load balancer DNS names, open ports, security group IDs and internal CIDRs — `adjacency.md` included, which is why it is evidence and not a wiki diagram. Drata is the single home — it is access-controlled, it is where an auditor looks, and its renewal clock chases the artefact |
| **Process hub** | Bitpool Private Wiki, `security-documentation` → `compliance/network-segmentation-evidence.md` | The human-readable stub: what this is, how it runs, where output goes |
| **Current network state** | Bitpool Private Wiki, `it-documentation` → `notes/networking/network-segmentation.md` | The verified position, separate from the process that verifies it |
| **Recurrence** | The Drata evidence **renewal schedule**, set to annual | No Jira ticket. The renewal clock watches the artefact and marks the control not ready when it lapses — a calendar task would be a second chaser for the same thing |
