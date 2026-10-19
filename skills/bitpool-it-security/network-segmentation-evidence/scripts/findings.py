"""Findings are COMPUTED from the model, never hand-written.

SCOPE — narrowed 2026-09-01, and the narrowing is the point.

This artefact is evidence for exactly two controls:

  DCF-748  segmentation and/or other techniques to isolate portions of the
           environment, and to CONTROL TRAFFIC BETWEEN THEM based on security
           and business needs
  DCF-22   a documented representation of SYSTEM BOUNDARIES and CONNECTIONS TO
           EXTERNAL NETWORKS

A finding is emitted ONLY if it bears on one of those. The first version also
reported flow-log coverage, unrestricted egress, regional VPC spread and unused
default VPCs. Every one of those belongs to a different control -- logging,
DCF-85, DCF-20 -- and none was in scope of the review that produced the pack.

That is not harmless. An evidence artefact that volunteers findings against
controls it did not assess hands an auditor questions nobody has answered, and
invites them into a scope the review never covered. **Adding a check here is a
scope decision, not an improvement.** Before adding one, name which of the two
controls' words it tests. If you cannot, it does not belong.

Scope COVERAGE is different from a finding and stays: an account that was never
surveyed means the segmentation claim does not cover it, which bounds the claim
rather than volunteering an unrelated issue.
"""


def _allvpcs(model):
    return [(a, v) for a in model["accounts"] for v in a["vpcs"]]


def compute(model):
    f = []
    live = [(a, v) for a, v in _allvpcs(model) if v["enis"] > 0]

    # --- scope: the claim cannot cover what was never looked at --------------
    # Bounds the DCF-748 claim. Not a DCF-20 asset-inventory finding, and must
    # not be cited as one.
    unc = model.get("uncovered_accounts") or []
    if unc:
        names = ", ".join(f'{x.get("Name", "?")} ({x.get("Id")})' for x in unc)
        f.append({"sev": "high", "ctl": "DCF-748 · DCF-22",
                  "title": f"{len(unc)} accounts are neither surveyed nor excluded",
                  "body": f'AWS Organizations reports {model.get("org_account_count")} active accounts. '
                          f'{len(unc)} have no local profile and carry no written exclusion: {names}. '
                          f'Nothing here describes their segmentation, and nothing says it should not.',
                  "test": "Segmentation can only be claimed for what was examined. An account neither "
                          "surveyed nor excluded leaves the boundary of this claim undefined."})

    # --- DCF-22: a segment carrying live workloads that no document shows -----
    for a, v in live:
        if v["default"]:
            svc = ", ".join(f"{k} x{n}" for k, n in
                            sorted(v["eni_types"].items(), key=lambda x: -x[1]))
            f.append({"sev": "high", "ctl": "DCF-748 · DCF-22",
                      "title": f'Default VPC "{v["name"]}" carries live workloads',
                      "body": f'{v["id"]} ({v["cidr"]}) in {a["profile"]}/{v["region"]} holds '
                              f'{v["enis"]} live network interfaces ({svc}). It is the account default '
                              f'network, was never designed as a segment, and appears in no '
                              f'architecture document — so it is both an undocumented system boundary '
                              f'and an unplanned one.',
                      "test": "DCF-22 asks that system boundaries be documented. A segment nobody "
                              "drew is one nobody is reasoning about."})

    # --- DCF-748: paths between segments that should not carry traffic --------
    names = {v["id"]: v["name"] for _, v in _allvpcs(model)}
    for p in model["peerings"]:
        if p.get("external") or p["a_owner"] != p["b_owner"]:
            continue
        pair = {names.get(p["a_vpc"]), names.get(p["b_vpc"])}
        if pair == {"production", "development"}:
            f.append({"sev": "high", "ctl": "DCF-748",
                      "title": "Production and development are peered, with active routes both ways",
                      "body": f'{p["id"]} — tagged "{p["name"]}", state {p["state"]}. '
                              f'{p["a_cidr"]} and {p["b_cidr"]} each carry a route to the other. The '
                              f'path is whole-network to whole-network, not scoped to the services '
                              f'that depend on it.',
                      "test": "DCF-748 asks that traffic between segments be controlled based on "
                              "security and business needs. A stated need makes the path legitimate; "
                              "its breadth is what remains to be justified or narrowed."})

    # --- DCF-748: traffic between segments is not actually restricted --------
    exp = [(a, v, e) for a, v in _allvpcs(model) for e in v["exposures"]]
    if exp:
        groups = {e["sg"] for _, _, e in exp}
        by_scheme = {}
        for _, _, e in exp:
            by_scheme.setdefault(e["scheme"], set()).add(e["sg"])
        svcs = sorted({s for _, _, e in exp for s in e["services"]})
        inet = by_scheme.get("internet-facing", set())
        parts = "; ".join(f"{len(g)} on {k}" for k, g in
                          sorted(by_scheme.items(), key=lambda x: -len(x[1])))
        f.append({"sev": "high" if inet else "medium", "ctl": "DCF-748",
                  "title": f"Data-store ports are unrestricted by source on {len(groups)} security groups",
                  "body": f'{len(exp)} rules across {len(groups)} groups, affecting {", ".join(svcs)}. '
                          f'By attachment: {parts}. '
                          + ("No data store is reachable from the internet. " if not inet else
                             f"{len(inet)} group(s) sit on an internet-facing load balancer. ")
                          + "What is absent is the restriction that would bound which segments can "
                            "reach the data tier at all.",
                  "test": "This is the “control traffic between them” half of DCF-748. An unrestricted "
                          "source range on an internal load balancer is not internet exposure — it is "
                          "the absence of any boundary between segments that can already route there."})

    # --- DCF-748: which layer actually enforces separation -------------------
    nn = [(a, v) for a, v in live if not v["nacl_filters"]]
    if nn and len(nn) == len(live):
        f.append({"sev": "low", "ctl": "DCF-748",
                  "title": "Security groups are the sole enforcement layer between segments",
                  "body": f"All {len(nn)} live networks run the default allow-all network ACL for both "
                          f"IPv4 and IPv6, so no filtering happens at that layer. Separation between "
                          f"segments rests entirely on security groups.",
                  "test": "Recorded so a single enforcement layer reads as a design choice rather than "
                          "an oversight. DCF-748 permits “segmentation and/or other techniques”, so "
                          "one layer satisfies it — provided it is stated."})

    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(f, key=lambda x: order[x["sev"]])
