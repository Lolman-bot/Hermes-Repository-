# Drata behaviour this skill relies on

> Relocated verbatim from this skill's `SKILL.md` when it was ported to Hermes; `SKILL.md` keeps the
> route and a one-line summary of each rule, and this file is the full text. Rule numbers (rule 1–14)
> refer to `references/vendor-rules.md`; §1–§3 to `references/workflows.md`; "the behaviour table" to
> `references/drata-vendor-behaviour.md`.

Vendor-specific. Connection-level quirks belong in `/ask-drata`, not here — and when you confirm a
new one, add it there.

| Behaviour | What to do about it |
|---|---|
| **No natural-language vendor search exists.** Not "unreliable" — the tool has no `query` parameter at all | Page, or use the structured filters |
| **`latestSecurityReviews` expand is unreliable** — returned `[]` for AWS on 2026-09-03 while `Drata_listVendorSecurityReviews` reported `totalCount: 2`, both `COMPLETED` | Always take review history from the reviews endpoint |
| **`breakdown.current` vs `totalCount`** | `totalCount` counts archived. Report `breakdown.current` as the headline |
| **`size=50` exceeds the response limit** | Page smaller, or use the `size=1` + filter trick for counts |
| **`cost` is in cents** | `"12000000"` is $120,000 |
| **`status` has `APPROVED`, and so does a security review `decision`** — two different things | Vendor `status` is lifecycle. `APPROVED_WITH_CONDITIONS` is a review `decision` and does not appear on the vendor at all |
| **`critical` and `impact_level` disagree in the data** | AWS was `critical: false` at `impact_level: CRITICAL`. `impact_level` is the one Bitpool uses; `critical` is on the wipe list |
| **`is_sub_processor_active` is `[Deprecated]`** in the schema | Wipe it. Use `is_sub_processor` |
| **`renewalDateStatus` lies about whether a review has happened** | It reads `COMPLETED` whenever the renewal date is in the future — **including on a vendor that has never been reviewed at all.** Verified 2026-09-04 on `GitBook` (`136`): created with `renewalDate: 2027-09-04` and zero security reviews, and the field came back `COMPLETED`. Such a vendor appears in neither the `OVERDUE` nor the `DUE_SOON` filter. Read review history from `Drata_listVendorSecurityReviews`, never from this field |
| **A first review IS trackable — via `status`, not the renewal fields** | `status: UNDER_REVIEW` is the state for a vendor in use whose assessment is not finished, and it **is filterable**: `Drata_listVendors(status=["UNDER_REVIEW"])` returned exactly the one such vendor on 2026-09-04. Corrected the same day — this skill had claimed a first-review obligation "cannot be tracked in Drata", which was wrong. The renewal machinery does not track it; `status` does. So set `UNDER_REVIEW` deliberately, and treat an `IRT` ticket as carrying the *dated commitment*, not as the only record that the review is outstanding |
| **`create:vendor` is granted** | Verified 2026-09-04. A missing-custom-field `400` proves it, since a scope failure would `403` before validation |
