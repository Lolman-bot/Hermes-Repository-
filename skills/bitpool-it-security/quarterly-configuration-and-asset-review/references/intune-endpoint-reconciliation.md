# Intune endpoint reconciliation

**Microsoft Intune is the asset register of record for laptops and desktops.** The wiki's Windows and
MacBook tables *support* it by holding the purchase dates Intune does not record.

Where the two disagree about **which devices exist, Intune wins.** Where they disagree about
**purchase or replacement dates, the wiki wins** — Intune has no such field.

Mobile handsets are **out of scope here** and belong to `references/manual-registers.md`.

## The two exports

Both are needed. This is structural, not a preference.

| | Export | Answers |
|---|---|---|
| **1** | Intune admin centre → **Devices** → **All devices** → **Export** → **Export all data** | Which devices exist, and each one's primary user |
| **2** | Entra ID → **Users** → **Download users**, *or* Drata → **Personnel** | Whether that primary user is still with Bitpool |

Export 1 carries ~53 columns. The ones used: `Device name`, `Serial number`, `Manufacturer`, `Model`,
`OS`, `OS version`, `Enrollment date`, `Last check-in`, `Compliance`, `Ownership`, `Encrypted`,
`Primary user UPN`, `Primary user display name`.

**Take both on the same day** and record the date against each.

> **Export 1 has no account-state column, and no variant of it does.** Re-exporting will never
> produce one. The leaver question can only be answered by joining to a second source. This is the
> whole reason the cycle takes two exports.

> **Add the `Account enabled` column in Entra *before* downloading.** Entra's *Download users*
> exports whatever columns are **visible in the list view**. The default download returns eight
> columns — `id`, `displayName`, `userPrincipalName`, `userType`, `onPremisesSyncEnabled`,
> `identities`, `companyName`, `creationType` — with no `accountEnabled`, and cannot answer the
> leaver question at all. Verified 2026-08-28: the first export looked complete and was useless.
>
> Drata → Personnel avoids the trap entirely, carrying `employmentStatus` directly
> (`CURRENT_EMPLOYEE`, `CURRENT_CONTRACTOR`, `FORMER_EMPLOYEE`, `FORMER_CONTRACTOR`,
> `SERVICE_ACCOUNT`).

Note also: `accountEnabled` is written `True`/`False` with a leading capital. Compare
case-insensitively — a lowercase `"true"` test silently matches nothing and reports every holder as a
problem.

## The cycle

### 1. Every enrolled device has a primary user

`Primary user UPN` populated on every row. A device with none has no recorded owner and fails
`A.5.9`.

### 2. Resolve every distinct primary user against account state

Join export 1's primary users to export 2. Each must resolve to an enabled account, a current
employee or contractor, or a **declared** service account.

A disabled account or a `FORMER_*` status is the finding this step exists to produce: a live,
encrypted, compliant endpoint belonging to someone who has left.

### 3. Reconcile against the wiki register, both directions

- **In Intune, not in the register** — add it. Intune wins on existence.
- **In the register, not in Intune** — *not* automatically a deletion. Mark it and confirm.
- **In both but disagreeing** on model, owner or date — record the disagreement rather than picking a
  side silently.

### 4. Check for one person holding two endpoints

Group export 1 by primary user. Anyone holding two is almost always a replacement where the old
device was never retired.

### 5. Set lifecycle status on the register

Anything not simply in service gets a **Status**: `Replaced — pending retirement`,
`Retired — confirm disposal`, `Test`, or `Stock`.

### 6. Evidence

Per `references/evidence-contract.md`. Retain **both** exports in the cycle folder.

## Running the script

```bash
wsl -e bash -lc 'python3 "<skill>/scripts/reconcile_intune.py" --devices "<intune.csv>" --users "<entra.csv>"'
```

Windows paths become `/mnt/c/...` inside WSL. Native Windows `python`/`python3` are broken Microsoft
Store stubs and will exit without running.

Add `--register-labels` with a newline-separated list of the labels currently on the wiki register to
get the both-directions comparison in step 3.

## The four traps

**A stale check-in is not a leaver signal.** Board members' laptops sit idle for months by design,
miss their compliance grace period, and report `Noncompliant` with a check-in the better part of a
year old — indistinguishable from an abandoned device. On the 2026-08-28 run, the single most
leaver-looking endpoint in the estate (305 days idle, non-compliant since its grace expired) belonged
to a **current employee and board member.** Resolve employment status from export 2. Never from
check-in age, never from compliance state.

**A replaced laptop that is still enrolled is invisible.** It reports compliant, encrypted and
checking in — identical to a device in active use. No Intune view flags it and no compliance test
fails. **One person holding two endpoints is the only signal**, which is why step 4 is a deliberate
step rather than something expected to fall out of the list.

**A service account can be a primary user.** A populated `Primary user UPN` does not mean a person
owns the device. Test endpoints held by service accounts are still corporate-owned assets under
`A.5.9` — record them with status `Test`, visible in the count, not dropped because nobody owns them
personally.

**A device that is Entra-joined but never enrolled is invisible to export 1**, which lists only
Intune-managed records. It is caught only from the register side, which is why step 3 runs both
directions.

## What this does not rely on

**Drata's device list is not the endpoint inventory and must not be used to reconcile the export.**
It is personnel-scoped, so it includes contractor-owned devices Bitpool does not own.

Drata **Personnel** is a different matter and is a valid source for step 2. The distinction is
between Drata's device list, which is not authoritative here, and its employment records, which are.

## Naming

Enrolled endpoints are labelled `LAPTOP-<serial>`. Older devices predate the format — names like
`MSI-LAPTOP` or `ROSS-BITPOOL` are expected on the older fleet and are **not** defects; they are
renamed as devices are replaced. macOS cannot be renamed by an Intune naming policy and must be
renamed by hand after enrolment.

`Department-Type-OS-Serial` is **withdrawn**. Do not apply it, and do not treat an endpoint that does
not match it as mislabelled.
