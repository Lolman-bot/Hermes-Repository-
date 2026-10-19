#!/usr/bin/env python3
"""Diff two asset-register snapshots and report what changed without being accounted for.

This is the point of retaining snapshots. A live tag query only ever shows today, so it
cannot answer "what appeared since June, and did anyone notice". Two dated snapshots can.

Reports four sets. The first two are the review's actual output:

    ADDED     in the new snapshot, absent from the old -- a new asset nobody has
              dispositioned yet
    REMOVED   in the old, absent from the new -- decommissioned, or quietly deleted.
              Record the removal; never let a row vanish silently
    CHANGED   same id, different attributes
    REGRESSED a unit that HELD all required keys and no longer does. Called out
              separately because it is a register defect rather than an estate change --
              the asset still exists, but the register stopped describing it

A clean diff is a result, not an absence of one. Print it and record it.

Pure stdlib. Run through WSL.

Usage:
    diff_snapshots.py old.json new.json
    diff_snapshots.py old.json new.json --format markdown   # paste into the ticket
"""

import argparse
import json
import os
import sys

REQUIRED = ["OwnerGroup", "Purpose", "Criticality", "DataClassification", "IsPersonalData"]

# Attributes that describe placement rather than ownership. A change here is worth seeing
# but is not a governance regression.
POSITIONAL = {"resourceGroup", "location", "visibility", "archived"}


def load(p):
    with open(p, encoding="utf-8-sig") as f:
        d = json.load(f)
    if "items" not in d:
        sys.exit("%s is not a snapshot (no 'items' key). Produce it with snapshot.py." % p)
    return d


def complete(attrs):
    return all(attrs.get(k) for k in REQUIRED)


def coverage(snap):
    """(units expected to carry the required keys, how many carry all of them).

    Derived from items on every call. Azure tags at resource-group level, so its
    resources are not expected to carry keys and counting them would invent a shortfall.
    """
    units = [i for i in snap["items"].values()
             if i.get("unit") == "group" or
             (snap.get("register") != "azure" and i.get("unit") in ("resource", "repository"))]
    return len(units), sum(1 for i in units if complete(i.get("attrs", {})))


def diff(old, new):
    o, n = old["items"], new["items"]
    ok, nk = set(o), set(n)

    added = sorted(nk - ok, key=lambda k: (n[k].get("unit", ""), (n[k].get("name") or "").lower()))
    removed = sorted(ok - nk, key=lambda k: (o[k].get("unit", ""), (o[k].get("name") or "").lower()))

    changed, regressed = [], []
    for k in sorted(ok & nk, key=lambda k: (n[k].get("unit", ""), (n[k].get("name") or "").lower())):
        oa, na = o[k].get("attrs", {}), n[k].get("attrs", {})
        deltas = []
        for key in sorted(set(oa) | set(na)):
            if oa.get(key) != na.get(key):
                deltas.append((key, oa.get(key), na.get(key)))
        # A rename is a change, not a delete plus an add -- which is why ids are the key.
        if o[k].get("name") != n[k].get("name"):
            deltas.insert(0, ("name", o[k].get("name"), n[k].get("name")))
        if deltas:
            changed.append((k, deltas))
        if complete(oa) and not complete(na):
            lost = [key for key in REQUIRED if oa.get(key) and not na.get(key)]
            regressed.append((k, lost))

    return added, removed, changed, regressed


def render(old, new, added, removed, changed, regressed, fmt):
    md = fmt == "markdown"
    B = "**" if md else ""
    out = []
    w = out.append

    w("%sAsset register diff -- %s%s" % (B, new["register"], B))
    w("")
    if md:
        w("| | Snapshot | Captured | Items |")
        w("|---|---|---|---|")
    for label, s in (("previous", old), ("this cycle", new)):
        if md:
            w("| %s | `%s` | %s | %d |" % (label, s.get("cycle"), s.get("captured"), len(s["items"])))
        else:
            w("  %-12s cycle=%-9s captured=%-22s items=%d"
              % (label, s.get("cycle"), s.get("captured"), len(s["items"])))
    w("")

    # Recomputed from items, never read from the stored `coverage` block. A snapshot that
    # was hand-edited after capture would otherwise report the coverage it had at capture
    # time, which is exactly the number a reader would trust and exactly the one that lies.
    ob, oc = coverage(old)
    nb, nc = coverage(new)
    if ob or nb:
        w("Required-key coverage: %d of %d  ->  %d of %d%s"
          % (oc, ob, nc, nb, "   <-- WENT BACKWARDS" if nc < oc else ""))
        w("")

    def block(title, rows, body):
        w("%s%s -- %d%s" % (B, title, len(rows), B))
        if not rows:
            w("  none")
        else:
            for r in rows:
                for line in body(r):
                    w("  " + line)
        w("")

    block("ADDED (not yet accounted for)", added,
          lambda k: ["+ %-12s %-44s %s" % (new["items"][k].get("unit", ""),
                                           new["items"][k].get("name", ""),
                                           new["items"][k].get("type", ""))])

    block("REMOVED (record the removal, do not delete the row silently)", removed,
          lambda k: ["- %-12s %-44s %s" % (old["items"][k].get("unit", ""),
                                           old["items"][k].get("name", ""),
                                           old["items"][k].get("type", ""))])

    def changed_body(item):
        k, deltas = item
        lines = ["~ %-12s %s" % (new["items"][k].get("unit", ""), new["items"][k].get("name", ""))]
        for key, ov, nv in deltas:
            mark = "" if key in POSITIONAL else "  *"
            lines.append("      %-22s %r -> %r%s" % (key, ov, nv, mark))
        return lines

    block("CHANGED", changed, changed_body)

    block("REGRESSED -- required keys lost (register defect)", regressed,
          lambda item: ["! %-44s lost: %s" % (new["items"][item[0]].get("name", ""),
                                              ", ".join(item[1]))])

    if not (added or removed or changed or regressed):
        w("No change this cycle. That is the evidence the review ran -- record it in full,")
        w("with the counts above, rather than writing \"no change\".")

    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("old", help="previous cycle's snapshot")
    ap.add_argument("new", help="this cycle's snapshot")
    ap.add_argument("--format", choices=["text", "markdown"], default="text")
    a = ap.parse_args()

    old, new = load(a.old), load(a.new)
    if old["register"] != new["register"]:
        sys.exit("refusing to diff %s against %s -- different registers."
                 % (old["register"], new["register"]))

    # A snapshot diffed against ITSELF reports a clean run: no additions, no removals,
    # nothing regressed. That is the most convincing wrong answer this tool can produce,
    # because it looks exactly like the outcome everyone hopes for and reads as evidence
    # the review was done. Refuse it rather than print it.
    #
    # Two ways it happens, both mundane: the same path passed twice, or this cycle's file
    # copied over last cycle's in the evidence folder. Identity is checked on content, not
    # on path, so a renamed copy is caught too.
    if os.path.realpath(a.old) == os.path.realpath(a.new):
        sys.exit("refusing to diff a snapshot against itself (%s).\n"
                 "A self-diff always reports no change, which is indistinguishable from a\n"
                 "clean cycle. Supply the PREVIOUS cycle's snapshot as the first argument."
                 % a.old)
    if old.get("captured") and old["captured"] == new.get("captured") \
            and old.get("items") == new.get("items"):
        sys.exit("refusing to diff: both files were captured at %s and hold identical\n"
                 "items -- this is the same snapshot under two names, and it would report\n"
                 "no change. Supply the PREVIOUS cycle's snapshot as the first argument."
                 % old["captured"])
    if old.get("cycle") == new.get("cycle"):
        sys.stderr.write(
            "warning: both snapshots are labelled cycle=%s. Diffing within one cycle is\n"
            "         valid for a re-run, but if you meant to compare quarters, one of\n"
            "         these is the wrong file.\n\n" % old.get("cycle"))

    added, removed, changed, regressed = diff(old, new)
    print(render(old, new, added, removed, changed, regressed, a.format))

    # Exit 0 always. A diff with findings is a successful run, not a failure.
    return 0


if __name__ == "__main__":
    sys.exit(main())
