# Manual registers — the physical walk

One sub-task covering **the hand-maintained hardware classes**, because they share one register, one maintenance method
and one walk of the office:

- Mobile handsets
- Monitors and docking stations
- Printers, AV and office equipment
- Other computing equipment — NUCs, tablets not in Intune
- Office network equipment
- Access cards
- Portable storage media — USB drives, encrypted or not

The register is the *Hardware assets* page on the wiki, under the *Asset register* parent. Unlike the
cloud registers, **this page IS the inventory** — nothing else records that these assets exist. There
is no live system to reconcile against, which is exactly why it needs a physical check.

## A further class — non-human identities

On the register's *Digital assets* page, under `## Non-human identities`, added 2026-09-18.
Hand-maintained the same way as the hardware tables, so it belongs to this reference — but **it is
not part of the office walk**, and the difference matters:

| | Hardware sections | Identity sections |
|---|---|---|
| What proves a row is real | Walking to the desk and reading the label | An Entra export |
| Live counterpart | None | Entra — every identity outside the `Drata Sync Group` |
| Where it is checked | This sub-task, on foot | The Microsoft dump, then sub-task 6 |

It covers service accounts, shared mailboxes, automation identities, admin and break-glass accounts,
test identities, guests and room mailboxes — **every Entra identity that is not a member of staff**.
Drata's sync group rule excludes anything tagged `jobTitle = "Service Account"` plus guests, so all
57 of them are invisible to Drata by design and were in no register at all before that date.

**Each identity needs a recorded reason for existing and a named owner.** When the register was
seeded, **27 of 57 had no recorded purpose and 10 of those were enabled** — live credentials nobody
had written down a reason for. Those rows are the work.

**Never infer a purpose from an account name.** `edge-alarms@` plausibly delivers edge-device
alarms; recording that as fact without confirming it puts an invention in the register that the next
reader cannot distinguish from a checked answer. `Unrecorded` is the honest value and it is
countable, which is what makes it get fixed.

## Ownership model

**Monitors and docking stations are assigned to a desk, not a person.** The desk resolves to its
occupant, who is the owner. An **empty desk** or the **hot desk** is owned by **IT**, labelled
`IT - Empty` and `IT - Hot desk`.

This is the point of the model: a desk outlives its occupant, so when someone moves or leaves, the
desk stays put and its equipment stays with it. Nothing is left owned by a person who has gone.

**Laptops, MacBooks and handsets are not desk-scoped** — they travel with the person and live in
their own tables.

Printers, AV and network equipment are owned by **IT** except where an item is held by a named
person, who then owns it. Access cards are owned by IT and issued to an individual.

Desk-to-occupant comes from the seating chart page on the wiki. **Change an occupant there and the
ownership of that desk's equipment changes with it** — update both in the same pass.

## Labels

The label — not the model, not the holder — is the identifier a row is keyed on. **Always UPPERCASE.**

| Scheme | Used for |
|---|---|
| `LAPTOP-<serial>` | Intune-enrolled endpoints. The Intune device name *is* the label |
| `Department-Type-Brand-Serial` | Everything else — e.g. `IT-MON-BEN-ETRCK0358201Q` |
| The number printed on the card | Access cards, because that is what the door reader matches |

Where no serial can be read, assign a random 8-digit string prefixed `UKWN` — e.g. `UKWN32596586`.

`Department-Type-OS-Serial` is **withdrawn**. Do not apply it and do not treat an asset that does not
match it as mislabelled.

The type and brand code lists live on the *Device Asset Naming/Labeling Convention* page. **A code
not on that list is a gap in the page, not a mislabelled asset** — add the code.

## The cycle

### 1. Walk the office against the register

Desk by desk. For each item, confirm the label on the unit matches a row, and that the row's desk and
therefore owner are right. An item with no readable label gets one.

### 2. Reconcile both directions

- **On a desk, not on the register** — add it.
- **On the register, not found** — do not delete. Mark it and confirm: returned to IT stock, disposed
  of, or genuinely missing. A row deleted because nobody could find it that afternoon destroys the
  only record Bitpool owned the item.

### 3. Confirm IT stock

Everything held by IT and not issued. Stock is where returned and superseded kit accumulates, so it
drifts fastest and is the easiest section to leave stale.

### 4. Confirm the access cards

Every active card against its holder, and every spare against the spare count. A card belonging to a
leaver that was never returned is the finding this step exists to produce.

Contractors do not get access cards. Where a contractor holds one as a historical exception, it stays
recorded as an exception rather than being quietly normalised.

### 5. Confirm the portable storage media

Every row of the *Portable storage media* table against the drive itself — its label, whether it is
encrypted, and whether it may hold sensitive data or PII — and every drive found in the office
against a row. A drive with no row, a row whose drive cannot be found, and a drive in use whose row
says otherwise are the findings. Which unencrypted drives need an exemption is set on the wiki's
*Portable media encryption policy* page; check each has one.

### 6. Mobile handsets

The register is authoritative for mobile. **Handset enrolment in Intune is a discontinued process** —
a handful carry legacy enrolments, and those are being wound down.

Where a handset *does* still carry one, Intune is the better source for who holds it, and has
resolved handsets the register had recorded as lost with leavers. Use it as corroboration when it
exists.

**Do not enrol a handset to make the fleet consistent.** That reverses a deliberate decision.

### 7. Set lifecycle status and record the evidence

Anything not simply in service gets a **Status**: `Replaced — pending retirement`,
`Retired — confirm disposal`, `Test`, or `Stock`. Then evidence per
`references/evidence-contract.md`.

## Traps

**This register has no live counterpart, so nothing will contradict a wrong row.** The cloud
registers self-correct because the tag is the asset. Here a row can be wrong for years and look
exactly like a right one. The physical walk is the only control — a desk check done from memory is
not a check.

**One unit, several labels, or one label on several units.** Duplicate labels do occur. Record the
duplicate as found rather than picking one and moving on, so the physical fix can be done against a
written record.

**A single record covering several units.** Mesh Wi-Fi access points and similar multi-unit kit get
recorded once. Each physical unit needs its own label and row, or the count is wrong.

**Do not assess OT or edge-device posture from this register.** It covers office equipment. Edge
devices deployed at customer sites are a separate estate with its own documentation, and answering
from here overstates coverage.
