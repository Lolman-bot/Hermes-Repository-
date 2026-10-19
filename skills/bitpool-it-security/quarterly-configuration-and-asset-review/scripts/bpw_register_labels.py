#!/usr/bin/env python3
"""Extract endpoint labels from the BPW hardware asset inventory page.

The wiki page IS the register for physical assets. This turns its endpoint tables into a
flat label list so `reconcile_intune.py --register-labels` can run the
in-register-but-not-in-Intune direction of the comparison.

Only the three endpoint fleets are extracted, because only those have an Intune counterpart
to reconcile against. Monitors, docks, printers, network gear and access cards have no live
system behind them at all -- they are confirmed by the physical walk, not by a diff.

**Handset labels are rewritten to their Intune form.** The register labels a handset
`IT-MOB-APP-<serial>` per the naming convention, but Intune enrols it as `iPhone-<serial>`.
Comparing the raw strings reports every handset as missing from both sides at once, which
looks like a catastrophic register failure and is purely a naming mismatch.

Pure stdlib. Run through WSL.

Usage:
    bpw_register_labels.py hardware-asset-inventory.md -o register-labels.txt
"""

import argparse
import re
import sys

# Only these sections carry endpoints Intune can be reconciled against.
FLEET_HEADINGS = (
    "## Current Windows fleet",
    "### Windows endpoints with no Intune record",
    "## Current MacBook fleet",
    "## Current iPhone fleet",
)
# Any heading at this level or above ends the section we are in.
HEADING = re.compile(r"^#{2,3} ")

HANDSET = re.compile(r"^IT-MOB-APP-(.+)$", re.I)


def extract(text):
    labels, current, seen_header = {}, None, False
    for line in text.splitlines():
        stripped = line.strip()

        if HEADING.match(stripped):
            current = stripped if stripped in FLEET_HEADINGS else None
            seen_header = False
            continue

        if current is None or not stripped.startswith("|"):
            continue

        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells:
            continue

        # Skip the header row and the |---|---| separator beneath it.
        if cells[0].lower() == "label":
            seen_header = True
            continue
        if set(cells[0]) <= {"-", ":"} and cells[0]:
            continue
        if not seen_header:
            continue

        label = cells[0].replace("`", "").replace("**", "").strip()
        if not label:
            # A blank label is a real state on this page -- an asset Bitpool owns that was
            # never labelled. Count it rather than dropping it silently.
            labels.setdefault("(unlabelled)", []).append(current)
            continue

        m = HANDSET.match(label)
        if m:
            label = "iPhone-%s" % m.group(1)
        labels.setdefault(label, []).append(current)
    return labels


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", help="the hardware-asset-inventory markdown")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()

    with open(a.page, encoding="utf-8-sig") as fh:
        labels = extract(fh.read())

    if not labels:
        sys.exit("ERROR: no endpoint labels found. Have the fleet headings been renamed?\n"
                 "Expected one of:\n  " + "\n  ".join(FLEET_HEADINGS))

    real = {k: v for k, v in labels.items() if k != "(unlabelled)"}
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write("# Endpoint labels from the BPW hardware asset inventory.\n")
        fh.write("# Handset labels rewritten IT-MOB-APP-<serial> -> iPhone-<serial>.\n")
        for label in sorted(real):
            fh.write(label + "\n")

    by_section = {}
    for label, sections in labels.items():
        for s in sections:
            by_section.setdefault(s, []).append(label)
    for section in FLEET_HEADINGS:
        print("  %-46s %d" % (section.lstrip("# "), len(by_section.get(section, []))))
    if "(unlabelled)" in labels:
        print("  %-46s %d  <-- rows with no label recorded"
              % ("unlabelled rows", len(labels["(unlabelled)"])))
    print("\nwritten: %s  (%d labels)" % (a.out, len(real)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
