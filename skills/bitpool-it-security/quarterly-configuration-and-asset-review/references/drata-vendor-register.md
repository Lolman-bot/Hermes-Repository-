# Drata vendor register

**Drata is the register of record for SaaS vendors and third parties.** That is the whole of its
inventory role at Bitpool.

## The boundary — read this before anything else

| Drata holds | Is it the register? |
|---|---|
| **Vendors** | **Yes.** This is the one asset class Drata owns |
| Devices | **No.** Personnel-scoped, so it includes contractor-owned kit Bitpool does not own. Answers "what accesses our data", not "what do we own"; `A.5.9` asks the second. Endpoints are Intune's |
| Cloud resources | **No.** Tags are the register. The Azure connection was reporting a single asset out of the full estate and had gone eighteen months without updating |
| Personnel | Not an asset class at all — people are not assets. But the records **are** a valid source for employment status, which the Intune cycle uses |
| Policies | Documented information under clause **7.5**, not `A.5.9` assets |

**Do not delete the Drata AWS connection.** Roughly 35 enabled infrastructure monitoring tests read
from it. It stays connected; its asset list simply is not the register.

## Access

Read-only. This skill is **read-only by policy** against Drata — `Drata_listVendors`,
`Drata_getVendor`, `Drata_listVendorDocuments`, `Drata_listVendorSecurityReviews`.

The write verbs exist on the connection and it will not refuse them, because OAuth scope is
account-level. Only `/manage-drata-control` and `/manage-drata-risks` are permitted to use them. The
authority is the *Drata write policy by skill* table in `/ask-drata`, never a skill's own claim.

**Any vendor record that needs changing gets listed for the user to change**, not written from here.

## The cycle

### 1. List the vendors

Read the full register. **Paginate properly** — list mode is easy to under-read as complete, and a
truncated read reports a tidy register that isn't. `/ask-drata` carries the connection's quirks,
including that AI `query` search fails account-wide and silently discards list filters.

### 2. Check each record for the things that go stale

- **A security owner**, and one who is still here. A vendor owned by a leaver has no owner.
- **Risk or criticality** set, not left at the default.
- **A security review** where the vendor's criticality calls for one, and its date.
- **Status** — vendors no longer in use marked accordingly rather than left active.

### 3. Reconcile against what Bitpool actually uses

The register drifts in both directions:

- **In use, not in the register** — a SaaS tool adopted without going through the register. This is
  the finding that matters most, because an unregistered vendor has had no review.
- **In the register, no longer used** — mark as inactive. Do not delete: the record that Bitpool once
  used it, and what review it had, is worth keeping.

Sources for what is genuinely in use: the identity provider's application list, and the AI spend and
vendor billing view. Name whichever you used and its date — a reconciliation against nothing is just
the register agreeing with itself.

### 4. Evidence

Per `references/evidence-contract.md`. Retain the vendor list as extracted, in the cycle folder.

<!-- TODO: needs owner input — Bitpool's threshold for which vendor criticality requires a security
     review, and the review cadence, are not recorded here. Read them from the Third Party /
     Vendor Management Policy and add them to step 2 rather than inferring a threshold. -->

## Status flags that lie

Drata carries several fields that read as authoritative and are not. `/ask-drata` is the living
reference for which ones. Before reporting a vendor as compliant, reviewed or ready on the strength
of a single flag, check that file — this cycle's whole value is that it does not simply restate what
the tool already claims.
